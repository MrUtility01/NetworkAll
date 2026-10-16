package com.netenc.app

import android.content.Intent
import android.os.Bundle
import android.util.Base64
import android.view.Gravity
import android.view.View
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import java.security.MessageDigest
import java.security.SecureRandom
import javax.crypto.SecretKeyFactory
import javax.crypto.spec.PBEKeySpec

/**
 * Local application gate. The user creates a password on first launch;
 * no shared/default password is shipped with the application.
 */
class SplashActivity : AppCompatActivity() {
    private val prefs by lazy { getSharedPreferences("netenc_security", MODE_PRIVATE) }
    private val iterations = 160_000
    private val saltBytes = 16
    private val keyBits = 256

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        if (prefs.getString("password_hash", null).isNullOrBlank()) showCreatePassword()
        else showUnlock()
    }

    private fun showCreatePassword() {
        val password = passwordField("حداقل ۸ نویسه")
        val confirm = passwordField("تکرار گذرواژه")
        val box = form(password, confirm, "برای محافظت از برنامه، یک گذرواژه بسازید.")
        val dialog = AlertDialog.Builder(this)
            .setTitle("تنظیم گذرواژه برنامه")
            .setView(box)
            .setCancelable(false)
            .setPositiveButton("ذخیره", null)
            .create()
        dialog.setOnShowListener {
            dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener {
                val p1 = password.text.toString()
                val p2 = confirm.text.toString()
                when {
                    p1.length < 8 -> password.error = "حداقل ۸ نویسه لازم است"
                    p1 != p2 -> confirm.error = "دو گذرواژه یکسان نیستند"
                    else -> {
                        val salt = ByteArray(saltBytes).also { SecureRandom().nextBytes(it) }
                        val hash = derive(p1, salt)
                        prefs.edit()
                            .putString("password_salt", Base64.encodeToString(salt, Base64.NO_WRAP))
                            .putString("password_hash", Base64.encodeToString(hash, Base64.NO_WRAP))
                            .putInt("password_iterations", iterations)
                            .apply()
                        NetEncApplication.isAuthenticated = true
                        dialog.dismiss()
                        enterApp()
                    }
                }
            }
        }
        dialog.show()
        dialog.window?.setSoftInputMode(android.view.WindowManager.LayoutParams.SOFT_INPUT_STATE_ALWAYS_VISIBLE)
    }

    private fun showUnlock() {
        val password = passwordField("گذرواژه برنامه")
        val box = form(password, null, "برای ادامه، گذرواژه محلی برنامه را وارد کنید.")
        val dialog = AlertDialog.Builder(this)
            .setTitle("قفل برنامه")
            .setView(box)
            .setCancelable(false)
            .setPositiveButton("ورود", null)
            .create()
        dialog.setOnShowListener {
            dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener {
                val saltText = prefs.getString("password_salt", null)
                val hashText = prefs.getString("password_hash", null)
                val candidate = password.text.toString()
                try {
                    val salt = Base64.decode(saltText, Base64.NO_WRAP)
                    val expected = Base64.decode(hashText, Base64.NO_WRAP)
                    val rounds = prefs.getInt("password_iterations", iterations).coerceIn(100_000, 500_000)
                    if (MessageDigest.isEqual(expected, derive(candidate, salt, rounds))) {
                        NetEncApplication.isAuthenticated = true
                        dialog.dismiss()
                        enterApp()
                    } else {
                        password.text?.clear()
                        password.error = "گذرواژه نادرست است"
                    }
                } catch (_: Exception) {
                    password.error = "اطلاعات قفل قابل خواندن نیست؛ داده‌ها را پاک نکنید و پشتیبانی بگیرید."
                }
            }
        }
        dialog.show()
    }

    private fun enterApp() {
        val destination = when (intent.getStringExtra("open_mode")) {
            "tasks" -> Intent(this, WorkspaceActivity::class.java).putExtra("mode", "tasks")
            "flashcards" -> Intent(this, FlashcardActivity::class.java).putExtra("mode", "review")
            "study" -> Intent(this, StudyHubActivity::class.java)
            else -> Intent(this, MainActivity::class.java)
        }.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK)
        startActivity(destination)
        finish()
    }

    private fun passwordField(hintText: String) = EditText(this).apply {
        hint = hintText
        inputType = android.text.InputType.TYPE_CLASS_TEXT or android.text.InputType.TYPE_TEXT_VARIATION_PASSWORD
        layoutDirection = View.LAYOUT_DIRECTION_LTR
        textAlignment = View.TEXT_ALIGNMENT_VIEW_START
        isSingleLine = true
    }

    private fun form(first: EditText, second: EditText?, message: String) = LinearLayout(this).apply {
        orientation = LinearLayout.VERTICAL
        layoutDirection = View.LAYOUT_DIRECTION_RTL
        setPadding(36, 8, 36, 4)
        addView(TextView(this@SplashActivity).apply {
            text = message
            textSize = 15f
            setPadding(0, 8, 0, 16)
        })
        addView(first)
        if (second != null) addView(second)
        addView(TextView(this@SplashActivity).apply {
            text = "این گذرواژه روی همین دستگاه ذخیره می‌شود؛ آن را در جای امن نگه دارید."
            textSize = 12f
            setPadding(0, 14, 0, 0)
        })
    }

    private fun derive(password: String, salt: ByteArray, rounds: Int = iterations): ByteArray {
        val spec = PBEKeySpec(password.toCharArray(), salt, rounds, keyBits)
        return try {
            SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256").generateSecret(spec).encoded
        } finally {
            spec.clearPassword()
        }
    }

    @Deprecated("Deprecated in Android")
    override fun onBackPressed() {
        // The entry gate must not be dismissible without authentication.
    }
}
