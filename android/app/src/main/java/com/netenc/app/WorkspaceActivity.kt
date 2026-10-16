package com.netenc.app

import android.graphics.Color
import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.netenc.app.data.AppDatabase
import com.netenc.app.data.NoteEntity
import com.netenc.app.data.TaskEntity
import com.netenc.app.data.VaultEntity
import com.netenc.app.reminder.ReminderScheduler
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.time.Instant
import java.util.UUID
import android.icu.util.PersianCalendar
import android.icu.util.ULocale
import android.util.Base64
import javax.crypto.Cipher
import javax.crypto.spec.SecretKeySpec

class WorkspaceActivity : AppCompatActivity() {
    private val db by lazy { AppDatabase.get(this) }
    private lateinit var listView: LinearLayout
    private var mode = "tasks" // tasks | notes | vault

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        mode = intent.getStringExtra("mode") ?: "tasks"
        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            layoutDirection = android.view.View.LAYOUT_DIRECTION_RTL
            setBackgroundColor(Color.parseColor("#F7F8FA"))
            setPadding(20, 20, 20, 20)
        }
        root.addView(TextView(this).apply {
            text = when (mode) {
                "notes" -> "یادداشت‌ها"
                "tips" -> "نکته‌ها"
                "vault" -> "مدیریت رمزها"
                else -> "کارها و یادآوری‌ها"
            }
            textSize = 20f
            setTextColor(Color.parseColor("#0F172A"))
        })
        if (mode == "tasks") {
            root.addView(TextView(this).apply {
                text = "برای یادآوری، تاریخ شمسی مثل ۱۴۰۵/۰۷/۲۴ و ساعت ۱۸:۳۰ وارد کن."
                textSize = 13f
                setTextColor(Color.DKGRAY)
                setPadding(0, 8, 0, 8)
            })
        }
        root.addView(Button(this).apply {
            text = "+ جدید"
            setOnClickListener { addItem() }
        })
        listView = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL }
        root.addView(listView)
        setContentView(ScrollView(this).apply { addView(root) })
        refresh()
    }

    private fun now() = Instant.now().toString()

    private fun parseJalaliDateTime(dateText: String, timeText: String): Long? {
        if (dateText.isBlank() && timeText.isBlank()) return null
        val date = dateText.trim().replace('۰','0').replace('۱','1').replace('۲','2')
            .replace('۳','3').replace('۴','4').replace('۵','5').replace('۶','6')
            .replace('۷','7').replace('۸','8').replace('۹','9')
        val time = timeText.trim().replace('۰','0').replace('۱','1').replace('۲','2')
            .replace('۳','3').replace('۴','4').replace('۵','5').replace('۶','6')
            .replace('۷','7').replace('۸','8').replace('۹','9')
        val dm = Regex("^(\\d{4})[/-](\\d{1,2})[/-](\\d{1,2})$").matchEntire(date)
            ?: throw IllegalArgumentException("تاریخ را به شکل ۱۴۰۵/۰۷/۲۴ وارد کن.")
        val tm = Regex("^(\\d{1,2}):(\\d{2})$").matchEntire(time)
            ?: throw IllegalArgumentException("ساعت را به شکل ۱۸:۳۰ وارد کن.")
        val y = dm.groupValues[1].toInt()
        val m = dm.groupValues[2].toInt()
        val d = dm.groupValues[3].toInt()
        val h = tm.groupValues[1].toInt()
        val minute = tm.groupValues[2].toInt()
        if (m !in 1..12 || d !in 1..31 || h !in 0..23 || minute !in 0..59)
            throw IllegalArgumentException("تاریخ یا ساعت خارج از محدوده است.")
        val cal = PersianCalendar(android.icu.util.TimeZone.getDefault(), ULocale("fa_IR")).apply {
            isLenient = false
            clear()
            set(PersianCalendar.YEAR, y)
            set(PersianCalendar.MONTH, m - 1)
            set(PersianCalendar.DAY_OF_MONTH, d)
            set(PersianCalendar.HOUR_OF_DAY, h)
            set(PersianCalendar.MINUTE, minute)
            set(PersianCalendar.SECOND, 0)
            set(PersianCalendar.MILLISECOND, 0)
        }
        val millis = try { cal.timeInMillis } catch (_: Exception) {
            throw IllegalArgumentException("این تاریخ شمسی معتبر نیست.")
        }
        if (millis <= System.currentTimeMillis()) throw IllegalArgumentException("زمان یادآوری باید در آینده باشد.")
        return millis
    }

    private fun jalaliLabel(raw: String): String {
        val millis = raw.toLongOrNull() ?: runCatching { Instant.parse(raw).toEpochMilli() }.getOrNull() ?: return ""
        val cal = PersianCalendar(TimeZone.getDefault(), ULocale("fa_IR")).apply { timeInMillis = millis }
        return "یادآوری: %04d/%02d/%02d  %02d:%02d".format(
            cal.get(PersianCalendar.YEAR), cal.get(PersianCalendar.MONTH) + 1,
            cal.get(PersianCalendar.DAY_OF_MONTH), cal.get(PersianCalendar.HOUR_OF_DAY),
            cal.get(PersianCalendar.MINUTE)
        )
    }

    private fun refresh() {
        lifecycleScope.launch {
            val rows = withContext(Dispatchers.IO) {
                when (mode) {
                    "notes" -> db.workspaceDao().allNotes().filter { it.tags != "tip" }.map { Triple(it.uid, it.title, it.body) }
                    "tips" -> db.workspaceDao().allNotes().filter { it.tags == "tip" }.map { Triple(it.uid, it.title, it.body) }
                    "vault" -> db.workspaceDao().allVault().map { Triple(it.uid, it.title, it.username) }
                    else -> db.workspaceDao().allTasks().map {
                        val due = if (it.dueAt.isNotBlank()) "\\n" + jalaliLabel(it.dueAt) else ""
                        Triple(it.uid, (if (it.done) "✓ " else "○ ") + it.title, it.body + due)
                    }
                }
            }
            listView.removeAllViews()
            if (rows.isEmpty()) listView.addView(TextView(this@WorkspaceActivity).apply {
                text = "موردی نیست — دکمه + جدید را بزن"
                setTextColor(Color.GRAY)
            })
            rows.forEach { (uid, title, sub) ->
                listView.addView(TextView(this@WorkspaceActivity).apply {
                    text = "$title\\n$sub"
                    textSize = 15f
                    setPadding(8, 16, 8, 16)
                    setTextColor(Color.parseColor("#1E293B"))
                    setOnClickListener { editItem(uid) }
                    setOnLongClickListener {
                        lifecycleScope.launch {
                            withContext(Dispatchers.IO) {
                                when (mode) {
                                    "notes", "tips" -> db.workspaceDao().deleteNote(uid)
                                    "vault" -> db.workspaceDao().deleteVault(uid)
                                    else -> db.workspaceDao().deleteTask(uid)
                                }
                            }
                            if (mode == "tasks") ReminderScheduler.cancelTask(this@WorkspaceActivity, uid)
                            refresh()
                        }
                        true
                    }
                })
            }
        }
    }

    private fun addItem() {
        val title = EditText(this).apply { hint = "عنوان" }
        val body = EditText(this).apply { hint = if (mode == "vault") "رمز / توضیحات" else if (mode == "tips") "نکته کاربردی" else "متن یادداشت" }
        val user = EditText(this).apply { hint = "نام کاربری (اختیاری)" }
        val dueDate = EditText(this).apply { hint = "تاریخ شمسی یادآوری: ۱۴۰۵/۰۷/۲۴" }
        val dueTime = EditText(this).apply { hint = "ساعت یادآوری: ۱۸:۳۰" }
        val box = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            addView(title); addView(body)
            if (mode == "vault") addView(user)
            if (mode == "tasks") { addView(dueDate); addView(dueTime) }
        }
        AlertDialog.Builder(this)
            .setTitle("مورد جدید")
            .setView(box)
            .setPositiveButton("ذخیره") { _, _ ->
                val t = title.text.toString().trim()
                if (t.isEmpty()) return@setPositiveButton
                val dueEpoch = try {
                    if (mode == "tasks" && (dueDate.text.isNotBlank() || dueTime.text.isNotBlank()))
                        parseJalaliDateTime(dueDate.text.toString(), dueTime.text.toString())
                    else null
                } catch (e: IllegalArgumentException) {
                    Toast.makeText(this, e.message ?: "تاریخ/ساعت نامعتبر", Toast.LENGTH_LONG).show()
                    return@setPositiveButton
                }
                lifecycleScope.launch {
                    val id = UUID.randomUUID().toString()
                    withContext(Dispatchers.IO) {
                        when (mode) {
                            "notes", "tips" -> db.workspaceDao().upsertNote(NoteEntity(id, t, body.text.toString(), tags = if (mode == "tips") "tip" else "note", lastUpdated = now()))
                            "vault" -> db.workspaceDao().upsertVault(VaultEntity(
                                id, t, user.text.toString(), secretEnc = simpleEnc(body.text.toString()), lastUpdated = now()
                            ))
                            else -> db.workspaceDao().upsertTask(TaskEntity(
                                uid = id, title = t, body = body.text.toString(),
                                dueAt = dueEpoch?.toString() ?: "", lastUpdated = now()
                            ))
                        }
                    }
                    if (mode == "tasks" && dueEpoch != null)
                        ReminderScheduler.scheduleTask(this@WorkspaceActivity, id, t, body.text.toString(), dueEpoch)
                    refresh()
                }
            }
            .setNegativeButton("لغو", null)
            .show()
    }

    private fun editItem(uid: String) {
        if (mode != "tasks") return
        lifecycleScope.launch {
            val task = withContext(Dispatchers.IO) { db.workspaceDao().allTasks().find { it.uid == uid } } ?: return@launch
            withContext(Dispatchers.IO) {
                db.workspaceDao().upsertTask(task.copy(done = !task.done, lastUpdated = now()))
            }
            if (!task.done) ReminderScheduler.cancelTask(this@WorkspaceActivity, uid)
            else if (task.dueAt.isNotBlank()) {
                val epoch = task.dueAt.toLongOrNull()
                if (epoch != null && epoch > System.currentTimeMillis())
                    ReminderScheduler.scheduleTask(this@WorkspaceActivity, uid, task.title, task.body, epoch)
            }
            refresh()
            Toast.makeText(this@WorkspaceActivity, if (!task.done) "انجام شد" else "باز شد", Toast.LENGTH_SHORT).show()
        }
    }

    /** Legacy vault encoding retained for existing local records; do not treat it as strong encryption. */
    private fun simpleEnc(plain: String): String {
        return try {
            val key = SecretKeySpec("NetEncJokarKey16".toByteArray(), "AES")
            val c = Cipher.getInstance("AES/ECB/PKCS5Padding")
            c.init(Cipher.ENCRYPT_MODE, key)
            Base64.encodeToString(c.doFinal(plain.toByteArray()), Base64.NO_WRAP)
        } catch (_: Exception) { plain }
    }
}
