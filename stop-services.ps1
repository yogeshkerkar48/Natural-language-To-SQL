# Stop all services for NLP to SQL project
# This script stops backend, frontend, and nginx

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "NLP to SQL - Service Stopper" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Stop processes by port
function Stop-ProcessByPort {
    param (
        [int]$Port,
        [string]$ServiceName
    )
    
    Write-Host "Stopping $ServiceName (port $Port)..." -ForegroundColor Yellow
    
    $connections = netstat -ano | Select-String ":$Port\s" | Select-String "LISTENING"
    
    if ($connections) {
        foreach ($connection in $connections) {
            $parts = $connection -split '\s+' | Where-Object { $_ -ne '' }
            $pid = $parts[-1]
            
            if ($pid -and $pid -match '^\d+$') {
                try {
                    Stop-Process -Id $pid -Force -ErrorAction Stop
                    Write-Host "  ✓ Stopped process $pid" -ForegroundColor Green
                } catch {
                    Write-Host "  ✗ Failed to stop process $pid" -ForegroundColor Red
                }
            }
        }
    } else {
        Write-Host "  No process found on port $Port" -ForegroundColor Gray
    }
}

# Stop Nginx
Write-Host "[1/3] Stopping Nginx..." -ForegroundColor Yellow
$nginxPath = "C:\nginx\nginx.exe"
if (Test-Path $nginxPath) {
    try {
        & $nginxPath -s stop
        Write-Host "  ✓ Nginx stopped" -ForegroundColor Green
    } catch {
        Write-Host "  ✗ Failed to stop nginx gracefully, trying force stop..." -ForegroundColor Yellow
        Stop-ProcessByPort -Port 8081 -ServiceName "Nginx"
    }
} else {
    Write-Host "  Nginx not installed" -ForegroundColor Gray
}

# Stop Frontend
Write-Host "[2/3] Stopping Frontend..." -ForegroundColor Yellow
Stop-ProcessByPort -Port 8080 -ServiceName "Frontend"

# Stop Backend
Write-Host "[3/3] Stopping Backend..." -ForegroundColor Yellow
Stop-ProcessByPort -Port 8000 -ServiceName "Backend"

Write-Host ""
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "All Services Stopped!" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
