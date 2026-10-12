package com.netenc.app.reminder

import android.Manifest
import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import androidx.core.app.NotificationCompat
import androidx.core.content.ContextCompat
import androidx.work.CoroutineWorker
import androidx.work.WorkerParameters
import com.netenc.app.PlannerActivity
import com.netenc.app.data.AppDatabase
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.time.Instant

class TaskReminderWorker(
    appContext: Context,
    params: WorkerParameters
) : CoroutineWorker(appContext, params) {
    override suspend fun doWork(): Result {
        val uid = inputData.getString(KEY_TASK_UID)?.takeIf { it.isNotBlank() } ?: return Result.failure()
        val dao = AppDatabase.get(applicationContext).workspaceDao()
        val task = withContext(Dispatchers.IO) { dao.taskByUid(uid) } ?: return Result.success()

        if (task.deleted || task.done || task.remindAt.isBlank() || task.remindedAt.isNotBlank()) {
            return Result.success()
        }

        val fireAt = TaskReminderScheduler.parseReminderMillis(task.remindAt) ?: return Result.failure()
        if (fireAt > System.currentTimeMillis() + 1_000L) {
            TaskReminderScheduler.schedule(applicationContext, task.uid, fireAt)
            return Result.success()
        }

        if (Build.VERSION.SDK_INT >= 33 &&
            ContextCompat.checkSelfPermission(applicationContext, Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED
        ) {
            // Do not mark it delivered. MainActivity/Planner will reconcile after permission changes.
            return Result.success()
        }

        return try {
            val manager = applicationContext.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                manager.createNotificationChannel(
                    NotificationChannel(CHANNEL_ID, "یادآوری کارها", NotificationManager.IMPORTANCE_HIGH).apply {
                        description = "یادآوری کارهای زمان‌بندی‌شده در NetworkAll"
                        lockscreenVisibility = Notification.VISIBILITY_PRIVATE
                    }
                )
            }
            val intent = Intent(applicationContext, PlannerActivity::class.java)
                .putExtra("task_uid", task.uid)
                .addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP or Intent.FLAG_ACTIVITY_SINGLE_TOP)
            val pending = PendingIntent.getActivity(
                applicationContext,
                task.uid.hashCode(),
                intent,
                PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
            )
            val notification = NotificationCompat.Builder(applicationContext, CHANNEL_ID)
                .setSmallIcon(android.R.drawable.ic_popup_reminder)
                .setContentTitle("یادآوری کار: ${task.title}")
                .setContentText(task.body.ifBlank { "زمان یادآوری این کار فرا رسیده است." }.take(180))
                .setStyle(NotificationCompat.BigTextStyle().bigText(task.body.ifBlank { "زمان یادآوری این کار فرا رسیده است." }))
                .setContentIntent(pending)
                .setAutoCancel(true)
                .setCategory(NotificationCompat.CATEGORY_REMINDER)
                .setPriority(NotificationCompat.PRIORITY_HIGH)
                .build()
            manager.notify(task.uid.hashCode(), notification)
            withContext(Dispatchers.IO) { dao.markTaskReminded(task.uid, Instant.now().toString()) }
            Result.success()
        } catch (_: SecurityException) {
            // Keep the item eligible for scheduling after the user grants notification permission.
            Result.success()
        } catch (_: Exception) {
            Result.retry()
        }
    }

    companion object {
        const val KEY_TASK_UID = "task_uid"
        private const val CHANNEL_ID = "netenc_task_reminders"
    }
}
