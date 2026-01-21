# Change to project root directory
Set-Location -Path "$PSScriptRoot\.."

Write-Host "Stopping services..." -ForegroundColor Yellow
docker-compose down
Write-Host "Services stopped." -ForegroundColor Green