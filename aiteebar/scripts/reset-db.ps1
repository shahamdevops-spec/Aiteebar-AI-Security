# Reset database script (PowerShell version)
# Removes all data and recreates the database from scratch
# WARNING: This will delete all data!

param(
    [switch]$Force = $false
)

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptPath

Write-Host ""
Write-Host "⚠️  WARNING: This will DELETE all data from the database!" -ForegroundColor Yellow
Write-Host ""

if (-not $Force) {
    $confirm = Read-Host "Are you sure? Type 'yes' to confirm"
    if ($confirm -ne "yes") {
        Write-Host "❌ Aborted." -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "🔄 Resetting database..." -ForegroundColor Cyan
Write-Host ""

try {
    # Check if docker-compose is available
    $dockerCompose = Get-Command docker-compose -ErrorAction SilentlyContinue

    if (-not $dockerCompose) {
        # Try 'docker compose' (newer syntax)
        $dockerCompose = Get-Command docker -ErrorAction SilentlyContinue
        if ($dockerCompose) {
            $useNewSyntax = $true
        } else {
            throw "Docker is not installed"
        }
    } else {
        $useNewSyntax = $false
    }

    Push-Location $projectRoot

    if ($useNewSyntax) {
        $composeCmd = "docker compose"
    } else {
        $composeCmd = "docker-compose"
    }

    Write-Host "1. Stopping containers..." -ForegroundColor Cyan
    & powershell -Command "$composeCmd down" -ErrorAction Continue

    Write-Host ""
    Write-Host "2. Removing volumes..." -ForegroundColor Cyan
    & powershell -Command "$composeCmd down -v" -ErrorAction Continue

    Write-Host ""
    Write-Host "3. Starting fresh..." -ForegroundColor Cyan
    & powershell -Command "$composeCmd up -d" -ErrorAction Stop

    Write-Host ""
    Write-Host "4. Waiting for services to start..." -ForegroundColor Cyan
    Start-Sleep -Seconds 10

    Write-Host ""
    Write-Host "5. Running migrations..." -ForegroundColor Cyan
    & powershell -Command "$composeCmd exec -T backend alembic upgrade head" -ErrorAction Continue

    Pop-Location

    Write-Host ""
    Write-Host "✅ Database reset complete!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Running services:" -ForegroundColor Cyan
    & powershell -Command "$composeCmd ps"

} catch {
    Write-Host "❌ Error: $_" -ForegroundColor Red
    Pop-Location
    exit 1
}

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  - Frontend: http://localhost:3000"
Write-Host "  - Backend API: http://localhost:8000"
Write-Host "  - API Docs: http://localhost:8000/docs"
Write-Host "  - Database UI: http://localhost:8080"
Write-Host ""
