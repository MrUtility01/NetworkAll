package com.netenc.app

import android.os.Bundle
import android.view.View
import android.webkit.WebView
import android.widget.ArrayAdapter
import android.widget.LinearLayout
import android.widget.ListView
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import org.json.JSONArray
import org.json.JSONObject

class DiagramGalleryActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            layoutDirection = View.LAYOUT_DIRECTION_RTL
            setBackgroundColor(0xFFF8FAFC.toInt())
        }
        val heading = TextView(this).apply {
            text = "کتابخانهٔ دیاگرام‌های NetworkAll"
            textSize = 20f
            setPadding(20, 16, 20, 12)
            setTextColor(0xFF0F172A.toInt())
        }
        val list = ListView(this)
        val web = WebView(this).apply {
            setBackgroundColor(0xFFF8FAFC.toInt())
            settings.javaScriptEnabled = false
            settings.allowFileAccess = true
            settings.allowContentAccess = false
        }
        root.addView(heading)
        root.addView(list, LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, 0, 1.0f))
        root.addView(web, LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, 0, 1.5f))
        setContentView(root)

        try {
            val index = assets.open("diagrams/combined_index.json")
                .bufferedReader(Charsets.UTF_8).use { it.readText() }
            val arr = JSONObject(index).getJSONArray("diagrams")
            if (arr.length() == 0) {
                heading.text = "هنوز دیاگرامی برای نمایش وجود ندارد"
                Toast.makeText(this, "فهرست دیاگرام‌ها خالی است", Toast.LENGTH_LONG).show()
                return
            }

            // General diagrams use numeric IDs; chapter manifests use string IDs
            // such as "arp-flow". Never assume every entry has an integer ID.
            val titles = (0 until arr.length()).map { i ->
                val item = arr.getJSONObject(i)
                "${displayId(item, i + 1)} · ${item.optString("title_fa", "دیاگرام بدون عنوان")}"
            }
            list.adapter = ArrayAdapter(this, android.R.layout.simple_list_item_1, titles)
            list.setOnItemClickListener { _, _, position, _ ->
                showDiagram(arr.getJSONObject(position), position + 1, heading, web)
            }
            showDiagram(arr.getJSONObject(0), 1, heading, web)
            Toast.makeText(this, "دیاگرام‌ها: ${arr.length()}", Toast.LENGTH_SHORT).show()
        } catch (e: Exception) {
            heading.text = "کتابخانهٔ دیاگرام بارگذاری نشد"
            Toast.makeText(this, "خطای خواندن دیاگرام‌ها: ${e.message ?: "نامشخص"}", Toast.LENGTH_LONG).show()
        }
    }

    private fun displayId(item: JSONObject, fallback: Int): String {
        val raw = item.opt("id")?.toString()?.trim().orEmpty()
        if (raw.isBlank() || raw == "null") return "%03d".format(fallback)
        val number = raw.toIntOrNull()
        return if (number != null) "%03d".format(number) else raw
    }

    private fun showDiagram(item: JSONObject, fallback: Int, heading: TextView, web: WebView) {
        val asset = item.optString("asset", "").trim()
        if (asset.isBlank() || asset.startsWith("/") || asset.split('/').any { it == ".." }) {
            Toast.makeText(this, "مسیر فایل دیاگرام نامعتبر است", Toast.LENGTH_LONG).show()
            return
        }
        val title = item.optString("title_fa", "دیاگرام بدون عنوان")
        val chapter = item.optInt("chapter_order", 0)
        heading.text = if (chapter > 0) {
            "فصل $chapter · ${displayId(item, fallback)} · $title"
        } else {
            "دیاگرام ${displayId(item, fallback)} · $title"
        }
        web.loadUrl("file:///android_asset/diagrams/$asset")
    }
}
