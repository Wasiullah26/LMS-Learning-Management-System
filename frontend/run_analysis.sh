#!/bin/bash
# Static Code Analysis and Security Scanning Script for Frontend

echo "========================================="
echo "Frontend Static Code Analysis"
echo "========================================="
echo ""

# Create reports directory
mkdir -p reports

echo "1. Running ESLint..."
echo "----------------------------------------"
npx eslint src --ext .js,.jsx --max-warnings 0 > reports/eslint_report.txt 2>&1
if [ $? -eq 0 ]; then
    echo "ESLint: No issues found"
else
    echo "ESLint: Issues found - check report"
fi
echo "ESLint report saved to reports/eslint_report.txt"
echo ""

echo "2. Running npm audit (Dependency Vulnerability Check)..."
echo "----------------------------------------"
npm audit --audit-level=moderate > reports/npm_audit_report.txt 2>&1
if [ $? -eq 0 ]; then
    echo "npm audit: No vulnerabilities found"
else
    echo "npm audit: Vulnerabilities found - check report"
fi
echo "npm audit report saved to reports/npm_audit_report.txt"
echo ""

echo "========================================="
echo "Analysis Complete!"
echo "========================================="
echo "Reports saved in reports/ directory"

