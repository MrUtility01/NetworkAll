package com.netenc.app

import android.content.Intent
import android.os.Bundle
import android.view.View
import android.widget.ArrayAdapter
import android.widget.LinearLayout
import android.widget.ListView
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.netenc.app.data.AppDatabase
import com.netenc.app.data.OfflineSeeder
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

/** Virtualized lesson list for a single subchapter. Avoids rendering thousands of views in the tree. */
class SubchapterLessonsActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val chapterOrder = intent.getIntExtra("chapter_order", 0)
        val chapterTitle = intent.getStringExtra("chapter_title").orEmpty()
        val subTitle = intent.getStringExtra("sub_title").orEmpty()
        val subDisplayTitle = intent.getStringExtra("sub_display_title").orEmpty()
        val header = TextView(this).apply {
            text = "در حال بارگذاری درس‌ها…"
            textSize = 15f
            setTextColor(Ui.TEXT)
            typeface = Ui.persianTypeface()
            setPadding(24, 20, 24, 16)
        }
        val list = ListView(this).apply {
            layoutDirection = View.LAYOUT_DIRECTION_RTL
            setBackgroundColor(Ui.BG)
        }
        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            layoutDirection = View.LAYOUT_DIRECTION_RTL
            setBackgroundColor(Ui.BG)
            addView(header)
            addView(
                list,
                LinearLayout.LayoutParams(
                    LinearLayout.LayoutParams.MATCH_PARENT, 0, 1f
                )
            )
        }
        setContentView(root)

        lifecycleScope.launch {
            try {
                val lessons = withContext(Dispatchers.IO) {
                    // Safe even when opened before the main screen finishes seeding.
                    OfflineSeeder.ensureSeeded(this@SubchapterLessonsActivity)
                    AppDatabase.get(this@SubchapterLessonsActivity)
                        .lessonDao()
                        .byChapter(chapterOrder)
                        .filter { it.subTitle == subTitle }
                }
                header.text = "$chapterTitle  ›  $subDisplayTitle  (${lessons.size} درس)"
                list.adapter = ArrayAdapter(
                    this@SubchapterLessonsActivity,
                    android.R.layout.simple_list_item_1,
                    lessons.map { it.titleFa.ifBlank { it.uid } }
                )
                if (lessons.isEmpty()) {
                    header.text = "$chapterTitle  ›  $subDisplayTitle\nدرسی در این زیرشاخه یافت نشد."
                    return@launch
                }
                list.setOnItemClickListener { _, _, position, _ ->
                    startActivity(
                        Intent(this@SubchapterLessonsActivity, LessonDetailActivity::class.java)
                            .putExtra("uid", lessons[position].uid)
                    )
                }
            } catch (e: Exception) {
                header.text = "خطا در بارگذاری درس‌ها: ${e.message ?: "خطای نامشخص"}"
            }
        }
    }
}
