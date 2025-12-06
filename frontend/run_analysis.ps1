# Frontend Static Code Analysis and Security Scanning Script (PowerShell)

Write-Host "========================================="
Write-Host "Frontend Static Code Analysis"
Write-Host "========================================="
Write-Host ""

# Create reports directory
if (-not (Test-Path "reports")) {
    New-Item -ItemType Directory -Path "reports" | Out-Null
}

Write-Host "1. Running ESLint..."
Write-Host "----------------------------------------"
$eslintOutput = npx eslint src --ext .js,.jsx --max-warnings 0 2>&1
$eslintOutput | Out-File -FilePath "reports\eslint_report.txt" -Encoding utf8

if ($LASTEXITCODE -eq 0) {
    Write-Host "ESLint: No issues found" -ForegroundColor Green
} else {
    Write-Host "ESLint: Issues found - check report" -ForegroundColor Yellow
}
Write-Host "ESLint report saved to reports\eslint_report.txt"
Write-Host ""

Write-Host "2. Running npm audit (Dependency Vulnerability Check)..."
Write-Host "----------------------------------------"
$auditOutput = npm audit --audit-level=moderate 2>&1
$auditOutput | Out-File -FilePath "reports\npm_audit_report.txt" -Encoding utf8

if ($LASTEXITCODE -eq 0) {
    Write-Host "npm audit: No vulnerabilities found" -ForegroundColor Green
} else {
    Write-Host "npm audit: Vulnerabilities found - check report" -ForegroundColor Yellow
}
Write-Host "npm audit report saved to reports\npm_audit_report.txt"
Write-Host ""

Write-Host "========================================="
Write-Host "Analysis Complete!"
Write-Host "========================================="
Write-Host "Reports saved in reports\ directory"

