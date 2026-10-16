package com.netenc.app.reminder

import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.os.Build
import androidx.core.app.NotificationCompat
import com.netenc.app.SplashActivity

class TaskReminderReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        val uid = intent.getStringExtra("uid").orEmpty()
        val title = intent.getStringExtra("title").orEmpty().ifBlank { "یادآوری کار" }
        val body = intent.getStringExtra("body").orEmpty()
        val manager = context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        val channel = "netenc_tasks"
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            manager.createNotificationChannel(
                NotificationChannel(channel, "یادآوری کارها", NotificationManager.IMPORTANCE_HIGH)
            )
        }
        val open = PendingIntent.getActivity(
            context, uid.hashCode(), Intent(context, SplashActivity::class.java).putExtra("open_mode", "tasks"),
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
        val text = if (body.isBlank()) "زمان انجام این کار رسیده است." else body
        val notification = NotificationCompat.Builder(context, channel)
            .setSmallIcon(android.R.drawable.ic_menu_my_calendar)
            .setContentTitle("یادآوری: $title")
            .setContentText(text)
            .setStyle(NotificationCompat.BigTextStyle().bigText(text))
            .setContentIntent(open)
            .setAutoCancel(true)
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .build()
        manager.notify(2000 + (uid.hashCode() and 0x0fffffff), notification)
    }
}
