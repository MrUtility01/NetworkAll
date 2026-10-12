package com.netenc.app.data

import android.content.Context
import org.json.JSONArray
import org.json.JSONObject
import java.time.Instant
import java.time.OffsetDateTime

/**
 * Cross-platform sync projection for user-owned tasks and notes.
 * Vault data is intentionally excluded because its encryption keys are not shared.
 */
class WorkspaceSyncRepository(context: Context) {
    private val dao = AppDatabase.get(context).workspaceDao()

    suspend fun upsertFromPullJson(recordsJson: String): Int {
        val root = JSONObject(recordsJson)
        val arr = root.optJSONArray("records") ?: JSONArray()
        var applied = 0
        for (i in 0 until arr.length()) {
            val record = arr.optJSONObject(i) ?: continue
            val uid = record.optString("uid", "").trim()
            val entity = record.optString("entity", "")
            if (uid.isEmpty()) continue
            val remoteUpdated = record.optString("last_updated", record.optString("lastUpdated", ""))
            val deviceId = record.optString("device_id", record.optString("deviceId", "server"))
            val deleted = record.optBoolean("deleted", false)

            when (entity) {
                "task" -> {
                    val title = record.optString("title", "").trim()
                    if (title.isEmpty()) continue
                    val local = dao.taskByUid(uid)
                    // Do not erase an offline edit just because a pull ran before push.
                    if (local != null && !isRemoteNewer(remoteUpdated, local.lastUpdated)) continue
                    dao.upsertTask(
                        TaskEntity(
                            uid = uid,
                            title = title,
                            body = record.optString("body", ""),
                            done = record.optBoolean("done", false),
                            dueAt = record.optString("due_at", record.optString("dueAt", "")),
                            priority = record.optInt("priority", 1).coerceIn(1, 3),
                            lastUpdated = remoteUpdated,
                            deviceId = deviceId,
                            deleted = deleted
                        )
                    )
                    applied++
                }
                "note" -> {
                    val title = record.optString("title", "").trim()
                    if (title.isEmpty()) continue
                    // WorkspaceDao exposes a point lookup only for tasks. Use the sync
                    // projection to avoid treating the existence of a note as a new row.
                    val local = dao.allNotesForSync().firstOrNull { it.uid == uid }
                    if (local != null && !isRemoteNewer(remoteUpdated, local.lastUpdated)) continue
                    dao.upsertNote(
                        NoteEntity(
                            uid = uid,
                            title = title,
                            body = record.optString("body", ""),
                            tags = record.optString("tags", ""),
                            lastUpdated = remoteUpdated,
                            deviceId = deviceId,
                            deleted = deleted
                        )
                    )
                    applied++
                }
            }
        }
        return applied
    }

    suspend fun buildPushArray(): JSONArray {
        val out = JSONArray()
        for (task in dao.allTasksForSync()) {
            out.put(
                JSONObject()
                    .put("uid", task.uid)
                    .put("entity", "task")
                    .put("title", task.title)
                    .put("body", task.body)
                    .put("done", task.done)
                    .put("due_at", task.dueAt)
                    .put("priority", task.priority)
                    .put("last_updated", task.lastUpdated)
                    .put("device_id", task.deviceId)
                    .put("deleted", task.deleted)
            )
        }
        for (note in dao.allNotesForSync()) {
            out.put(
                JSONObject()
                    .put("uid", note.uid)
                    .put("entity", "note")
                    .put("title", note.title)
                    .put("body", note.body)
                    .put("tags", note.tags)
                    .put("last_updated", note.lastUpdated)
                    .put("device_id", note.deviceId)
                    .put("deleted", note.deleted)
            )
        }
        return out
    }

    private fun isRemoteNewer(remote: String, local: String): Boolean {
        if (local.isBlank()) return remote.isNotBlank()
        if (remote.isBlank()) return false
        val remoteMillis = timestampMillis(remote)
        val localMillis = timestampMillis(local)
        // Equal timestamps are kept locally: the server will report a conflict
        // instead of silently replacing a potentially distinct offline edit.
        return remoteMillis > localMillis
    }

    private fun timestampMillis(value: String): Long {
        return try {
            Instant.parse(value).toEpochMilli()
        } catch (_: Exception) {
            try {
                OffsetDateTime.parse(value).toInstant().toEpochMilli()
            } catch (_: Exception) {
                Long.MIN_VALUE
            }
        }
    }
}
