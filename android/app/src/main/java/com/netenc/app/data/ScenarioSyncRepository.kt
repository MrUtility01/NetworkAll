package com.netenc.app.data

import android.content.Context
import org.json.JSONArray
import org.json.JSONObject
import java.time.Instant
import java.time.OffsetDateTime

/** Applies server scenario updates only to known, locally seeded scenario identities. */
class ScenarioSyncRepository(context: Context) {
    private val dao = AppDatabase.get(context).scenarioDao()

    suspend fun upsertFromPullJson(recordsJson: String): Int {
        val arr = JSONObject(recordsJson).optJSONArray("records") ?: JSONArray()
        val existing = dao.allForSync().associateBy { it.code }
        val updates = mutableListOf<ScenarioEntity>()
        for (i in 0 until arr.length()) {
            val r = arr.optJSONObject(i) ?: continue
            if (r.optString("entity") != "scenario") continue
            val uid = r.optString("uid", "")
            val code = r.optString("code", "").ifBlank { uid.removePrefix("scenario:") }
            val local = existing[code] ?: continue
            val timestamp = r.optString("last_updated", "")
            if (!newer(timestamp, local.lastUpdated)) continue
            updates.add(local.copy(
                titleFa = r.optString("title_fa", local.titleFa),
                tasks = r.optString("tasks", local.tasks),
                solution = r.optString("solution", local.solution),
                verification = r.optString("verification", local.verification),
                lastUpdated = timestamp,
                contentHash = r.optString("content_hash", ""),
                deviceId = r.optString("device_id", "server"),
                deleted = r.optBoolean("deleted", false)
            ))
        }
        if (updates.isNotEmpty()) dao.upsertAll(updates)
        return updates.size
    }

    private fun newer(remote: String, local: String): Boolean {
        if (local.isBlank()) return remote.isNotBlank()
        if (remote.isBlank()) return false
        return millis(remote) > millis(local)
    }

    private fun millis(value: String): Long = try {
        Instant.parse(value).toEpochMilli()
    } catch (_: Exception) {
        try { OffsetDateTime.parse(value).toInstant().toEpochMilli() }
        catch (_: Exception) { Long.MIN_VALUE }
    }
}
