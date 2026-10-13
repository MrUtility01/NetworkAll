# Install a per-user logon task for NetworkAll's local server and Windows toast reminders.
# Does NOT enable LAN access; the server remains bound to 127.0.0.1 by default.
[CmdletBinding()]
param([switch]$StartNow)

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$runner = Join-Path $PSScriptRoot "run_windows_server_hidden.ps1"
if (!(Test-Path (Join-Path $repoRoot "server\app.py"))) { throw "server\app.py not found under $repoRoot" }
if (!(Get-Command "python.exe" -ErrorAction SilentlyContinue)) { throw "Python was not found on PATH. Install Python and server requirements first." }

$taskName = "NetworkAll Local Server and Reminders"
$powerShell = (Get-Command "powershell.exe").Source
$action = New-ScheduledTaskAction -Execute $powerShell -Argument ('-NoProfile -NonInteractive -ExecutionPolicy Bypass -WindowStyle Hidden -File "' + $runner + '"') -WorkingDirectory $repoRoot
$userId = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
$trigger = New-ScheduledTaskTrigger -AtLogOn -User $userId
$principal = New-ScheduledTaskPrincipal -UserId $userId -LogonType Interactive -RunLevel Limited
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -MultipleInstances IgnoreNew -ExecutionTimeLimit ([TimeSpan]::Zero) -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Description "Starts the NetworkAll local Flask server in the signed-in session so Windows task reminders can display toast notifications." -Force | Out-Null
Write-Host "Registered per-user logon task: $taskName"
Write-Host "Default server binding remains local-only (127.0.0.1). No firewall rule or LAN exposure was added."
Write-Host "Log files: $env:LOCALAPPDATA\NetworkAll\logs"
if ($StartNow) { Start-ScheduledTask -TaskName $taskName; Write-Host "Started task." }
else { Write-Host "It will start at the next sign-in. Use -StartNow to start it now." }
