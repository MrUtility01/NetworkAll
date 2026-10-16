package com.netenc.app.reminder

import android.app.AlarmManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.os.Build
import androidx.work.ExistingPeriodicWorkPolicy
import androidx.work.PeriodicWorkRequestBuilder
import androidx.work.WorkManager
import java.util.concurrent.TimeUnit

object ReminderScheduler {
    private const val UNIQUE = "netenc_review_periodic"

    fun scheduleHourly(context: Context) {
        scheduleMinutes(context, 60)
    }

    /** Periodic review reminders; WorkManager minimum interval is 15 minutes. */
    fun scheduleMinutes(context: Context, minutes: Int) {
        val m = minutes.coerceIn(15, 24 * 60)
        val req = PeriodicWorkRequestBuilder<ReviewWorker>(m.toLong(), TimeUnit.MINUTES).build()
        WorkManager.getInstance(context).enqueueUniquePeriodicWork(
            UNIQUE, ExistingPeriodicWorkPolicy.UPDATE, req
        )
    }

    /** Schedule one task reminder at the requested local epoch time. */
    fun scheduleTask(context: Context, uid: String, title: String, body: String, atMillis: Long) {
        if (atMillis <= System.currentTimeMillis()) return
        val alarm = context.getSystemService(Context.ALARM_SERVICE) as AlarmManager
        val intent = Intent(context, TaskReminderReceiver::class.java).apply {
            action = "com.netenc.app.TASK_REMINDER"
            putExtra("uid", uid)
            putExtra("title", title)
            putExtra("body", body)
        }
        val pi = PendingIntent.getBroadcast(
            context, uid.hashCode(), intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
        try {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                alarm.setExactAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, atMillis, pi)
            } else {
                alarm.setExact(AlarmManager.RTC_WAKEUP, atMillis, pi)
            }
        } catch (_: SecurityException) {
            // Android 12+ may require special exact-alarm access; still provide a best-effort reminder.
            alarm.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, atMillis, pi)
        }
    }

    fun cancelTask(context: Context, uid: String) {
        val intent = Intent(context, TaskReminderReceiver::class.java).apply {
            action = "com.netenc.app.TASK_REMINDER"
        }
        val pi = PendingIntent.getBroadcast(
            context, uid.hashCode(), intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
        (context.getSystemService(Context.ALARM_SERVICE) as AlarmManager).cancel(pi)
        pi.cancel()
    }

    fun cancel(context: Context) {
        WorkManager.getInstance(context).cancelUniqueWork(UNIQUE)
    }
}
