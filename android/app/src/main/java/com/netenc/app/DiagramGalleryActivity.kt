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
        }
        root.addView(heading)
        root.addView(list, LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, 0, 1.0f))
        root.addView(web, LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, 0, 1.5f))
        setContentView(root)
        try {
            val index = assets.open("diagrams/index.json").bufferedReader(Charsets.UTF_8).use { it.readText() }
            val arr = JSONObject(index).getJSONArray("diagrams")
            val titles = (0 until arr.length()).map { i ->
                "%03d · %s".format(arr.getJSONObject(i).getInt("id"), arr.getJSONObject(i).getString("title_fa"))
            }
            list.adapter = ArrayAdapter(this, android.R.layout.simple_list_item_1, titles)
            list.setOnItemClickListener { _, _, position, _ ->
                val item = arr.getJSONObject(position)
                val asset = item.getString("asset")
                val title = item.getString("title_fa")
                web.loadUrl("file:///android_asset/diagrams/$asset")
                heading.text = "دیاگرام ${item.getInt("id")} · $title"
            }
            if (arr.length() > 0) {
                val first = arr.getJSONObject(0)
                web.loadUrl("file:///android_asset/diagrams/" + first.getString("asset"))
            }
            Toast.makeText(this, "دیاگرام‌ها: ${arr.length()}", Toast.LENGTH_SHORT).show()
        } catch (e: Exception) {
            heading.text = "کتابخانهٔ دیاگرام بارگذاری نشد"
            Toast.makeText(this, e.message ?: "خطای خواندن فهرست", Toast.LENGTH_LONG).show()
        }
    }
}
