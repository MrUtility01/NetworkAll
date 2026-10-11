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
import com.netenc.app.FlashcardActivity
import com.netenc.app.StudyHubActivity
import com.netenc.app.WorkspaceActivity
import com.netenc.app.data.AppDatabase
import java.time.Instant
import com.netenc.app.data.StudyRepository

class ReviewWorker(ctx: Context, params: WorkerParameters) : CoroutineWorker(ctx, params) {
    override suspend fun doWork(): Result {
        val study = StudyRepository(applicationContext)
        val due = study.dueNow(50)
        val dueTasks = AppDatabase.get(applicationContext).workspaceDao().dueTasks(Instant.now().toString())
        val today = study.todayCount()
        val goal = study.dailyGoal()
        val streak = study.currentStreak()

        if (due.isEmpty() && dueTasks.isEmpty() && today >= goal) return Result.success()

        val nm = applicationContext.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        val channelId = "netenc_review"
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            nm.createNotificationChannel(
                NotificationChannel(channelId, "یادآوری مطالعه", NotificationManager.IMPORTANCE_DEFAULT)
            )
        }
        val target = when {
            dueTasks.isNotEmpty() -> WorkspaceActivity::class.java
            due.isNotEmpty() -> FlashcardActivity::class.java
            else -> StudyHubActivity::class.java
        }
        val open = Intent(applicationContext, target).apply {
            if (dueTasks.isNotEmpty()) putExtra("mode", "tasks")
        }
        val pi = PendingIntent.getActivity(
            applicationContext, 0, open,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
        val title = when {
            dueTasks.isNotEmpty() -> "موعد کار: ${dueTasks.size} کار سررسیدشده"
            due.isNotEmpty() -> "Engineer Jokar — ${due.size} کارت due"
            else -> "هدف روزانه ناقص ($today/$goal)"
        }
        val body = buildString {
            if (dueTasks.isNotEmpty()) {
                append("کارهای سررسیدشده: ")
                append(dueTasks.take(3).joinToString("، ") { it.title })
                append(". ")
            }
            if (due.isNotEmpty()) append("${due.size} کارت برای مرور فاصله‌دار. ")
            append("امروز $today/$goal · زنجیره $streak روز")
        }
        val notif = NotificationCompat.Builder(applicationContext, channelId)
            .setSmallIcon(android.R.drawable.ic_menu_agenda)
            .setContentTitle(title)
            .setContentText(body)
            .setStyle(NotificationCompat.BigTextStyle().bigText(body + "\nAgain/Hard/Good/Easy برای SRS"))
            .setContentIntent(pi)
            .setAutoCancel(true)
            .build()
        nm.notify(1001, notif)
        return Result.success()
    }
}
