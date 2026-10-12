package com.netenc.app

import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.netenc.app.data.AppDatabase
import com.netenc.app.data.LessonRepository
import com.netenc.app.data.OfflineSeeder
import com.netenc.app.data.ScenarioSeeder
import com.netenc.app.data.StudyRepository
import com.netenc.app.data.WorkspaceSyncRepository
import com.netenc.app.data.ScenarioSyncRepository
import com.netenc.app.data.StudySyncRepository
import com.netenc.app.reminder.ReminderScheduler
import com.netenc.app.sync.SyncClient
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.time.Instant

class MainActivity : AppCompatActivity() {
    private lateinit var hostInput: EditText
    private lateinit var tokenInput: EditText
    private lateinit var logView: TextView
    private lateinit var repo: LessonRepository
    private lateinit var workspaceSyncRepo: WorkspaceSyncRepository
    private lateinit var scenarioSyncRepo: ScenarioSyncRepository
    private lateinit var studySyncRepo: StudySyncRepository

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        repo = LessonRepository(this)
        workspaceSyncRepo = WorkspaceSyncRepository(this)
        scenarioSyncRepo = ScenarioSyncRepository(this)
        studySyncRepo = StudySyncRepository(this)
        hostInput = findViewById(R.id.hostInput)
        tokenInput = findViewById(R.id.tokenInput)
        logView = findViewById(R.id.logView)

        val prefs = getSharedPreferences("netenc", MODE_PRIVATE)
        // Remove an older hard-coded numeric token from previous builds.
        if (prefs.getString("token", "")?.matches(Regex("[0-9]{11}")) == true) {
            prefs.edit().putString("token", "").apply()
        }
        hostInput.setText(prefs.getString("host", ""))
        tokenInput.setText(prefs.getString("token", SettingsActivity.DEFAULT_TOKEN) ?: "")

        ReminderScheduler.scheduleHourly(this)

