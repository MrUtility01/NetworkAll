package com.netenc.app.reminder

import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.os.Build
import androidx.core.app.NotificationCompat
import androidx.work.CoroutineWorker
import androidx.work.WorkerParameters
import com.netenc.app.WorkspaceActivity

class TaskReminderWorker(ctx: Context, params: WorkerParameters) : CoroutineWorker(ctx, params) {
    override suspend fun doWork(): Result {
        val title = inputData.getString("title") ?: "یادآوری کار NetworkAll"
        val body = inputData.getString("body").orEmpty()
        val nm = applicationContext.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        val channel = "networkall_tasks"
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            nm.createNotificationChannel(NotificationChannel(channel, "یادآوری کارها", NotificationManager.IMPORTANCE_HIGH))
        }
        val open = Intent(applicationContext, WorkspaceActivity::class.java).putExtra("mode", "tasks")
        val pi = PendingIntent.getActivity(applicationContext, inputData.getString("uid").hashCode(), open,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE)
        val n = NotificationCompat.Builder(applicationContext, channel)
            .setSmallIcon(android.R.drawable.ic_menu_agenda)
            .setContentTitle(title)
            .setContentText(body.ifBlank { "زمان انجام کار فرا رسیده است." })
            .setStyle(NotificationCompat.BigTextStyle().bigText(body.ifBlank { "زمان انجام کار فرا رسیده است." }))
            .setContentIntent(pi).setAutoCancel(true).build()
        nm.notify(inputData.getString("uid").hashCode(), n)
        return Result.success()
    }
}
