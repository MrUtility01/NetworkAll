@echo off
setlocal EnableExtensions
cd /d "%~dp0.."
title NetworkAll - Windows Server

where py >nul 2>nul
if errorlevel 1 (
  where python >nul 2>nul
  if errorlevel 1 (
    echo Python 3.11 or newer is required.
    echo Install Python from https://www.python.org/downloads/windows/
    echo Enable "Add python.exe to PATH" during installation.
    pause
    exit /b 1
  )
  set "PYTHON=python"
) else (
  set "PYTHON=py -3"
)

if not exist ".venv\Scripts\python.exe" (
  echo [1/4] Creating private Python environment...
  %PYTHON% -m venv .venv
  if errorlevel 1 goto :error
)

echo [2/4] Installing or updating server dependencies...
".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -r server\requirements.txt
if errorlevel 1 goto :error

if not exist "server\data" mkdir "server\data"
if not exist "server\data\sync-token.txt" (
  echo [3/4] Creating a private random LAN sync token...
  ".venv\Scripts\python.exe" -c "import secrets,pathlib; pathlib.Path(r'server/data/sync-token.txt').write_text(secrets.token_urlsafe(32),encoding='utf-8')"
  if errorlevel 1 goto :error
)
set /p NETENC_TOKEN=<"server\data\sync-token.txt"
if "%NETENC_TOKEN%"=="" (
  echo Could not read the LAN token from server\data\sync-token.txt
  goto :error
)
set "NETENC_HOST=0.0.0.0"
set "NETENC_PORT=5050"

echo.
echo [4/4] Starting NetworkAll server...
echo Keep this window open while using the Android sync.
echo Private LAN sync token is stored in server\data\sync-token.txt
echo Do not share that file or expose port 5050 to the public Internet.
echo.
".venv\Scripts\python.exe" server\app.py
set "APP_EXIT=%ERRORLEVEL%"
echo.
echo NetworkAll server stopped with exit code %APP_EXIT%.
pause
exit /b %APP_EXIT%

:error
echo.
echo NetworkAll startup failed. Read the error above.
pause
exit /b 1
