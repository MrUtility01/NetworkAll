# پروتکل همگام‌سازی NetworkAll v1

## قرارداد API

| عملیات | روش و مسیر | شرح |
|---|---|---|
| Hello | `GET /api/sync/hello` | وضعیت و نسخهٔ schema |
| Manifest | `GET /api/sync/manifest?since=<iso>` | UIDها و زمان تغییر |
| Pull | `POST /api/sync/pull` | بدنهٔ `{"uids":[]}` |
| Push | `POST /api/sync/push` | بدنهٔ `{"records":[]}` |
| Health | `GET /api/health` | وضعیت کلی API |

## اتصال شبکه

پورت ثابت برنامه TCP/86 است:

- همان کامپیوتر: `http://127.0.0.1:86`
- Android در شبکهٔ محلی: `http://<IP-کامپیوتر>:86`

برای اجرای دستی، سرور به‌صورت امن روی loopback شروع می‌شود. Windows launcher از `NETENC_HOST=0.0.0.0` برای LAN استفاده می‌کند؛ Firewall را فقط روی شبکهٔ خصوصی و در حد لازم باز کنید. برنامه برای اینترنت عمومی طراحی نشده است.

## احراز هویت

توکن از یکی از این منابع پذیرفته می‌شود:

```text
Authorization: Bearer <NETENC_TOKEN>
X-NetEnc-Token: <NETENC_TOKEN>
Cookie: netenc_token=<NETENC_TOKEN>
```

توکن نباید در query string URL قرار گیرد؛ URLها ممکن است در history و log ذخیره شوند.

اگر `NETENC_TOKEN` از محیط تنظیم نشود، سرور یک توکن تصادفی برای همان نصب تولید و آن را در `server/data/networkall.token` ذخیره می‌کند. رابط وب با رمز محلی و Session مستقل باز می‌شود؛ Session فقط در مرورگر احراز هویت‌شده به endpointهای آموزشی وب اجازه می‌دهد. Android و کلاینت‌های دیگر هنوز باید توکن Sync را ارسال کنند. توکن را در Android Settings وارد کنید و به‌صورت عمومی منتشر نکنید. اگر مسیر اجرا با متغیر محیطی باشد، مقدار `NETENC_TOKEN` جایگزین فایل محلی می‌شود.

## تعارض

قانون فعلی Last-Write-Wins بر پایهٔ `last_updated` و `content_hash` است. Timestamp به‌تنهایی برای همهٔ موارد همزمان کافی نیست؛ همگام‌سازی دادهٔ مهم باید با بررسی تعارض و بازبینی رکورد پشتیبانی شود.

## محدودیت‌های پذیرفته‌شده در v1

وجود endpointها تضمین‌کنندهٔ Sync واقعی همهٔ Entityها نیست. تا زمانی که create/update/delete/tombstone برای Tasks، Notes و Study Progress، retry/chunking، قطع شبکه، تعارض هم‌زمان و restore تست نشده، این بخش را «آزمایشی» فرض کنید. Vault/رمزهای شخصی نباید از طریق Sync عمومی منتقل شوند مگر سازوکار کلید و بازیابی مستقل تعریف شود.

`schema_version: 1`
