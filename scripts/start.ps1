# Change to project root directory
Set-Location -Path "$PSScriptRoot\.."

Write-Host "Starting Notion Ory Agent with Docker Compose..." -ForegroundColor Green

# Check Docker
try {
    docker info | Out-Null
} catch {
    Write-Host "Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Check .env
if (-Not (Test-Path .env)) {
    Write-Host "Creating .env file..." -ForegroundColor Yellow
    Copy-Item .env.example .env -ErrorAction SilentlyContinue
    Write-Host "Please update .env file with your credentials" -ForegroundColor Yellow
}

Write-Host "Building and starting services..." -ForegroundColor Cyan
docker-compose up --build -d

Write-Host "`nServices started!" -ForegroundColor Green
Write-Host "`nAccess URLs:" -ForegroundColor Yellow
Write-Host "  Your App:      http://localhost:8000" -ForegroundColor Cyan
Write-Host "  API Docs:      http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "  Kratos:        http://localhost:4433" -ForegroundColor Cyan
Write-Host "  Kratos Admin:  http://localhost:4434" -ForegroundColor Cyan
Write-Host "  Hydra:         http://localhost:4444" -ForegroundColor Cyan
Write-Host "  Hydra Admin:   http://localhost:4445" -ForegroundColor Cyan

Write-Host "`nTo view logs: docker-compose logs -f" -ForegroundColor White
Write-Host "To stop: scripts\stop.ps1" -ForegroundColor White