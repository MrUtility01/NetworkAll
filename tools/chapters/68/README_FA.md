# فصل ۶۸: دانشنامه جامع دستورات و عملیات سیستم

این فصل، مرجع عملیاتی چندسکویی برای مدیریت شبکه و سیستم‌عامل است.

## دانشنامه enrichment (جدید)

- **فایل ZIP:** `ch68_all_domains.zip`
- **مسیر استخراج:** `commands/sources/encyclopedia/`
- **اسکریپت:** `commands/sources/encyclopedia/EXTRACT.sh`

```bash
cd tools/chapters/68
bash commands/sources/encyclopedia/EXTRACT.sh
# یا:
unzip -o ch68_all_domains.zip
mkdir -p commands/sources/encyclopedia
cp -r ch68_commands_encyclopedia/* commands/sources/encyclopedia/
# پاک‌سازی مسیر تو در توی اشتباه:
rm -rf commands/sources/tools
```

| حوزه | تعداد |
|------|--------|
| Linux | 500 |
| Windows PowerShell | 500 |
| Windows Batch/CMD | 500 |
| Cisco IOS-XE | 500 |
| MikroTik | 500 |
| FortiGate | 500 |
| Docker | 300 |
| Windows Server/AD | 300 |
| **جمع دستورات SCHEMA** | **3600** |
| آزمون کاربرد دستور | **1120** |

هر رکورد شامل: vendor، category، when_to_use_fa، flashcards، assessment (دستور→کاربرد).

## محتوای canonical قبلی

- `lessons/base_curriculum.json`: ۱۴ مسیر/درس پایه
- `lessons/lessons.json`: محتوای افزودهٔ قبلی
- `commands/commands.json`: ۳٬۰۴۶ رکورد موجود (حفظ شود؛ overwrite نشود)
- `examples/examples.json`: ۳٬۰۴۶ رکورد
- `questions/questions.json` / `answers/answer_key.json`: ۵۱ سؤال/پاسخ قبلی
- `labs/labs.json`: ۱۸ لاب

## ایمنی

- فقط Lab / با مجوز
- secret در لاگ ذخیره نشود
- فایروال را سراسری خاموش نکنید

## سازگاری

`build/chapter.json` را دستی ویرایش نکنید. `manifest.json` شمارش encyclopedia را دارد. status enrichment: review_required
