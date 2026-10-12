package com.netenc.app.data

import android.content.Context
import android.util.JsonReader
import android.util.JsonToken
import android.util.Log
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import kotlinx.coroutines.withContext
import org.json.JSONArray
import org.json.JSONObject
import java.io.BufferedInputStream
import java.io.InputStream
import java.io.InputStreamReader
import java.util.zip.GZIPInputStream

object OfflineSeeder {
    private const val META_SEEDED = "offline_seeded_v15"
    private const val BATCH_SIZE = 50
    private val seedMutex = Mutex()

    suspend fun ensureSeeded(context: Context, force: Boolean = false): Int = seedMutex.withLock {
        withContext(Dispatchers.IO) {
            val dao = AppDatabase.get(context).lessonDao()
            val existing = dao.countActive()
            val filled = if (existing > 0) dao.countFilled() else 0
            val treeReady = if (existing > 0) dao.countTreeReady() else 0
            // Older builds could mark a large database as seeded even when its rows lacked
            // chapter/subchapter metadata. Do not skip seeding while the tree is incomplete.
            val hierarchyHealthy = existing > 0 && treeReady >= (existing * 0.90).toInt()
            if (!force && dao.getMeta(META_SEEDED) == "1" &&
                existing > 5000 && filled > 2000 && hierarchyHealthy
            ) {
                return@withContext existing
            }

            // This map contains only UID/deleted projections, not the 100+ MB lesson bodies.
            val existingRows = dao.allDeletionStates().associateBy { it.uid }
            val input = openCurriculumAsset(context) ?: return@withContext existing
            val imported = try {
                input.use { raw ->
                    JsonReader(InputStreamReader(BufferedInputStream(raw), Charsets.UTF_8)).use { reader ->
                        streamCurriculum(reader, dao, existingRows)
                    }
                }
            } catch (e: Exception) {
                // Some batches may already have been upserted. The seed marker is intentionally
                // not written, so the next launch safely retries and finishes the same upserts.
                Log.e("OfflineSeeder", "Could not stream curriculum asset; seed marker was not advanced", e)
                return@withContext dao.countActive()
            }

            if (imported <= 0) return@withContext existing
            dao.putMeta(SyncMetaEntity(META_SEEDED, "1"))
            dao.countActive()
        }
    }

