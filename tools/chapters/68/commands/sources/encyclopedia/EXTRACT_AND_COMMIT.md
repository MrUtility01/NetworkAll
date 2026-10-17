# استخراج کامل ZIP روی مخزن

ZIP از قبل در این مسیر است:
`tools/chapters/68/ch68_all_domains.zip`

## روی ماشین محلی (یک‌بار)

```bash
git clone https://github.com/MrUtility01/NetworkAll.git
cd NetworkAll
git pull

cd tools/chapters/68
unzip -o ch68_all_domains.zip
mkdir -p commands/sources/encyclopedia
cp -f ch68_commands_encyclopedia/*.json commands/sources/encyclopedia/
cp -f ch68_commands_encyclopedia/VALIDATION.md commands/sources/encyclopedia/ 2>/dev/null || true

# پاک‌سازی مسیر تو در توی اشتباه
rm -rf commands/sources/tools

cd ../../..
git add tools/chapters/68/commands/sources/encyclopedia/
git add -u tools/chapters/68/commands/sources/tools 2>/dev/null || true
git commit -m "content(ch68): extract 3600 commands + 1120 exam Q into encyclopedia/"
git push origin main
```

## یا با اسکریپت

```bash
bash tools/chapters/68/commands/sources/encyclopedia/EXTRACT.sh
git add tools/chapters/68/commands/sources/encyclopedia/
git commit -m "content(ch68): extract encyclopedia JSON"
git push
```

پس از push، این فایل‌ها باید در encyclopedia دیده شوند:
- commands_linux.json (500)
- commands_windows.json (500)
- commands_windows_batch.json (500)
- commands_cisco.json (500)
- commands_mikrotik.json (500)
- commands_fortigate.json (500)
- commands_docker.json (300)
- commands_windows_server.json (300)
- questions_commands_usage.json (1120)
- answers_commands_usage.json (1120)
