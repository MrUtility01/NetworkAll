package com.netenc.app

import android.content.Intent
import android.graphics.Color
import android.os.Bundle
import android.util.Base64
import android.view.Gravity
import android.view.View
import android.widget.Button
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.TextView
import android.widget.Toast
import android.text.InputType
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.security.MessageDigest
import java.security.SecureRandom
import javax.crypto.SecretKeyFactory
import javax.crypto.spec.PBEKeySpec

/**
 * Local launch gate. The password is configured on first launch and only a salted
 * PBKDF2 hash is stored in app-private preferences; it is not an account system
 * and does not encrypt the app database.
 */
class SplashActivity : AppCompatActivity() {
    private val prefs by lazy { getSharedPreferences("networkall_lock", MODE_PRIVATE) }
    private lateinit var passwordInput: EditText
    private lateinit var confirmationInput: EditText
    private lateinit var confirmationLabel: TextView
    private lateinit var status: TextView
    private lateinit var submit: Button
    private var setupMode = true

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        setupMode = prefs.getString("password_hash", null).isNullOrBlank() ||
            prefs.getString("password_salt", null).isNullOrBlank()

        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            gravity = Gravity.CENTER_HORIZONTAL
            setBackgroundColor(Color.parseColor("#F4F6F9"))
            setPadding(28, 36, 28, 36)
        }
        root.addView(TextView(this).apply {
            text = "NetworkAll"
            textSize = 28f
            setTextColor(Color.parseColor("#1D4ED8"))
            gravity = Gravity.CENTER
            setPadding(0, 0, 0, 10)
        }, match(LinearLayout.LayoutParams.WRAP_CONTENT))
        root.addView(TextView(this).apply {
            text = "دانشنامه شبکه و زیرساخت · نسخه ۱٫۰٫۰"
            textSize = 16f
            setTextColor(Color.parseColor("#334155"))
            gravity = Gravity.CENTER
            setPadding(0, 0, 0, 24)
        }, match(LinearLayout.LayoutParams.WRAP_CONTENT))

        root.addView(TextView(this).apply {
            text = if (setupMode) "تنظیم رمز ورود محلی" else "ورود به NetworkAll"
            textSize = 20f
            setTextColor(Color.parseColor("#0F172A"))
            gravity = Gravity.CENTER
        }, match(LinearLayout.LayoutParams.WRAP_CONTENT))

        root.addView(TextView(this).apply {
            text = if (setupMode)
                "برای اولین اجرا یک رمز محلی و تأیید آن وارد کنید. رمز در دستگاه ذخیره می‌شود."
            else
                "رمز محلی این دستگاه را وارد کنید."
            textSize = 13f
            setTextColor(Color.parseColor("#475569"))
            gravity = Gravity.CENTER
            setPadding(0, 12, 0, 12)
        }, match(LinearLayout.LayoutParams.WRAP_CONTENT))

        passwordInput = EditText(this).apply {
            hint = if (setupMode) "رمز جدید (حداقل ۸ نویسه)" else "رمز ورود"
            inputType = InputType.TYPE_CLASS_TEXT or InputType.TYPE_TEXT_VARIATION_PASSWORD
            setSingleLine(true)
            textAlignment = View.TEXT_ALIGNMENT_VIEW_START
            layoutDirection = View.LAYOUT_DIRECTION_LTR
        }
        root.addView(passwordInput, match(LinearLayout.LayoutParams.WRAP_CONTENT))

        confirmationLabel = TextView(this).apply {
            text = "تأیید رمز جدید"
            textSize = 13f
            setTextColor(Color.parseColor("#475569"))
            setPadding(0, 8, 0, 0)
            visibility = if (setupMode) View.VISIBLE else View.GONE
        }
        root.addView(confirmationLabel, match(LinearLayout.LayoutParams.WRAP_CONTENT))

        confirmationInput = EditText(this).apply {
            hint = "رمز را دوباره وارد کنید"
            inputType = InputType.TYPE_CLASS_TEXT or InputType.TYPE_TEXT_VARIATION_PASSWORD
            setSingleLine(true)
            textAlignment = View.TEXT_ALIGNMENT_VIEW_START
            layoutDirection = View.LAYOUT_DIRECTION_LTR
            visibility = if (setupMode) View.VISIBLE else View.GONE
        }
        root.addView(confirmationInput, match(LinearLayout.LayoutParams.WRAP_CONTENT))

        status = TextView(this).apply {
            textSize = 12f
            setTextColor(Color.parseColor("#B45309"))
            setPadding(0, 12, 0, 4)
        }
        root.addView(status, match(LinearLayout.LayoutParams.WRAP_CONTENT))

        submit = Button(this).apply {
            text = if (setupMode) "ذخیره رمز و ورود" else "ورود"
            setOnClickListener { handleSubmit() }
        }
        root.addView(submit, match(LinearLayout.LayoutParams.WRAP_CONTENT))

        root.addView(TextView(this).apply {
            text = "قفل محلی، رمزگذاری دیتابیس یا حفاظت در برابر دسترسی ریشه‌ای نیست. رمز را فراموش نکنید."
            textSize = 11f
            setTextColor(Color.parseColor("#64748B"))
            gravity = Gravity.CENTER
            setPadding(0, 20, 0, 0)
        }, match(LinearLayout.LayoutParams.WRAP_CONTENT))

        setContentView(root)
    }

    private fun match(height: Int) = LinearLayout.LayoutParams(
        LinearLayout.LayoutParams.MATCH_PARENT,
        height
    ).apply { setMargins(0, 5, 0, 5) }

    private fun handleSubmit() {
        val password = passwordInput.text.toString()
        if (setupMode) {
            val confirmation = confirmationInput.text.toString()
            if (password.length < 8) {
                status.text = "رمز باید دست‌کم ۸ نویسه داشته باشد."
                return
            }
            if (password != confirmation) {
                status.text = "دو رمز یکسان نیستند."
                return
            }
            setBusy(true)
            lifecycleScope.launch {
                val salt = ByteArray(16).also { SecureRandom().nextBytes(it) }
                val hash = withContext(Dispatchers.IO) { derivePassword(password, salt) }
                prefs.edit()
                    .putString("password_salt", Base64.encodeToString(salt, Base64.NO_WRAP))
                    .putString("password_hash", Base64.encodeToString(hash, Base64.NO_WRAP))
                    .apply()
                openMain()
            }
        } else {
            val saltText = prefs.getString("password_salt", null)
            val hashText = prefs.getString("password_hash", null)
            if (password.isBlank() || saltText.isNullOrBlank() || hashText.isNullOrBlank()) {
                status.text = "اطلاعات قفل محلی ناقص است؛ داده‌ها را پاک نکنید مگر اینکه نسخهٔ پشتیبان دارید."
                return
            }
            setBusy(true)
            lifecycleScope.launch {
                val valid = withContext(Dispatchers.IO) {
                    val salt = Base64.decode(saltText, Base64.NO_WRAP)
                    val expected = Base64.decode(hashText, Base64.NO_WRAP)
                    val actual = derivePassword(password, salt)
                    MessageDigest.isEqual(expected, actual)
                }
                if (valid) {
                    openMain()
                } else {
                    setBusy(false)
                    status.text = "رمز نادرست است."
                    Toast.makeText(this@SplashActivity, "ورود انجام نشد", Toast.LENGTH_SHORT).show()
                    passwordInput.text?.clear()
                }
            }
        }
    }

    private fun setBusy(busy: Boolean) {
        submit.isEnabled = !busy
        passwordInput.isEnabled = !busy
        confirmationInput.isEnabled = !busy
        status.text = if (busy) "در حال بررسی..." else ""
    }

    private fun openMain() {
        startActivity(Intent(this, MainActivity::class.java))
        finish()
    }

    private fun derivePassword(password: String, salt: ByteArray): ByteArray {
        val spec = PBEKeySpec(password.toCharArray(), salt, 120_000, 256)
        return try {
            SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256")
                .generateSecret(spec).encoded
        } finally {
            spec.clearPassword()
        }
    }
}
