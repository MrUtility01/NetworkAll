# وضعیت استخراج دانشنامه دستورات

منبع ZIP: `tools/chapters/68/ch68_all_domains.zip`

## فایل‌های کامل (باید از ZIP استخراج شوند)

| فایل | تعداد |
|------|--------|
| commands_linux.json | 500 |
| commands_windows.json | 500 |
| commands_windows_batch.json | 500 |
| commands_cisco.json | 500 |
| commands_mikrotik.json | 500 |
| commands_fortigate.json | 500 |
| commands_docker.json | 300 |
| commands_windows_server.json | 300 |
| questions_commands_usage.json | 1120 |
| answers_commands_usage.json | 1120 |

## استخراج

```bash
cd tools/chapters/68
unzip -o ch68_all_domains.zip
cp -f ch68_commands_encyclopedia/*.json commands/sources/encyclopedia/
rm -rf commands/sources/tools
```

یا: `bash commands/sources/encyclopedia/EXTRACT.sh`

## پاک‌سازی
مسیر تو در توی `commands/sources/tools/` اشتباه است و باید حذف شود.
