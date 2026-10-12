package com.netenc.app

import android.content.Intent
import android.app.Activity
import android.net.Uri
import android.os.Bundle
import android.os.Environment
import android.widget.Button
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.FileProvider
import androidx.lifecycle.lifecycleScope
import com.netenc.app.data.AppDatabase
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.json.JSONArray
import org.json.JSONObject
import java.io.File

class JsonIoActivity : AppCompatActivity() {
    private lateinit var log: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        log = TextView(this).apply {
            textSize = 13f
            setTextIsSelectable(true)
            setPadding(16, 16, 16, 16)
        }
        val exportBtn = Button(this).apply {
            text = "خروجی JSON (دروس + سناریو)"
            setOnClickListener { exportJson() }
        }
        val openBtn = Button(this).apply {
            text = "📂 باز کردن مسیر / فایل JSON"
            setOnClickListener { openExport() }
        }
        val shareBtn = Button(this).apply {
            text = "اشتراک‌گذاری فایل JSON"
            setOnClickListener { shareExport() }
        }
        val importBtn = Button(this).apply {
            text = "ورودی JSON از همان مسیر"
            setOnClickListener { openImportPicker() }
        }
        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            layoutDirection = android.view.View.LAYOUT_DIRECTION_RTL
            setPadding(20, 20, 20, 20)
            addView(TextView(this@JsonIoActivity).apply {
                text = "ورود / خروج JSON"
                textSize = 18f
                setPadding(0, 0, 0, 12)
            })
            addView(exportBtn)
            addView(openBtn)
            addView(shareBtn)
            addView(importBtn)
            addView(ScrollView(this@JsonIoActivity).apply { addView(log) },
                LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, 0, 1f))
        }
        setContentView(root)
        log.text = "مسیر:\n${exportFile().absolutePath}"
    }

    private fun exportFile(): File {
        val dir = getExternalFilesDir(Environment.DIRECTORY_DOCUMENTS) ?: filesDir
        if (!dir.exists()) dir.mkdirs()
        return File(dir, "NetEnc_export.json")
    }

    private fun openExport() {
        val f = exportFile()
        log.text = "مسیر کامل:\n${f.absolutePath}\n\nوجود دارد: ${f.exists()}\nحجم: ${if (f.exists()) f.length() else 0} بایت"
        if (!f.exists()) {
            Toast.makeText(this, "اول خروجی بگیرید", Toast.LENGTH_SHORT).show()
            return
        }
        try {
            val uri = FileProvider.getUriForFile(this, "$packageName.fileprovider", f)
            val intent = Intent(Intent.ACTION_VIEW).apply {
                setDataAndType(uri, "application/json")
                addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            }
            startActivity(Intent.createChooser(intent, "باز کردن JSON"))
        } catch (e: Exception) {
            // fallback: share sheet
            shareExport()
        }
    }

    private fun shareExport() {
        val f = exportFile()
        if (!f.exists()) {
            Toast.makeText(this, "اول خروجی بگیرید", Toast.LENGTH_SHORT).show()
            return
        }
        try {
            val uri = FileProvider.getUriForFile(this, "$packageName.fileprovider", f)
            startActivity(Intent.createChooser(Intent(Intent.ACTION_SEND).apply {
                type = "application/json"
                putExtra(Intent.EXTRA_STREAM, uri)
                addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            }, "اشتراک JSON"))
        } catch (e: Exception) {
            log.append("\nخطا: ${e.message}\nمسیر: ${f.absolutePath}")
        }
    }

    private fun exportJson() {
        lifecycleScope.launch {
            try {
                val db = AppDatabase.get(this@JsonIoActivity)
                val lessons = withContext(Dispatchers.IO) { db.lessonDao().allActive() }
                val scenarios = withContext(Dispatchers.IO) { db.scenarioDao().all() }
                val root = JSONObject()
                root.put("app", "EngineerJokar-NetEnc")
                root.put("version", 3)
                root.put("backup_type", "portable-personal-backup")
                root.put("created_at", java.time.Instant.now().toString())
                val arr = JSONArray()
                for (e in lessons) {
                    arr.put(JSONObject().apply {
                        put("uid", e.uid)
                        put("title_fa", e.titleFa)
                        put("summary", e.summary)
                        put("full_content", e.fullContent)
                        put("commands", e.commands)
                        put("examples", e.examples)
                        put("notes", e.notes)
                        put("chapter", e.chapterTitle)
                        put("sub", e.subTitle)
                        put("level", e.tags)
                    })
                }
                root.put("lessons", arr)
                val scArr = JSONArray()
                for (s in scenarios) {
                    scArr.put(JSONObject().apply {
                        put("code", s.code)
                        put("title_fa", s.titleFa)
                        put("business_context", s.businessContext)
                        put("tasks", s.tasks)
                        put("expected_result", s.expectedResult)
                        put("incident", s.incident)
                    })
                }
                root.put("scenarios", scArr)

                // Portable personal data backup. Vault secrets are deliberately excluded:
                // Android Keystore and Windows DPAPI keys are device-bound and cannot be copied safely.
                val workspaceDao = db.workspaceDao()
                val tasks = withContext(Dispatchers.IO) { workspaceDao.allTasksForSync() }
                val notes = withContext(Dispatchers.IO) { workspaceDao.allNotesForSync() }
                val studyRows = withContext(Dispatchers.IO) { db.studyDao().allForSync() }

                root.put("tasks", JSONArray().apply {
                    tasks.forEach { t -> put(JSONObject().apply {
                        put("uid", t.uid); put("title", t.title); put("body", t.body)
                        put("done", t.done); put("due_at", t.dueAt); put("priority", t.priority)
                        put("last_updated", t.lastUpdated); put("device_id", t.deviceId)
                        put("deleted", t.deleted); put("remind_at", t.remindAt)
                        // remindedAt is local delivery history; it must not move between devices.
                    }) }
                })
                root.put("notes", JSONArray().apply {
                    notes.forEach { n -> put(JSONObject().apply {
                        put("uid", n.uid); put("title", n.title); put("body", n.body)
                        put("tags", n.tags); put("last_updated", n.lastUpdated)
                        put("device_id", n.deviceId); put("deleted", n.deleted)
                    }) }
                })
                root.put("study_progress", JSONArray().apply {
                    studyRows.forEach { s -> put(JSONObject().apply {
                        put("lesson_uid", s.lessonUid); put("status", s.status); put("ease", s.ease)
                        put("interval_hours", s.intervalHours); put("last_studied", s.lastStudied)
                        put("next_review", s.nextReview); put("times_studied", s.timesStudied)
                        put("notes", s.notes); put("last_updated", s.lastUpdated)
                        put("device_id", s.deviceId); put("deleted", s.deleted)
                    }) }
                })
                val f = exportFile()
                withContext(Dispatchers.IO) { f.writeText(root.toString()) }
                log.text = "ذخیره شد:\n${f.absolutePath}\n\nدروس: ${lessons.size}\nسناریو: ${scenarios.size}\nحجم: ${f.length()} بایت\n\nدکمه «باز کردن مسیر» را بزنید."
                Toast.makeText(this@JsonIoActivity, "Export OK", Toast.LENGTH_SHORT).show()
            } catch (e: Exception) {
                log.text = "خطا: ${e.message}"
            }
        }
    }

    private fun openImportPicker() {
        val intent = Intent(Intent.ACTION_OPEN_DOCUMENT).apply {
            addCategory(Intent.CATEGORY_OPENABLE)
            type = "application/json"
        }
        startActivityForResult(intent, 7301)
    }

    @Deprecated("Use Activity Result APIs; retained for compatibility with current activity")
    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        if (requestCode != 7301 || resultCode != Activity.RESULT_OK) return
        val uri = data?.data ?: return
        lifecycleScope.launch {
            try {
                val text = withContext(Dispatchers.IO) {
                    contentResolver.openInputStream(uri)?.bufferedReader(Charsets.UTF_8)?.use { it.readText() }
                        ?: throw IllegalStateException("فایل انتخاب‌شده قابل خواندن نیست")
                }
                // Stage the chosen JSON in app-private storage; the existing importer validates and merges it.
                withContext(Dispatchers.IO) { exportFile().writeText(text) }
                importJson()
            } catch (e: Exception) {
                log.text = "خطا در خواندن فایل: ${e.message}"
            }
        }
    }

    private fun importJson() {
        lifecycleScope.launch {
            try {
                val f = exportFile()
                if (!f.exists()) {
                    log.text = "فایل نیست:\n${f.absolutePath}"
                    return@launch
                }
                val text = withContext(Dispatchers.IO) { f.readText() }
                val root = JSONObject(text)
                val arr = root.optJSONArray("lessons") ?: JSONArray()
                val dao = AppDatabase.get(this@JsonIoActivity).lessonDao()
                val batch = mutableListOf<com.netenc.app.data.LessonEntity>()
                for (i in 0 until arr.length()) {
                    val o = arr.getJSONObject(i)
                    val uid = o.optString("uid")
                    if (uid.isBlank()) continue
                    val old = withContext(Dispatchers.IO) { dao.byUid(uid) }
                    batch.add(
                        (old ?: com.netenc.app.data.LessonEntity(uid = uid)).copy(
                            titleFa = o.optString("title_fa", old?.titleFa ?: ""),
                            summary = o.optString("summary", old?.summary ?: ""),
                            fullContent = o.optString("full_content", old?.fullContent ?: ""),
                            commands = o.optString("commands", old?.commands ?: ""),
                            examples = o.optString("examples", old?.examples ?: ""),
                            notes = o.optString("notes", old?.notes ?: ""),
                            contentHash = "json-import",
                            lastUpdated = java.time.Instant.now().toString()
                        )
                    )
                    if (batch.size >= 80) {
                        withContext(Dispatchers.IO) { dao.upsertAll(batch.toList()) }
                        batch.clear()
                    }
                }
                if (batch.isNotEmpty()) withContext(Dispatchers.IO) { dao.upsertAll(batch) }

                val backupType = root.optString("backup_type", "")
                if (backupType == "portable-personal-backup") {
                    val workspaceDao = AppDatabase.get(this@JsonIoActivity).workspaceDao()
                    val tasks = root.optJSONArray("tasks") ?: JSONArray()
                    var restoredTasks = 0
                    for (i in 0 until tasks.length()) {
                        val o = tasks.optJSONObject(i) ?: continue
                        val uid = o.optString("uid", "").trim()
                        val title = o.optString("title", "").trim()
                        if (uid.isEmpty() || title.isEmpty()) continue
                        val old = withContext(Dispatchers.IO) { workspaceDao.taskByUid(uid) }
                        val incomingUpdated = o.optString("last_updated", "")
                        // Restore is a merge: never overwrite a newer local version.
                        if (old != null && old.lastUpdated >= incomingUpdated) continue
                        workspaceDao.upsertTask(com.netenc.app.data.TaskEntity(
                            uid = uid, title = title, body = o.optString("body", ""),
                            done = o.optBoolean("done", false), dueAt = o.optString("due_at", ""),
                            priority = o.optInt("priority", 1).coerceIn(1, 3),
                            lastUpdated = incomingUpdated, deviceId = o.optString("device_id", "restore"),
                            deleted = o.optBoolean("deleted", false), remindAt = o.optString("remind_at", ""),
                            remindedAt = ""
                        ))
                        restoredTasks++
                    }
                    val notes = root.optJSONArray("notes") ?: JSONArray()
                    var restoredNotes = 0
                    for (i in 0 until notes.length()) {
                        val o = notes.optJSONObject(i) ?: continue
                        val uid = o.optString("uid", "").trim()
                        val title = o.optString("title", "").trim()
                        if (uid.isEmpty() || title.isEmpty()) continue
                        val old = withContext(Dispatchers.IO) { workspaceDao.noteByUid(uid) }
                        val incomingUpdated = o.optString("last_updated", "")
                        if (old != null && old.lastUpdated >= incomingUpdated) continue
                        workspaceDao.upsertNote(com.netenc.app.data.NoteEntity(
                            uid = uid, title = title, body = o.optString("body", ""),
                            tags = o.optString("tags", ""), lastUpdated = incomingUpdated,
                            deviceId = o.optString("device_id", "restore"), deleted = o.optBoolean("deleted", false)
                        ))
                        restoredNotes++
                    }
                    val study = root.optJSONArray("study_progress") ?: JSONArray()
                    var restoredStudy = 0
                    for (i in 0 until study.length()) {
                        val o = study.optJSONObject(i) ?: continue
                        val uid = o.optString("lesson_uid", "").trim()
                        if (uid.isEmpty()) continue
                        val old = withContext(Dispatchers.IO) { AppDatabase.get(this@JsonIoActivity).studyDao().byUid(uid) }
                        val incomingUpdated = o.optString("last_updated", "")
                        if (old != null && old.lastUpdated >= incomingUpdated) continue
                        val status = o.optString("status", "new")
                        if (status !in setOf("new", "learning", "known", "review")) continue
                        AppDatabase.get(this@JsonIoActivity).studyDao().upsert(com.netenc.app.data.StudyEntity(
                            lessonUid = uid, status = status, ease = o.optDouble("ease", 2.5).coerceIn(1.0, 4.0),
                            intervalHours = o.optInt("interval_hours", 1).coerceIn(0, 8760),
                            lastStudied = o.optString("last_studied", ""), nextReview = o.optString("next_review", ""),
                            timesStudied = o.optInt("times_studied", 0).coerceAtLeast(0),
                            notes = o.optString("notes", ""), lastUpdated = incomingUpdated,
                            deviceId = o.optString("device_id", "restore"), deleted = o.optBoolean("deleted", false)
                        ))
                        restoredStudy++
                    }
                    log.text = "بازیابی ادغامی انجام شد.\nدرس‌ها: ${arr.length()}\nکارها: $restoredTasks\nیادداشت‌ها: $restoredNotes\nپیشرفت مطالعه: $restoredStudy\n\nVault عمداً در بکاپ قابل‌انتقال نیست.\n${f.absolutePath}"
                } else {
                    log.text = "Import محتوای آموزشی انجام شد — ${arr.length()} درس\nاین فایل بکاپ کامل داده‌های شخصی نیست."
                }
            } catch (e: Exception) {
                log.text = "خطا import: ${e.message}"
            }
        }
    }
}
