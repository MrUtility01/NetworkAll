package com.netenc.app.data

import android.content.Context
import android.util.JsonReader
import android.util.JsonToken
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.BufferedInputStream
import java.io.InputStream
import java.io.InputStreamReader
import java.nio.charset.StandardCharsets
import java.util.zip.GZIPInputStream

/**
 * Streams the curriculum directly into Room in small batches.
 *
 * The complete curriculum remains bundled and available offline, but we never
 * build one giant String/JSONObject containing every lesson in memory.
 */
object OfflineSeeder {
    private const val META_SEEDED = "offline_seeded_v14"
    private const val BATCH_SIZE = 50

    suspend fun ensureSeeded(context: Context): Int = withContext(Dispatchers.IO) {
        val dao = AppDatabase.get(context).lessonDao()
        val existing = dao.countActive()
        val filled = if (existing > 0) dao.countFilled() else 0
        if (dao.getMeta(META_SEEDED) == "1" && existing > 5000 && filled > 2000) {
            return@withContext existing
        }

        val input = openCurriculumStream(context) ?: return@withContext existing
        val batch = mutableListOf<LessonEntity>()
        var imported = 0

        val reader = JsonReader(InputStreamReader(BufferedInputStream(input), StandardCharsets.UTF_8))
        try {
            reader.beginObject()
            while (reader.hasNext()) {
                when (reader.nextName()) {
                    "chapters" -> {
                        reader.beginArray()
                        while (reader.hasNext()) {
                            imported += readChapter(reader, dao, batch)
                        }
                        reader.endArray()
                    }
                    else -> reader.skipValue()
                }
            }
            reader.endObject()
            if (batch.isNotEmpty()) {
                dao.upsertAll(batch.toList())
                batch.clear()
            }
        } finally {
            reader.close()
        }

        if (imported > 0 || existing == 0) {
            dao.putMeta(SyncMetaEntity(META_SEEDED, "1"))
        }
        android.util.Log.i("NetworkAll", "Streaming seed complete: imported=$imported active=${dao.countActive()}")
        dao.countActive()
    }

    private suspend fun readChapter(
        reader: JsonReader,
        dao: LessonDao,
        batch: MutableList<LessonEntity>
    ): Int {
        var chapterOrder = 0
        var chapterTitle = ""
        var imported = 0
        val lessonCounter = ChapterLessonCounter()

        reader.beginObject()
        while (reader.hasNext()) {
            when (reader.nextName()) {
                "order" -> chapterOrder = readInt(reader)
                "title_fa" -> chapterTitle = readString(reader)
                "subchapters" -> {
                    reader.beginArray()
                    while (reader.hasNext()) {
                        imported += readSubchapter(
                            reader, dao, batch, chapterOrder, chapterTitle, lessonCounter
                        )
                    }
                    reader.endArray()
                }
                else -> reader.skipValue()
            }
        }
        reader.endObject()
        return imported
    }

    private suspend fun readSubchapter(
        reader: JsonReader,
        dao: LessonDao,
        batch: MutableList<LessonEntity>,
        chapterOrder: Int,
        chapterTitle: String,
        lessonCounter: ChapterLessonCounter
    ): Int {
        var subTitle = ""
        var imported = 0
        reader.beginObject()
        while (reader.hasNext()) {
            when (reader.nextName()) {
                "title_fa" -> subTitle = readString(reader)
                "lessons" -> {
                    reader.beginArray()
                    while (reader.hasNext()) {
                        val lesson = readLesson(reader)
                        if (lesson.uid.isNotBlank()) {
                            lessonCounter.value += 1
                            batch.add(
                                lesson.copy(
                                    chapterOrder = chapterOrder,
                                    chapterTitle = chapterTitle,
                                    subTitle = subTitle,
                                    lessonOrder = lessonCounter.value
                                )
                            )
                            imported += 1
                            if (batch.size >= BATCH_SIZE) {
                                dao.upsertAll(batch.toList())
                                batch.clear()
                            }
                        }
                    }
                    reader.endArray()
                }
                else -> reader.skipValue()
            }
        }
        reader.endObject()
        return imported
    }

    private fun readLesson(reader: JsonReader): LessonEntity {
        var uid = ""
        var titleFa = ""
        var titleEn = ""
        var level = "L0"
        var summary = ""
        var fullContent = ""
        var commands = ""
        var examples = ""
        var notes = ""

        reader.beginObject()
        while (reader.hasNext()) {
            when (reader.nextName()) {
                "uid" -> uid = readString(reader)
                "title_fa" -> titleFa = readString(reader)
                "title_en" -> titleEn = readString(reader)
                "level" -> level = readString(reader)
                "summary" -> summary = readString(reader)
                "full_content" -> fullContent = readString(reader)
                "commands" -> commands = readString(reader)
                "examples" -> examples = readString(reader)
                "notes" -> notes = readString(reader)
                else -> reader.skipValue()
            }
        }
        reader.endObject()

        return LessonEntity(
            uid = uid,
            titleFa = titleFa,
            titleEn = titleEn,
            tags = level,
            summary = summary,
            fullContent = fullContent,
            commands = commands,
            examples = examples,
            notes = notes,
            lastUpdated = "2026-10-15T00:00:00Z",
            contentHash = "offline-stream-v14",
            deviceId = "android-offline"
        )
    }

    private fun readString(reader: JsonReader): String {
        return if (reader.peek() == JsonToken.NULL) {
            reader.nextNull()
            ""
        } else {
            reader.nextString()
        }
    }

    private fun readInt(reader: JsonReader): Int {
        return if (reader.peek() == JsonToken.NULL) {
            reader.nextNull()
            0
        } else {
            reader.nextInt()
        }
    }

    private fun openCurriculumStream(context: Context): InputStream? {
        try {
            return context.assets.open("curriculum_index.json")
        } catch (_: Exception) {
            // Fall through to the gzip asset for development/source builds.
        }
        return try {
            GZIPInputStream(BufferedInputStream(context.assets.open("curriculum_index.json.gz")))
        } catch (_: Exception) {
            null
        }
    }

    private class ChapterLessonCounter(var value: Int = 0)
}
