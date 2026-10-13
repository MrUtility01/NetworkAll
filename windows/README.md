# NetworkAll — Windows Host

## اجرا
```bat
start.bat
```

- سرور روی پورت **86**
- توکن پیش‌فرض: **09136555866** (متغیر `NETENC_TOKEN`)
- اندروید روی همان Wi‑Fi با همین توکن همگام می‌شود

## تغییر توکن
```bat
set NETENC_TOKEN=رمز_دلخواه
start.bat
```

## نیازمندی
Python 3.10+ و دسترسی به `pip`

مرورگر: http://127.0.0.1:86

## Windows Firewall (فقط یک‌بار، با دسترسی Administrator)

برای اجازهٔ اتصال گوشی از شبکهٔ محلی به وب‌سرور NetworkAll روی TCP/86:

```bat
netsh advfirewall firewall add rule name="NetworkAll Web TCP 86" dir=in action=allow protocol=TCP localport=86
```

آدرس در گوشی: `http://IP-کامپیوتر:86`. کامپیوتر و گوشی باید روی شبکه‌ای باشند که ارتباط بین دستگاه‌ها را مسدود نکرده باشد.
