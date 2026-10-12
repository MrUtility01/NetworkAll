package com.netenc.app.data

import android.content.Context
import org.json.JSONArray
import org.json.JSONObject
import java.time.Instant
import java.time.OffsetDateTime

/** Two-way sync for spaced-repetition state; stable identity is the lesson UID. */
class StudySyncRepository(context: Context) {
    private val dao = AppDatabase.get(context).studyDao()

    suspend fun upsertFromPullJson(recordsJson: String): Int {
        val arr = JSONObject(recordsJson).optJSONArray("records") ?: JSONArray()
        var applied = 0
        for (i in 0 until arr.length()) {
            val r = arr.optJSONObject(i) ?: continue
            if (r.optString("entity", "") != "study") continue
            val uid = r.optString("uid", "").trim()
            if (uid.isEmpty()) continue
            val updated = r.optString("last_updated", r.optString("lastUpdated", ""))
            val local = dao.byUid(uid)
            if (local != null && !isRemoteNewer(updated, local.lastUpdated)) continue
            val status = r.optString("status", "new")
            if (status !in setOf("new", "learning", "known", "review")) continue
            val ease = r.optDouble("ease", 2.5)
            val interval = r.optInt("interval_hours", r.optInt("intervalHours", 1))
            val times = r.optInt("times_studied", r.optInt("timesStudied", 0))
            if (ease !in 1.0..4.0 || interval !in 0..(24 * 365) || times < 0) continue
            dao.upsert(
                StudyEntity(
                    lessonUid = uid,
                    status = status,
                    ease = ease,
                    intervalHours = interval,
                    lastStudied = r.optString("last_studied", r.optString("lastStudied", "")),
                    nextReview = r.optString("next_review", r.optString("nextReview", "")),
                    timesStudied = times,
                    notes = r.optString("notes", ""),
                    lastUpdated = updated,
                    deviceId = r.optString("device_id", r.optString("deviceId", "server")),
                    deleted = r.optBoolean("deleted", false)
                )
            )
            applied++
        }
        return applied
    }

    suspend fun buildPushArray(): JSONArray {
        val out = JSONArray()
        for (row in dao.allForSync()) {
            out.put(
                JSONObject()
                    .put("uid", row.lessonUid)
                    .put("entity", "study")
                    .put("status", row.status)
                    .put("ease", row.ease)
                    .put("interval_hours", row.intervalHours)
                    .put("last_studied", row.lastStudied)
                    .put("next_review", row.nextReview)
                    .put("times_studied", row.timesStudied)
                    .put("notes", row.notes)
                    .put("last_updated", row.lastUpdated)
                    .put("device_id", row.deviceId)
                    .put("deleted", row.deleted)
            )
        }
        return out
    }

    private fun isRemoteNewer(remote: String, local: String): Boolean {
        if (local.isBlank()) return remote.isNotBlank()
        if (remote.isBlank()) return false
        return timestampMillis(remote) > timestampMillis(local)
    }

    private fun timestampMillis(value: String): Long = try {
        Instant.parse(value).toEpochMilli()
    } catch (_: Exception) {
        try { OffsetDateTime.parse(value).toInstant().toEpochMilli() }
        catch (_: Exception) { Long.MIN_VALUE }
    }
}
