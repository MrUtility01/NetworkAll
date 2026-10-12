package com.netenc.app.reminder

import android.content.Context
import androidx.work.Data
import androidx.work.ExistingWorkPolicy
import androidx.work.OneTimeWorkRequestBuilder
import androidx.work.WorkManager
import androidx.work.workDataOf
import com.netenc.app.data.AppDatabase
import com.netenc.app.data.TaskEntity
import java.time.Instant
import java.time.LocalDateTime
import java.time.ZoneId
import java.time.format.DateTimeParseException
import java.util.concurrent.TimeUnit

object TaskReminderScheduler {
    private fun uniqueName(uid: String) = "netenc-task-reminder:$uid"

    fun schedule(context: Context, uid: String, atMillis: Long) {
        if (uid.isBlank()) return
        val delay = (atMillis - System.currentTimeMillis()).coerceAtLeast(0L)
        val request = OneTimeWorkRequestBuilder<TaskReminderWorker>()
            .setInitialDelay(delay, TimeUnit.MILLISECONDS)
            .setInputData(workDataOf(TaskReminderWorker.KEY_TASK_UID to uid))
            .addTag("netenc-task-reminder")
            .build()
        WorkManager.getInstance(context.applicationContext)
            .enqueueUniqueWork(uniqueName(uid), ExistingWorkPolicy.REPLACE, request)
    }

    fun cancel(context: Context, uid: String) {
        if (uid.isBlank()) return
        WorkManager.getInstance(context.applicationContext).cancelUniqueWork(uniqueName(uid))
    }

    /**
     * Reconcile durable work after process restart, sync, edits, completion/deletion or
     * returning from Android notification settings. Only remindAt is synchronized;
     * remindedAt remains a delivery guard on each device.
     */
    suspend fun reconcileAll(context: Context) {
        val dao = AppDatabase.get(context.applicationContext).workspaceDao()
        val tasks = dao.allTasksForSync()
        for (task in tasks) {
            if (task.deleted || task.done || task.remindAt.isBlank() || task.remindedAt.isNotBlank()) {
                cancel(context, task.uid)
                continue
            }
            val atMillis = parseReminderMillis(task.remindAt)
            if (atMillis == null) {
                cancel(context, task.uid)
                continue
            }
            schedule(context, task.uid, atMillis)
        }
    }

    fun parseReminderMillis(value: String): Long? {
        val raw = value.trim()
        if (raw.isBlank()) return null
        return try {
            // Planner and Windows store local wall-clock times without a zone suffix.
            LocalDateTime.parse(raw).atZone(ZoneId.systemDefault()).toInstant().toEpochMilli()
        } catch (_: DateTimeParseException) {
            try {
                // Accept explicit ISO-8601 instants from migrated/externally-created records.
                Instant.parse(raw).toEpochMilli()
            } catch (_: Exception) {
                null
            }
        } catch (_: Exception) {
            null
        }
    }
}
