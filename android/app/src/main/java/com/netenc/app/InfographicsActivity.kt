package com.netenc.app

import android.app.Activity
import android.content.Intent
import android.graphics.Bitmap
import android.graphics.Canvas
import android.net.Uri
import android.os.Bundle
import android.view.View
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.Button
import android.widget.LinearLayout
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity

/** Shared offline infographic library with an explicit, permission-free PNG export. */
class InfographicsActivity : AppCompatActivity() {
    private lateinit var infographicView: WebView
    private var pendingBitmap: Bitmap? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        infographicView = WebView(this).apply {
            settings.javaScriptEnabled = false
            settings.domStorageEnabled = false
            settings.allowFileAccess = true
            settings.allowContentAccess = false
            settings.mixedContentMode = WebSettings.MIXED_CONTENT_NEVER_ALLOW
            webViewClient = WebViewClient()
            loadUrl("file:///android_asset/index.html")
        }
        val save = Button(this).apply {
            text = "ذخیره تصویر قابل‌مشاهده به‌صورت PNG"
            setOnClickListener { prepareImageExport() }
        }
        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            layoutDirection = View.LAYOUT_DIRECTION_RTL
            addView(save, LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT
            ))
            addView(infographicView, LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, 0, 1f
            ))
        }
        setContentView(root)
    }

    private fun prepareImageExport() {
        if (!::infographicView.isInitialized || infographicView.width <= 0 || infographicView.height <= 0) {
            Toast.makeText(this, "تصویر هنوز آماده نیست", Toast.LENGTH_SHORT).show()
            return
        }
        try {
            val bitmap = Bitmap.createBitmap(
                infographicView.width, infographicView.height, Bitmap.Config.ARGB_8888
            )
            infographicView.draw(Canvas(bitmap))
            pendingBitmap = bitmap
            val intent = Intent(Intent.ACTION_CREATE_DOCUMENT).apply {
                addCategory(Intent.CATEGORY_OPENABLE)
                type = "image/png"
                putExtra(Intent.EXTRA_TITLE, "NetworkAll-infographic.png")
            }
            startActivityForResult(intent, REQUEST_SAVE_IMAGE)
        } catch (e: Exception) {
            pendingBitmap?.recycle()
            pendingBitmap = null
            Toast.makeText(this, "ساخت تصویر ناموفق بود: ${e.message}", Toast.LENGTH_LONG).show()
        }
    }

    @Deprecated("Uses the existing Activity callback for compatibility with the current app")
    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        if (requestCode != REQUEST_SAVE_IMAGE) return
        val bitmap = pendingBitmap
        pendingBitmap = null
        if (resultCode != Activity.RESULT_OK || data?.data == null || bitmap == null) {
            bitmap?.recycle()
            return
        }
        try {
            contentResolver.openOutputStream(data.data!!)?.use { output ->
                if (!bitmap.compress(Bitmap.CompressFormat.PNG, 100, output)) {
                    throw IllegalStateException("PNG encoding failed")
                }
            } ?: throw IllegalStateException("فایل مقصد قابل نوشتن نیست")
            Toast.makeText(this, "تصویر ذخیره شد", Toast.LENGTH_SHORT).show()
        } catch (e: Exception) {
            Toast.makeText(this, "ذخیره تصویر ناموفق بود: ${e.message}", Toast.LENGTH_LONG).show()
        } finally {
            bitmap.recycle()
        }
    }

    override fun onDestroy() {
        if (::infographicView.isInitialized) infographicView.destroy()
        pendingBitmap?.recycle()
        pendingBitmap = null
        super.onDestroy()
    }

    companion object { private const val REQUEST_SAVE_IMAGE = 7401 }
}
