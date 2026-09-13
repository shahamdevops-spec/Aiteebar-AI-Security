# Generate .env file from .env.example (PowerShell version)
# This script creates a .env file with secure defaults for Windows

param(
    [switch]$Force = $false
)

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptPath
$envExample = Join-Path $projectRoot ".env.example"
$envFile = Join-Path $projectRoot ".env"

if (-not (Test-Path $envExample)) {
    Write-Host "❌ Error: .env.example not found at $envExample" -ForegroundColor Red
    exit 1
}

if ((Test-Path $envFile) -and -not $Force) {
    Write-Host "⚠️  .env file already exists. Use -Force to overwrite." -ForegroundColor Yellow
    exit 0
}

if ((Test-Path $envFile) -and $Force) {
    Write-Host "🔄 Creating backup of existing .env..." -ForegroundColor Cyan
    $timestamp = Get-Date -Format "yyyyMMddHHmmss"
    Copy-Item $envFile "$envFile.backup.$timestamp"
}

Write-Host "📝 Generating .env file from .env.example..." -ForegroundColor Cyan
Write-Host ""

# Copy example to .env
Copy-Item $envExample $envFile -Force

# Generate secure random values for secrets
function New-RandomString {
    param([int]$Length = 32)
    $chars = [char[]]"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
    $random = New-Object Random
    $password = -join (1..$Length | ForEach-Object { $chars[$random.Next($chars.Length)] })
    return $password
}

$jwtSecret = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes((New-RandomString -Length 32)))
$postgresPassword = New-RandomString -Length 16
$redisPassword = New-RandomString -Length 16

Write-Host "🔐 Generating secure secrets..." -ForegroundColor Cyan

# Read the file and update secrets
$envContent = Get-Content $envFile -Raw

# Replace placeholders with generated values
$envContent = $envContent -replace "JWT_SECRET_KEY=.*", "JWT_SECRET_KEY=$jwtSecret"
$envContent = $envContent -replace "POSTGRES_PASSWORD=.*", "POSTGRES_PASSWORD=$postgresPassword"
$envContent = $envContent -replace "REDIS_PASSWORD=.*", "REDIS_PASSWORD=$redisPassword"

# Write updated content back
$envContent | Set-Content $envFile -Encoding UTF8

Write-Host "✓ Secrets generated and inserted"
Write-Host ""
Write-Host "✅ .env file generated successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Generated secrets (save for reference):"
Write-Host "  JWT_SECRET_KEY: $(($jwtSecret).Substring(0, 20))..."
Write-Host "  POSTGRES_PASSWORD: $(($postgresPassword).Substring(0, 10))..."
Write-Host "  REDIS_PASSWORD: $(($redisPassword).Substring(0, 10))..."
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Review .env file and update any values as needed"
Write-Host "  2. Run: docker-compose up -d"
Write-Host ""
