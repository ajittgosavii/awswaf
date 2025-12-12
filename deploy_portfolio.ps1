################################################################################
# AWS WAF Advisor - Multi-Account Portfolio Deployment Script (Windows)
# 
# PowerShell script for Windows deployment
# 
# Usage: 
#   Right-click this file and select "Run with PowerShell"
#   OR
#   Open PowerShell and run: .\deploy_portfolio.ps1
################################################################################

# Set execution policy for this session (if needed)
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force

# Colors
$Green = "Green"
$Red = "Red"
$Yellow = "Yellow"
$Blue = "Cyan"

# Configuration
$ProjectDir = "aws-waf-advisor"
$BackupDir = "backups\portfolio_deployment_$(Get-Date -Format 'yyyyMMdd_HHmmss')"

Write-Host "========================================" -ForegroundColor $Blue
Write-Host "AWS WAF Advisor - Portfolio Deployment" -ForegroundColor $Blue
Write-Host "========================================" -ForegroundColor $Blue
Write-Host ""

# Function to print colored messages
function Print-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor $Green
}

function Print-Error {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor $Red
}

function Print-Warning {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor $Yellow
}

function Print-Info {
    param([string]$Message)
    Write-Host "ℹ️  $Message" -ForegroundColor $Blue
}

# Check if project directory exists
if (-not (Test-Path $ProjectDir)) {
    Print-Error "Project directory '$ProjectDir' not found!"
    Write-Host ""
    $ProjectDir = Read-Host "Enter your project directory path"
    
    if (-not (Test-Path $ProjectDir)) {
        Print-Error "Directory still not found. Exiting."
        exit 1
    }
}

Print-Success "Found project directory: $ProjectDir"
Write-Host ""

# Create backup directory
Print-Info "Creating backup directory..."
New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
Print-Success "Backup directory created: $BackupDir"
Write-Host ""

# Step 1: Backup existing files
Print-Info "Step 1: Backing up existing files..."

if (Test-Path "$ProjectDir\pdf_report_generator.py") {
    Copy-Item "$ProjectDir\pdf_report_generator.py" "$BackupDir\pdf_report_generator.py.backup"
    Print-Success "Backed up pdf_report_generator.py"
}

if (Test-Path "$ProjectDir\waf_review_module.py") {
    Copy-Item "$ProjectDir\waf_review_module.py" "$BackupDir\waf_review_module.py.backup"
    Print-Success "Backed up waf_review_module.py"
}

if (Test-Path "$ProjectDir\app.py") {
    Copy-Item "$ProjectDir\app.py" "$BackupDir\app.py.backup"
    Print-Success "Backed up app.py"
}

Write-Host ""

# Step 2: Copy new files
Print-Info "Step 2: Copying new portfolio files..."

$FilesToCopy = @(
    "portfolio_data_model.py",
    "multi_account_scanner.py",
    "waf_portfolio_integration.py"
)

foreach ($file in $FilesToCopy) {
    if (Test-Path $file) {
        Copy-Item $file "$ProjectDir\"
        Print-Success "Copied $file"
    } else {
        Print-Warning "$file not found in current directory"
    }
}

Write-Host ""

# Step 3: Replace PDF generator
Print-Info "Step 3: Replacing PDF generator..."

if (Test-Path "pdf_report_generator_MULTI_ACCOUNT.py") {
    Copy-Item "pdf_report_generator_MULTI_ACCOUNT.py" "$ProjectDir\pdf_report_generator.py"
    Print-Success "Replaced pdf_report_generator.py with multi-account version"
} else {
    Print-Error "pdf_report_generator_MULTI_ACCOUNT.py not found!"
    Print-Warning "You'll need to manually copy this file"
}

Write-Host ""

# Step 4: Check Python dependencies
Print-Info "Step 4: Checking Python dependencies..."

$dependencies = @("boto3", "reportlab", "streamlit")

foreach ($package in $dependencies) {
    try {
        python -c "import $package" 2>$null
        if ($LASTEXITCODE -eq 0) {
            Print-Success "$package is installed"
        } else {
            Print-Warning "$package not found. Install with: pip install $package"
        }
    } catch {
        Print-Warning "$package not found. Install with: pip install $package"
    }
}

