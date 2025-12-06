@echo off
REM Static Code Analysis and Security Scanning Script for Frontend (Windows)

echo =========================================
echo Frontend Static Code Analysis
echo =========================================
echo.

REM Create reports directory
if not exist reports mkdir reports

echo 1. Running ESLint...
echo ----------------------------------------
if exist node_modules\eslint (
    npx eslint src --ext .js,.jsx --max-warnings 0 > reports\eslint_report.txt 2>&1
) else (
    echo ESLint not found in node_modules. Installing...
    npm install
    npx eslint src --ext .js,.jsx --max-warnings 0 > reports\eslint_report.txt 2>&1
)
if %ERRORLEVEL% EQU 0 (
    echo ESLint: No issues found
) else (
    echo ESLint: Issues found - check report
)
echo ESLint report saved to reports\eslint_report.txt
echo.

echo 2. Running npm audit (Dependency Vulnerability Check)...
echo ----------------------------------------
npm audit --audit-level=moderate > reports\npm_audit_report.txt 2>&1
if %ERRORLEVEL% EQU 0 (
    echo npm audit: No vulnerabilities found
) else (
    echo npm audit: Vulnerabilities found - check report
)
echo npm audit report saved to reports\npm_audit_report.txt
echo.

echo =========================================
echo Analysis Complete!
echo =========================================
echo Reports saved in reports\ directory

