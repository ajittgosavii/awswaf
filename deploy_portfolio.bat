@echo off
REM ============================================================================
REM AWS WAF Advisor - Multi-Account Portfolio Deployment Script (Windows)
REM 
REM Simple batch file for Windows deployment
REM 
REM Usage: Double-click this file OR run: deploy_portfolio.bat
REM ============================================================================

echo.
echo ========================================
echo AWS WAF Advisor - Portfolio Deployment
echo ========================================
echo.

REM Configuration
set PROJECT_DIR=aws-waf-advisor

REM Check if project directory exists
if not exist "%PROJECT_DIR%" (
    echo ERROR: Project directory '%PROJECT_DIR%' not found!
    echo.
    set /p PROJECT_DIR="Enter your project directory path: "
    
    if not exist "%PROJECT_DIR%" (
        echo ERROR: Directory still not found. Exiting.
        pause
        exit /b 1
    )
)

echo SUCCESS: Found project directory: %PROJECT_DIR%
echo.

REM Create backup directory
set BACKUP_DIR=backups\portfolio_deployment_%date:~-4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set BACKUP_DIR=%BACKUP_DIR: =0%
echo Creating backup directory...
mkdir "%BACKUP_DIR%" 2>nul
echo SUCCESS: Backup directory created: %BACKUP_DIR%
echo.

REM Step 1: Backup existing files
echo Step 1: Backing up existing files...

if exist "%PROJECT_DIR%\pdf_report_generator.py" (
    copy "%PROJECT_DIR%\pdf_report_generator.py" "%BACKUP_DIR%\pdf_report_generator.py.backup" >nul
    echo SUCCESS: Backed up pdf_report_generator.py
)

if exist "%PROJECT_DIR%\waf_review_module.py" (
    copy "%PROJECT_DIR%\waf_review_module.py" "%BACKUP_DIR%\waf_review_module.py.backup" >nul
    echo SUCCESS: Backed up waf_review_module.py
)

if exist "%PROJECT_DIR%\app.py" (
    copy "%PROJECT_DIR%\app.py" "%BACKUP_DIR%\app.py.backup" >nul
    echo SUCCESS: Backed up app.py
)

echo.

REM Step 2: Copy new files
echo Step 2: Copying new portfolio files...

if exist "portfolio_data_model.py" (
    copy "portfolio_data_model.py" "%PROJECT_DIR%\" >nul
    echo SUCCESS: Copied portfolio_data_model.py
) else (
    echo WARNING: portfolio_data_model.py not found
)

if exist "multi_account_scanner.py" (
    copy "multi_account_scanner.py" "%PROJECT_DIR%\" >nul
    echo SUCCESS: Copied multi_account_scanner.py
) else (
    echo WARNING: multi_account_scanner.py not found
)

if exist "waf_portfolio_integration.py" (
    copy "waf_portfolio_integration.py" "%PROJECT_DIR%\" >nul
    echo SUCCESS: Copied waf_portfolio_integration.py
) else (
    echo WARNING: waf_portfolio_integration.py not found
)

echo.

REM Step 3: Replace PDF generator
echo Step 3: Replacing PDF generator...

if exist "pdf_report_generator_MULTI_ACCOUNT.py" (
    copy "pdf_report_generator_MULTI_ACCOUNT.py" "%PROJECT_DIR%\pdf_report_generator.py" >nul
    echo SUCCESS: Replaced pdf_report_generator.py with multi-account version
) else (
    echo ERROR: pdf_report_generator_MULTI_ACCOUNT.py not found!
    echo WARNING: You'll need to manually copy this file
)

echo.

REM Step 4: Check Python dependencies
echo Step 4: Checking Python dependencies...

python -c "import boto3" 2>nul
if %errorlevel% equ 0 (
    echo SUCCESS: boto3 is installed
) else (
    echo WARNING: boto3 not found. Install with: pip install boto3
)

python -c "import reportlab" 2>nul
if %errorlevel% equ 0 (
    echo SUCCESS: reportlab is installed
) else (
    echo WARNING: reportlab not found. Install with: pip install reportlab
)

python -c "import streamlit" 2>nul
if %errorlevel% equ 0 (
    echo SUCCESS: streamlit is installed
) else (
    echo WARNING: streamlit not found. Install with: pip install streamlit
)

echo.

REM Step 5: Create integration notes
echo Step 5: Creating integration notes...

(
echo # Portfolio Integration Notes
echo.
echo ## Files Added:
echo 1. portfolio_data_model.py - Data structures and utilities
echo 2. multi_account_scanner.py - Multi-account AWS scanner
echo 3. waf_portfolio_integration.py - Streamlit UI integration
echo 4. pdf_report_generator.py - Updated ^(auto-detects portfolios^)
echo.
echo ## Next Steps:
echo.
echo ### 1. Add Import to Your Main File
echo.
echo In your app.py or waf_review_module.py, add:
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
echo In your assessment creation section, add:
echo.
echo ```python
echo assessment_type = render_assessment_type_selector^(^)
echo.
echo if assessment_type == "Multi-Account Portfolio":
echo     render_portfolio_workflow^(^)
echo else:
echo     # Your existing single-account code
echo     pass
echo ```
echo.
echo ### 3. Test
echo.
echo 1. Run: streamlit run app.py
echo 2. Select "Multi-Account Portfolio"
echo 3. Create portfolio with 2 accounts
echo 4. Export PDF
echo.
echo ## Rollback
echo.
echo Your original files are backed up in: %BACKUP_DIR%
echo.
echo ## Documentation
echo.
echo See:
echo - MULTI_ACCOUNT_DEPLOYMENT_GUIDE.md - Complete guide
echo - MULTI_ACCOUNT_QUICK_REF.md - Quick reference
echo - app_integration_example.py - Full example
) > "%PROJECT_DIR%\PORTFOLIO_INTEGRATION_NOTES.md"

echo SUCCESS: Created PORTFOLIO_INTEGRATION_NOTES.md
echo.

REM Summary
echo.
echo ==========================================
echo           Deployment Complete!
echo ==========================================
echo.
echo Files copied:
echo   - portfolio_data_model.py
echo   - multi_account_scanner.py
echo   - waf_portfolio_integration.py
echo   - pdf_report_generator.py ^(updated^)
echo.
echo Backups created in:
echo   - %BACKUP_DIR%
echo.
echo Next Steps:
echo   1. Review: %PROJECT_DIR%\PORTFOLIO_INTEGRATION_NOTES.md
echo   2. Add imports to your main file
echo   3. Add UI toggle for portfolio selection
echo   4. Test: streamlit run %PROJECT_DIR%\app.py
echo.
echo Documentation:
echo   - MULTI_ACCOUNT_DEPLOYMENT_GUIDE.md
echo   - MULTI_ACCOUNT_QUICK_REF.md
echo   - app_integration_example.py
echo.
echo Ready to integrate! Follow PORTFOLIO_INTEGRATION_NOTES.md
echo.

REM Open integration notes
set /p OPEN="Open integration notes now? (Y/N): "
if /i "%OPEN%"=="Y" (
    notepad "%PROJECT_DIR%\PORTFOLIO_INTEGRATION_NOTES.md"
)

echo.
echo SUCCESS: Deployment script complete!
echo.
pause
