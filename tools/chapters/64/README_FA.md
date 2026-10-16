# فصل ۶۴: Git و GitHub

این فصل با حفظ ۳۰۰ عنوان پایه، از مبانی Git تا workflow تیمی، GitHub، امنیت، CI/CD و مدیریت release غنی‌سازی شده است.

## منابع مرجع

- `lessons/base_curriculum.json`: منبع اصلی ۳۰۰ درس در ۸ بخش و سطوح L0 تا L4.
- `lessons/lessons.json`: محتوای تکمیلی هم‌عنوان با درس‌های پایه؛ شامل مفهوم، کاربرد واقعی، فرمان‌ها، روال اجرا، ریسک‌ها، تمرین و معیار پذیرش. این فایل عنوان‌های پایه را حذف یا جایگزین نمی‌کند.
- `commands/commands.json`: مجموعه فرمان‌های مرتبط با ۶۰ موضوع Git/GitHub.
- `examples/examples.json`: مثال‌های سناریومحور برای ۶۰ موضوع.
- `questions/questions.json`: بانک سؤال چندگزینه‌ای با پاسخ‌نامه مستقل.
- `answers/answer_key.json`: پاسخ‌های تشریحی با UID متناظر.
- `labs/labs.json`: لابراتوارهای گام‌به‌گام با شواهد و معیار ارزیابی.
- `manifest.json`: شمار رکوردها و وضعیت بازبینی.

## سرفصل‌های اصلی

مبانی و نصب؛ Working Tree و Index؛ staging و commit؛ branch و merge؛ conflict resolution؛ reset/revert/restore؛ remote و fetch/pull/push؛ GitHub fork و Pull Request؛ tag و release؛ rebase و cherry-pick؛ .gitignore و مدیریت secret؛ GitHub Actions و CI؛ Git LFS؛ backup و mirror؛ عیب‌یابی و پروژه نهایی.

## نکات اجرایی و ایمنی

- تمرین‌های تغییر تاریخچه را در مخزن disposable اجرا کنید.
- پیش از push، مقصد remote، visibility مخزن و محتوای staged را بازبینی کنید.
- فایل‌های secret را وارد Git نکنید. اگر secret منتشر شد، آن را افشاشده فرض کنید و فوراً rotate/revoke کنید؛ حذف فایل در commit بعدی تاریخچه را پاک نمی‌کند.
- `build/chapter.json` خروجی تولیدشده است؛ آن را دستی ویرایش نکنید.
- وضعیت نهایی هنوز `review_required` است تا اعتبارسنجی خودکار مخزن و Build واقعی Android/Windows اجرا شود.
