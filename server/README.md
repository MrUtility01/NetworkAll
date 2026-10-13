# NetworkAll v1.0.0 — Windows Web/API Host

Flask + SQLite، رابط وب فارسی راست‌چین و API همگام‌سازی روی TCP/86.

## اجرا

از بستهٔ Windows:
```bat
windows\start.bat
```

یا با Python 3.11+ و محیط مجازی فعال:
```bat
cd server
python -m pip install -r requirements.txt
python app.py
```

اجرای مستقیم سرور به‌صورت پیش‌فرض روی `127.0.0.1:86` گوش می‌دهد. برای اتصال LAN باید `NETENC_HOST=0.0.0.0` و یک قانون Firewall محدود به شبکهٔ خصوصی تنظیم شود.

## APIهای اصلی

- `GET /api/stats`
- `GET /api/chapters`
- `GET /api/chapters/<id>/levels`
- `GET /api/levels/<id>/lessons`
- `GET /api/lessons/<id>`
- `GET /api/scenarios` / `GET /api/scenarios/<id>`
- `GET /api/search?q=...`
- `GET /diagrams` — گالری دیاگرام‌های SVG
- `GET /api/sync/hello`
- `GET /api/sync/manifest`
- `POST /api/sync/pull`
- `POST /api/sync/push`

## رابط وب و احراز هویت

رابط مرورگر با رمز محلی ویندوز باز می‌شود؛ پس از ورود، Session برای APIهای آموزشی مرورگر پذیرفته می‌شود. کلاینت‌های غیرمرورگری مثل Android همچنان باید توکن Sync را بفرستند. Endpointهای destructive برای بازسازی دیتابیس در UI عمومی قرار ندارند.

## Seed و محتوا

بستهٔ Windows v1 از `android/app/src/main/assets/curriculum_index.json.gz` استفاده می‌کند، به شرط آنکه Asset از Workflow validate‌شده تهیه شده باشد. اگر این Asset وجود نداشته یا نامعتبر باشد، مسیر legacy fallback ممکن است فقط ساختار کم‌عمق‌تری ایجاد کند. برای توزیع، ZIP خروجی Workflow را استفاده کنید.

داشتن ۶۸ ردیف فصل به معنای عمیق و بازبینی‌شده بودن تمام درس‌ها نیست. وضعیت و شکاف‌ها در `docs/APP_STATUS_FA.md` و `docs/V1_RELEASE_AUDIT_FA.md` ثبت شده‌اند.
