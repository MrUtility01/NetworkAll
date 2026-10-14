package com.netenc.app

import android.graphics.Color
import android.os.Bundle
import android.view.View
import android.widget.Button
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity

/** شبیه‌ساز آموزشی مرحله‌ای؛ برای capture زنده باید pcap واقعی وارد ابزار تحلیل شود. */
class PacketTraceActivity : AppCompatActivity() {
    private data class Step(
        val title: String, val layer: String, val protocol: String,
        val srcMac: String, val dstMac: String, val srcIp: String, val dstIp: String,
        val srcPort: String, val dstPort: String, val ttl: String, val flags: String,
        val checksum: String, val payload: String, val analysis: String
    )
    private val steps = listOf(
        Step("۱. DNS Lookup","Application / Transport","DNS over UDP","00:11:22:33:44:55","ff:ff:ff:ff:ff:ff","192.168.10.25","192.168.10.10","53001","53","64","UDP","محاسبه‌شده","QNAME=portal.example.test; QTYPE=A","برنامه ابتدا نام را به IP تبدیل می‌کند. DNS معمولاً UDP/53 است؛ پاسخ ممکن است cache شود. مسیر واقعی DNS با محل resolver تعیین می‌شود."),
        Step("۲. ARP برای Gateway","Layer 2 / ARP","ARP Request","00:11:22:33:44:55","ff:ff:ff:ff:ff:ff","192.168.10.25","192.168.10.1","—","—","N/A","Who has gateway?","بدون IP checksum","Sender MAC/IP + Target IP","مقصد خارج subnet است؛ بنابراین کلاینت MAC دروازه را پیدا می‌کند، نه MAC سرور اینترنتی را. ARP از روتر عبور نمی‌کند."),
        Step("۳. کلاینت TCP SYN می‌سازد","Layer 2–4","Ethernet / IPv4 / TCP","00:11:22:33:44:55","00:aa:bb:cc:dd:01","192.168.10.25","203.0.113.20","52144","443","64","SYN, Seq=1000","IPv4 + TCP checksum","TCP options: MSS/SACK/Window Scale","MAC مقصد همان gateway است اما IP مقصد سرور نهایی است. پورت مبدأ ephemeral است؛ TTL=64 فقط مقدار نمونه است."),
        Step("۴. سوئیچ لایه ۲","Layer 2","Ethernet switching","00:11:22:33:44:55","00:aa:bb:cc:dd:01","192.168.10.25","203.0.113.20","52144","443","بدون تغییر","SYN","در سوئیچ عادی بدون تغییر","VLAN 10; FCS روی خروجی جدید می‌شود","سوئیچ براساس VLAN و MAC table فریم را forward می‌کند. معمولاً IP مقصد را route نمی‌کند و TTL را کم نمی‌کند."),
        Step("۵. Router: Route + TTL","Layer 2–3","IPv4 forwarding","00:bb:bb:bb:00:01","00:cc:cc:cc:00:01","192.168.10.25","203.0.113.20","52144","443","63","SYN","IPv4 header checksum به‌روز می‌شود","Ethernet header از نو نوشته می‌شود","روتر route و next-hop را انتخاب می‌کند، TTL را کاهش می‌دهد و یک فریم L2 جدید می‌سازد. بدون NAT، IP/port معمولاً ثابت می‌مانند."),
        Step("۶. Edge NAT/PAT","Layer 3–4","IPv4 + TCP SNAT/PAT","00:dd:dd:dd:00:01","00:ee:ee:ee:00:01","198.51.100.10","203.0.113.20","62001 (ترجمه‌شده)","443","62 (مثال)","SYN","IPv4 و TCP checksum اصلاح می‌شود","Conntrack: 192.168.10.25:52144 ↔ 198.51.100.10:62001","در PAT، IP/port مبدأ خصوصی به IP عمومی و پورت ترجمه‌شده نگاشت می‌شود؛ جدول state امکان ترجمه معکوس را نگه می‌دارد."),
        Step("۷. روترهای ISP","Layer 3","IPv4 forwarding","MAC لینک فعلی","MAC next-hop بعدی","198.51.100.10","203.0.113.20","62001","443","در هر روتر کم می‌شود","SYN","با تغییر IPv4 header به‌روز می‌شود","Ethernet header در هر لینک عوض می‌شود","MAC فریم Ethernet در هر لینک محلی است؛ end-to-end نمی‌ماند. TTL در هر روتر کاهش می‌یابد؛ IP ممکن است با NAT/middlebox تغییر کند."),
        Step("۸. پاسخ سرور SYN-ACK","Layer 2–4","TCP SYN-ACK","MAC سرور/شبکه مقصد","MAC دروازه مقصد","203.0.113.20","198.51.100.10","443","62001","بسته به OS/hops","SYN, ACK; Ack=1001","IPv4 + TCP checksum","TCP options negotiated","اگر سرویس روی TCP/443 گوش بدهد، SYN-ACK برمی‌گرداند. مسیر برگشت می‌تواند با مسیر رفت متفاوت باشد."),
        Step("۹. NAT معکوس به LAN","Layer 3–4","Reverse translation","00:aa:aa:aa:00:01","00:11:22:33:44:55","203.0.113.20","192.168.10.25","443","52144 (برگردانده شد)","کاهش‌یافته","SYN-ACK","IP/TCP checksum پس از NAT اصلاح می‌شود","Conntrack lookup به original tuple","جدول state مقصد عمومی و پورت ترجمه‌شده را دوباره به IP خصوصی و پورت اصلی برمی‌گرداند؛ روتر Ethernet header جدید می‌سازد."),
        Step("۱۰. TCP برقرار و TLS شروع می‌شود","Layer 4 / 7","ACK → TLS ClientHello","00:11:22:33:44:55","00:aa:bb:cc:dd:01","192.168.10.25","203.0.113.20","52144","443","64 (بسته جدید)","ACK سپس TLS ClientHello","checksum برای هر segment جدا","SNI=portal.example.test; TLS cipher negotiation","بعد از SYN → SYN-ACK → ACK اتصال TCP برقرار می‌شود. محتوای HTTP در TLS موفق، در pcap عادی به‌صورت رکورد رمز‌شده دیده می‌شود.")
    )
    private lateinit var body: LinearLayout
    private lateinit var header: TextView
    private var current = 0

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            layoutDirection = View.LAYOUT_DIRECTION_RTL
            setPadding(18, 18, 18, 18)
            setBackgroundColor(Color.rgb(15, 20, 30))
        }
        root.addView(TextView(this).apply {
            text = "آزمایشگاه مسیر پکت · تاریخ شمسی ${JalaliDate.today()}"
            textSize = 19f
            setTextColor(Color.WHITE)
            typeface = Ui.persianTypeface()
        })
        root.addView(TextView(this).apply {
            text = "شبیه‌سازی آموزشی با مقادیر نمونه — این صفحه capture زنده از NIC نیست."
            textSize = 12f
            setTextColor(Color.LTGRAY)
            setPadding(0, 8, 0, 12)
        })
        val stepsRow = LinearLayout(this).apply { orientation = LinearLayout.HORIZONTAL; layoutDirection = View.LAYOUT_DIRECTION_RTL }
        steps.forEachIndexed { index, _ ->
            stepsRow.addView(Button(this).apply {
                text = (index + 1).toString()
                textSize = 11f
                setOnClickListener { current = index; render() }
            }, LinearLayout.LayoutParams((44 * resources.displayMetrics.density).toInt(), LinearLayout.LayoutParams.WRAP_CONTENT).apply { setMargins(2, 2, 2, 2) })
        }
        root.addView(ScrollView(this).apply { isHorizontalScrollBarEnabled = false; addView(stepsRow) },
            LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT))
        header = TextView(this).apply {
            textSize = 18f
            setTextColor(Color.rgb(147, 197, 253))
            setPadding(0, 12, 0, 8)
            typeface = Ui.persianTypeface()
        }
        root.addView(header)
        body = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL; setPadding(14, 14, 14, 14); setBackgroundColor(Color.rgb(26, 35, 50)) }
        root.addView(ScrollView(this).apply { addView(body) },
            LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, 0, 1f))
        val controls = LinearLayout(this).apply { orientation = LinearLayout.HORIZONTAL; layoutDirection = View.LAYOUT_DIRECTION_RTL }
        controls.addView(Button(this).apply { text = "قبلی"; setOnClickListener { current = (current - 1).coerceAtLeast(0); render() } },
            LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f))
        controls.addView(Button(this).apply { text = "بازنشانی"; setOnClickListener { current = 0; render() } },
            LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f))
        controls.addView(Button(this).apply { text = "بعدی"; setOnClickListener { current = (current + 1).coerceAtMost(steps.lastIndex); render() } },
            LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f))
        root.addView(controls)
        setContentView(root)
        render()
    }

    private fun render() {
        val s = steps[current]
        header.text = "${s.title} · ${current + 1}/${steps.size}"
        body.removeAllViews()
        val fields = listOf(
            "لایه" to s.layer, "پروتکل" to s.protocol, "MAC مبدأ" to s.srcMac,
            "MAC مقصد" to s.dstMac, "IP مبدأ" to s.srcIp, "IP مقصد" to s.dstIp,
            "پورت مبدأ" to s.srcPort, "پورت مقصد" to s.dstPort, "TTL" to s.ttl,
            "Flags" to s.flags, "Checksum" to s.checksum, "Payload/Options" to s.payload
        )
        fields.forEach { (name, value) ->
            body.addView(TextView(this).apply {
                text = "$name: $value"; textSize = 13f; setTextColor(Color.WHITE)
                typeface = Ui.persianTypeface(); setPadding(6, 6, 6, 6); setTextIsSelectable(true)
            })
        }
        body.addView(TextView(this).apply {
            text = "تحلیل این مرحله\n${s.analysis}"
            textSize = 14f; setTextColor(Color.rgb(187, 247, 208)); typeface = Ui.persianTypeface()
            setPadding(6, 18, 6, 12); setLineSpacing(0f, 1.2f)
        })
        body.addView(TextView(this).apply {
            text = "نکته: آدرس‌های 203.0.113.0/24 و 198.51.100.0/24 برای مستندسازی رزرو شده‌اند. برای تحلیل واقعی باید pcap خود شبکه را در Wireshark بررسی کنید."
            textSize = 11f; setTextColor(Color.LTGRAY); typeface = Ui.persianTypeface(); setPadding(6, 10, 6, 10)
        })
    }
}