        findViewById<Button>(R.id.btnStudyHub).setOnClickListener {
            startActivity(Intent(this, StudyHubActivity::class.java))
        }
        // Workspace
        safeBtn(R.id.btnTasks) {
            startActivity(Intent(this, PlannerActivity::class.java))
        }
        safeBtn(R.id.btnNotes) {
            startActivity(Intent(this, WorkspaceActivity::class.java).putExtra("mode", "notes"))
        }
        safeBtn(R.id.btnVault) {
            startActivity(Intent(this, WorkspaceActivity::class.java).putExtra("mode", "vault"))
        }
        findViewById<Button>(R.id.btnQuiz).setOnClickListener {
            startActivity(Intent(this, QuizActivity::class.java))
        }
        findViewById<Button>(R.id.btnFlash).setOnClickListener {
            startActivity(Intent(this, FlashcardActivity::class.java).putExtra("mode", "review"))
        }
        findViewById<Button>(R.id.btnTree).setOnClickListener {
            startActivity(Intent(this, TreeCatalogActivity::class.java))
        }
        findViewById<Button>(R.id.btnCatalog).setOnClickListener {
            startActivity(Intent(this, CatalogActivity::class.java))
        }
        findViewById<Button>(R.id.btnSearch).setOnClickListener { askSearch() }
        findViewById<Button>(R.id.btnScenarios).setOnClickListener {
            startActivity(Intent(this, ScenarioListActivity::class.java))
        }
        findViewById<Button>(R.id.btnStats).setOnClickListener { showStats() }
        findViewById<Button>(R.id.btnApi).setOnClickListener {
            startActivity(Intent(this, ApiExplorerActivity::class.java))
        }
        findViewById<Button>(R.id.btnJson).setOnClickListener {
            startActivity(Intent(this, JsonIoActivity::class.java))
        }
        findViewById<Button>(R.id.btnSettings).setOnClickListener {
            startActivity(Intent(this, SettingsActivity::class.java))
        }
        findViewById<Button>(R.id.btnReseed).setOnClickListener { forceReseed() }
        findViewById<Button>(R.id.btnHello).setOnClickListener { hello() }
        findViewById<Button>(R.id.btnSync).setOnClickListener { sync() }
        findViewById<Button>(R.id.btnOpenWeb).setOnClickListener {
            val h = hostInput.text.toString().trim()
            if (h.isBlank()) log("IP را وارد کنید")
            else startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(h)))
        }
        findViewById<Button>(R.id.btnAbout).setOnClickListener {
            AlertDialog.Builder(this)
                .setTitle("Engineer Jokar")
                .setMessage("یادگیری عمیق + کارها + یادداشت + رمز")
                .setPositiveButton("باشه", null)
                .show()
        }

        lifecycleScope.launch { seedAll(force = false) }
        if (prefs.getBoolean("auto_sync", false) && !prefs.getString("host", "").isNullOrBlank()) {
            hostInput.postDelayed({ sync() }, 2500)
        }
    }

    private fun safeBtn(id: Int, block: () -> Unit) {
        try {
            findViewById<Button>(id)?.setOnClickListener { block() }
        } catch (_: Exception) {}
    }

    private fun forceReseed() {
        // Force is passed to the current seeder version; resetting an obsolete v11 marker
        // did not invalidate the v13 marker and therefore did not actually force a reseed.
        lifecycleScope.launch { seedAll(force = true) }
    }

    private suspend fun seedAll(force: Boolean) {
        log(if (force) "بازسازی…" else "بارگذاری…")
        try {
            val n = withContext(Dispatchers.IO) { OfflineSeeder.ensureSeeded(this@MainActivity, force = force) }
            val sc = withContext(Dispatchers.IO) { ScenarioSeeder.ensure(this@MainActivity) }
            val st = withContext(Dispatchers.IO) { StudyRepository(this@MainActivity).stats() }
            log("✓ درس=$n سناریو=$sc")
            log("مطالعه: due=${st["due"]} today=${st["today"]}/${st["goal"]} streak=${st["streak"]}")
        } catch (e: Exception) {
            log("seed: ${e.message}")
        }
    }

    private fun showStats() {
        lifecycleScope.launch {
            val db = AppDatabase.get(this@MainActivity)
            val lessons = withContext(Dispatchers.IO) { db.lessonDao().countActive() }
            val filled = withContext(Dispatchers.IO) { db.lessonDao().countFilled() }
            val sc = withContext(Dispatchers.IO) { db.scenarioDao().count() }
            val st = withContext(Dispatchers.IO) { StudyRepository(this@MainActivity).stats() }
            val today = st["today"]
            val goal = st["goal"]
            AlertDialog.Builder(this@MainActivity)
                .setTitle("آمار")
                .setMessage("درس: $lessons\nمتن‌دار: $filled\nسناریو: $sc\nامروز: $today/$goal")
                .setPositiveButton("باشه", null)
                .show()
        }
    }

    private fun askSearch() {
        val input = EditText(this).apply { hint = "VLAN / OSPF" }
        AlertDialog.Builder(this)
            .setTitle("جستجو")
            .setView(input)
            .setPositiveButton("برو") { _, _ ->
                val q = input.text.toString().trim()
                if (q.isNotBlank()) startActivity(Intent(this, SearchActivity::class.java).putExtra("q", q))
            }
            .setNegativeButton("لغو", null)
            .show()
    }

    private fun savePrefs() {
        getSharedPreferences("netenc", MODE_PRIVATE).edit()
            .putString("host", hostInput.text.toString().trim())
            .putString("token", tokenInput.text.toString())
            .apply()
    }

    private fun client(): SyncClient {
        savePrefs()
        return SyncClient(
            baseUrl = hostInput.text.toString().trim(),
            token = tokenInput.text.toString().trim(),
            deviceId = android.provider.Settings.Secure.getString(
                contentResolver, android.provider.Settings.Secure.ANDROID_ID
            ) ?: "android"
        )
    }

    private fun log(msg: String) { logView.append("\n$msg") }

    private fun hello() {
        if (hostInput.text.toString().trim().isBlank()) { log("API خالی"); return }
        lifecycleScope.launch {
            try { log(withContext(Dispatchers.IO) { client().hello() }) }
            catch (e: Exception) { log("${e.message}") }
        }
    }

    private fun sync() {
        if (hostInput.text.toString().trim().isBlank()) { log("IP لازم است"); return }
        lifecycleScope.launch {
            try {
                val c = client()
                val since = withContext(Dispatchers.IO) { repo.getLastSync() }.ifBlank { null }
                val m = withContext(Dispatchers.IO) { c.manifest(since) }
                var pulled = 0
                // Lesson and study records intentionally share a lesson UID; pull each UID once and let entity routing split the returned records.
                for (chunk in m.items.map { it.uid }.distinct().chunked(80)) {
                    val body = withContext(Dispatchers.IO) { c.pull(chunk) }
                    pulled += withContext(Dispatchers.IO) { repo.upsertFromPullJson(body) }
                    pulled += withContext(Dispatchers.IO) { workspaceSyncRepo.upsertFromPullJson(body) }
                    pulled += withContext(Dispatchers.IO) { scenarioSyncRepo.upsertFromPullJson(body) }
                    pulled += withContext(Dispatchers.IO) { studySyncRepo.upsertFromPullJson(body) }
                }
                val pushArr = withContext(Dispatchers.IO) {
                    val combined = repo.buildPushArray(since)
                    val workspace = workspaceSyncRepo.buildPushArray()
                    for (i in 0 until workspace.length()) combined.put(workspace.get(i))
                    val study = studySyncRepo.buildPushArray()
                    for (i in 0 until study.length()) combined.put(study.get(i))
                    combined
                }
                var pushSummary = "push=0"
                if (pushArr.length() > 0) {
                    var accepted = 0
                    var kept = 0
                    var conflicts = 0
                    var unsupported = 0
                    var missing = 0
                    var invalid = 0
                    var applyRejected = 0
                    var start = 0
                    // Keep requests below both the server's 1000-record cap and its
                    // 8 MiB request limit. A single oversized record still fails loudly.
                    while (start < pushArr.length()) {
                        val end = minOf(start + 25, pushArr.length())
                        val batch = org.json.JSONArray()
                        for (i in start until end) batch.put(pushArr.get(i))
                        val pushBody = withContext(Dispatchers.IO) { c.push(batch) }
                        val result = org.json.JSONObject(pushBody)
                        accepted += result.optInt("accepted", 0)
                        kept += result.optInt("kept", 0)
                        conflicts += result.optInt("conflicts", 0)
                        unsupported += result.optInt("unsupported", 0)
                        missing += result.optInt("missing_targets", 0)
                        invalid += result.optInt("invalid", 0)
                        applyRejected += result.optInt("apply_rejected", 0)
                        start = end
                        // Don't advance the cursor or continue a misleading partial push.
                        if (unsupported > 0 || missing > 0 || conflicts > 0 || invalid > 0 || applyRejected > 0) break
                    }
                    pushSummary = "push=${pushArr.length()} accepted=$accepted kept=$kept conflicts=$conflicts unsupported=$unsupported missing=$missing invalid=$invalid rejected=$applyRejected"
                    if (unsupported > 0 || missing > 0 || conflicts > 0 || invalid > 0 || applyRejected > 0) {
                        log("⚠ sync ناقص: pull=$pulled $pushSummary")
                        return@launch
                    }
                }
                // Use the server's manifest snapshot, not the phone clock after the
                // sync. This prevents edits made during sync from falling behind the cursor.
                val cursor = m.generated_at?.takeIf { it.isNotBlank() } ?: Instant.now().toString()
                withContext(Dispatchers.IO) { repo.setLastSync(cursor) }
                log("✓ sync pull=$pulled $pushSummary")
            } catch (e: Exception) { log("sync: ${e.message}") }
        }
    }
}
