# NetworkAll v1.0.0 — Windows Host

## نیازمندی و اجرا

- Python 3.11+ و دسترسی شبکه برای نصب وابستگی‌های اولیه
- استخراج کامل بسته به پوشهٔ قابل‌نوشتن
- اجرا: `windows\start.bat`

Launcher یک `.venv` خصوصی در ریشه می‌سازد، وابستگی‌ها را نصب می‌کند و وب/API را روی TCP/86 بالا می‌آورد.

- مرورگر محلی: `http://127.0.0.1:86`\n- در اولین بازدید، یک رمز ورود محلی با حداقل ۸ نویسه تنظیم کنید؛ برای یکسان بودن تجربه می‌توانید همان رمزی را انتخاب کنید که در Android تنظیم می‌کنید.
- آدرس گوشی: `http://IP-کامپیوتر:86`

## توکن Sync

برای هر نصب یک توکن تصادفی در `server\data\networkall.token` ساخته می‌شود. این مقدار را در Android → Settings → API token وارد کنید. توکن واقعی را در Git یا مستندات عمومی commit نکنید.

برای اجرای مستقیم `python server\app.py`، سرور به‌صورت پیش‌فرض فقط روی loopback گوش می‌دهد. Launcher ویندوز برای اتصال LAN، `NETENC_HOST=0.0.0.0` را تنظیم می‌کند.

## Windows Firewall

فقط در شبکهٔ خصوصی مورداعتماد، پنجرهٔ CMD را با دسترسی Administrator باز کنید و قانون TCP/86 را اضافه کنید:

```bat
netsh advfirewall firewall add rule name="NetworkAll Web TCP 86" dir=in action=allow protocol=TCP localport=86 profile=private
```

این برنامه برای expose شدن مستقیم به اینترنت عمومی طراحی نشده است.

## داده‌ها و نسخهٔ قبلی

فایل `server\data\encyclopedia.db` حاوی دادهٔ محلی است. پیش از Reset/Clear data یا جایگزینی دستی دیتابیس، نسخهٔ پشتیبان بگیرید. بستهٔ Windows v1 دیتابیس شخصی همراه ندارد و در نصب تازه، فهرست آموزشی مشترک با اندروید را Seed می‌کند. این خروجی یک ZIP از سورس/میزبان Python است، نه EXE مستقل.
