@echo off
REM Run server in PRODUCTION mode
echo ================================================================================
echo 🚀 STARTING SERVER IN PRODUCTION MODE
echo ================================================================================
echo Database: data/invoice_system.db
echo SQL Logging: Disabled
echo.
echo ⚠️  WARNING: Changes will affect production data!
echo ================================================================================
echo.

set INVOICE_ENV=prod
cd dev
python -m uvicorn app.api.server:app --reload --host 0.0.0.0 --port 8000

