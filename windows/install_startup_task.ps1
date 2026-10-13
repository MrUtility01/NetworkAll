# Run this script in the current user's PowerShell session after manually testing server/app.py.
# Creates an opt-in interactive logon task so Windows toast reminders can run after sign-in.
$ErrorActionPreference = "Stop"
$TaskName = "EngineerJokar-NetworkAll-Server"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$ServerDir = Join-Path $RepoRoot "server"
$Pythonw = Join-Path $ServerDir ".venv\Scripts\pythonw.exe"
$App = Join-Path $ServerDir "app.py"

if (-not (Test-Path $Pythonw)) {
    throw "Python virtual environment not found at $Pythonw. Follow README.md to create server/.venv and install requirements first."
}
if (-not (Test-Path $App)) {
    throw "Flask entry point not found: $App"
}

$user = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
$action = New-ScheduledTaskAction -Execute $Pythonw -Argument ('"{0}"' -f $App) -WorkingDirectory $ServerDir
$trigger = New-ScheduledTaskTrigger -AtLogOn -User $user
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Days 0)
$principal = New-ScheduledTaskPrincipal -UserId $user -LogonType Interactive -RunLevel Limited

Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description "NetworkAll local server and Windows toast reminders; LAN remains opt-in." -Force | Out-Null
Write-Host "Created task '$TaskName' for $user."
Write-Host "The task runs after this Windows user signs in. Use windows/remove_startup_task.ps1 to remove it."
Write-Host "The default server bind remains 127.0.0.1. LAN mode requires a strong persisted NETENC_TOKEN and explicit NETENC_HOST=0.0.0.0."
