# NetworkEncyclopedia / ENGINEER JOKAR

دانشنامه آموزشی شبکه و زیرساخت IT — ویندوز (Flask) + اندروید (Kotlin) + همگام‌سازی LAN.

## شروع سریع

**ویندوز**
```bash
git clone https://github.com/MrUtility01/NetworkEncyclopedia.git
cd NetworkEncyclopedia/server
python -m pip install -r requirements.txt
set NETENC_TOKEN=change-me
python app.py
```

**اندروید:** Actions → Build Android APK → نصب → در صورت نیاز Clear data.

## ساختار

جزئیات کامل: [docs/REPO_LAYOUT_FA.md](docs/REPO_LAYOUT_FA.md)

| مسیر | نقش |
|------|-----|
| `server/` | API + SQLite + وب |
| `android/` | اپ آفلاین |
| `tools/packs/` | JSON محتوای نهایی |
| `scripts/merge_content_packs_into_android.py` | ادغام پک‌ها در asset |
| `docs/` | معماری، Sync، وضعیت |

## محتوای جدید

1. JSON را در `tools/packs/<موضوع>/` بگذار  
2. `python scripts/merge_content_packs_into_android.py`  
3. commit + push + Actions  

## امنیت

توکن پیش‌فرض را عوض کن: `NETENC_TOKEN`. مستند Sync: `docs/SYNC_PROTOCOL.md`.
