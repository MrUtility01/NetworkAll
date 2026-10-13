package com.netenc.app

import android.graphics.Color
import android.graphics.drawable.GradientDrawable
import android.os.Bundle
import android.text.InputType
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
import android.app.TimePickerDialog
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.netenc.app.data.AppDatabase
import com.netenc.app.data.NoteEntity
import com.netenc.app.data.TaskEntity
import com.netenc.app.data.VaultEntity
import com.netenc.app.reminder.TaskReminderScheduler
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.time.Instant
import java.util.UUID
import android.util.Base64
import javax.crypto.Cipher
import javax.crypto.spec.SecretKeySpec

class WorkspaceActivity : AppCompatActivity() {
    private val db by lazy { AppDatabase.get(this) }
    private lateinit var listView: LinearLayout
    private lateinit var summaryView: TextView
    private lateinit var searchInput: EditText
    private var mode = "tasks" // tasks | notes | vault
    private var taskFilter = "open" // all | open | done

    private data class Row(
        val uid: String,
        val title: String,
        val body: String,
        val meta: String = "",
        val done: Boolean = false
    )

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        mode = intent.getStringExtra("mode") ?: "tasks"
        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            layoutDirection = View.LAYOUT_DIRECTION_RTL
            setBackgroundColor(Ui.BG)
            setPadding(Ui.dp(this@WorkspaceActivity, 16), Ui.dp(this@WorkspaceActivity, 16),
                Ui.dp(this@WorkspaceActivity, 16), Ui.dp(this@WorkspaceActivity, 16))
        }
        root.addView(Ui.text(this, when (mode) {
            "notes" -> "دفتر یادداشت"
            "vault" -> "مدیریت رمزها"
            else -> "برنامه‌ریز کارها"
        }, 22f))
        root.addView(Ui.text(this, when (mode) {
            "notes" -> "یادداشت‌های دسته‌بندی‌شده، قابل جست‌وجو و ویرایش"
            "vault" -> "اطلاعات ذخیره‌شده در این دستگاه"
            else -> "کارها، اولویت‌ها و یادآوری با تاریخ شمسی و ساعت محلی"
        }, 12f, Ui.MUTED))
        summaryView = Ui.text(this, "", 13f)
        root.addView(summaryView)

        if (mode == "tasks") {
            val filters = LinearLayout(this).apply {
                orientation = LinearLayout.HORIZONTAL
                layoutDirection = View.LAYOUT_DIRECTION_RTL
            }
            filters.addView(actionButton("باز", Ui.ACCENT) { taskFilter = "open"; refresh() }, weighted())
            filters.addView(actionButton("همه", Color.parseColor("#475569")) { taskFilter = "all"; refresh() }, weighted())
            filters.addView(actionButton("انجام‌شده", Ui.SUCCESS) { taskFilter = "done"; refresh() }, weighted())
            root.addView(filters)
        } else if (mode == "notes") {
            searchInput = EditText(this).apply {
                hint = "جست‌وجوی عنوان، متن یا برچسب"
                inputType = InputType.TYPE_CLASS_TEXT
                setSingleLine(true)
            }
            root.addView(searchInput)
            searchInput.addTextChangedListener(object : android.text.TextWatcher {
                override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}
                override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) { refresh() }
                override fun afterTextChanged(s: android.text.Editable?) {}
            })
        }

        root.addView(actionButton(if (mode == "tasks") "+ افزودن کار" else if (mode == "notes") "+ یادداشت جدید" else "+ مورد جدید",
            Ui.ACCENT) { addItem() })
        listView = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            layoutDirection = View.LAYOUT_DIRECTION_RTL
        }
        root.addView(listView)
        setContentView(ScrollView(this).apply {
            setFillViewport(true)
            addView(root)
        })
        refresh()
    }

    private fun now() = Instant.now().toString()

    private fun weighted() = LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f).apply {
        setMargins(3, 3, 3, 8)
    }

    private fun actionButton(label: String, color: Int, action: () -> Unit) = Button(this).apply {
        text = label
        typeface = Ui.persianTypeface()
        setTextColor(Color.WHITE)
        setBackgroundColor(color)
        setOnClickListener { action() }
    }

    private fun refresh() {
        lifecycleScope.launch {
            val rows = withContext(Dispatchers.IO) {
                when (mode) {
                    "notes" -> db.workspaceDao().allNotes().map {
                        Row(it.uid, it.title, it.body, if (it.tags.isBlank()) "بدون برچسب" else it.tags)
                    }
                    "vault" -> db.workspaceDao().allVault().map {
                        Row(it.uid, it.title, "نام کاربری: ${it.username}", "ذخیره‌شده روی دستگاه")
                    }
                    else -> db.workspaceDao().allTasks().map {
                        val due = if (it.dueAt.isNotBlank()) "⏰ ${JalaliDate.formatStored(it.dueAt)}" else "بدون یادآوری"
                        val priority = when (it.priority) { 3 -> "بالا"; 2 -> "متوسط"; else -> "عادی" }
                        Row(it.uid, it.title, it.body, "${if (it.done) "✓ انجام‌شده" else "○ باز"} · اولویت $priority · $due", it.done)
                    }
                }
            }
            val filtered = when (mode) {
                "notes" -> {
                    val q = searchInput.text.toString().trim()
                    if (q.isBlank()) rows else rows.filter {
                        it.title.contains(q, true) || it.body.contains(q, true) || it.meta.contains(q, true)
                    }
                }
                "tasks" -> when (taskFilter) {
                    "open" -> rows.filterNot { it.done }
                    "done" -> rows.filter { it.done }
                    else -> rows
                }
                else -> rows
            }
            summaryView.text = when (mode) {
                "tasks" -> "کل: ${rows.size} · باز: ${rows.count { !it.done }} · انجام‌شده: ${rows.count { it.done }} · نمایش: ${filtered.size}"
                "notes" -> "یادداشت‌ها: ${rows.size} · نتیجه: ${filtered.size}"
                else -> "موارد ذخیره‌شده: ${rows.size}"
            }
            listView.removeAllViews()
            if (filtered.isEmpty()) {
                listView.addView(Ui.text(this@WorkspaceActivity,
                    if (mode == "notes" && rows.isNotEmpty()) "موردی با این جست‌وجو پیدا نشد." else "هنوز موردی ثبت نشده است. از دکمه افزودن شروع کن.",
                    14f, Ui.MUTED))
            }
            filtered.forEach { row ->
                val card = LinearLayout(this@WorkspaceActivity).apply {
                    orientation = LinearLayout.VERTICAL
                    layoutDirection = View.LAYOUT_DIRECTION_RTL
                    setPadding(Ui.dp(this@WorkspaceActivity, 12), Ui.dp(this@WorkspaceActivity, 8),
                        Ui.dp(this@WorkspaceActivity, 12), Ui.dp(this@WorkspaceActivity, 8))
                    background = GradientDrawable().apply {
                        setColor(Ui.CARD)
                        cornerRadius = Ui.dp(this@WorkspaceActivity, 14).toFloat()
                        setStroke(Ui.dp(this@WorkspaceActivity, 1), Ui.BORDER)
                    }
                }
                card.addView(Ui.text(this@WorkspaceActivity, row.title, 16f, Ui.TEXT))
                if (row.meta.isNotBlank()) card.addView(Ui.text(this@WorkspaceActivity, row.meta, 12f,
                    if (row.done) Ui.SUCCESS else Ui.MUTED))
                if (row.body.isNotBlank()) card.addView(Ui.text(this@WorkspaceActivity, row.body.take(420), 13f, Ui.TEXT))
                card.setOnClickListener { showItemActions(row) }
                card.setOnLongClickListener { showItemActions(row); true }
                card.layoutParams = LinearLayout.LayoutParams(
                    LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT
                ).apply { setMargins(0, Ui.dp(this@WorkspaceActivity, 4), 0, Ui.dp(this@WorkspaceActivity, 8)) }
                listView.addView(card)
            }
        }
    }

    private fun showItemActions(row: Row) {
        val options = when (mode) {
            "notes" -> arrayOf("ویرایش یادداشت", "حذف یادداشت")
            "vault" -> arrayOf("نمایش اطلاعات")
            else -> if (row.done) arrayOf("ویرایش کار", "بازگرداندن به کارهای باز", "حذف کار")
                else arrayOf("ویرایش کار", "علامت‌گذاری به‌عنوان انجام‌شده", "حذف کار")
        }
        AlertDialog.Builder(this).setTitle(row.title).setItems(options) { _, which ->
            when (mode) {
                "notes" -> if (which == 0) addItem(row.uid) else confirmDelete(row.uid, row.title)
                "vault" -> AlertDialog.Builder(this).setTitle(row.title).setMessage(row.body)
                    .setPositiveButton("بستن", null).show()
                else -> when (which) {
                    0 -> addItem(row.uid)
                    1 -> toggleTask(row.uid)
                    else -> confirmDelete(row.uid, row.title)
                }
            }
        }.setNegativeButton("بستن", null).show()
    }

    private fun confirmDelete(uid: String, title: String) {
        AlertDialog.Builder(this).setTitle("حذف مورد")
            .setMessage("«$title» حذف شود؟ این کار قابل بازگشت نیست.")
            .setNegativeButton("لغو", null)
            .setPositiveButton("حذف") { _, _ ->
                lifecycleScope.launch {
                    withContext(Dispatchers.IO) {
                        when (mode) {
                            "notes" -> db.workspaceDao().deleteNote(uid)
                            "vault" -> db.workspaceDao().deleteVault(uid)
                            else -> db.workspaceDao().deleteTask(uid)
                        }
                    }
                    if (mode == "tasks") TaskReminderScheduler.cancel(this@WorkspaceActivity, uid)
                    refresh()
                }
            }.show()
    }

    private fun toggleTask(uid: String) {
        lifecycleScope.launch {
            val task = withContext(Dispatchers.IO) { db.workspaceDao().allTasks().find { it.uid == uid } }
                ?: return@launch
            val updated = task.copy(done = !task.done, lastUpdated = now())
            withContext(Dispatchers.IO) { db.workspaceDao().upsertTask(updated) }
            if (updated.done) TaskReminderScheduler.cancel(this@WorkspaceActivity, uid)
            else if (updated.dueAt.isNotBlank()) TaskReminderScheduler.schedule(
                this@WorkspaceActivity, uid, updated.title, updated.body, updated.dueAt
            )
            Toast.makeText(this@WorkspaceActivity, if (updated.done) "کار انجام شد" else "کار دوباره باز شد", Toast.LENGTH_SHORT).show()
            refresh()
        }
    }

    private fun addItem(uid: String? = null) {
        lifecycleScope.launch {
            val existingTask = if (mode == "tasks" && uid != null) withContext(Dispatchers.IO) {
                db.workspaceDao().allTasks().find { it.uid == uid }
            } else null
            val existingNote = if (mode == "notes" && uid != null) withContext(Dispatchers.IO) {
                db.workspaceDao().allNotes().find { it.uid == uid }
            } else null
            val existingVault = if (mode == "vault" && uid != null) withContext(Dispatchers.IO) {
                db.workspaceDao().allVault().find { it.uid == uid }
            } else null

            val title = EditText(this@WorkspaceActivity).apply {
                hint = "عنوان روشن و قابل جست‌وجو"
                setText(existingTask?.title ?: existingNote?.title ?: existingVault?.title.orEmpty())
                setSingleLine(true)
            }
            val body = EditText(this@WorkspaceActivity).apply {
                hint = when (mode) { "vault" -> "رمز / توضیحات"; "notes" -> "متن یادداشت"; else -> "شرح، چک‌لیست یا نتیجه مورد انتظار" }
                minLines = 3
                gravity = android.view.Gravity.TOP
                setText(existingTask?.body ?: existingNote?.body ?: existingVault?.notes.orEmpty())
            }
            val tags = EditText(this@WorkspaceActivity).apply {
                hint = "برچسب‌ها با ویرگول جدا شوند (اختیاری)"
                setText(existingNote?.tags.orEmpty())
            }
            val user = EditText(this@WorkspaceActivity).apply {
                hint = "نام کاربری (اختیاری)"
                setText(existingVault?.username.orEmpty())
            }
            val dateText = existingTask?.dueAt?.takeIf { it.isNotBlank() }?.let { JalaliDate.datePartStored(it) }
                ?: JalaliDate.today()
            val timeText = existingTask?.dueAt?.takeIf { it.isNotBlank() }?.let { JalaliDate.timePartStored(it) }
                ?: JalaliDate.currentTime()
            val date = EditText(this@WorkspaceActivity).apply {
                hint = "تاریخ شمسی: ۱۴۰۵/۰۷/۲۱"
                setText(dateText)
                setSingleLine(true)
                isFocusable = false
                isClickable = false
            }
            val time = EditText(this@WorkspaceActivity).apply {
                hint = "ساعت: ۱۴:۳۰"
                setText(timeText)
                setSingleLine(true)
                inputType = InputType.TYPE_CLASS_DATETIME
                isFocusable = false
                setOnClickListener { openTimePicker(time) }
            }
            val reminder = CheckBox(this@WorkspaceActivity).apply {
                text = "یادآوری در تاریخ و ساعت بالا"
                isChecked = existingTask?.dueAt?.isNotBlank() == true
                typeface = Ui.persianTypeface()
            }
            val priority = Spinner(this@WorkspaceActivity).apply {
                adapter = ArrayAdapter(this@WorkspaceActivity, android.R.layout.simple_spinner_dropdown_item,
                    listOf("عادی", "متوسط", "بالا"))
                setSelection(((existingTask?.priority ?: 1) - 1).coerceIn(0, 2))
            }
            val form = LinearLayout(this@WorkspaceActivity).apply {
                orientation = LinearLayout.VERTICAL
                layoutDirection = View.LAYOUT_DIRECTION_RTL
                setPadding(20, 4, 20, 4)
                addView(title); addView(body)
                when (mode) {
                    "notes" -> addView(tags)
                    "vault" -> addView(user)
                    else -> {
                        addView(Ui.text(this@WorkspaceActivity, "سررسید شمسی", 13f, Ui.MUTED))
                        addView(date)
                        addView(actionButton("انتخاب تاریخ شمسی", Color.parseColor("#475569")) {
                            openJalaliDatePicker(date)
                        })
                        addView(time)
                        addView(actionButton("انتخاب ساعت", Color.parseColor("#475569")) {
                            openTimePicker(time)
                        })
                        addView(reminder)
                        addView(Ui.text(this@WorkspaceActivity, "اولویت", 13f, Ui.MUTED))
                        addView(priority)
                    }
                }
            }
            val dialogTitle = when (mode) {
                "notes" -> if (uid == null) "یادداشت جدید" else "ویرایش یادداشت"
                "vault" -> if (uid == null) "مورد جدید" else "ویرایش مورد"
                else -> if (uid == null) "کار جدید" else "ویرایش کار"
            }
            AlertDialog.Builder(this@WorkspaceActivity)
                .setTitle(dialogTitle)
                .setView(ScrollView(this@WorkspaceActivity).apply { addView(form) })
                .setPositiveButton("ذخیره", null)
                .setNegativeButton("لغو", null)
                .create().also { dialog ->
                    dialog.setOnShowListener {
                        dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener {
                            val t = title.text.toString().trim()
                            if (t.isEmpty()) {
                                title.error = "عنوان الزامی است"
                                return@setOnClickListener
                            }
                            val savedId = uid ?: UUID.randomUUID().toString()
                            val dueAt = if (mode == "tasks" && reminder.isChecked) {
                                try { JalaliDate.parseJalali(date.text.toString(), time.text.toString()) }
                                catch (e: Exception) {
                                    Toast.makeText(this@WorkspaceActivity, e.message ?: "تاریخ یا ساعت معتبر نیست", Toast.LENGTH_LONG).show()
                                    return@setOnClickListener
                                }
                            } else ""
                            if (mode == "tasks" && reminder.isChecked && dueAt.isNotBlank() &&
                                JalaliDate.parseStored(dueAt).atZone(java.time.ZoneId.systemDefault()).toInstant().isBefore(java.time.Instant.now())) {
                                Toast.makeText(this@WorkspaceActivity, "زمان یادآوری گذشته است؛ تاریخ و ساعت آینده را انتخاب کن.", Toast.LENGTH_LONG).show()
                                return@setOnClickListener
                            }
                            lifecycleScope.launch {
                                withContext(Dispatchers.IO) {
                                    val id = savedId
                                    when (mode) {
                                        "notes" -> db.workspaceDao().upsertNote(NoteEntity(
                                            id, t, body.text.toString().trim(), tags.text.toString().trim(), now()
                                        ))
                                        "vault" -> db.workspaceDao().upsertVault(VaultEntity(
                                            id, t, user.text.toString().trim(),
                                            secretEnc = if (body.text.isNotBlank()) simpleEnc(body.text.toString()) else existingVault?.secretEnc.orEmpty(),
                                            url = existingVault?.url.orEmpty(), notes = existingVault?.notes.orEmpty(), lastUpdated = now()
                                        ))
                                        else -> db.workspaceDao().upsertTask(TaskEntity(
                                            id, t, body.text.toString().trim(), existingTask?.done ?: false, dueAt,
                                            priority.selectedItemPosition + 1, now(), existingTask?.deviceId ?: "android"
                                        ))
                                    }
                                }
                                if (mode == "tasks") {
                                    if (dueAt.isBlank()) TaskReminderScheduler.cancel(this@WorkspaceActivity, savedId)
                                    else TaskReminderScheduler.schedule(this@WorkspaceActivity, savedId, t, body.text.toString(), dueAt)
                                }
                                dialog.dismiss()
                                Toast.makeText(this@WorkspaceActivity, "ذخیره شد", Toast.LENGTH_SHORT).show()
                                refresh()
                            }
                        }
                    }
                    dialog.show()
                }
        }
    }

    private fun openJalaliDatePicker(field: EditText) {
        val current = JalaliDate.today().split("/")
        val initial = field.text.toString().split("/")
        val currentYear = current.getOrNull(0)?.toIntOrNull() ?: 1405
        val year = initial.getOrNull(0)?.toIntOrNull() ?: currentYear
        val month = initial.getOrNull(1)?.toIntOrNull()?.coerceIn(1, 12) ?: 1
        val day = initial.getOrNull(2)?.toIntOrNull() ?: 1
        val yearPicker = android.widget.NumberPicker(this).apply {
            minValue = (currentYear - 2).coerceAtLeast(1300)
            maxValue = currentYear + 8
            value = year.coerceIn(minValue, maxValue)
            wrapSelectorWheel = false
        }
        val monthPicker = android.widget.NumberPicker(this).apply {
            minValue = 1
            maxValue = 12
            value = month
            displayedValues = arrayOf("فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
                "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند")
            wrapSelectorWheel = false
        }
        val dayPicker = android.widget.NumberPicker(this).apply {
            minValue = 1
            maxValue = JalaliDate.daysInMonth(yearPicker.value, monthPicker.value)
            value = day.coerceIn(1, maxValue)
            wrapSelectorWheel = false
        }
        fun updateDayRange() {
            val maxDay = JalaliDate.daysInMonth(yearPicker.value, monthPicker.value)
            dayPicker.maxValue = maxDay
            if (dayPicker.value > maxDay) dayPicker.value = maxDay
        }
        yearPicker.setOnValueChangedListener { _, _, _ -> updateDayRange() }
        monthPicker.setOnValueChangedListener { _, _, _ -> updateDayRange() }
        val row = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            layoutDirection = View.LAYOUT_DIRECTION_RTL
            addView(dayPicker, LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f))
            addView(monthPicker, LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f))
            addView(yearPicker, LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f))
        }
        AlertDialog.Builder(this)
            .setTitle("انتخاب تاریخ شمسی")
            .setView(row)
            .setPositiveButton("انتخاب") { _, _ ->
                field.setText("%04d/%02d/%02d".format(java.util.Locale.ROOT,
                    yearPicker.value, monthPicker.value, dayPicker.value))
            }
            .setNegativeButton("لغو", null)
            .show()
    }

    private fun openTimePicker(field: EditText) {
        val pieces = field.text.toString().split(":")
        val hour = pieces.getOrNull(0)?.toIntOrNull()?.coerceIn(0, 23) ?: 9
        val minute = pieces.getOrNull(1)?.toIntOrNull()?.coerceIn(0, 59) ?: 0
        TimePickerDialog(this, { _, h, m ->
            field.setText("%02d:%02d".format(java.util.Locale.ROOT, h, m))
        }, hour, minute, true).show()
    }

    /** Legacy local vault encoding retained only for compatibility with existing records. */
    private fun simpleEnc(plain: String): String {
        return try {
            val key = SecretKeySpec("NetEncJokarKey16".toByteArray(), "AES")
            val c = Cipher.getInstance("AES/ECB/PKCS5Padding")
            c.init(Cipher.ENCRYPT_MODE, key)
            Base64.encodeToString(c.doFinal(plain.toByteArray()), Base64.NO_WRAP)
        } catch (_: Exception) { plain }
    }
}
