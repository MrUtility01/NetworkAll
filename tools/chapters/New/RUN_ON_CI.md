# ادغام خودکار

اگر Actions یا ماشین دیگری به مخزن دسترسی دارد:

```bash
bash tools/chapters/New/INTEGRATE.sh
git config user.email "bot@networkall.local"
git config user.name "NetworkAll Bot"
git add tools/chapters/
git commit -m "content: integrate enrichment from New/" || true
git push origin main
```

فایل‌های ZIP از قبل در New/ هستند؛ INTEGRATE.sh آن‌ها را در پوشهٔ هر فصل می‌ریزد.
