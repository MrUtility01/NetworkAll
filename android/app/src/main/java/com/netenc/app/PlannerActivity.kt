package com.netenc.app

import android.Manifest
import android.app.TimePickerDialog
import android.content.pm.PackageManager
import android.graphics.Color
import android.graphics.Typeface
import android.graphics.drawable.GradientDrawable
import android.os.Build
import android.os.Bundle
import android.view.Gravity
import android.view.View
import android.widget.ArrayAdapter
import android.widget.Button
import android.widget.CheckBox
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.Spinner
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import androidx.lifecycle.lifecycleScope
import android.icu.util.Calendar
import android.icu.util.PersianCalendar
import com.netenc.app.data.AppDatabase
import com.netenc.app.data.TaskEntity
import com.netenc.app.reminder.TaskReminderScheduler
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.text.SimpleDateFormat
import java.time.Instant
import java.util.Date
import java.util.Locale
import java.util.TimeZone
import java.util.UUID

class PlannerActivity : AppCompatActivity() {
    private val database by lazy { AppDatabase.get(this) }
    private lateinit var calendarGrid: LinearLayout
    private lateinit var monthTitle: TextView
    private lateinit var selectedTitle: TextView
    private lateinit var taskList: LinearLayout
    private var tasks: List<TaskEntity> = emptyList()
    private var selectedDay = PersianCalendar().apply {
        timeInMillis = System.currentTimeMillis()
        set(Calendar.HOUR_OF_DAY, 12)
        set(Calendar.MINUTE, 0)
        set(Calendar.SECOND, 0)
        set(Calendar.MILLISECOND, 0)
    }

