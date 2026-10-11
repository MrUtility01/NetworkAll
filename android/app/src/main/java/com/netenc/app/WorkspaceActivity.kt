package com.netenc.app

import android.graphics.Color
import android.content.Intent
import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.Spinner
import android.widget.ArrayAdapter
import android.widget.ScrollView
import android.widget.TextView
import android.widget.Toast
import android.app.DatePickerDialog
import android.app.TimePickerDialog
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.netenc.app.data.AppDatabase
import com.netenc.app.data.NoteEntity
import com.netenc.app.data.TaskEntity
import com.netenc.app.data.VaultEntity
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.time.Instant
import java.time.ZoneId
import java.util.UUID
import java.util.Calendar
import com.netenc.app.util.JalaliDate
import android.security.keystore.KeyGenParameterSpec
import android.security.keystore.KeyProperties
import android.util.Base64
import java.security.KeyStore
import javax.crypto.Cipher
import javax.crypto.KeyGenerator
import javax.crypto.SecretKey
import javax.crypto.spec.GCMParameterSpec

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
                "vault" -> "مدیریت رمزها"
                else -> "مدیریت کارها"
            }
            textSize = 20f
            setTextColor(Color.parseColor("#0F172A"))
        })
        if (mode == "tasks") {
            root.addView(Button(this).apply {
                text = "تقویم شمسی"
                setOnClickListener { startActivity(Intent(this@WorkspaceActivity, JalaliCalendarActivity::class.java)) }
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

    private fun refresh() {
        lifecycleScope.launch {
            val rows = withContext(Dispatchers.IO) {
                when (mode) {
                    "notes" -> db.workspaceDao().allNotes().map { Triple(it.uid, it.title, it.body) }
                    "vault" -> db.workspaceDao().allVault().map { Triple(it.uid, it.title, it.username) }
                    else -> db.workspaceDao().allTasks().map {
                        val dueLabel = if (it.dueAt.isBlank()) "" else "\nموعد شمسی: " + JalaliDate.formatIso(it.dueAt)
                        val priorityLabel = "\nاولویت: " + it.priority
                        Triple(it.uid, (if (it.done) "✓ " else "○ ") + it.title, it.body + dueLabel + priorityLabel)
                    }
                }
            }
            listView.removeAllViews()
            if (rows.isEmpty()) {
                listView.addView(TextView(this@WorkspaceActivity).apply {
                    text = "موردی نیست — دکمه + جدید را بزن"
                    setTextColor(Color.GRAY)
                })
            }
            rows.forEach { (uid, title, sub) ->
                listView.addView(TextView(this@WorkspaceActivity).apply {
                    text = "$title\n$sub"
                    textSize = 15f
                    setPadding(8, 16, 8, 16)
                    setTextColor(Color.parseColor("#1E293B"))
                    setOnClickListener { editItem(uid) }
                    setOnLongClickListener {
                        lifecycleScope.launch {
                            withContext(Dispatchers.IO) {
                                when (mode) {
                                    "notes" -> db.workspaceDao().deleteNote(uid)
                                    "vault" -> db.workspaceDao().deleteVault(uid)
                                    else -> db.workspaceDao().deleteTask(uid)
                                }
                            }
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
        val body = EditText(this).apply { hint = if (mode == "vault") "رمز / توضیحات" else "متن" }
        val user = EditText(this).apply { hint = "نام کاربری (اختیاری)" }
        var dueAt = ""
        val recurrenceSpinner = Spinner(this).apply {
            adapter = ArrayAdapter(this@WorkspaceActivity, android.R.layout.simple_spinner_dropdown_item, listOf("یک‌باره", "روزانه", "هفتگی"))
        }
        lateinit var dueButton: Button
        dueButton = Button(this).apply {
            text = "انتخاب موعد (نمایش شمسی)"
            setOnClickListener {
                val nowCal = Calendar.getInstance()
                DatePickerDialog(
                    this@WorkspaceActivity,
                    { _, year, month, day ->
                        val timeCal = Calendar.getInstance()
                        TimePickerDialog(
                            this@WorkspaceActivity,
                            { _, hour, minute ->
                                val selected = Calendar.getInstance().apply {
                                    set(Calendar.YEAR, year)
                                    set(Calendar.MONTH, month)
                                    set(Calendar.DAY_OF_MONTH, day)
                                    set(Calendar.HOUR_OF_DAY, hour)
                                    set(Calendar.MINUTE, minute)
                                    set(Calendar.SECOND, 0)
                                    set(Calendar.MILLISECOND, 0)
                                }
                                dueAt = Instant.ofEpochMilli(selected.timeInMillis).toString()
                                dueButton.text = "موعد شمسی: " + JalaliDate.formatIso(dueAt)
                            },
                            timeCal.get(Calendar.HOUR_OF_DAY),
                            timeCal.get(Calendar.MINUTE),
                            true
                        ).show()
                    },
                    nowCal.get(Calendar.YEAR),
                    nowCal.get(Calendar.MONTH),
                    nowCal.get(Calendar.DAY_OF_MONTH)
                ).show()
            }
        }
        val box = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            addView(title); addView(body)
            if (mode == "tasks") { addView(dueButton); addView(recurrenceSpinner) }
            if (mode == "vault") addView(user)
        }
        AlertDialog.Builder(this)
            .setTitle("مورد جدید")
            .setView(box)
            .setPositiveButton("ذخیره") { _, _ ->
                val t = title.text.toString().trim()
                if (t.isEmpty()) return@setPositiveButton
                lifecycleScope.launch {
                    withContext(Dispatchers.IO) {
                        val id = UUID.randomUUID().toString()
                        when (mode) {
                            "notes" -> db.workspaceDao().upsertNote(
                                NoteEntity(id, t, body.text.toString(), lastUpdated = now())
                            )
                            "vault" -> db.workspaceDao().upsertVault(
                                VaultEntity(
                                    id, t, user.text.toString(),
                                    secretEnc = simpleEnc(body.text.toString()),
                                    lastUpdated = now()
                                )
                            )
                            else -> db.workspaceDao().upsertTask(
                                TaskEntity(id, t, body.text.toString(), dueAt = dueAt, recurrence = when (recurrenceSpinner.selectedItemPosition) { 1 -> "daily"; 2 -> "weekly"; else -> "none" }, lastUpdated = now())
                            )
                        }
                    }
                    refresh()
                }
            }
            .setNegativeButton("لغو", null)
            .show()
    }

    private fun editItem(uid: String) {
        if (mode != "tasks") return
        lifecycleScope.launch {
            val task = withContext(Dispatchers.IO) {
                db.workspaceDao().allTasks().find { it.uid == uid }
            } ?: return@launch
            var rescheduled = false
            withContext(Dispatchers.IO) {
                val updated = if (!task.done && task.recurrence in setOf("daily", "weekly") && task.dueAt.isNotBlank()) {
                    val parsed = runCatching { Instant.parse(task.dueAt) }.getOrNull()
                    if (parsed != null) {
                        val base = if (parsed.isBefore(Instant.now())) Instant.now() else parsed
                        val local = base.atZone(ZoneId.systemDefault())
                        val next = if (task.recurrence == "daily") local.plusDays(1) else local.plusWeeks(1)
                        rescheduled = true
                        task.copy(done = false, dueAt = next.toInstant().toString(), lastUpdated = now())
                    } else {
                        task.copy(done = true, lastUpdated = now())
                    }
                } else {
                    task.copy(done = !task.done, lastUpdated = now())
                }
                db.workspaceDao().upsertTask(updated)
            }
            refresh()
            val message = when {
                rescheduled -> "موعد بعدی تنظیم شد"
                !task.done -> "انجام شد"
                else -> "باز شد"
            }
            Toast.makeText(this@WorkspaceActivity, message, Toast.LENGTH_SHORT).show()
        }
    }

    /** Authenticated AES-GCM encryption with a non-exportable Android Keystore key. */
    private fun simpleEnc(plain: String): String {
        if (plain.isEmpty()) return ""
        return try {
            val alias = "networkall-vault-aes-gcm"
            val store = KeyStore.getInstance("AndroidKeyStore").apply { load(null) }
            val key = (store.getKey(alias, null) as? SecretKey) ?: run {
                val generator = KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, "AndroidKeyStore")
                generator.init(
                    KeyGenParameterSpec.Builder(
                        alias,
                        KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT
                    )
                        .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
                        .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
                        .setRandomizedEncryptionRequired(true)
                        .build()
                )
                generator.generateKey()
            }
            val cipher = Cipher.getInstance("AES/GCM/NoPadding")
            cipher.init(Cipher.ENCRYPT_MODE, key)
            val encrypted = cipher.doFinal(plain.toByteArray(Charsets.UTF_8))
            val combined = cipher.iv + encrypted
            "gcm1:" + Base64.encodeToString(combined, Base64.NO_WRAP)
        } catch (e: Exception) {
            // Never fall back to plaintext if encryption fails.
            "enc-error"
        }
    }
}
