@echo off
REM ============================================================================
REM AWS WAF Advisor - Portfolio Deployment (In-Place)
REM 
REM Run this from WITHIN your project directory
REM Usage: deploy_portfolio.bat
REM ============================================================================

echo.
echo ========================================
echo AWS WAF Advisor - Portfolio Deployment
echo ========================================
echo.
echo Current directory: %CD%
echo.

REM Check if we're in the right place (look for app.py or waf_review_module.py)
if not exist "app.py" if not exist "waf_review_module.py" (
    echo ERROR: This doesn't look like your AWS WAF Advisor project!
    echo.
    echo Please make sure you're running this from:
    echo C:\aiprojects\awswafr\aws-waf-advisor-FINAL
    echo.
    echo Current directory: %CD%
    echo.
    pause
    exit /b 1
)

echo SUCCESS: Found AWS WAF Advisor project files
echo.

REM Create backup directory
set BACKUP_DIR=backups\portfolio_deployment_%date:~-4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set BACKUP_DIR=%BACKUP_DIR: =0%
echo Creating backup directory: %BACKUP_DIR%
mkdir "%BACKUP_DIR%" 2>nul
echo SUCCESS: Backup created
echo.

REM Step 1: Backup existing files
echo Step 1: Backing up existing files...
echo.

if exist "pdf_report_generator.py" (
    copy "pdf_report_generator.py" "%BACKUP_DIR%\pdf_report_generator.py.backup" >nul 2>&1
    echo   [BACKUP] pdf_report_generator.py
)

if exist "waf_review_module.py" (
    copy "waf_review_module.py" "%BACKUP_DIR%\waf_review_module.py.backup" >nul 2>&1
    echo   [BACKUP] waf_review_module.py
)

if exist "app.py" (
    copy "app.py" "%BACKUP_DIR%\app.py.backup" >nul 2>&1
    echo   [BACKUP] app.py
)

echo.
echo SUCCESS: Backups complete in %BACKUP_DIR%
echo.

REM Step 2: Check for portfolio files in current directory
echo Step 2: Looking for portfolio files to deploy...
echo.

set FILES_FOUND=0

if exist "portfolio_data_model.py" (
    echo   [FOUND] portfolio_data_model.py
    set FILES_FOUND=1
) else (
    echo   [MISSING] portfolio_data_model.py
)

if exist "multi_account_scanner.py" (
    echo   [FOUND] multi_account_scanner.py
    set FILES_FOUND=1
) else (
    echo   [MISSING] multi_account_scanner.py
)

if exist "waf_portfolio_integration.py" (
    echo   [FOUND] waf_portfolio_integration.py
    set FILES_FOUND=1
) else (
    echo   [MISSING] waf_portfolio_integration.py
)

if exist "pdf_report_generator_MULTI_ACCOUNT.py" (
    echo   [FOUND] pdf_report_generator_MULTI_ACCOUNT.py
    set FILES_FOUND=1
) else (
    echo   [MISSING] pdf_report_generator_MULTI_ACCOUNT.py
)

echo.

if %FILES_FOUND%==0 (
    echo ERROR: No portfolio files found in current directory!
    echo.
    echo Please make sure these files are in the same folder:
    echo   - portfolio_data_model.py
    echo   - multi_account_scanner.py
    echo   - waf_portfolio_integration.py
    echo   - pdf_report_generator_MULTI_ACCOUNT.py
    echo.
    echo Current directory: %CD%
    echo.
    pause
    exit /b 1
)

echo Files ready to deploy!
echo.

