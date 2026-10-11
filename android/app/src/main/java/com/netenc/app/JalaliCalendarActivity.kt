package com.netenc.app

import android.graphics.Color
import android.os.Bundle
import android.view.Gravity
import android.view.View
import android.widget.Button
import android.widget.LinearLayout
import android.widget.TextView
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.netenc.app.data.AppDatabase
import com.netenc.app.data.TaskEntity
import com.netenc.app.util.JalaliDate
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.time.Instant
import java.time.ZoneId

/** Monthly Jalali agenda for local task due dates. */
class JalaliCalendarActivity : AppCompatActivity() {
    private var jalaliYear = 1405
    private var jalaliMonth = 1
    private var tasks: List<TaskEntity> = emptyList()
    private lateinit var monthTitle: TextView
    private lateinit var calendarBody: LinearLayout

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val today = JalaliDate.fromGregorian(java.time.LocalDate.now())
        jalaliYear = today.first
        jalaliMonth = today.second

        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            layoutDirection = View.LAYOUT_DIRECTION_RTL
            setPadding(dp(12), dp(12), dp(12), dp(12))
            setBackgroundColor(Color.WHITE)
        }
        val nav = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = Gravity.CENTER_VERTICAL
            addView(Button(this@JalaliCalendarActivity).apply {
                text = "ماه قبل"
                setOnClickListener { moveMonth(-1) }
            }, LinearLayout.LayoutParams(0, dp(48), 1f))
            monthTitle = TextView(this@JalaliCalendarActivity).apply {
                textSize = 18f
                gravity = Gravity.CENTER
                setTextColor(Color.BLACK)
            }
            addView(monthTitle, LinearLayout.LayoutParams(0, dp(48), 2f))
            addView(Button(this@JalaliCalendarActivity).apply {
                text = "ماه بعد"
                setOnClickListener { moveMonth(1) }
            }, LinearLayout.LayoutParams(0, dp(48), 1f))
        }
        root.addView(nav)
        root.addView(TextView(this).apply {
            text = "تقویم شمسی کارها · نقطه یعنی برای آن روز موعد ثبت شده"
            textSize = 13f
            setTextColor(Color.DKGRAY)
            setPadding(0, dp(8), 0, dp(8))
        })
        calendarBody = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL }
        root.addView(calendarBody)
        root.addView(Button(this).apply {
            text = "رفتن به فهرست کارها"
            setOnClickListener { startActivity(android.content.Intent(this@JalaliCalendarActivity, WorkspaceActivity::class.java).putExtra("mode", "tasks")) }
        })
        setContentView(root)
        lifecycleScope.launch {
            tasks = withContext(Dispatchers.IO) { AppDatabase.get(this@JalaliCalendarActivity).workspaceDao().allTasks() }
            render()
        }
    }

    private fun moveMonth(delta: Int) {
        jalaliMonth += delta
        if (jalaliMonth < 1) { jalaliMonth = 12; jalaliYear-- }
        if (jalaliMonth > 12) { jalaliMonth = 1; jalaliYear++ }
        render()
    }

    private fun render() {
        monthTitle.text = JalaliDate.monthName(jalaliMonth) + " " + JalaliDate.persianDigits(jalaliYear.toString())
        calendarBody.removeAllViews()
        val names = listOf("شنبه", "یکشنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنجشنبه", "جمعه")
        val header = LinearLayout(this).apply { orientation = LinearLayout.HORIZONTAL }
        names.forEach { name ->
            header.addView(TextView(this).apply {
                text = name
                textSize = 11f
                gravity = Gravity.CENTER
                setTextColor(Color.DKGRAY)
            }, LinearLayout.LayoutParams(0, dp(34), 1f))
        }
        calendarBody.addView(header)

        val firstDate = JalaliDate.toGregorian(jalaliYear, jalaliMonth, 1)
        val offset = (firstDate.dayOfWeek.value + 1) % 7 // Saturday is column zero.
        val length = JalaliDate.monthLength(jalaliYear, jalaliMonth)
        val rows = (offset + length + 6) / 7
        for (rowIndex in 0 until rows) {
            val row = LinearLayout(this).apply { orientation = LinearLayout.HORIZONTAL }
            for (col in 0..6) {
                val day = rowIndex * 7 + col - offset + 1
                if (day in 1..length) {
                    val count = tasksForDay(day).size
                    val label = JalaliDate.persianDigits(day.toString()) + if (count > 0) "\n• " + JalaliDate.persianDigits(count.toString()) else ""
                    row.addView(Button(this).apply {
                        text = label
                        textSize = 12f
                        setTextColor(if (count > 0) Color.WHITE else Color.DKGRAY)
                        setBackgroundColor(if (count > 0) Color.rgb(37, 99, 235) else Color.rgb(241, 245, 249))
                        setOnClickListener { showDay(day) }
                    }, LinearLayout.LayoutParams(0, dp(58), 1f).apply { setMargins(dp(2), dp(2), dp(2), dp(2)) })
                } else {
                    row.addView(TextView(this), LinearLayout.LayoutParams(0, dp(58), 1f))
                }
            }
            calendarBody.addView(row)
        }
    }

    private fun tasksForDay(day: Int): List<TaskEntity> = tasks.filter { task ->
        if (task.dueAt.isBlank()) false else runCatching {
            val local = Instant.parse(task.dueAt).atZone(ZoneId.systemDefault()).toLocalDate()
            JalaliDate.fromGregorian(local) == Triple(jalaliYear, jalaliMonth, day)
        }.getOrDefault(false)
    }

    private fun showDay(day: Int) {
        val rows = tasksForDay(day)
        val message = if (rows.isEmpty()) "برای این روز موعدی ثبت نشده است."
        else rows.joinToString("\n\n") { task ->
            val state = if (task.done) "انجام‌شده" else "باز"
            task.title + " — " + state + "\n" + task.body
        }
        AlertDialog.Builder(this)
            .setTitle(JalaliDate.persianDigits(day.toString()) + " " + JalaliDate.monthName(jalaliMonth) + " " + JalaliDate.persianDigits(jalaliYear.toString()))
            .setMessage(message)
            .setPositiveButton("فهرست کارها") { _, _ ->
                startActivity(android.content.Intent(this, WorkspaceActivity::class.java).putExtra("mode", "tasks"))
            }
            .setNegativeButton("بستن", null)
            .show()
    }

    private fun dp(value: Int): Int = (value * resources.displayMetrics.density).toInt()
}
