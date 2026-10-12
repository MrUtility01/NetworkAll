package com.netenc.app

import android.content.Intent
import android.os.Bundle
import android.view.View
import android.view.ViewGroup
import android.widget.BaseExpandableListAdapter
import android.widget.EditText
import android.widget.ExpandableListView
import android.widget.LinearLayout
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.netenc.app.data.AppDatabase
import com.netenc.app.data.LessonEntity
import com.netenc.app.data.OfflineSeeder
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class TreeCatalogActivity : AppCompatActivity() {
    data class SubNode(val title: String, val sourceTitle: String, val lessons: List<LessonEntity>)
    data class ChapterNode(val order: Int, val title: String, val subs: List<SubNode>)

    private lateinit var list: ExpandableListView
    private lateinit var header: TextView
    private var tree: List<ChapterNode> = emptyList()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val search = EditText(this).apply {
            hint = "جستجو در عناوین و محتوا…"
            setPadding(24, 16, 24, 16)
            textSize = 14f
            setTextColor(Ui.TEXT)
            setHintTextColor(Ui.MUTED)
            setBackgroundColor(Ui.CARD)
        }
        header = TextView(this).apply {
            text = "در حال بارگذاری درخت…"
            setPadding(24, 12, 24, 8)
            textSize = 13f
            setTextColor(Ui.MUTED)
        }
        list = ExpandableListView(this).apply {
            setBackgroundColor(Ui.BG)
        }
        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            layoutDirection = View.LAYOUT_DIRECTION_RTL
            setBackgroundColor(Ui.BG)
            addView(search)
            addView(header)
            addView(list, LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, 0, 1f
            ))
        }
        setContentView(root)
        search.setOnEditorActionListener { _, _, _ ->
            val q = search.text.toString().trim()
            if (q.isNotBlank()) {
                startActivity(Intent(this, SearchActivity::class.java).putExtra("q", q))
            }
            true
        }
        lifecycleScope.launch { loadTree() }
    }

    private suspend fun loadTree() {
        val lessons = try {
            withContext(Dispatchers.IO) {
                // Do not depend on MainActivity's background seeding having finished before
                // the user opens the tree. This also repairs old databases missing hierarchy.
                OfflineSeeder.ensureSeeded(this@TreeCatalogActivity)
                AppDatabase.get(this@TreeCatalogActivity).lessonDao().allActive()
            }
        } catch (e: Exception) {
            header.text = "خطا در بارگذاری محتوا: " + (e.message ?: "خطای نامشخص")
            return
        }
        if (lessons.isEmpty()) {
            header.text = "محتوایی بارگذاری نشد. به صفحه اصلی برگردید و وضعیت بارگذاری را بررسی کنید."
            return
        }
        // Repair display hierarchy defensively for older or partially imported rows.
        // The seeder normally fills these fields, but the UI must remain usable even
        // if an earlier database version stored missing metadata.
        val byChapter = lessons.groupBy {
            val order = it.chapterOrder.takeIf { n -> n > 0 }
                ?: Regex("""(?:ch|chapter)[-_: ]?(\d+)""", RegexOption.IGNORE_CASE)
                    .find(it.uid)?.groupValues?.getOrNull(1)?.toIntOrNull() ?: 0
            val title = it.chapterTitle.ifBlank {
                if (order > 0) "فصل $order" else "فصل‌بندی نشده"
            }
            order to title
        }.toSortedMap(compareBy({ it.first }, { it.second }))
        tree = byChapter.map { (key, listL) ->
            val subs = listL.groupBy { it.subTitle.ifBlank {
                it.titleFa.substringBefore(" — ").ifBlank { "عمومی" }
            } }
                .map { (st, ls) ->
                    SubNode(st, st, ls.sortedWith(compareBy<LessonEntity>({ it.lessonOrder }, { it.titleFa })))
                }.sortedBy { it.title }
            ChapterNode(key.first, key.second, subs)
        }
        header.text = "${tree.size} فصل · ${lessons.size} درس"
        list.setAdapter(object : BaseExpandableListAdapter() {
            override fun getGroupCount() = tree.size
            override fun getChildrenCount(g: Int) = tree[g].subs.size
            override fun getGroup(g: Int) = tree[g]
            override fun getChild(g: Int, c: Int) = tree[g].subs[c]
            override fun getGroupId(g: Int) = g.toLong()
            override fun getChildId(g: Int, c: Int) = (g * 10000 + c).toLong()
            override fun hasStableIds() = true
            override fun isChildSelectable(g: Int, c: Int) = true
            override fun getGroupView(g: Int, expanded: Boolean, convert: View?, parent: ViewGroup?): View {
                val tv = (convert as? TextView) ?: TextView(this@TreeCatalogActivity).apply {
                    setPadding(32, 28, 32, 28)
                    textSize = 16f
                    typeface = Ui.persianTypeface()
                }
                tv.text = "${tree[g].order}. ${tree[g].title}"
                tv.setTextColor(Ui.TEXT)
                tv.setBackgroundColor(Ui.CARD)
                return tv
            }
            override fun getChildView(g: Int, c: Int, last: Boolean, convert: View?, parent: ViewGroup?): View {
                val sub = tree[g].subs[c]
                // Keep the expandable tree lightweight: a child is one subchapter row,
                // not a container that eagerly creates hundreds of lesson TextViews.
                val row = (convert as? TextView) ?: TextView(this@TreeCatalogActivity).apply {
                    setPadding(48, 22, 24, 22)
                    textSize = 14f
                    typeface = Ui.persianTypeface()
                }
                row.text = "${sub.title}  (${sub.lessons.size} درس)  ›"
                row.setTextColor(Ui.ACCENT)
                row.setBackgroundColor(Ui.CARD)
                row.setOnClickListener {
                    startActivity(
                        Intent(this@TreeCatalogActivity, SubchapterLessonsActivity::class.java)
                            .putExtra("chapter_order", tree[g].order)
                            .putExtra("chapter_title", tree[g].title)
                            .putExtra("sub_title", sub.sourceTitle)
                            .putExtra("sub_display_title", sub.title)
                    )
                }
                return row
            }
        })
    }
}
