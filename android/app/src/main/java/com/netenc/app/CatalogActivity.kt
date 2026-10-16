package com.netenc.app

import android.os.Bundle
import android.view.View
import android.widget.ArrayAdapter
import android.widget.Button
import android.widget.LinearLayout
import android.widget.ListView
import android.widget.TextView
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.netenc.app.data.AppDatabase
import com.netenc.app.data.ChapterRow
import com.netenc.app.data.LessonEntity
import com.netenc.app.data.LessonListRow
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

/**
 * Offline catalog with staged loading:
 * 1) fetch chapter names, 2) fetch lightweight lesson rows for one chapter,
 * 3) load the full lesson text only when the user opens that lesson.
 * No lesson content is removed from SQLite.
 */
class CatalogActivity : AppCompatActivity() {
    private lateinit var title: TextView
    private lateinit var back: Button
    private lateinit var list: ListView
    private var selectedChapter: ChapterRow? = null
    private var chapters: List<ChapterRow> = emptyList()
    private var lessonRows: List<LessonListRow> = emptyList()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        title = TextView(this).apply {
            text = "فهرست آفلاین"
            textSize = 18f
            setPadding(32, 28, 32, 12)
        }
        back = Button(this).apply {
            text = "بازگشت به فصل‌ها"
            visibility = View.GONE
            setOnClickListener { showChapters() }
        }
        list = ListView(this)
        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            layoutDirection = View.LAYOUT_DIRECTION_RTL
            addView(title)
            addView(back)
            addView(
                list,
                LinearLayout.LayoutParams(
                    LinearLayout.LayoutParams.MATCH_PARENT, 0, 1f
                )
            )
        }
        setContentView(root)

        lifecycleScope.launch {
            chapters = withContext(Dispatchers.IO) {
                AppDatabase.get(this@CatalogActivity).lessonDao().chapters()
            }
            showChapters()
        }
    }

    private fun showChapters() {
        selectedChapter = null
        lessonRows = emptyList()
        back.visibility = View.GONE
        title.text = "فهرست آفلاین — ${chapters.size} فصل"
        list.adapter = ArrayAdapter(
            this, android.R.layout.simple_list_item_1,
            chapters.map { "فصل ${it.chapterOrder} — ${it.chapterTitle}" }
        )
        list.setOnItemClickListener { _, _, pos, _ ->
            openChapter(chapters[pos])
        }
    }

    private fun openChapter(chapter: ChapterRow) {
        selectedChapter = chapter
        title.text = "در حال بارگذاری فصل ${chapter.chapterOrder}…"
        back.visibility = View.VISIBLE
        lifecycleScope.launch {
            lessonRows = withContext(Dispatchers.IO) {
                AppDatabase.get(this@CatalogActivity).lessonDao()
                    .lessonRowsByChapter(chapter.chapterOrder)
            }
            title.text = "${chapter.chapterTitle} — ${lessonRows.size} درس"
            list.adapter = ArrayAdapter(
                this@CatalogActivity,
                android.R.layout.simple_list_item_1,
                lessonRows.mapIndexed { index, row ->
                    "${index + 1}. ${row.titleFa.ifBlank { row.uid }}"
                }
            )
            list.setOnItemClickListener { _, _, pos, _ ->
                lifecycleScope.launch {
                    val full = withContext(Dispatchers.IO) {
                        AppDatabase.get(this@CatalogActivity).lessonDao()
                            .byUid(lessonRows[pos].uid)
                    }
                    if (full != null) showLesson(full)
                }
            }
        }
    }

    private fun showLesson(e: LessonEntity) {
        val body = buildString {
            appendLine(e.titleFa)
            appendLine()
            appendLine("—— خلاصه / دیدگاه کلی ——")
            appendLine(e.summary.ifBlank { "(خلاصه خالی)" })
            appendLine()
            appendLine("—— متن درس ——")
            appendLine(e.fullContent.ifBlank { "(متن کامل ثبت نشده است)" })
            if (e.commands.isNotBlank()) {
                appendLine()
                appendLine("—— دستورات ——")
                appendLine(e.commands)
            }
            if (e.examples.isNotBlank()) {
                appendLine()
                appendLine("—— مثال ——")
                appendLine(e.examples)
            }
            if (e.notes.isNotBlank()) {
                appendLine()
                appendLine("—— نکات ——")
                appendLine(e.notes)
            }
        }
        AlertDialog.Builder(this)
            .setTitle(e.titleFa.take(48))
            .setMessage(body)
            .setPositiveButton("بستن", null)
            .show()
    }
}
