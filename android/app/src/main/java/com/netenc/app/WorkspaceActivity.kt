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
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.time.Instant
import java.util.UUID
import android.util.Base64
import android.security.keystore.KeyGenParameterSpec
import android.security.keystore.KeyProperties
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
                        Triple(it.uid, (if (it.done) "✓ " else "○ ") + it.title, it.body)
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
                    setOnClickListener { if (mode == "vault") showVaultItem(uid) else editItem(uid) }
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
        val box = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            addView(title); addView(body)
            if (mode == "vault") addView(user)
        }
        AlertDialog.Builder(this)
            .setTitle("مورد جدید")
            .setView(box)
            .setPositiveButton("ذخیره") { _, _ ->
                val t = title.text.toString().trim()
                if (t.isEmpty()) return@setPositiveButton
                lifecycleScope.launch {
                    try {
                        withContext(Dispatchers.IO) {
                            val id = UUID.randomUUID().toString()
                            when (mode) {
                                "notes" -> db.workspaceDao().upsertNote(
                                    NoteEntity(id, t, body.text.toString(), lastUpdated = now())
                                )
                                "vault" -> db.workspaceDao().upsertVault(
                                    VaultEntity(
                                        id, t, user.text.toString(),
                                        secretEnc = encryptVaultSecret(body.text.toString()),
                                        lastUpdated = now()
                                    )
                                )
                                else -> db.workspaceDao().upsertTask(
                                    TaskEntity(id, t, body.text.toString(), lastUpdated = now())
                                )
                            }
                        }
                        refresh()
                    } catch (e: Exception) {
                        Toast.makeText(this@WorkspaceActivity, "ذخیره امن انجام نشد: " + (e.message ?: "خطای رمزنگاری"), Toast.LENGTH_LONG).show()
                    }
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
            withContext(Dispatchers.IO) {
                db.workspaceDao().upsertTask(task.copy(done = !task.done, lastUpdated = now()))
            }
            refresh()
            Toast.makeText(this@WorkspaceActivity, if (!task.done) "انجام شد" else "باز شد", Toast.LENGTH_SHORT).show()
        }
    }

    private fun vaultKey(): SecretKey {
        val alias = "netenc.vault.aesgcm.v1"
        val store = KeyStore.getInstance("AndroidKeyStore").apply { load(null) }
        if (store.containsAlias(alias)) return store.getKey(alias, null) as SecretKey
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
        return generator.generateKey()
    }

    /** New secrets use authenticated AES-GCM and a device-bound Android Keystore key. */
    private fun encryptVaultSecret(plain: String): String {
        val cipher = Cipher.getInstance("AES/GCM/NoPadding")
        cipher.init(Cipher.ENCRYPT_MODE, vaultKey())
        val encrypted = cipher.doFinal(plain.toByteArray(Charsets.UTF_8))
        val payload = cipher.iv + encrypted
        return "v2:" + Base64.encodeToString(payload, Base64.NO_WRAP)
    }

    private fun decryptVaultSecret(blob: String): String {
        if (!blob.startsWith("v2:")) {
            throw IllegalStateException("این رکورد از نسخه قدیمی است؛ در حال مهاجرت امن آن هستیم.")
        }
        val payload = Base64.decode(blob.removePrefix("v2:"), Base64.NO_WRAP)
        if (payload.size <= 12) throw IllegalArgumentException("داده رمزگذاری‌شده ناقص است.")
        val iv = payload.copyOfRange(0, 12)
        val encrypted = payload.copyOfRange(12, payload.size)
        val cipher = Cipher.getInstance("AES/GCM/NoPadding")
        cipher.init(Cipher.DECRYPT_MODE, vaultKey(), GCMParameterSpec(128, iv))
        return String(cipher.doFinal(encrypted), Charsets.UTF_8)
    }

    /** Decrypt older static-key AES/ECB values so they can be re-sealed. */
    private fun decryptLegacyVaultSecret(blob: String): String {
        return try {
            val key = javax.crypto.spec.SecretKeySpec("NetEncJokarKey16".toByteArray(Charsets.UTF_8), "AES")
            val cipher = Cipher.getInstance("AES/ECB/PKCS5Padding")
            cipher.init(Cipher.DECRYPT_MODE, key)
            String(cipher.doFinal(Base64.decode(blob, Base64.DEFAULT)), Charsets.UTF_8)
        } catch (_: Exception) {
            // Previous versions could fall back to plaintext when encryption failed.
            blob
        }
    }

    private fun showVaultItem(uid: String) {
        lifecycleScope.launch {
            val item = withContext(Dispatchers.IO) {
                db.workspaceDao().allVault().find { it.uid == uid }
            } ?: return@launch
            try {
                val secret = withContext(Dispatchers.IO) {
                    val value = if (item.secretEnc.startsWith("v2:")) {
                        decryptVaultSecret(item.secretEnc)
                    } else {
                        decryptLegacyVaultSecret(item.secretEnc)
                    }
                    if (!item.secretEnc.startsWith("v2:")) {
                        db.workspaceDao().upsertVault(
                            item.copy(secretEnc = encryptVaultSecret(value), lastUpdated = now())
                        )
                    }
                    value
                }
                AlertDialog.Builder(this@WorkspaceActivity)
                    .setTitle(item.title)
                    .setMessage("نام کاربری: " + item.username + "\n\nرمز: " + secret)
                    .setPositiveButton("باشه", null)
                    .show()
            } catch (e: Exception) {
                AlertDialog.Builder(this@WorkspaceActivity)
                    .setTitle("رمز قابل نمایش نیست")
                    .setMessage(e.message ?: "داده رمز شده قابل خواندن نیست.")
                    .setPositiveButton("باشه", null)
                    .show()
            }
        }
    }}
