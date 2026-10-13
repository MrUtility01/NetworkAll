package com.netenc.app

import android.content.Intent
import android.os.Bundle
import android.view.View
import android.view.ViewGroup
import android.widget.BaseExpandableListAdapter
import android.widget.Button
import android.widget.EditText
import android.widget.ExpandableListView
import android.widget.LinearLayout
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.netenc.app.data.AppDatabase
import com.netenc.app.data.LessonNavRow
import com.netenc.app.data.OfflineSeeder
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class TreeCatalogActivity : AppCompatActivity() {
    data class SubNode(val title: String, val lessons: List<LessonNavRow>)
    data class ChapterNode(val order: Int, val title: String, val subs: List<SubNode>)

    private lateinit var list: ExpandableListView
    private lateinit var header: TextView
    private var tree: List<ChapterNode> = emptyList()
    private var treeAdapter: BaseExpandableListAdapter? = null
    private val visibleLessonCounts = mutableMapOf<Pair<Int, String>, Int>()
    private val initialLessonPageSize = 30

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
        lifecycleScope.launch {
            try {
                loadTree()
            } catch (e: Exception) {
                header.text = "بارگذاری فهرست ناموفق بود: ${e.message ?: "خطای ناشناخته"}"
            }
        }
    }

    private suspend fun loadTree() {
        // Wait for the first seed to finish; the seeder is single-flight so this
        // cannot race MainActivity or SyncClient and expose a partial curriculum.
        val lessons = withContext(Dispatchers.IO) {
            OfflineSeeder.ensureSeeded(this@TreeCatalogActivity)
            AppDatabase.get(this@TreeCatalogActivity).lessonDao().navigationRows()
        }
        val byChapter = lessons.groupBy { it.chapterOrder to it.chapterTitle }
            .toSortedMap(compareBy({ it.first }, { it.second }))
        tree = byChapter.map { (key, chapterLessons) ->
            val subs = chapterLessons.groupBy { it.subTitle.ifBlank { "عمومی" } }
                .map { (subTitle, subLessons) ->
                    SubNode(subTitle, subLessons.sortedBy { it.lessonOrder })
                }
                .sortedBy { it.title }
            ChapterNode(key.first, key.second, subs)
        }
        header.text = "${tree.size} فصل · ${lessons.size} درس · بارگذاری مرحله‌ای"
        treeAdapter = object : BaseExpandableListAdapter() {
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
                val chapter = tree[g]
                val sub = chapter.subs[c]
                val key = chapter.order to sub.title
                val limit = visibleLessonCounts[key] ?: initialLessonPageSize
                val box = LinearLayout(this@TreeCatalogActivity).apply {
                    orientation = LinearLayout.VERTICAL
                    setPadding(48, 12, 24, 12)
                    setBackgroundColor(Ui.BG)
                }
                box.addView(TextView(this@TreeCatalogActivity).apply {
                    text = "${sub.title} (${sub.lessons.size} درس)"
                    setTextColor(Ui.ACCENT)
                    textSize = 14f
                    typeface = Ui.persianTypeface()
                })
                sub.lessons.take(limit).forEach { lesson ->
                    box.addView(TextView(this@TreeCatalogActivity).apply {
                        text = "  · ${lesson.titleFa}"
                        setTextColor(Ui.TEXT)
                        textSize = 13f
                        setPadding(8, 10, 8, 10)
                        typeface = Ui.persianTypeface()
                        setOnClickListener {
                            startActivity(
                                Intent(this@TreeCatalogActivity, LessonDetailActivity::class.java)
                                    .putExtra("uid", lesson.uid)
                            )
                        }
                    })
                }
                val remaining = sub.lessons.size - minOf(limit, sub.lessons.size)
                if (remaining > 0) {
                    box.addView(Button(this@TreeCatalogActivity).apply {
                        text = "نمایش 30 درس دیگر (باقی‌مانده: $remaining)"
                        textSize = 12f
                        typeface = Ui.persianTypeface()
                        setOnClickListener {
                            visibleLessonCounts[key] = limit + initialLessonPageSize
                            treeAdapter?.notifyDataSetChanged()
                        }
                    })
                }
                return box
            }
        }
        list.setAdapter(treeAdapter)
    }
}
