@echo off
setlocal
chcp 65001 >nul
title NetworkAll v1.0.0 — Engineer Jokar
cd /d "%~dp0..\server"

REM Release defaults: LAN binding on TCP/86; secret is generated per installation.
if not defined NETENC_DEVICE set NETENC_DEVICE=%COMPUTERNAME%
if not defined NETENC_PORT set NETENC_PORT=86
if not defined NETENC_HOST set NETENC_HOST=0.0.0.0
set "VENV=%~dp0..\.venv"
set "VPY=%VENV%\Scripts\python.exe"

echo ============================================
echo  NetworkAll v1.0.0 Server
echo  Host  : %NETENC_HOST%
echo  Port  : %NETENC_PORT%
echo  Token : %~dp0..\server\data\networkall.token (copy to Android Settings)
echo ============================================
echo.

where python >nul 2>&1
if errorlevel 1 (
  echo [ERROR] Python 3.11+ not found. Install Python from python.org with Add Python to PATH.
  pause
  exit /b 1
)

if not exist "%VPY%" (
  echo Creating private Python environment...
  python -m venv "%VENV%"
  if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment.
    pause
    exit /b 1
  )
)

echo Installing/verifying dependencies...
"%VPY%" -m pip install --disable-pip-version-check -r requirements.txt
if errorlevel 1 (
  echo [ERROR] Dependency installation failed. Check internet access and requirements.txt.
  pause
  exit /b 1
)

echo.
echo Refreshing the shared 68-chapter curriculum and command packs...
pushd "%~dp0.."
"%VPY%" scripts\export_android_index.py
if errorlevel 1 goto curriculum_error
"%VPY%" scripts\merge_content_packs_into_android.py
if errorlevel 1 goto curriculum_error
"%VPY%" scripts\import_networkencyclopedia_reference.py
if errorlevel 1 goto curriculum_error
popd
cd /d "%~dp0..\server"
goto curriculum_done
:curriculum_error
popd
echo [ERROR] Shared course content could not be refreshed. Review Python output above.
pause
exit /b 1
:curriculum_done
echo.
echo Web UI: http://127.0.0.1:%NETENC_PORT%
echo Android: set API host to http://COMPUTER-LAN-IP:%NETENC_PORT%
echo First start creates the sync token file under server\data.
echo.
"%VPY%" app.py
pause
