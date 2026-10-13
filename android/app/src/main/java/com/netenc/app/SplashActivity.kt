package com.netenc.app

import android.content.Intent
import android.graphics.Color
import android.os.Bundle
import android.text.InputType
import android.view.Gravity
import android.widget.Button
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import javax.crypto.SecretKeyFactory
import javax.crypto.spec.PBEKeySpec

/**
 * Local app-entry gate. The password is verified as a salted PBKDF2 hash, never stored in plaintext.
 * This is a personal-device access gate, not a replacement for Android device lock/encryption.
 */
class SplashActivity : AppCompatActivity() {
    companion object {
        private const val PASSWORD_SALT_HEX = "5f3a9c71d8e2046bb6f9012ac48d735e"
        private const val PASSWORD_HASH_HEX = "aaf49102a320825f15b1dc26866c722203ccffec8e9a7d49d186ac9119a1e540"
        private const val PASSWORD_ITERATIONS = 200_000
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        showGate()
    }

    private fun showGate() {
        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            gravity = Gravity.CENTER
            setBackgroundColor(Color.parseColor("#F4F6F9"))
            setPadding(48, 48, 48, 48)
        }
        root.addView(TextView(this).apply {
            text = "Engineer Jokar · NetworkAll"
            textSize = 26f
            setTextColor(Color.parseColor("#1D4ED8"))
            gravity = Gravity.CENTER
        })
        root.addView(TextView(this).apply {
            text = "ورود به دانشنامه شبکه و زیرساخت"
            textSize = 16f
            setTextColor(Ui.TEXT)
            gravity = Gravity.CENTER
            setPadding(0, 16, 0, 20)
        })
        val pin = EditText(this).apply {
            hint = "رمز ورود برنامه"
            inputType = InputType.TYPE_CLASS_TEXT or InputType.TYPE_TEXT_VARIATION_PASSWORD or InputType.TYPE_TEXT_FLAG_NO_SUGGESTIONS
            gravity = Gravity.CENTER
            textAlignment = android.view.View.TEXT_ALIGNMENT_CENTER
            contentDescription = "رمز ورود برنامه"
        }
        root.addView(pin, LinearLayout.LayoutParams(-1, -2))
        val error = TextView(this).apply {
            text = ""
            setTextColor(Color.rgb(185, 28, 28))
            gravity = Gravity.CENTER
            setPadding(0, 8, 0, 8)
        }
        root.addView(error)
        root.addView(Button(this).apply {
            text = "ورود"
            setOnClickListener {
                val entered = pin.text?.toString().orEmpty()
                if (verifyPin(entered)) {
                    startActivity(Intent(this@SplashActivity, MainActivity::class.java))
                    finish()
                } else {
                    error.text = "رمز صحیح نیست."
                    pin.text?.clear()
                    pin.requestFocus()
                }
            }
        }, LinearLayout.LayoutParams(-1, -2))
        setContentView(root)
    }

    private fun verifyPin(value: String): Boolean {
        if (value.length !in 8..32) return false
        return try {
            val salt = PASSWORD_SALT_HEX.chunked(2).map { it.toInt(16).toByte() }.toByteArray()
            val expected = PASSWORD_HASH_HEX.chunked(2).map { it.toInt(16).toByte() }.toByteArray()
            val spec = PBEKeySpec(value.toCharArray(), salt, PASSWORD_ITERATIONS, expected.size * 8)
            val actual = SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256").generateSecret(spec).encoded
            spec.clearPassword()
            java.security.MessageDigest.isEqual(expected, actual)
        } catch (_: Exception) {
            false
        }
    }
}
