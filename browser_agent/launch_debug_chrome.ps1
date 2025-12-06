# launch_debug_chrome.ps1
# This script restarts Chrome in "Debug Mode" so the bot can connect to it.

$chromePath = "C:\Program Files\Google\Chrome\Application\chrome.exe"
$userDataDir = "$env:LOCALAPPDATA\Google\Chrome\User Data"
$port = 9223

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "   CHROME DEBUG MODE LAUNCHER" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# 1. Check if Chrome is running
# Always force kill to ensure clean state
Write-Host "🧹 Cleaning up old Chrome processes..." -ForegroundColor Yellow
cmd /c "taskkill /F /IM chrome.exe /T" | Out-Null
Start-Sleep -Seconds 3

# Double check for any lingering processes
$lingering = Get-Process -Name "chrome" -ErrorAction SilentlyContinue
if ($lingering) {
    Write-Host "⚠️  Force killing lingering Chrome processes..." -ForegroundColor Red
    cmd /c "taskkill /F /IM chrome.exe /T" | Out-Null
    Start-Sleep -Seconds 2
}

# 2. Launch Chrome with Debugging Port
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
$userDataDir = Join-Path $scriptPath "user_chrome_profile"

# Ensure dir exists
if (-not (Test-Path $userDataDir)) {
    New-Item -ItemType Directory -Path $userDataDir -Force | Out-Null
}

Write-Host "🚀 Launching Chrome with Remote Debugging Port $port..." -ForegroundColor Green
Write-Host "   Profile: BOT PROFILE ($userDataDir)" -ForegroundColor Gray

# Start Chrome as a detached process
# We use Start-Process with -WindowStyle Normal to ensure it's visible
$process = Start-Process -FilePath $chromePath -ArgumentList "--remote-debugging-port=$port", "--user-data-dir=""$userDataDir""", "--no-first-run", "--no-default-browser-check" -PassThru

if ($process) {
    Write-Host "⏳ Waiting for port $port to open..." -ForegroundColor Cyan
    $maxRetries = 10
    $retry = 0
    $portOpen = $false
    
    while ($retry -lt $maxRetries) {
        try {
            $conn = New-Object System.Net.Sockets.TcpClient("localhost", $port)
            $conn.Close()
            $portOpen = $true
            break
        } catch {
            Start-Sleep -Seconds 1
            $retry++
        }
    }

    if ($portOpen) {
        Write-Host "✅ Chrome launched successfully and port $port is OPEN!" -ForegroundColor Green
        Write-Host "   You can now browse normally." -ForegroundColor Green
        Write-Host "   Run your bot scripts anytime, and they will attach to this window." -ForegroundColor Cyan
    } else {
        Write-Host "❌ Chrome launched, but port $port is NOT responding." -ForegroundColor Red
        Write-Host "   This usually means an old Chrome process is still running in the background." -ForegroundColor Red
        Write-Host "   Please check Task Manager and kill all 'chrome.exe' processes manually." -ForegroundColor Red
    }
} else {
    Write-Host "❌ Failed to launch Chrome." -ForegroundColor Red
}
