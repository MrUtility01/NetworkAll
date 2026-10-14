package com.netenc.app

import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.graphics.Color
import android.os.Bundle
import android.text.Editable
import android.text.TextWatcher
import android.view.Gravity
import android.view.View
import android.widget.ArrayAdapter
import android.widget.Button
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.ListView
import android.widget.ScrollView
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import org.json.JSONArray
import org.json.JSONObject
import java.util.Locale

class IncidentRunbookActivity : AppCompatActivity() {
    private lateinit var search: EditText
    private lateinit var list: ListView
    private lateinit var detail: LinearLayout
    private lateinit var adapter: ArrayAdapter<String>
    private var all: List<JSONObject> = emptyList()
    private var filtered: List<JSONObject> = emptyList()
    private var commands = ""

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        title = "سناریوهای واقعی عیب‌یابی"
        all = loadRunbooks()
        filtered = all
        val page = ScrollView(this).apply { setBackgroundColor(Color.rgb(245, 247, 251)); isFillViewport = true }
        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            layoutDirection = View.LAYOUT_DIRECTION_RTL
            setPadding(dp(14), dp(12), dp(14), dp(24))
        }
        root.addView(label("کتابخانه سناریوهای عملیاتی", 21, Color.rgb(22, 55, 99), true))
        root.addView(label(all.size.toString() + " سناریو؛ شواهد، علت ریشه‌ای، اصلاح، Verify و Rollback", 13, Color.rgb(71, 85, 105)))
        root.addView(label("پیش از اجرا، نسخه، نام interface و آدرس‌ها را با محیط خودت تطبیق بده. تغییر Production نیازمند مجوز، baseline و روش بازگشت است.", 12, Color.rgb(124, 45, 18)).apply {
            setPadding(dp(10), dp(8), dp(10), dp(8)); setBackgroundColor(Color.rgb(255, 247, 237))
        })
        search = EditText(this).apply { hint = "جستجو: VLAN، OSPF، DHCP، NAT، DNS، MTU…"; setSingleLine(true); textSize = 14f }
        root.addView(search, LinearLayout.LayoutParams(-1, dp(50)).apply { topMargin = dp(8) })
        list = ListView(this).apply { dividerHeight = dp(1); isNestedScrollingEnabled = false; setBackgroundColor(Color.WHITE) }
        adapter = ArrayAdapter(this, android.R.layout.simple_list_item_1, mutableListOf<String>())
        list.adapter = adapter
        root.addView(list, LinearLayout.LayoutParams(-1, dp(260)).apply { topMargin = dp(6) })
        detail = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL; layoutDirection = View.LAYOUT_DIRECTION_RTL; setPadding(0, dp(10), 0, 0) }
        root.addView(detail, LinearLayout.LayoutParams(-1, -2))
        page.addView(root); setContentView(page)
        refreshList()
        list.setOnItemClickListener { _, _, position, _ -> showRunbook(filtered[position]) }
        search.addTextChangedListener(object : TextWatcher {
            override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}
            override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) { filter(s?.toString().orEmpty()) }
            override fun afterTextChanged(s: Editable?) {}
        })
        if (all.isNotEmpty()) showRunbook(all.first())
        else detail.addView(label("فایل incident_runbooks.json در بسته پیدا نشد؛ نسخه را از شاخه به‌روز بساز.", 14, Color.RED))
    }

    private fun loadRunbooks(): List<JSONObject> = try {
        val raw = assets.open("incident_runbooks.json").bufferedReader(Charsets.UTF_8).use { it.readText() }
        val rows = JSONObject(raw).optJSONArray("incidents") ?: JSONArray()
        (0 until rows.length()).mapNotNull { rows.optJSONObject(it) }
    } catch (_: Exception) { emptyList() }

    private fun filter(query: String) {
        val q = query.trim().lowercase(Locale.ROOT)
        filtered = if (q.isEmpty()) all else all.filter { row ->
            listOf("id", "code", "title_fa", "title_en", "domain", "platform", "impact", "environment", "root_cause")
                .any { row.optString(it).lowercase(Locale.ROOT).contains(q) } ||
                row.optJSONArray("symptoms").asLines().lowercase(Locale.ROOT).contains(q)
        }
        refreshList()
    }

    private fun refreshList() {
        adapter.clear()
        adapter.addAll(filtered.map { it.optString("code") + " · " + it.optString("title_fa") + "\n" +
            it.optString("domain") + " | " + it.optString("platform") })
        adapter.notifyDataSetChanged()
    }

    private fun showRunbook(row: JSONObject) {
        detail.removeAllViews()
        commands = ""
        detail.addView(label(row.optString("code") + " · " + row.optString("title_fa"), 19, Color.rgb(22, 55, 99), true))
        detail.addView(label(row.optString("domain") + " · " + row.optString("platform") + " · شدت: " +
            row.optString("severity") + " · زمان: " + row.optString("duration"), 12, Color.rgb(71, 85, 105)))
        block("محیط", row.optString("environment"))
        block("اثر و نشانه‌ها", row.optString("impact") + "\n" + row.optJSONArray("symptoms").asLines())
        block("علت ریشه‌ای", row.optString("root_cause"))
        block("اصلاح", row.optString("fix_summary"))
        val steps = row.optJSONArray("steps") ?: row.optJSONArray("diagnostic_steps") ?: JSONArray()
        detail.addView(label("روند عیب‌یابی؛ " + steps.length() + " مرحله", 16, Color.rgb(15, 118, 110), true))
        for (i in 0 until steps.length()) {
            val st = steps.optJSONObject(i) ?: continue
            detail.addView(label("مرحله " + (i + 1) + ": " + st.optString("title"), 15, Color.rgb(30, 64, 115), true))
            block("هدف", st.optString("purpose"))
            val cmd = st.optString("commands")
            if (cmd.isNotBlank()) {
                commands += "\n\n# " + st.optString("title") + "\n" + cmd
                block("فرمان‌ها / فیلترها", cmd, true)
            }
            block("خروجی مورد انتظار", st.optString("expected"))
            block("تفسیر شواهد", st.optString("interpretation"))
            block("اگر تأیید شد", st.optString("if_match"))
            block("اگر تأیید نشد", st.optString("if_not_match"))
            detail.addView(View(this).apply {
                setBackgroundColor(Color.rgb(219, 228, 240))
                layoutParams = LinearLayout.LayoutParams(-1, dp(1)).apply { topMargin = dp(8); bottomMargin = dp(8) }
            })
        }
        block("Verify / تأیید رفع", row.optString("verification"))
        block("Rollback / بازگشت", row.optString("rollback"))
        block("پیشگیری", row.optString("prevention"))
        detail.addView(label("وضعیت محتوا: پیش از اجرا باید متناسب با نسخه و توپولوژی بازبینی شود.", 12, Color.rgb(124, 45, 18)).apply {
            setPadding(dp(10), dp(8), dp(10), dp(8)); setBackgroundColor(Color.rgb(255, 247, 237))
        })
        detail.addView(Button(this).apply {
            text = "کپی همه فرمان‌های سناریو"
            setOnClickListener {
                val cb = getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
                cb.setPrimaryClip(ClipData.newPlainText("NetworkAll runbook", commands))
                Toast.makeText(this@IncidentRunbookActivity, "فرمان‌ها کپی شدند", Toast.LENGTH_SHORT).show()
            }
        })
    }

    private fun block(heading: String, value: String, code: Boolean = false) {
        if (value.isBlank()) return
        detail.addView(label(heading, 12, Color.rgb(71, 85, 105), true))
        detail.addView(label(value, if (code) 12 else 13, if (code) Color.rgb(226, 232, 240) else Color.rgb(30, 41, 59)).apply {
            setPadding(dp(10), dp(9), dp(10), dp(9))
            if (code) {
                typeface = android.graphics.Typeface.MONOSPACE
                textDirection = View.TEXT_DIRECTION_LTR
                gravity = Gravity.START
                setBackgroundColor(Color.rgb(15, 23, 42))
            } else setBackgroundColor(Color.WHITE)
            layoutParams = LinearLayout.LayoutParams(-1, -2).apply { bottomMargin = dp(7) }
        })
    }

    private fun label(value: String, size: Int, color: Int, bold: Boolean = false) = TextView(this).apply {
        text = value; textSize = size.toFloat(); setTextColor(color); gravity = Gravity.START
        layoutDirection = View.LAYOUT_DIRECTION_RTL
        if (bold) setTypeface(typeface, android.graphics.Typeface.BOLD)
        setPadding(dp(2), dp(4), dp(2), dp(4))
    }
    private fun JSONArray?.asLines(): String = this?.let { a -> (0 until a.length()).joinToString("\n") { "• " + a.optString(it) } }.orEmpty()
    private fun dp(n: Int): Int = (n * resources.displayMetrics.density).toInt()
}
