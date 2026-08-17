param(
    [string]$TaskName = "Organizador-Respaldos-Windows",
    [string]$PythonExe = "",
    [switch]$Remove
)

$ErrorActionPreference = "Stop"
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$ScriptPath = Join-Path $ProjectRoot "src\main.py"

if ($Remove) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
    Write-Host "Tarea eliminada: $TaskName"
    exit 0
}

if (-not $PythonExe) {
    $PythonExe = (Get-Command python).Source
}
$PythonExe = (Resolve-Path $PythonExe).Path

$Action = New-ScheduledTaskAction `
    -Execute $PythonExe `
    -Argument ('"{0}"' -f $ScriptPath) `
    -WorkingDirectory $ProjectRoot

$Trigger = New-ScheduledTaskTrigger -Daily -At 7:00AM
$Settings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Description "Organiza archivos InDesign del turno nocturno tras al menos 2 horas sin actividad." `
    -Force | Out-Null

Write-Host "Tarea registrada: $TaskName"
Write-Host "Ejecuta a las 07:00 y usa rutas absolutas."
Write-Host "No requiere privilegios de administrador para una tarea del usuario actual."
