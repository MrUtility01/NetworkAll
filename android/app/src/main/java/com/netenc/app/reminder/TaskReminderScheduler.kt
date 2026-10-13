package com.netenc.app.reminder

import android.content.Context
import androidx.work.Data
import androidx.work.ExistingWorkPolicy
import androidx.work.OneTimeWorkRequestBuilder
import androidx.work.WorkManager
import java.time.LocalDateTime
import java.time.ZoneId
import java.time.format.DateTimeFormatter
import java.util.concurrent.TimeUnit

object TaskReminderScheduler {
    fun schedule(context: Context, uid: String, title: String, body: String, dueAt: String) {
        val instant = try {
            val local = LocalDateTime.parse(dueAt.trim(), DateTimeFormatter.ISO_LOCAL_DATE_TIME)
            local.atZone(ZoneId.systemDefault()).toInstant()
        } catch (_: Exception) {
            return
        }
        val delay = (instant.toEpochMilli() - System.currentTimeMillis()).coerceAtLeast(0L)
        val data = Data.Builder().putString("uid", uid).putString("title", title).putString("body", body).build()
        val req = OneTimeWorkRequestBuilder<TaskReminderWorker>()
            .setInputData(data).setInitialDelay(delay, TimeUnit.MILLISECONDS).build()
        WorkManager.getInstance(context).enqueueUniqueWork("networkall-task-$uid", ExistingWorkPolicy.REPLACE, req)
    }
    fun cancel(context: Context, uid: String) {
        WorkManager.getInstance(context).cancelUniqueWork("networkall-task-$uid")
    }
}
