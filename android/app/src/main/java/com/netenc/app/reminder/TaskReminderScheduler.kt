package com.netenc.app.reminder

import android.content.Context
import androidx.work.Data
import androidx.work.ExistingWorkPolicy
import androidx.work.OneTimeWorkRequestBuilder
import androidx.work.WorkManager
import com.netenc.app.data.AppDatabase
import java.time.Instant
import java.time.LocalDateTime
import java.time.OffsetDateTime
import java.time.ZoneId
import java.time.format.DateTimeFormatter
import java.util.Locale
import java.util.concurrent.TimeUnit

object TaskReminderScheduler {
    private fun workName(uid: String) = "netenc_task_reminder_" + uid

    fun schedule(context: Context, uid: String, triggerAtMillis: Long) {
        val delay = (triggerAtMillis - System.currentTimeMillis()).coerceAtLeast(0L)
        val request = OneTimeWorkRequestBuilder<TaskReminderWorker>()
            .setInputData(Data.Builder().putString(TaskReminderWorker.KEY_UID, uid).build())
            .setInitialDelay(delay, TimeUnit.MILLISECONDS)
            .build()
        WorkManager.getInstance(context).enqueueUniqueWork(
            workName(uid),
            ExistingWorkPolicy.REPLACE,
            request
        )
    }

    fun cancel(context: Context, uid: String) {
        WorkManager.getInstance(context).cancelUniqueWork(workName(uid))
    }

    /**
     * Rebuild schedules from durable Room data. WorkManager survives process death/reboot,
     * but reconciliation also covers newly synced tasks, restored backups and changed due times.
     * Each device stores remindedAt locally, so Windows delivery never suppresses Android alerts.
     */
    suspend fun reconcileAll(context: Context): Int {
        val dao = AppDatabase.get(context).workspaceDao()
        val tasks = dao.allTasksForSync()
        var scheduled = 0
        for (task in tasks) {
            if (task.deleted || task.done || task.remindAt.isBlank() || task.remindedAt.isNotBlank()) {
                cancel(context, task.uid)
                continue
            }
            val at = parseReminderAtMillis(task.remindAt)
            if (at == null) {
                cancel(context, task.uid)
                continue
            }
            schedule(context, task.uid, at)
            scheduled++
        }
        return scheduled
    }

    fun parseReminderAtMillis(value: String): Long? {
        val raw = value.trim()
        if (raw.isEmpty()) return null
        try { return Instant.parse(raw).toEpochMilli() } catch (_: Exception) { }
        try { return OffsetDateTime.parse(raw).toInstant().toEpochMilli() } catch (_: Exception) { }
        return try {
            // The planner stores local wall time as yyyy-MM-dd'T'HH:mm (without a zone).
            val local = LocalDateTime.parse(
                raw.take(16),
                DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm", Locale.US)
            )
            local.atZone(ZoneId.systemDefault()).toInstant().toEpochMilli()
        } catch (_: Exception) {
            null
        }
    }
}
