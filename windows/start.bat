@echo off
chcp 65001 >nul
setlocal EnableExtensions
title NetworkEncyclopedia — Engineer Jokar

REM Use a random per-installation token instead of a shared default secret.
set "TOKEN_FILE=%~dp0.netenc_token"
if not defined NETENC_TOKEN (
  if exist "%TOKEN_FILE%" set /p "NETENC_TOKEN=" < "%TOKEN_FILE%"
)
if not defined NETENC_TOKEN (
  for /f %%T in ('powershell -NoProfile -Command "[guid]::NewGuid().ToString() + [guid]::NewGuid().ToString()"') do set "NETENC_TOKEN=%%T"
  if defined NETENC_TOKEN > "%TOKEN_FILE%" echo %NETENC_TOKEN%
)
if not defined NETENC_TOKEN (
  echo [ERROR] Could not create a sync token.
  echo Set NETENC_TOKEN manually and run this file again.
  pause
  exit /b 1
)

cd /d "%~dp0..\server"
if not defined NETENC_DEVICE set "NETENC_DEVICE=%COMPUTERNAME%"
if not defined NETENC_PORT set "NETENC_PORT=5050"
if not defined NETENC_HOST set "NETENC_HOST=0.0.0.0"

echo ============================================
echo  NetworkEncyclopedia Server
echo  Token : %NETENC_TOKEN%
echo  Port  : %NETENC_PORT%
echo ============================================
echo.
echo Save this token in the Android app's sync settings.
echo Token file: %TOKEN_FILE%
echo.
where python >nul 2>&1
if errorlevel 1 (
  echo [ERROR] Python was not found. Install Python 3.11+ from python.org.
  pause
  exit /b 1
)
python -m pip install -q -r requirements.txt
if errorlevel 1 (
  echo [WARN] Dependency installation reported a problem.
)
echo.
echo Starting server and importing chapter folders...
echo Browser: http://127.0.0.1:%NETENC_PORT%
echo Android: same Wi-Fi + token shown above
echo.
python ..\scripts\assemble_chapter_packs.py --strict
if errorlevel 1 (
  echo [ERROR] Chapter assembly failed; stopping startup.
  pause
  exit /b 1
)
python app.py
pause
