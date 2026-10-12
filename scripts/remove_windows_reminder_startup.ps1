# Remove the per-user NetworkAll background server task.
$ErrorActionPreference = "Stop"
$taskName = "NetworkAll Local Server and Reminders"
$task = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($task) {
    Stop-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
    Write-Host "Removed scheduled task: $taskName"
} else {
    Write-Host "Scheduled task was not registered."
}
Write-Host "Logs and local data were not deleted."
