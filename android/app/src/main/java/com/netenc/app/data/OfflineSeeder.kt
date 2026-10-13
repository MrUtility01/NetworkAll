package com.netenc.app.data

import android.content.Context
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import kotlinx.coroutines.sync.Mutex
import org.json.JSONObject
import org.json.JSONArray
import java.io.BufferedInputStream
import java.util.zip.GZIPInputStream
import java.security.MessageDigest
import java.time.Instant

object OfflineSeeder {
    private const val META_SEEDED = "offline_seeded_v21"
    // MainActivity, sync and the catalog can all request seeding during startup.
    // Serialize them so no screen observes a half-imported curriculum.
    private val seedMutex = Mutex()

    suspend fun ensureSeeded(context: Context): Int {
        seedMutex.lock()
        try {
            return withContext(Dispatchers.IO) {
            val dao = AppDatabase.get(context).lessonDao()
            val existing = dao.countActive()
            val filled = if (existing > 0) dao.countFilled() else 0
            if (dao.getMeta(META_SEEDED) == "1" && existing > 5000 && filled > 2000) {
                return@withContext existing
            }
            val json = readCurriculumAsset(context) ?: throw IllegalStateException("فایل curriculum_index.json.gz در بسته NetworkAll وجود ندارد")
            val root = JSONObject(json)
            val assetVersion = root.optInt("version", 0)
            if (assetVersion < 11) throw IllegalStateException("بسته محتوای NetworkAll قدیمی یا نامعتبر است (version=$assetVersion)")
            val chapters = root.optJSONArray("chapters") ?: throw IllegalStateException("درخت فصل‌های NetworkAll در بسته وجود ندارد")
            if (chapters.length() == 0) throw IllegalStateException("درخت فصل‌های NetworkAll خالی است")

            val batch = mutableListOf<LessonEntity>()
            for (ci in 0 until chapters.length()) {
                val ch = chapters.getJSONObject(ci)
                val chOrder = ch.optInt("order", ci + 1)
                val chTitle = ch.optString("title_fa")
                val subs = ch.optJSONArray("subchapters") ?: continue
                var lessonOrd = 0
                for (si in 0 until subs.length()) {
                    val sub = subs.getJSONObject(si)
                    val subTitle = sub.optString("title_fa")
                    val lessons = sub.optJSONArray("lessons") ?: continue
                    for (li in 0 until lessons.length()) {
                        val les = lessons.getJSONObject(li)
                        val uid = les.optString("uid")
                        if (uid.isBlank()) continue
                        lessonOrd++
                        val titleFa = les.optString("title_fa")
                        val titleEn = les.optString("title_en")
                        val summary = les.optString("summary")
                        val fullContent = les.optString("full_content")
                        val commands = les.optString("commands")
                        val examples = les.optString("examples")
                        val notes = les.optString("notes")
                        val metaJson = les.optJSONObject("meta")?.let { canonicalJson(it) } ?: "{}"
                        val objectives = les.optJSONArray("learning_objectives")
                        val objectivesText = if (objectives == null) "" else
                            (0 until objectives.length()).joinToString("\n") { objectives.optString(it) }
                        val keywords = les.optJSONArray("search_keywords")?.let { arr ->
                            (0 until arr.length()).joinToString(" ") { arr.optString(it) }
                        } ?: ""
                        val searchQuery = les.optString("search_query").ifBlank { keywords }
                        val levelTag = les.optString("level").ifBlank { "L0" }
                        val sourceStatus = les.optString("source_status").ifBlank { "review_required" }
                        val generatedAt = root.optString("generated_at", Instant.now().toString())
                        val contentHash = syncContentHash(
                            uid, titleFa, titleEn, levelTag, summary, fullContent,
                            commands, examples, notes, metaJson, searchQuery,
                            objectivesText, sourceStatus
                        )
                        batch.add(
                            LessonEntity(
                                uid = uid,
                                entity = "lesson",
                                titleFa = titleFa,
                                titleEn = titleEn,
                                tags = levelTag,
                                summary = summary,
                                fullContent = fullContent,
                                commands = commands,
                                examples = examples,
                                notes = notes,
                                metaJson = metaJson,
                                searchQuery = searchQuery,
                                learningObjectives = objectivesText,
                                sourceStatus = sourceStatus,
                                lastUpdated = generatedAt,
                                contentHash = contentHash,
                                deviceId = "android-offline-v1",
                                chapterOrder = chOrder,
                                chapterTitle = chTitle,
                                subTitle = subTitle,
                                lessonOrder = lessonOrd
                            )
                        )
                        if (batch.size >= 50) {
                            dao.upsertAll(batch.toList())
                            batch.clear()
                        }
                    }
                }
            }
            if (batch.isNotEmpty()) dao.upsertAll(batch)
            dao.putMeta(SyncMetaEntity(META_SEEDED, "1"))
            val finalCount = dao.countActive()
            if (finalCount == 0) throw IllegalStateException("هیچ درسی از بستهٔ NetworkAll وارد پایگاه داده نشد")
            finalCount
            }
        } finally {
            seedMutex.unlock()
        }
    }

    /**
     * Mirrors shared.sync_engine.content_hash: canonical JSON with sorted keys,
     * omitting device_id, last_updated and content_hash. Keep this in lockstep
     * with server/core/db.py so an unchanged lesson is not a false sync conflict.
     */
    private fun syncContentHash(
        uid: String,
        titleFa: String,
        titleEn: String,
        tags: String,
        summary: String,
        fullContent: String,
        commands: String,
        examples: String,
        notes: String,
        metaJson: String,
        searchQuery: String,
        learningObjectives: String,
        sourceStatus: String
    ): String {
        val payload = JSONObject()
            .put("uid", uid)
            .put("entity", "lesson")
            .put("title_fa", titleFa)
            .put("title_en", titleEn)
            .put("tags", tags)
            .put("summary", summary)
            .put("full_content", fullContent)
            .put("commands", commands)
            .put("examples", examples)
            .put("notes", notes)
            .put("meta_json", metaJson)
            .put("search_query", searchQuery)
            .put("learning_objectives", learningObjectives)
            .put("source_status", sourceStatus)
            .put("deleted", false)
        val canonical = canonicalJson(payload)
        val digest = MessageDigest.getInstance("SHA-256")
            .digest(canonical.toByteArray(Charsets.UTF_8))
        return digest.joinToString("") { "%02x".format(it.toInt() and 0xff) }
    }

    private fun canonicalJson(value: Any?): String = when (value) {
        null, JSONObject.NULL -> "null"
        is JSONObject -> {
            val keys = value.keys().asSequence().toList().sorted()
            keys.joinToString(prefix = "{", postfix = "}", separator = ",") { key ->
                JSONObject.quote(key) + ":" + canonicalJson(value.get(key))
            }
        }
        is JSONArray -> (0 until value.length()).joinToString(prefix = "[", postfix = "]", separator = ",") { i ->
            canonicalJson(value.get(i))
        }
        is String -> JSONObject.quote(value)
        is Boolean, is Int, is Long, is Short, is Byte -> value.toString()
        is Number -> value.toString()
        else -> JSONObject.quote(value.toString())
    }

    private fun readCurriculumAsset(context: Context): String? {
        try {
            context.assets.open("curriculum_index.json").use {
                return it.bufferedReader(Charsets.UTF_8).readText()
            }
        } catch (_: Exception) {}
        try {
            context.assets.open("curriculum_index.json.gz").use { raw ->
                return GZIPInputStream(BufferedInputStream(raw))
                    .bufferedReader(Charsets.UTF_8).readText()
            }
        } catch (_: Exception) {}
        return null
    }
}
