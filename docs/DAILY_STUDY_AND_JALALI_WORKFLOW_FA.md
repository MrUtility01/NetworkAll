# هدف عملکردی: تقویم شمسی، کارها و مطالعه روزانه NetworkAll

وجود Entity/API/Scheduler به‌تنهایی به معنای تکمیل end-to-end نیست.

نیازهای محصول:
- Task با عنوان، شرح، اولویت، موعد، وضعیت، برچسب، تاریخ ایجاد/تکمیل و یادداشت.
- تکرار روزانه/هفتگی/ماهانه، انتخاب روزهای هفته/ماه، پایان تکرار و استثناها.
- نمایش تاریخ شمسی؛ ذخیره canonical به ISO-8601 همراه timezone برای سازگاری Windows و Android.
- یادآوری در هر دو پلتفرم، permission، reboot، Doze/background، خاموشی و اعلان ازدست‌رفته.
- مطالعه 30/60/90 دقیقه‌ای با درس، مثال، لاب، مرور فاصله‌دار و آزمون کوتاه.
- ثبت نمره، زمان، پاسخ کاربر و پیوند به درس؛ answer_key جدا از سؤال.
- گزارش روزانه/هفتگی/ماهانه شامل تکمیل/عقب‌افتادگی، درصد، دقیقه مطالعه، درس‌ها، نمره و روند؛ export CSV/JSON.
- Sync دوطرفه create/update/delete برای Task/Note/Study Progress، tombstone، idempotency و حل تعارض.
- Backup/Restore شامل DB، کلید جداگانه Vault و manifest نسخه/hash؛ بازیابی روی مسیر یا دستگاه دیگر واقعاً آزموده شود.

معیار پذیرش: CRUD کار روی هر دستگاه و مشاهده روی دیگری؛ تکرار در مرز ماه/سال کبیسه شمسی؛ سازگاری timezone؛ یادآوری پس از reboot/Doze؛ sync note/progress بدون duplicate یا از دست‌رفتن؛ آزمون آفلاین و sync نمره؛ گزارش تطبیق‌پذیر با DB؛ backup/restore در محیط آزمایشی؛ migration امن از DB قدیمی؛ تست واقعی Windows و گوشی. کد بخشی از Task/Note و Android TaskReminderScheduler را دارد، اما Sync کامل Task/Note/Study Progress، تقویم شمسی و reboot/Doze/Restore نیاز به تکمیل و آزمون end-to-end دارند.