Write-Host ""

# Step 5: Create integration notes
Print-Info "Step 5: Creating integration notes..."

$IntegrationNotes = @"
# Portfolio Integration Notes

## Files Added:
1. portfolio_data_model.py - Data structures and utilities
2. multi_account_scanner.py - Multi-account AWS scanner
3. waf_portfolio_integration.py - Streamlit UI integration
4. pdf_report_generator.py - Updated (auto-detects portfolios)

## Next Steps:

### 1. Add Import to Your Main File

In your app.py or waf_review_module.py, add:

``````python
from waf_portfolio_integration import (
    render_assessment_type_selector,
    render_portfolio_workflow,
    is_portfolio_assessment
)
``````

### 2. Add UI Toggle

In your assessment creation section, add:

``````python
assessment_type = render_assessment_type_selector()

if assessment_type == "Multi-Account Portfolio":
    render_portfolio_workflow()
else:
    # Your existing single-account code
    pass
``````

### 3. Update Scan Handler

In your AWS scan section:

``````python
if is_portfolio_assessment(assessment):
    from waf_portfolio_integration import handle_portfolio_scan
    handle_portfolio_scan(assessment)
else:
    # Your existing scan code
    run_single_account_scan(assessment)
``````

### 4. Test

1. Run: streamlit run app.py
2. Select "Multi-Account Portfolio"
3. Create portfolio with 2 accounts
4. Export PDF

## Rollback

If you need to rollback, your original files are backed up in:
backups\portfolio_deployment_YYYYMMDD_HHMMSS\

To restore:
``````powershell
Copy-Item backups\portfolio_deployment_YYYYMMDD_HHMMSS\*.backup .
``````

## Support

See:
- MULTI_ACCOUNT_DEPLOYMENT_GUIDE.md - Complete guide
- MULTI_ACCOUNT_QUICK_REF.md - Quick reference
- app_integration_example.py - Full integration example
"@

$IntegrationNotes | Out-File -FilePath "$ProjectDir\PORTFOLIO_INTEGRATION_NOTES.md" -Encoding UTF8
Print-Success "Created PORTFOLIO_INTEGRATION_NOTES.md"
Write-Host ""

# Step 6: Summary
Write-Host "==========================================" -ForegroundColor $Green
Write-Host "Deployment Complete!" -ForegroundColor $Green
Write-Host "==========================================" -ForegroundColor $Green
Write-Host ""

Write-Host "Files copied:" -ForegroundColor $Green
Write-Host "  ✓ portfolio_data_model.py"
Write-Host "  ✓ multi_account_scanner.py"
Write-Host "  ✓ waf_portfolio_integration.py"
Write-Host "  ✓ pdf_report_generator.py (updated)"
Write-Host ""

Write-Host "Backups created in:" -ForegroundColor $Green
Write-Host "  📁 $BackupDir\"
Write-Host ""

Write-Host "Next Steps:" -ForegroundColor $Yellow
Write-Host "  1. Review: $ProjectDir\PORTFOLIO_INTEGRATION_NOTES.md"
Write-Host "  2. Add imports to your main file (see notes)"
Write-Host "  3. Add UI toggle for portfolio selection (see notes)"
Write-Host "  4. Test: streamlit run $ProjectDir\app.py"
Write-Host ""

Write-Host "Documentation:" -ForegroundColor $Blue
Write-Host "  📖 MULTI_ACCOUNT_DEPLOYMENT_GUIDE.md - Complete guide"
Write-Host "  ⚡ MULTI_ACCOUNT_QUICK_REF.md - Quick reference"
Write-Host "  📝 app_integration_example.py - Full example"
Write-Host ""

Print-Info "Ready to integrate! Follow the steps in PORTFOLIO_INTEGRATION_NOTES.md"
Write-Host ""

# Optional: Open integration notes
$response = Read-Host "Open integration notes now? (Y/N)"
if ($response -eq "Y" -or $response -eq "y") {
    if (Test-Path "$ProjectDir\PORTFOLIO_INTEGRATION_NOTES.md") {
        notepad "$ProjectDir\PORTFOLIO_INTEGRATION_NOTES.md"
    }
}

Print-Success "Deployment script complete!"
Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
