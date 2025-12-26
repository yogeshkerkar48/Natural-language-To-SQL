# Start all services for NLP to SQL project
# This script starts backend, frontend, and nginx

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "NLP to SQL - Service Starter" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Check if nginx is installed
$nginxPath = "C:\nginx\nginx.exe"
if (-not (Test-Path $nginxPath)) {
    Write-Host "WARNING: nginx not found at $nginxPath" -ForegroundColor Yellow
    Write-Host "Please install nginx first. See NGINX_SETUP.md for instructions." -ForegroundColor Yellow
    Write-Host ""
}

# Get the project root directory
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "Starting services..." -ForegroundColor Green
Write-Host ""

# Start Backend
Write-Host "[1/3] Starting Backend (port 8000)..." -ForegroundColor Yellow
$backendPath = Join-Path $projectRoot "backend"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$backendPath'; Write-Host 'Backend Server' -ForegroundColor Green; uvicorn app.main:app --reload --port 8000"
Start-Sleep -Seconds 2

# Start Frontend
Write-Host "[2/3] Starting Frontend (port 8080)..." -ForegroundColor Yellow
$frontendPath = Join-Path $projectRoot "frontend"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$frontendPath'; Write-Host 'Frontend Server' -ForegroundColor Green; npm run dev"
Start-Sleep -Seconds 2

# Start Nginx (if installed)
if (Test-Path $nginxPath) {
    Write-Host "[3/3] Starting Nginx (port 8081)..." -ForegroundColor Yellow
    
    # Copy nginx.conf to nginx directory
    $nginxConf = Join-Path $projectRoot "nginx.conf"
    $nginxConfDest = "C:\nginx\conf\nginx.conf"
    
    if (Test-Path $nginxConf) {
        Copy-Item $nginxConf $nginxConfDest -Force
        Write-Host "Nginx configuration copied." -ForegroundColor Gray
    }
    
    # Start nginx in a new window
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'C:\nginx'; Write-Host 'Nginx Server' -ForegroundColor Green; .\nginx.exe; Write-Host 'Nginx started on port 8081' -ForegroundColor Green"
    Start-Sleep -Seconds 1
} else {
    Write-Host "[3/3] Skipping Nginx (not installed)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Services Started!" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Access your application:" -ForegroundColor White
if (Test-Path $nginxPath) {
    Write-Host "  Main App:  http://localhost:8081" -ForegroundColor Cyan
    Write-Host "  API Docs:  http://localhost:8081/api/docs" -ForegroundColor Cyan
} else {
    Write-Host "  Frontend:  http://localhost:8080" -ForegroundColor Cyan
    Write-Host "  Backend:   http://localhost:8000/api/docs" -ForegroundColor Cyan
}
Write-Host ""
Write-Host "Press any key to exit this window..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