    private suspend fun streamCurriculum(
        reader: JsonReader,
        dao: LessonDao,
        existingRows: Map<String, LessonDeletionState>
    ): Int {
        val batch = mutableListOf<LessonEntity>()
        var lessonCount = 0
        var chapterCount = 0
        var chaptersSeen = false
        val lessonOrderCounter = intArrayOf(0)

        suspend fun flushBatch() {
            if (batch.isNotEmpty()) {
                dao.upsertAll(batch.toList())
                batch.clear()
            }
        }

        suspend fun readLessons(
            json: JsonReader,
            chapterOrder: Int,
            chapterTitle: String,
            subTitle: String
        ) {
            json.beginArray()
            while (json.hasNext()) {
                val lesson = readJsonValue(json) as? JSONObject
                    ?: throw IllegalStateException("Curriculum lesson must be a JSON object")
                val uid = lesson.optString("uid")
                if (uid.isBlank()) continue

                lessonOrderCounter[0]++
                batch.add(
                    LessonEntity(
                        uid = uid,
                        titleFa = lesson.optString("title_fa"),
                        titleEn = lesson.optString("title_en"),
                        tags = lesson.optString("level", "L0"),
                        summary = lesson.optString("summary"),
                        fullContent = lesson.optString("full_content"),
                        commands = lesson.optString("commands"),
                        examples = lesson.optString("examples"),
                        notes = lesson.optString("notes"),
                        metaJson = lesson.optString("meta_json", "{}"),
                        learningObjectives = lesson.optString("learning_objectives", ""),
                        sourceStatus = lesson.optString("source_status", "review_required"),
                        lastUpdated = "2026-10-11T12:00:00Z",
                        contentHash = "offline-v15-ch68",
                        deviceId = "android-offline",
                        // Preserve user soft-deletions when refreshing bundled content.
                        deleted = existingRows[uid]?.deleted ?: false,
                        chapterOrder = chapterOrder,
                        chapterTitle = chapterTitle,
                        subTitle = subTitle,
                        lessonOrder = lessonOrderCounter[0]
                    )
                )
                lessonCount++
                if (batch.size >= BATCH_SIZE) flushBatch()
            }
            json.endArray()
        }

        suspend fun readSubchapters(json: JsonReader, chapterOrder: Int, chapterTitle: String) {
            lessonOrderCounter[0] = 0
            json.beginArray()
            while (json.hasNext()) {
                var subTitle = ""
                json.beginObject()
                while (json.hasNext()) {
                    when (json.nextName()) {
                        "title_fa" -> subTitle = json.nextString()
                        "lessons" -> readLessons(json, chapterOrder, chapterTitle, subTitle)
                        else -> json.skipValue()
                    }
                }
                json.endObject()
            }
            json.endArray()
        }

        reader.beginObject()
        while (reader.hasNext()) {
            when (reader.nextName()) {
                "chapters" -> {
                    chaptersSeen = true
                    reader.beginArray()
                    while (reader.hasNext()) {
                        var chapterOrder = chapterCount + 1
                        var chapterTitle = ""
                        reader.beginObject()
                        while (reader.hasNext()) {
                            when (reader.nextName()) {
                                "order" -> chapterOrder = reader.nextInt()
                                "title_fa" -> chapterTitle = reader.nextString()
                                // The generated index contract places chapter title/order before
                                // subchapters so their metadata is known before streaming lessons.
                                "subchapters" -> readSubchapters(reader, chapterOrder, chapterTitle)
                                else -> reader.skipValue()
                            }
                        }
                        reader.endObject()
                        chapterCount++
                    }
                    reader.endArray()
                }
                else -> reader.skipValue()
            }
        }
        reader.endObject()
        flushBatch()

        if (!chaptersSeen || chapterCount == 0 || lessonCount == 0) {
            throw IllegalStateException("Curriculum asset contains no chapter lessons")
        }
        return lessonCount
    }

    /** Parse only one lesson object at a time; never build the entire curriculum tree in memory. */
    private fun readJsonValue(reader: JsonReader): Any? = when (reader.peek()) {
        JsonToken.BEGIN_OBJECT -> {
            val obj = JSONObject()
            reader.beginObject()
            while (reader.hasNext()) {
                val name = reader.nextName()
                obj.put(name, readJsonValue(reader) ?: JSONObject.NULL)
            }
            reader.endObject()
            obj
        }
        JsonToken.BEGIN_ARRAY -> {
            val arr = JSONArray()
            reader.beginArray()
            while (reader.hasNext()) arr.put(readJsonValue(reader) ?: JSONObject.NULL)
            reader.endArray()
            arr
        }
        JsonToken.STRING -> reader.nextString()
        JsonToken.NUMBER -> {
            val raw = reader.nextString()
            raw.toLongOrNull() ?: raw.toDoubleOrNull() ?: raw
        }
        JsonToken.BOOLEAN -> reader.nextBoolean()
        JsonToken.NULL -> {
            reader.nextNull()
            JSONObject.NULL
        }
        else -> throw IllegalStateException("Unexpected JSON token in curriculum asset: " + reader.peek())
    }

    private fun openCurriculumAsset(context: Context): InputStream? {
        try {
            return context.assets.open("curriculum_index.json")
        } catch (_: Exception) {
            // Optional for future smaller distributions that package a gzipped seed.
        }
        return try {
            GZIPInputStream(BufferedInputStream(context.assets.open("curriculum_index.json.gz")))
        } catch (_: Exception) {
            null
        }
    }
}
