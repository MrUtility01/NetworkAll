package com.netenc.app

import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.graphics.Color
import android.os.Bundle
import android.view.Gravity
import android.view.View
import android.widget.AdapterView
import android.widget.ArrayAdapter
import android.widget.Button
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.Spinner
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity

private data class PacketStage(
    val title: String, val point: String, val mac: String, val vlan: String,
    val ip: String, val tcp: String, val change: String,
    val expected: String, val absent: String, val filter: String
)
private data class PacketScenario(val name: String, val stages: List<PacketStage>)

class PacketLabActivity : AppCompatActivity() {
    private lateinit var picker: Spinner
    private lateinit var count: TextView
    private lateinit var headline: TextView
    private lateinit var location: TextView
    private lateinit var mac: TextView
    private lateinit var vlan: TextView
    private lateinit var ip: TextView
    private lateinit var tcp: TextView
    private lateinit var change: TextView
    private lateinit var expected: TextView
    private lateinit var absent: TextView
    private lateinit var filter: TextView
    private lateinit var previous: Button
    private lateinit var next: Button
    private var scenarioIndex = 0
    private var stageIndex = 0

    private fun st(t: String, p: String, m: String, v: String, i: String, tp: String,
                   c: String, e: String, a: String, f: String) =
        PacketStage(t, p, m, v, i, tp, c, e, a, f)

