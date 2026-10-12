# NetworkAll background server runner for Windows Task Scheduler.
# Runs only in the signed-in user's session so native toast notifications can appear.
$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$entry = Join-Path $repoRoot "server\app.py"
$pythonCmd = Get-Command "python.exe" -ErrorAction Stop
$python = $pythonCmd.Source
$logRoot = Join-Path $env:LOCALAPPDATA "NetworkAll\logs"
New-Item -ItemType Directory -Force -Path $logRoot | Out-Null
$stdout = Join-Path $logRoot "server.stdout.log"
$stderr = Join-Path $logRoot "server.stderr.log"
$runnerLog = Join-Path $logRoot "runner.log"
if (!(Test-Path $entry)) { throw "NetworkAll server entry was not found: $entry" }

while ($true) {
    $started = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content -LiteralPath $runnerLog -Value "[$started] Starting NetworkAll server from $repoRoot"
    try {
        $proc = Start-Process -FilePath $python -ArgumentList @("-u", ('"' + $entry + '"')) -WorkingDirectory $repoRoot -PassThru -Wait -NoNewWindow -RedirectStandardOutput $stdout -RedirectStandardError $stderr
        $ended = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        Add-Content -LiteralPath $runnerLog -Value "[$ended] Server exited with code $($proc.ExitCode); restarting in 10 seconds."
    } catch {
        $ended = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        Add-Content -LiteralPath $runnerLog -Value "[$ended] Launch failed: $($_.Exception.Message)"
    }
    Start-Sleep -Seconds 10
}
