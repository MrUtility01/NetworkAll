# وضعیت ادغام بسته‌های غنی‌سازی

## فایل‌های داخل `tools/chapters/New/`

| ZIP | فصل مقصد |
|-----|----------|
| ch22_wifi_enrichment.zip | 22 |
| ch23_ptp_ptmp_enrichment.zip | 23 |
| ch24_fortigate_enrichment.zip | 24 |
| ch32_endpoint_sec_enrichment.zip | 32 |
| ch33_entra_hybrid_enrichment.zip | 33 |
| ch52_dba_10x.zip | 52 |
| ch60_67_enrichment_all*.zip | 60–67 |
| ch69_70_all.zip | 69–70 |
| ch71_ai_leadership_it.zip | 71 (اگر آپلود شده باشد) |

## یک دستور ادغام

از ریشهٔ مخزن:

```bash
bash tools/chapters/New/INTEGRATE.sh
git add tools/chapters/
git status
git commit -m "content: integrate enrichment packs from tools/chapters/New"
git push origin main
```

## شمارش پس از استخراج (اعتبارسنجی محلی)

| فصل | lessons | questions |
|-----|---------|-----------|
| 22 | 175 | 450 |
| 23 | 231 | 450 |
| 24 | 138 | 450 |
| 32 | 198 | 400 |
| 33 | 242 | 400 |
| 52 | 254 | 520 |
| 60–67 | 44–88 | 400 |
| 69 | 792 | 2000 |
| 70 | 740 | 2500 |
| 71 | 1205 | 2000 |

`INTEGRATE.sh` روی مخزن قرار گرفت. فصل‌های ۶۹–۷۱ پوشهٔ کامل جدید می‌سازند.
