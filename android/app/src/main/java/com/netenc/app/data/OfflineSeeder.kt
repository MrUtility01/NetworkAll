package com.netenc.app.data

import android.content.Context
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.io.BufferedInputStream
import java.util.zip.GZIPInputStream
import java.security.MessageDigest
import java.time.Instant

object OfflineSeeder {
    private const val META_SEEDED = "offline_seeded_v18"

    suspend fun ensureSeeded(context: Context): Int = withContext(Dispatchers.IO) {
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
                    val metaJson = les.optJSONObject("meta")?.toString() ?: "{}"
                    val objectives = les.optJSONArray("learning_objectives")
                    val objectivesText = if (objectives == null) "" else
                        (0 until objectives.length()).joinToString("\n") { objectives.optString(it) }
                    val searchQuery = les.optString("search_query",
                        (les.optJSONArray("search_keywords")?.let { arr ->
                            (0 until arr.length()).joinToString(" ") { arr.optString(it) }
                        } ?: ""))
                    val generatedAt = root.optString("generated_at", Instant.now().toString())
                    batch.add(
                        LessonEntity(
                            uid = uid,
                            titleFa = titleFa,
                            titleEn = titleEn,
                            tags = les.optString("level", "L0"),
                            summary = summary,
                            fullContent = fullContent,
                            commands = commands,
                            examples = examples,
                            notes = notes,
                            metaJson = metaJson,
                            searchQuery = searchQuery,
                            learningObjectives = objectivesText,
                            sourceStatus = les.optString("source_status", "review_required"),
                            lastUpdated = generatedAt,
                            contentHash = sha256(uid, titleFa, titleEn, summary, fullContent, commands, examples, notes, metaJson),
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

    private fun sha256(vararg values: String): String {
        val source = values.joinToString("\u001f")
        val bytes = MessageDigest.getInstance("SHA-256").digest(source.toByteArray(Charsets.UTF_8))
        return bytes.joinToString("") { "%02x".format(it.toInt() and 0xff) }
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
