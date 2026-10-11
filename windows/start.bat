@echo off
chcp 65001 >nul
title NetworkEncyclopedia — Engineer Jokar
cd /d "%~dp0..\server"

REM ساخت توکن تصادفی پایدار؛ توکن ثابت داخل سورس استفاده نمی‌شود.
if not exist "data" mkdir "data"
set "TOKEN_FILE=%CD%\data\.netenc-token"
if not defined NETENC_TOKEN (
  if not exist "%TOKEN_FILE%" goto create_token
  for %%F in ("%TOKEN_FILE%") do if %%~zF LSS 32 goto create_token
  goto read_token

  :create_token
  powershell -NoProfile -Command "$rng=[Security.Cryptography.RandomNumberGenerator]::Create();$b=New-Object byte[] 32;$rng.GetBytes($b);[Console]::Write([Convert]::ToBase64String($b))" > "%TOKEN_FILE%"
  if errorlevel 1 (
    echo [ERROR] توکن امن ساخته نشد؛ NETENC_TOKEN را قبل از اجرا تنظيم کنيد.
    pause
    exit /b 1
  )
  :read_token
  set /p NETENC_TOKEN=<"%TOKEN_FILE%"
)
if not defined NETENC_TOKEN (
  echo [ERROR] توکن خالي است؛ فايل %TOKEN_FILE% را بررسي کنيد.
  pause
  exit /b 1
)
if not defined NETENC_DEVICE set NETENC_DEVICE=%COMPUTERNAME%
if not defined NETENC_PORT set NETENC_PORT=5050
REM دسترسي LAN براي اتصال گوشي لازم است؛ فقط در شبکه مورد اعتماد اجرا کنيد.
if not defined NETENC_HOST set NETENC_HOST=0.0.0.0

echo ============================================
echo  NetworkAll / Engineer Jokar
echo  Token : %NETENC_TOKEN%
echo  Port  : %NETENC_PORT%
echo  Bind  : %NETENC_HOST%
echo  Token file: %TOKEN_FILE%
echo ============================================
echo.

where python >nul 2>&1
if errorlevel 1 (
  echo [ERROR] Python پیدا نشد. از python.org نصب کنید.
  pause
  exit /b 1
)

python -m pip install -q -r requirements.txt
if errorlevel 1 (
  echo [ERROR] نصب وابستگي‌ها ناموفق بود؛ اتصال اينترنت و pip را بررسي کنيد.
  pause
  exit /b 1
)

echo.
echo در حال seed و اجرای سرور...
echo مرورگر: http://127.0.0.1:%NETENC_PORT%
echo اندروید: همان Wi-Fi مورد اعتماد + Token بالا
echo.
python app.py
pause
