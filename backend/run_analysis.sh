#!/bin/bash
# Static Code Analysis and Security Scanning Script for Backend

echo "========================================="
echo "Backend Static Code Analysis"
echo "========================================="
echo ""

# Create reports directory
mkdir -p reports

echo "1. Running Pylint..."
echo "----------------------------------------"
pylint --rcfile=.pylintrc app.py models/ routes/ utils/ setup/ > reports/pylint_report.txt 2>&1
echo "Pylint report saved to reports/pylint_report.txt"
echo ""

echo "2. Running Flake8..."
echo "----------------------------------------"
flake8 --config=.flake8 app.py models/ routes/ utils/ setup/ > reports/flake8_report.txt 2>&1
echo "Flake8 report saved to reports/flake8_report.txt"
echo ""

echo "3. Running Bandit (Security Analysis)..."
echo "----------------------------------------"
bandit -r app.py models routes utils setup -f txt -o reports/bandit_report.txt --exclude venv,__pycache__,.git,.venv,reports
echo "Bandit security report saved to reports/bandit_report.txt"
echo ""

echo "4. Running Safety (Dependency Vulnerability Check)..."
echo "----------------------------------------"
safety check --json > reports/safety_report.json 2>&1 || safety check > reports/safety_report.txt 2>&1
echo "Safety dependency report saved to reports/safety_report.txt"
echo ""

echo "========================================="
echo "Analysis Complete!"
echo "========================================="
echo "Reports saved in reports/ directory"

