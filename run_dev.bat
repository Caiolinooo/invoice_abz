@echo off
REM Run server in DEVELOPMENT mode
echo ================================================================================
echo 🔧 STARTING SERVER IN DEVELOPMENT MODE
echo ================================================================================
echo Database: data/invoice_system_dev.db
echo SQL Logging: Enabled
echo.
echo You can test without affecting production data!
echo ================================================================================
echo.

set INVOICE_ENV=dev
cd dev
python -m uvicorn app.api.server:app --reload --host 0.0.0.0 --port 8000