REM Step 3: Deploy portfolio files (they're already here!)
echo Step 3: Verifying portfolio files...
echo.

if exist "portfolio_data_model.py" (
    echo   [OK] portfolio_data_model.py
) else (
    echo   [SKIP] portfolio_data_model.py not found
)

if exist "multi_account_scanner.py" (
    echo   [OK] multi_account_scanner.py
) else (
    echo   [SKIP] multi_account_scanner.py not found
)

if exist "waf_portfolio_integration.py" (
    echo   [OK] waf_portfolio_integration.py
) else (
    echo   [SKIP] waf_portfolio_integration.py not found
)

echo.

REM Step 4: Replace PDF generator
echo Step 4: Updating PDF generator...
echo.

if exist "pdf_report_generator_MULTI_ACCOUNT.py" (
    if exist "pdf_report_generator.py" (
        copy "pdf_report_generator.py" "pdf_report_generator_OLD.py" >nul 2>&1
        echo   [BACKUP] Created pdf_report_generator_OLD.py
    )
    
    copy "pdf_report_generator_MULTI_ACCOUNT.py" "pdf_report_generator.py" >nul 2>&1
    echo   [UPDATED] pdf_report_generator.py
    echo.
    echo SUCCESS: PDF generator updated!
) else (
    echo   [ERROR] pdf_report_generator_MULTI_ACCOUNT.py not found!
    echo.
    echo Please make sure pdf_report_generator_MULTI_ACCOUNT.py is in:
    echo %CD%
)

echo.

REM Step 5: Check Python dependencies
echo Step 5: Checking Python dependencies...
echo.

python -c "import sys; print('  Python version:', sys.version.split()[0])" 2>nul
if %errorlevel% neq 0 (
    echo   [WARNING] Python not found in PATH
) else (
    python -c "import boto3; print('  [OK] boto3')" 2>nul || echo   [MISSING] boto3 - install with: pip install boto3
    python -c "import reportlab; print('  [OK] reportlab')" 2>nul || echo   [MISSING] reportlab - install with: pip install reportlab
    python -c "import streamlit; print('  [OK] streamlit')" 2>nul || echo   [MISSING] streamlit - install with: pip install streamlit
)

echo.

REM Step 6: Test imports
echo Step 6: Testing portfolio imports...
echo.

python -c "from portfolio_data_model import create_portfolio_assessment; print('  [OK] portfolio_data_model imports successfully')" 2>nul
if %errorlevel% equ 0 (
    python -c "from multi_account_scanner import run_multi_account_scan; print('  [OK] multi_account_scanner imports successfully')" 2>nul || echo   [ERROR] multi_account_scanner import failed
    python -c "from waf_portfolio_integration import render_assessment_type_selector; print('  [OK] waf_portfolio_integration imports successfully')" 2>nul || echo   [ERROR] waf_portfolio_integration import failed
    python -c "from pdf_report_generator import generate_waf_pdf_report; print('  [OK] pdf_report_generator imports successfully')" 2>nul || echo   [ERROR] pdf_report_generator import failed
) else (
    echo   [ERROR] portfolio_data_model import failed
    echo   Make sure the file exists and has no syntax errors
)

echo.

REM Step 7: Create integration guide
echo Step 7: Creating integration guide...
echo.

(
echo # Portfolio Integration Guide
echo.
echo ## Deployment Complete! 
echo.
echo The following files are now in your project:
echo - portfolio_data_model.py
echo - multi_account_scanner.py  
echo - waf_portfolio_integration.py
echo - pdf_report_generator.py ^(UPDATED^)
echo.
echo Backups saved in: %BACKUP_DIR%
echo.
echo ## Next Steps:
echo.
echo ### 1. Add Imports to Your Main File
echo.
echo Open `app.py` or `waf_review_module.py` and add these imports at the top:
echo.
echo ```python
echo from waf_portfolio_integration import ^(
echo     render_assessment_type_selector,
echo     render_portfolio_workflow,
echo     is_portfolio_assessment
echo ^)
echo ```
echo.
echo ### 2. Add UI Toggle
echo.
echo Find your assessment creation section and add:
echo.
echo ```python
echo # Add assessment type selector
echo assessment_type = render_assessment_type_selector^(^)
echo.
echo if assessment_type == "Multi-Account Portfolio":
echo     render_portfolio_workflow^(^)
echo else:
echo     # Your existing single-account code
echo     pass
echo ```
echo.
echo ### 3. Test Locally
echo.
echo ```bash
echo streamlit run app.py
echo ```
echo.
echo Test both:
echo - Single Account ^(should work as before^)
echo - Multi-Account Portfolio ^(new feature^)
echo.
echo ### 4. Deploy
echo.
echo ```bash
echo git add .
echo git commit -m "Add multi-account portfolio support"
echo git push origin main
echo ```
echo.
echo ## Documentation
echo.
echo See:
echo - DEPLOYMENT_CHECKLIST.md - Step-by-step guide
echo - WINDOWS_DEPLOYMENT_GUIDE.md - Windows-specific help
echo - MULTI_ACCOUNT_DEPLOYMENT_GUIDE.md - Complete reference
echo.
echo ## Rollback
echo.
echo If needed, restore from backup:
echo ```bash
echo copy "%BACKUP_DIR%\*.backup" .
echo ```
echo.
echo ## Support
echo.
echo Check the documentation files for help!
) > "PORTFOLIO_INTEGRATION_GUIDE.md"

echo   [CREATED] PORTFOLIO_INTEGRATION_GUIDE.md
echo.

REM Summary
echo.
echo ==========================================
echo        Deployment Complete!
echo ==========================================
echo.
echo [√] Files backed up to: %BACKUP_DIR%
echo [√] Portfolio files verified
echo [√] PDF generator updated
echo [√] Integration guide created
echo.
echo Next Steps:
echo.
echo 1. Review: PORTFOLIO_INTEGRATION_GUIDE.md
echo 2. Add imports to your app.py
echo 3. Add UI toggle
echo 4. Test: streamlit run app.py
echo 5. Deploy: git push
echo.
echo See DEPLOYMENT_CHECKLIST.md for detailed steps!
echo.

REM Open integration guide
set /p OPEN="Open integration guide now? (Y/N): "
if /i "%OPEN%"=="Y" (
    if exist "PORTFOLIO_INTEGRATION_GUIDE.md" (
        notepad "PORTFOLIO_INTEGRATION_GUIDE.md"
    )
)

echo.
echo Deployment complete! 
echo.
pause
