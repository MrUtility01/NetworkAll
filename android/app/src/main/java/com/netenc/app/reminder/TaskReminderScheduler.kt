package com.netenc.app.reminder

import android.content.Context
import androidx.work.Data
import androidx.work.ExistingWorkPolicy
import androidx.work.OneTimeWorkRequestBuilder
import androidx.work.WorkManager
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
}
