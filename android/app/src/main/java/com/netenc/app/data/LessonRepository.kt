package com.netenc.app.data

import android.content.Context
import org.json.JSONArray
import org.json.JSONObject
import java.time.Instant
import java.time.OffsetDateTime

class LessonRepository(context: Context) {
    private val dao = AppDatabase.get(context).lessonDao()

    suspend fun count(): Int = dao.countActive()

    suspend fun getLastSync(): String = dao.getMeta("last_sync") ?: ""

    suspend fun setLastSync(iso: String) {
        dao.putMeta(SyncMetaEntity("last_sync", iso))
    }

    suspend fun upsertFromPullJson(recordsJson: String): Int {
        val root = JSONObject(recordsJson)
        val arr = root.optJSONArray("records") ?: JSONArray()
        val list = mutableListOf<LessonEntity>()
        for (i in 0 until arr.length()) {
            val r = arr.getJSONObject(i)
            val uid = r.optString("uid")
            // Manifest pulls also contain scenarios, tasks, and notes. Never coerce
            // those rows into the lessons table.
            if (uid.isBlank() || r.optString("entity", "lesson") != "lesson") continue
            // A sync payload may omit the Android-only hierarchy columns. Room's
            // REPLACE strategy replaces the whole row, so preserve existing tree metadata
            // rather than silently moving a lesson into the "no chapter" bucket.
            val previous = dao.byUid(uid)
            list.add(
                LessonEntity(
                    uid = uid,
                    entity = r.optString("entity", "lesson"),
                    titleFa = r.optString("title_fa", r.optString("titleFa", "")),
                    titleEn = r.optString("title_en", r.optString("titleEn", "")),
                    tags = r.optString("tags", ""),
                    summary = r.optString("summary", ""),
                    fullContent = r.optString("full_content", r.optString("fullContent", "")),
                    commands = r.optString("commands", ""),
                    examples = r.optString("examples", ""),
                    notes = r.optString("notes", ""),
                    metaJson = r.optString("meta_json", r.optString("metaJson", "{}")),
                    searchQuery = r.optString("search_query", ""),
                    learningObjectives = r.optString("learning_objectives", ""),
                    sourceStatus = r.optString("source_status", "unverified"),
                    lastUpdated = r.optString("last_updated", ""),
                    contentHash = r.optString("content_hash", ""),
                    deviceId = r.optString("device_id", ""),
                    deleted = r.optBoolean("deleted", false),
                    chapterOrder = r.optInt("chapter_order", r.optInt("chapterOrder", previous?.chapterOrder ?: 0)),
                    chapterTitle = r.optString("chapter_title", r.optString("chapterTitle", previous?.chapterTitle ?: "")),
                    subTitle = r.optString("sub_title", r.optString("subTitle", previous?.subTitle ?: "")),
                    lessonOrder = r.optInt("lesson_order", r.optInt("lessonOrder", previous?.lessonOrder ?: 0))
                )
            )
        }
        if (list.isNotEmpty()) dao.upsertAll(list)
        return list.size
    }

    /**
     * Curriculum is server-authored. On a first sync, never upload the entire
     * offline seed/cache (thousands of rows). After the initial cursor is set,
     * only send locally changed rows newer than that cursor, including tombstones.
     */
    suspend fun buildPushArray(since: String?): JSONArray {
        val out = JSONArray()
        if (since.isNullOrBlank()) return out
        for (e in dao.allForPush()) {
            if (!isAfter(e.lastUpdated, since)) continue
            out.put(
                JSONObject()
                    .put("uid", e.uid)
                    .put("entity", e.entity)
                    .put("title_fa", e.titleFa)
                    .put("title_en", e.titleEn)
                    .put("tags", e.tags)
                    .put("summary", e.summary)
                    .put("full_content", e.fullContent)
                    .put("commands", e.commands)
                    .put("examples", e.examples)
                    .put("notes", e.notes)
                    .put("meta_json", e.metaJson)
                    .put("search_query", e.searchQuery)
                    .put("learning_objectives", e.learningObjectives)
                    .put("source_status", e.sourceStatus)
                    .put("last_updated", e.lastUpdated)
                    .put("content_hash", e.contentHash)
                    .put("device_id", e.deviceId)
                    .put("deleted", e.deleted)
            )
        }
        return out
    }

    private fun isAfter(candidate: String, reference: String): Boolean {
        if (candidate.isBlank() || reference.isBlank()) return false
        return timestampMillis(candidate) > timestampMillis(reference)
    }

    private fun timestampMillis(value: String): Long = try {
        Instant.parse(value).toEpochMilli()
    } catch (_: Exception) {
        try { OffsetDateTime.parse(value).toInstant().toEpochMilli() }
        catch (_: Exception) { Long.MIN_VALUE }
    }
}