    private val cases by lazy { listOf(
        PacketScenario("TCP اینترنت + NAT", listOf(
            st("۱/۶ · ARP Request", "کارت شبکه کلاینت، پیش از TCP", "client-MAC → FF:FF:FF:FF:FF:FF", "Access VLAN10؛ فریم untagged", "ARP: who has 192.168.10.1?؛ IP header وجود ندارد", "TCP header وجود ندارد", "چون مقصد 203.0.113.80 خارج subnet است، کلاینت ابتدا MAC دروازه را می‌یابد. هنوز SYN نفرستاده.", "ARP Reply از Gateway در همان VLAN دیده می‌شود.", "VLAN، SVI/Gateway، duplicate IP و خطای لایه۲ را بررسی کن.", "arp"),
            st("۲/۶ · ARP Reply", "کارت شبکه کلاینت؛ neighbor cache", "Gateway-MAC → client-MAC", "VLAN10؛ access بدون tag", "192.168.10.1 is-at Gateway-MAC", "TCP وجود ندارد؛ فقط ARP", "IP دروازه به MAC محلی نگاشت می‌شود. MAC سرور اینترنت روی LAN وجود ندارد.", "arp -a نگاشت Gateway به MAC درست را نشان می‌دهد.", "MAC ناپایدار: duplicate gateway/IP یا loop را بررسی کن.", "arp.src.proto_ipv4==192.168.10.1"),
            st("۳/۶ · TCP SYN در LAN", "SPAN پورت کلاینت / ingress LAN روتر، قبل NAT", "client-MAC → gateway-LAN-MAC", "VLAN10؛ access untagged", "192.168.10.25 → 203.0.113.80 · TTL=64", "51514 → 443 · SYN=1 ACK=0 · Seq=1000", "مقصد IP سرور عمومی است ولی مقصد Ethernet، MAC دروازه است. سوئیچ L2 IP/TTL را تغییر نمی‌دهد.", "SYN با tuple دقیق روی ingress روتر دیده می‌شود.", "اگر SYN نیست، NIC، access VLAN، ACL یا مسیر قبل روتر را بررسی کن.", "ip.src==192.168.10.25 && tcp.flags.syn==1"),
            st("۴/۶ · Route و Source NAT", "خروجی WAN روتر؛ مقایسه با capture LAN", "gateway-WAN-MAC → ISP-next-hop-MAC", "tag وابسته به لینک WAN است", "198.51.100.10 → 203.0.113.80 · TTL=63", "62001 → 443 · SYN=1؛ source port ترجمه می‌شود", "روتر TTL را از 64 به 63 کم و MACهای لینک WAN را بازسازی می‌کند؛ مبدأ خصوصی/پورت 51514 به آدرس عمومی/پورت 62001 تبدیل و checksumها اصلاح می‌شوند.", "WAN capture مبدأ عمومی :62001 و LAN capture مبدأ خصوصی :51514 را نشان می‌دهد.", "اگر SYN در LAN هست اما WAN نیست: route، policy، NAT counter و conntrack را بررسی کن.", "ip.src==198.51.100.10 && tcp.flags.syn==1"),
            st("۵/۶ · SYN-ACK و Reverse NAT", "ورودی WAN سپس خروجی LAN", "WAN: ISP-MAC → gateway-WAN-MAC; LAN: gateway-LAN-MAC → client-MAC", "در LAN به VLAN10 بازمی‌گردد", "WAN: 203.0.113.80 → 198.51.100.10؛ سپس مقصد 192.168.10.25 می‌شود", "443 → 62001؛ پس از de-NAT مقصد port=51514", "Connection tracking نگاشت را پیدا می‌کند و مقصد عمومی/پورت را به IP/پورت خصوصی برمی‌گرداند.", "همان flow در WAN و نسخه de-NAT شده در LAN دیده می‌شود.", "اگر پاسخ در WAN هست ولی LAN نیست: conntrack، policy برگشت و ARP داخلی را بررسی کن.", "tcp.flags.syn==1 && tcp.flags.ack==1"),
            st("۶/۶ · ACK و آغاز TLS", "Capture دو سمت روتر؛ ابتدا TCP سپس TLS", "MAC هر hop متناسب با همان لینک عوض می‌شود", "tag تابع VLAN هر لینک است", "LAN source خصوصی؛ WAN source عمومی NAT شده", "SYN → SYN-ACK → ACK؛ سپس TLS ClientHello", "ACK سوم TCP را کامل می‌کند. Established به تنهایی سلامت HTTPS را ثابت نمی‌کند؛ TLS و HTTP نیز باید Verify شوند.", "SYN/SYN-ACK/ACK و بعد ClientHello/ServerHello دیده می‌شود.", "اگر TCP کامل است ولی HTTPS خراب، SNI، certificate، MTU یا backend را بررسی کن.", "tcp.stream eq 0 || tls.handshake")
        )),
        PacketScenario("VLAN30 حذف‌شده از Trunk", listOf(
            st("۱/۵ · Access ingress", "SPAN پورت Gi1/0/17", "client-MAC → gateway-MAC", "Access frame بدون tag؛ سوئیچ آن را VLAN30 می‌داند", "10.30.30.47 → 10.30.30.1 · TTL=64", "ICMP Echo Request؛ ping دارای TCP نیست", "فریم وارد VLAN30 می‌شود و باید از trunk مجاز عبور کند.", "Capture ورودی access فریم ARP/ICMP را می‌بیند.", "NIC، کابل، access VLAN و host firewall را بررسی کن.", "arp || icmp"),
            st("۲/۵ · Allowed-list", "سوئیچ قبل خروجی trunk Gi1/0/48", "Destination MAC در MAC table lookup می‌شود", "VLAN30 مجاز نیست؛ VLAN10/20 مجازند", "IP و TTL در سوئیچ لایه۲ تغییر نمی‌کنند", "TCP header توسط L2 switch دستکاری نمی‌شود", "سوئیچ فریم VLAN30 را پیش از خروجی drop می‌کند؛ پس روی trunk فریم tagged VLAN30 دیده نمی‌شود.", "show interfaces trunk نبود VLAN30 در allowed-list را نشان می‌دهد.", "اگر VLAN30 مجاز است، STP، VLAN active و EtherChannel را بررسی کن.", "vlan.id==30 && (arp || icmp)"),
            st("۳/۵ · اثبات نقطه Drop", "Capture هم‌زمان Access ingress و Trunk egress", "Ingress: frame حاضر؛ egress: frame غایب", "باید 802.1Q VLAN ID=30 دیده شود، اما نیست", "Echo Request به Gateway در ingress هست؛ در egress نیست", "در ping، TCP header ندارد", "Timestamp مشترک و allowed-list شاهد مستقل محل توقف packet را محدود می‌کنند.", "فریم در ingress دیده و در egress غایب است.", "SPAN source/destination، فیلتر و ساعت دو capture را بررسی کن.", "vlan.id==30 && (arp || icmp)"),
            st("۴/۵ · اصلاح حداقلی", "SW-CORE؛ Change مجاز و baseline ذخیره‌شده", "MACهای endpoint تغییر نمی‌کنند", "فقط VLAN30 به allow-list فعلی اضافه می‌شود", "IP و TTL در L2 switch ثابت", "Transport header ثابت", "در IOS-XE از switchport trunk allowed vlan add 30 استفاده کن؛ این دستور VLANهای قبلی را حذف نمی‌کند.", "VLAN30 allowed/active و STP forwarding است.", "اگر frame عبور کرد اما Gateway پاسخ نداد، SVI/ARP/ACL را بررسی کن.", "vlan.id==30 && icmp"),
            st("۵/۵ · Verify", "Client، trunk دو طرف، Gateway و برنامه", "MAC در VLAN30 درست یاد گرفته شده", "VLAN30 دو سر trunk در حالت forwarding", "ARP و ICMP به Gateway موفق است", "TCP port-test جداگانه", "قبولی یعنی dataplane واقعی کار کند و VLANهای قبلی نیز سالم بمانند.", "ping Gateway و تست سرویس موفق‌اند.", "در مشکل یک‌طرفه، capture برگشت و MAC/ARP سمت مقابل را بگیر.", "vlan.id==30 && (arp || icmp)")
        )),
        PacketScenario("Drop شدن SYN در فایروال", listOf(
            st("۱/۴ · SYN به فایروال می‌رسد", "Client 10.20.30.45:51000 → Server 10.50.1.20:443", "client-MAC → firewall-LAN-MAC", "VLAN کاربر طبق طراحی", "10.20.30.45 → 10.50.1.20 · TTL=64", "51000 → 443 · SYN=1 ACK=0", "tuple و timestamp را ثبت کن؛ هنوز پاسخ نیامده است.", "SYN روی ingress capture دیده می‌شود.", "مسیر قبل firewall، VLAN، ACL و نقطه capture را بررسی کن.", "ip.src==10.20.30.45 && tcp.flags.syn==1"),
            st("۲/۴ · Route lookup", "Firewall؛ پیش از policy decision", "egress MAC هنوز ساخته نشده؛ next-hop باید resolve شود", "Egress باید سمت LAN server باشد", "10.20.30.45 → 10.50.1.20", "TCP handshake کامل نیست", "Routing محل خروج را تعیین می‌کند؛ route اشتباه را با policy deny یکی ندان.", "Route lookup خروجی و next-hop مورد انتظار را نشان می‌دهد.", "اگر route/VRF/SD-WAN اشتباه است اول همان را بررسی کن.", "ip.addr==10.50.1.20 && tcp.flags.syn==1"),
            st("۳/۴ · Policy Drop", "Ingress packet هست؛ egress سمت سرور غایب", "Frame خروجی ساخته یا ارسال نشده", "Drop قبل از egress", "IPهای اصلی در ingress مشاهده می‌شوند", "SYN هست؛ SYN-ACK نیست", "Policy no-match یا deny بسته را drop می‌کند؛ این به معنی down بودن سرور نیست.", "Deny log/counter بالا می‌رود و SYN در egress غایب است.", "اگر deny log نیست، local-in/forward plane، capture filter و offload counter را بررسی کن.", "tcp.flags.syn==1 && tcp.dstport==443"),
            st("۴/۴ · اصلاح و Verify", "Policy محدود؛ سپس capture دو جهت", "MAC next-hop مطابق egress صحیح", "VLAN مسیر طبق طراحی", "IP ثابت مگر NAT جداگانه وجود داشته باشد", "SYN → SYN-ACK → ACK؛ سپس TLS", "فقط source subnet، destination و service موردنیاز را Allow کن؛ any-any نساز.", "TCP handshake و تست HTTPS/service موفق‌اند.", "اگر SYN خارج می‌شود ولی پاسخ نیست، return route، listener و upstream را بررسی کن.", "tcp.stream eq 0 || tcp.flags.reset==1")
        )),
        PacketScenario("MTU و PMTUD در تونل", listOf(
            st("۱/۴ · پینگ کوچک موفق", "Client → VPN tunnel → 10.80.1.20", "MAC لایه۲ محلی", "VLAN سالم", "Packet کوچک؛ DF ممکن است فعال باشد", "TCP handshake ممکن است موفق باشد", "پینگ کوچک MTU کل مسیر را ثابت نمی‌کند؛ payload را با DF مرحله‌ای افزایش بده.", "تست کوچک موفق و DF probe بزرگ‌تر ممکن است fail شود.", "اگر SYN هم نمی‌رسد اول route/policy را بررسی کن.", "icmp || tcp.analysis.retransmission"),
            st("۲/۴ · Packet بزرگ‌تر از MTU", "Tunnel egress با MTU مؤثر 1400", "Encapsulation اندازه outer packet را افزایش می‌دهد", "VLAN tag لزوماً علت نیست؛ tunnel overhead مهم است", "IPv4 total length=1500 · DF=1 · MTU=1400", "TCP segment بزرگ‌تر از PMTU", "روتر packet را fragment نمی‌کند و باید drop + ICMP type3/code4 برگرداند.", "ICMP Fragmentation Needed یا drop counter دیده می‌شود.", "اگر ICMP feedback نیست، capture دو سوی تونل و ACL را بررسی کن.", "icmp.type==3 && icmp.code==4"),
            st("۳/۴ · ICMP لازم نمی‌رسد", "Capture کنار source و tunnel edge", "MAC برای هر hop محلی است", "Packet بزرگ داخل tunnel drop می‌شود", "DF packet retransmit می‌شود اما feedback غایب است", "TCP data retransmission؛ SYN قبلاً می‌تواند موفق باشد", "Source از PMTU آگاه نمی‌شود و segment بزرگ را تکرار می‌کند؛ HTTPS ممکن است ظاهراً hang کند.", "Retransmission بالا و ICMP Fragmentation Needed در source غایب است.", "ICMP type/code و ACL counters را بررسی کن؛ همه ICMP را کورکورانه باز نکن.", "tcp.analysis.retransmission || (icmp.type==3 && icmp.code==4)"),
            st("۴/۴ · اصلاح و تست بزرگ", "Path/tunnel اندازه‌گیری‌شده؛ هر دو جهت", "Ethernet MACها در هر hop بازسازی می‌شوند", "MTU overlay/underlay با overhead محاسبه شده", "PMTU اندازه‌گیری‌شده؛ MSS فقط در صورت ضرورت", "Retransmission غیرعادی باید کاهش یابد", "راه اصولی ICMP لازم و MTU سازگار است؛ MSS clamp فقط با علت و تغییر مستند.", "HTTPS/download بزرگ کامل و retransmission نزدیک baseline است.", "اگر یک جهت خراب است، MTU و ICMP برگشت را جدا capture کن.", "tcp.analysis.retransmission || icmp.type==3")
        ))
    ) }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        title = "آزمایشگاه تحلیل پکت"
        val page = ScrollView(this).apply { setBackgroundColor(Color.rgb(245, 247, 251)); isFillViewport = true }
        val root = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL; layoutDirection = View.LAYOUT_DIRECTION_RTL; setPadding(dp(14), dp(12), dp(14), dp(24)) }
        root.addView(label("جریان پکت از Ethernet/VLAN تا IP، TCP و NAT", 20, Color.rgb(22, 55, 99), true))
        root.addView(label("این صفحه جریان آموزشی را بازسازی می‌کند و Capture زنده نیست. فیلترها را روی PCAP مجاز خودت در Wireshark اجرا کن.", 13, Color.rgb(124, 45, 18)))
        picker = Spinner(this)
        picker.adapter = ArrayAdapter(this, android.R.layout.simple_spinner_dropdown_item, cases.map { it.name })
        root.addView(picker, LinearLayout.LayoutParams(-1, dp(52)))
        val controls = LinearLayout(this).apply { orientation = LinearLayout.HORIZONTAL; layoutDirection = View.LAYOUT_DIRECTION_LTR }
        previous = Button(this).apply { text = "◀ مرحله قبل" }
        next = Button(this).apply { text = "مرحله بعد ▶" }
        val reset = Button(this).apply { text = "از اول" }
        controls.addView(previous, LinearLayout.LayoutParams(0, dp(46), 1f))
        controls.addView(next, LinearLayout.LayoutParams(0, dp(46), 1f))
        controls.addView(reset, LinearLayout.LayoutParams(0, dp(46), 1f))
        root.addView(controls)
        count = label("", 12, Color.rgb(29, 78, 216), true); root.addView(count)
        headline = label("", 17, Color.rgb(30, 64, 115), true); root.addView(headline)
        location = label("", 12, Color.rgb(71, 85, 105)); root.addView(location)
        mac = field(root, "Ethernet MAC source/destination")
        vlan = field(root, "802.1Q / VLAN")
        ip = field(root, "ARP / IP / TTL")
        tcp = field(root, "TCP flags / ports / sequence")
        change = card(root, "در این hop چه تغییری رخ می‌دهد؟", Color.rgb(237, 245, 255), Color.rgb(30, 64, 115))
        expected = card(root, "شاهد مورد انتظار", Color.rgb(240, 253, 244), Color.rgb(20, 83, 45))
        absent = card(root, "اگر شاهد حاضر نیست", Color.rgb(255, 247, 237), Color.rgb(124, 45, 18))
        filter = field(root, "Wireshark display filter")
        root.addView(Button(this).apply {
            text = "کپی فیلتر Wireshark"
            setOnClickListener {
                val cb = getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
                cb.setPrimaryClip(ClipData.newPlainText("Wireshark filter", filter.text.toString()))
                Toast.makeText(this@PacketLabActivity, "فیلتر کپی شد", Toast.LENGTH_SHORT).show()
            }
        })
        page.addView(root); setContentView(page)
        picker.onItemSelectedListener = object : AdapterView.OnItemSelectedListener {
            override fun onNothingSelected(parent: AdapterView<*>?) {}
            override fun onItemSelected(parent: AdapterView<*>?, view: View?, position: Int, id: Long) {
                scenarioIndex = position; stageIndex = 0; render()
            }
        }
        previous.setOnClickListener { stageIndex = (stageIndex - 1).coerceAtLeast(0); render() }
        next.setOnClickListener { stageIndex = (stageIndex + 1).coerceAtMost(cases[scenarioIndex].stages.lastIndex); render() }
        reset.setOnClickListener { stageIndex = 0; render() }
        render()
    }

    private fun render() {
        val test = cases[scenarioIndex]
        val step = test.stages[stageIndex]
        count.text = "مرحله " + (stageIndex + 1) + " از " + test.stages.size + " · " + test.name
        headline.text = step.title; location.text = "نقطهٔ مشاهده: " + step.point
        mac.text = step.mac; vlan.text = step.vlan; ip.text = step.ip; tcp.text = step.tcp
        change.text = step.change; expected.text = step.expected; absent.text = step.absent; filter.text = step.filter
        previous.isEnabled = stageIndex > 0
        next.isEnabled = stageIndex < test.stages.lastIndex
    }

    private fun field(root: LinearLayout, heading: String): TextView {
        root.addView(label(heading, 12, Color.rgb(71, 85, 105), true))
        val out = label("", 12, Color.rgb(226, 232, 240)).apply {
            typeface = android.graphics.Typeface.MONOSPACE
            textDirection = View.TEXT_DIRECTION_LTR; gravity = Gravity.START
            setPadding(dp(10), dp(10), dp(10), dp(10)); setBackgroundColor(Color.rgb(15, 23, 42))
        }
        root.addView(out, LinearLayout.LayoutParams(-1, -2).apply { bottomMargin = dp(7) })
        return out
    }

    private fun card(root: LinearLayout, heading: String, bg: Int, fg: Int): TextView {
        root.addView(label(heading, 13, fg, true))
        val out = label("", 13, fg).apply { setPadding(dp(10), dp(9), dp(10), dp(9)); setBackgroundColor(bg) }
        root.addView(out, LinearLayout.LayoutParams(-1, -2).apply { bottomMargin = dp(8) })
        return out
    }

    private fun label(value: String, size: Int, color: Int, bold: Boolean = false) = TextView(this).apply {
        text = value; textSize = size.toFloat(); setTextColor(color)
        gravity = Gravity.START; layoutDirection = View.LAYOUT_DIRECTION_RTL
        if (bold) setTypeface(typeface, android.graphics.Typeface.BOLD)
        setPadding(dp(2), dp(4), dp(2), dp(4))
    }
    private fun dp(n: Int): Int = (n * resources.displayMetrics.density).toInt()
}