    private val monthNames = arrayOf(
        "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
        "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"
    )
    private val weekdayNames = arrayOf("شنبه", "یکشنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنجشنبه", "جمعه")
    private val isoDate = SimpleDateFormat("yyyy-MM-dd", Locale.US).apply { timeZone = TimeZone.getDefault() }
    private val isoDateTime = SimpleDateFormat("yyyy-MM-dd'T'HH:mm", Locale.US).apply { timeZone = TimeZone.getDefault() }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        askNotificationPermission()

        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            layoutDirection = View.LAYOUT_DIRECTION_RTL
            setPadding(dp(14), dp(12), dp(14), dp(16))
            setBackgroundColor(Color.rgb(241, 245, 249))
        }
        val header = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = Gravity.CENTER_VERTICAL
        }
        header.addView(TextView(this).apply {
            text = "برنامه‌ریز روزانه"
            textSize = 21f
            typeface = Typeface.DEFAULT_BOLD
            setTextColor(Color.rgb(15, 23, 42))
        }, LinearLayout.LayoutParams(0, -2, 1f))
        header.addView(actionButton("خانه") {
            finish()
        })
        root.addView(header)

        val calendarCard = card()
        val monthRow = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = Gravity.CENTER_VERTICAL
        }
        monthRow.addView(actionButton("ماه قبل") { shiftMonth(-1) })
        monthTitle = TextView(this).apply {
            textSize = 17f
            typeface = Typeface.DEFAULT_BOLD
            gravity = Gravity.CENTER
            setTextColor(Color.rgb(15, 23, 42))
        }
        monthRow.addView(monthTitle, LinearLayout.LayoutParams(0, -2, 1f))
        monthRow.addView(actionButton("ماه بعد") { shiftMonth(1) })
        calendarCard.addView(monthRow)
        calendarCard.addView(actionButton("رفتن به امروز") {
            selectedDay = persianAt(System.currentTimeMillis())
            renderCalendar()
            renderTasks()
        })
        calendarGrid = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL }
        calendarCard.addView(calendarGrid)
        root.addView(calendarCard)

        val taskCard = card()
        selectedTitle = TextView(this).apply {
            textSize = 18f
            typeface = Typeface.DEFAULT_BOLD
            setTextColor(Color.rgb(15, 23, 42))
        }
        taskCard.addView(selectedTitle)
        taskCard.addView(actionButton("+ کار جدید") { showAddTaskDialog() })
        taskList = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL }
        taskCard.addView(taskList)
        root.addView(taskCard)

        setContentView(ScrollView(this).apply { isFillViewport = true; addView(root) })
        renderCalendar()
        refreshTasks()
    }

    private fun askNotificationPermission() {
        if (Build.VERSION.SDK_INT >= 33 &&
            ContextCompat.checkSelfPermission(this, Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED
        ) {
            requestPermissions(arrayOf(Manifest.permission.POST_NOTIFICATIONS), 7103)
        }
    }

    private fun dp(value: Int): Int = (value * resources.displayMetrics.density).toInt()

    private fun card(): LinearLayout = LinearLayout(this).apply {
        orientation = LinearLayout.VERTICAL
        setPadding(dp(12), dp(12), dp(12), dp(12))
        setBackgroundColor(Color.WHITE)
        background = GradientDrawable().apply {
            setColor(Color.WHITE)
            cornerRadius = dp(14).toFloat()
            setStroke(dp(1), Color.rgb(226, 232, 240))
        }
        val lp = LinearLayout.LayoutParams(-1, -2)
        lp.setMargins(0, dp(10), 0, dp(4))
        layoutParams = lp
    }

    private fun actionButton(label: String, action: () -> Unit): Button = Button(this).apply {
        text = label
        textSize = 12f
        setOnClickListener { action() }
    }

    private fun persianAt(time: Long): PersianCalendar = PersianCalendar().apply {
        timeInMillis = time
        set(Calendar.HOUR_OF_DAY, 12)
        set(Calendar.MINUTE, 0)
        set(Calendar.SECOND, 0)
        set(Calendar.MILLISECOND, 0)
    }

    private fun cloneDay(day: PersianCalendar): PersianCalendar =
        persianAt(day.timeInMillis).apply {
            set(Calendar.YEAR, day.get(Calendar.YEAR))
            set(Calendar.MONTH, day.get(Calendar.MONTH))
            set(Calendar.DAY_OF_MONTH, day.get(Calendar.DAY_OF_MONTH))
        }

    private fun dateKey(time: Long): String = isoDate.format(Date(time))
    private fun dayLabel(day: PersianCalendar): String {
        val m = day.get(Calendar.MONTH).coerceIn(0, 11)
        return day.get(Calendar.DAY_OF_MONTH).toString() + " " + monthNames[m] + " " + day.get(Calendar.YEAR)
    }

    private fun taskDateKey(task: TaskEntity): String = task.dueAt.takeIf { it.isNotBlank() }?.take(10) ?: ""

    private fun shiftMonth(delta: Int) {
        val first = cloneDay(selectedDay).apply {
            set(Calendar.DAY_OF_MONTH, 1)
            add(Calendar.MONTH, delta)
        }
        selectedDay = first
        renderCalendar()
        renderTasks()
    }

    private fun renderCalendar() {
        calendarGrid.removeAllViews()
        val currentYear = selectedDay.get(Calendar.YEAR)
        val currentMonth = selectedDay.get(Calendar.MONTH)
        monthTitle.text = monthNames[currentMonth.coerceIn(0, 11)] + " " + currentYear

        val head = LinearLayout(this).apply { orientation = LinearLayout.HORIZONTAL }
        weekdayNames.forEach { label ->
            head.addView(TextView(this).apply {
                text = label
                textSize = 10f
                gravity = Gravity.CENTER
                setTextColor(Color.rgb(100, 116, 139))
                setPadding(0, dp(8), 0, dp(8))
            }, LinearLayout.LayoutParams(0, -2, 1f))
        }
        calendarGrid.addView(head)

        val first = cloneDay(selectedDay).apply { set(Calendar.DAY_OF_MONTH, 1) }
        val startOffset = first.get(Calendar.DAY_OF_WEEK) % 7 // Saturday=0, Sunday=1, ...
        val cursor = cloneDay(first).apply { add(Calendar.DAY_OF_MONTH, -startOffset) }
        val todayKey = dateKey(System.currentTimeMillis())
        val selectedKey = dateKey(selectedDay.timeInMillis)
        val dueCounts = tasks.filter { it.dueAt.isNotBlank() }.groupingBy { taskDateKey(it) }.eachCount()

        repeat(6) {
            val row = LinearLayout(this).apply { orientation = LinearLayout.HORIZONTAL }
            repeat(7) {
                val dayCopy = cloneDay(cursor)
                val key = dateKey(dayCopy.timeInMillis)
                val inMonth = dayCopy.get(Calendar.YEAR) == currentYear && dayCopy.get(Calendar.MONTH) == currentMonth
                val count = dueCounts[key] ?: 0
                val label = dayCopy.get(Calendar.DAY_OF_MONTH).toString() + if (count > 0) "\n" + count + " کار" else "\n "
                val cell = TextView(this).apply {
                    text = label
                    textSize = 12f
                    gravity = Gravity.CENTER
                    setTextColor(if (inMonth) Color.rgb(15, 23, 42) else Color.rgb(148, 163, 184))
                    background = GradientDrawable().apply {
                        cornerRadius = dp(8).toFloat()
                        val fill = when {
                            key == selectedKey -> Color.rgb(191, 219, 254)
                            key == todayKey -> Color.rgb(226, 232, 240)
                            else -> Color.rgb(248, 250, 252)
                        }
                        setColor(fill)
                        setStroke(dp(1), if (key == selectedKey) Color.rgb(37, 99, 235) else Color.rgb(226, 232, 240))
                    }
                    isClickable = true
                    setOnClickListener {
                        selectedDay = cloneDay(dayCopy)
                        renderCalendar()
                        renderTasks()
                    }
                }
                val lp = LinearLayout.LayoutParams(0, dp(52), 1f)
                lp.setMargins(dp(2), dp(2), dp(2), dp(2))
                row.addView(cell, lp)
                cursor.add(Calendar.DAY_OF_MONTH, 1)
            }
            calendarGrid.addView(row)
        }
    }

    private fun refreshTasks() {
        lifecycleScope.launch {
            tasks = withContext(Dispatchers.IO) { database.workspaceDao().allTasks() }
            renderCalendar()
            renderTasks()
        }
    }

    private fun renderTasks() {
        taskList.removeAllViews()
        selectedTitle.text = "کارهای " + dayLabel(selectedDay)
        val selectedKey = dateKey(selectedDay.timeInMillis)
        val todayKey = dateKey(System.currentTimeMillis())
        val dayTasks = tasks.filter { taskDateKey(it) == selectedKey }
        val undated = if (selectedKey == todayKey) tasks.filter { it.dueAt.isBlank() } else emptyList()
        val ordered = (dayTasks + undated).distinctBy { it.uid }.sortedWith(
            compareBy<TaskEntity> { it.done }.thenByDescending { it.priority }.thenBy { it.dueAt }
        )
        if (ordered.isEmpty()) {
            taskList.addView(TextView(this).apply {
                text = "برای این روز کاری ثبت نشده است."
                textSize = 14f
                setPadding(0, dp(12), 0, dp(12))
                setTextColor(Color.rgb(100, 116, 139))
            })
            return
        }
        ordered.forEach { task ->
            val row = LinearLayout(this).apply {
                orientation = LinearLayout.HORIZONTAL
                gravity = Gravity.CENTER_VERTICAL
                setPadding(0, dp(8), 0, dp(8))
            }
            val check = CheckBox(this).apply {
                isChecked = task.done
                setOnCheckedChangeListener { _, checked ->
                    lifecycleScope.launch {
                        withContext(Dispatchers.IO) {
                            database.workspaceDao().upsertTask(task.copy(done = checked, lastUpdated = Instant.now().toString()))
                        }
                        if (checked) TaskReminderScheduler.cancel(this@PlannerActivity, task.uid)
                        else scheduleTaskReminder(task.copy(done = false))
                        refreshTasks()
                    }
                }
            }
            row.addView(check)
            val column = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL }
            column.addView(TextView(this).apply {
                text = task.title
                textSize = 15f
                typeface = if (task.done) Typeface.DEFAULT else Typeface.DEFAULT_BOLD
                setTextColor(if (task.done) Color.rgb(100, 116, 139) else Color.rgb(15, 23, 42))
            })
            val details = ArrayList<String>()
            if (task.dueAt.contains("T")) details.add("ساعت " + task.dueAt.substringAfter("T").take(5))
            details.add("اولویت " + when (task.priority) { 3 -> "زیاد"; 2 -> "معمولی"; else -> "کم" })
            if (task.body.isNotBlank()) details.add(task.body.take(100))
            column.addView(TextView(this).apply {
                text = details.joinToString(" · ")
                textSize = 11f
                setTextColor(Color.rgb(100, 116, 139))
            })
            row.addView(column, LinearLayout.LayoutParams(0, -2, 1f))
            row.setOnLongClickListener {
                AlertDialog.Builder(this)
                    .setTitle("حذف کار")
                    .setMessage("کار «" + task.title + "» حذف شود؟")
                    .setNegativeButton("لغو", null)
                    .setPositiveButton("حذف") { _, _ ->
                        lifecycleScope.launch {
                            withContext(Dispatchers.IO) { database.workspaceDao().deleteTask(task.uid) }
                            TaskReminderScheduler.cancel(this@PlannerActivity, task.uid)
                            refreshTasks()
                        }
                    }.show()
                true
            }
            taskList.addView(row)
        }
    }

    private fun scheduleTaskReminder(task: TaskEntity) {
        if (task.done || !task.dueAt.contains("T")) return
        try {
            val whenDate = isoDateTime.parse(task.dueAt) ?: return
            TaskReminderScheduler.schedule(this, task.uid, whenDate.time)
        } catch (_: Exception) {
            // A date-only/all-day task has no exact notification time.
        }
    }

    private fun showAddTaskDialog() {
        val titleInput = EditText(this).apply { hint = "عنوان کار"; maxLines = 2 }
        val bodyInput = EditText(this).apply { hint = "توضیحات / سناریو (اختیاری)"; minLines = 2; gravity = Gravity.TOP }
        val timeLabel = TextView(this).apply {
            text = "تاریخ انتخاب‌شده: " + dayLabel(selectedDay) + "\nبدون ساعت (کار تمام‌روزه)"
            setTextColor(Color.rgb(71, 85, 105))
            setPadding(0, dp(6), 0, dp(6))
        }
        var chosenHour: Int? = null
        var chosenMinute: Int? = null
        val timeButton = Button(this).apply {
            text = "انتخاب ساعت سررسید (اختیاری)"
            setOnClickListener {
                val now = java.util.Calendar.getInstance()
                TimePickerDialog(this@PlannerActivity, { _, hour, minute ->
                    chosenHour = hour
                    chosenMinute = minute
                    timeLabel.text = "تاریخ: " + dayLabel(selectedDay) + " · ساعت " +
                        String.format(Locale.US, "%02d:%02d", hour, minute)
                    text = "تغییر ساعت"
                }, now.get(java.util.Calendar.HOUR_OF_DAY), now.get(java.util.Calendar.MINUTE), true).show()
            }
        }
        val clearTime = Button(this).apply {
            text = "پاک کردن ساعت"
            setOnClickListener {
                chosenHour = null
                chosenMinute = null
                timeLabel.text = "تاریخ انتخاب‌شده: " + dayLabel(selectedDay) + "\nبدون ساعت (کار تمام‌روزه)"
            }
        }
        val priority = Spinner(this).apply {
            adapter = ArrayAdapter(
                this@PlannerActivity,
                android.R.layout.simple_spinner_dropdown_item,
                arrayOf("اولویت کم", "اولویت معمولی", "اولویت زیاد")
            )
            setSelection(1)
        }
        val reminder = CheckBox(this).apply {
            text = "یادآوری هنگام سررسید (اگر ساعت مشخص شده باشد)"
            isChecked = true
        }
        val form = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(dp(8), dp(2), dp(8), dp(2))
            addView(titleInput)
            addView(bodyInput)
            addView(timeLabel)
            addView(timeButton)
            addView(clearTime)
            addView(TextView(this@PlannerActivity).apply { text = "اولویت" })
            addView(priority)
            addView(reminder)
        }
        val scroll = ScrollView(this).apply { addView(form) }
        val dialog = AlertDialog.Builder(this)
            .setTitle("کار جدید")
            .setView(scroll)
            .setNegativeButton("لغو", null)
            .setPositiveButton("ذخیره", null)
            .create()
        dialog.setOnShowListener {
            dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener {
                val title = titleInput.text.toString().trim()
                if (title.isEmpty()) {
                    Toast.makeText(this, "عنوان کار را وارد کنید.", Toast.LENGTH_SHORT).show()
                    return@setOnClickListener
                }
                val base = cloneDay(selectedDay).apply {
                    set(Calendar.HOUR_OF_DAY, chosenHour ?: 12)
                    set(Calendar.MINUTE, chosenMinute ?: 0)
                    set(Calendar.SECOND, 0)
                    set(Calendar.MILLISECOND, 0)
                }
                val due = if (chosenHour != null && chosenMinute != null)
                    isoDateTime.format(Date(base.timeInMillis))
                else
                    isoDate.format(Date(base.timeInMillis))
                val id = UUID.randomUUID().toString()
                val task = TaskEntity(
                    uid = id,
                    title = title,
                    body = bodyInput.text.toString().trim(),
                    done = false,
                    dueAt = due,
                    priority = priority.selectedItemPosition + 1,
                    lastUpdated = Instant.now().toString()
                )
                lifecycleScope.launch {
                    withContext(Dispatchers.IO) { database.workspaceDao().upsertTask(task) }
                    if (reminder.isChecked && chosenHour != null && chosenMinute != null) {
                        TaskReminderScheduler.schedule(this@PlannerActivity, id, base.timeInMillis)
                    }
                    dialog.dismiss()
                    refreshTasks()
                }
            }
        }
        dialog.show()
    }
}
