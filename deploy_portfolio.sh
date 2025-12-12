#!/bin/bash

################################################################################
# AWS WAF Advisor - Multi-Account Portfolio Deployment Script
# 
# This script automates the deployment of multi-account portfolio functionality
# 
# Usage: bash deploy_portfolio.sh
################################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="aws-waf-advisor"
BACKUP_DIR="backups/portfolio_deployment_$(date +%Y%m%d_%H%M%S)"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}AWS WAF Advisor - Portfolio Deployment${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Function to print colored messages
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if project directory exists
if [ ! -d "$PROJECT_DIR" ]; then
    print_error "Project directory '$PROJECT_DIR' not found!"
    echo ""
    read -p "Enter your project directory path: " PROJECT_DIR
    
    if [ ! -d "$PROJECT_DIR" ]; then
        print_error "Directory still not found. Exiting."
        exit 1
    fi
fi

print_success "Found project directory: $PROJECT_DIR"
echo ""

# Create backup directory
print_info "Creating backup directory..."
mkdir -p "$BACKUP_DIR"
print_success "Backup directory created: $BACKUP_DIR"
echo ""

# Step 1: Backup existing files
print_info "Step 1: Backing up existing files..."

if [ -f "$PROJECT_DIR/pdf_report_generator.py" ]; then
    cp "$PROJECT_DIR/pdf_report_generator.py" "$BACKUP_DIR/pdf_report_generator.py.backup"
    print_success "Backed up pdf_report_generator.py"
fi

if [ -f "$PROJECT_DIR/waf_review_module.py" ]; then
    cp "$PROJECT_DIR/waf_review_module.py" "$BACKUP_DIR/waf_review_module.py.backup"
    print_success "Backed up waf_review_module.py"
fi

if [ -f "$PROJECT_DIR/app.py" ]; then
    cp "$PROJECT_DIR/app.py" "$BACKUP_DIR/app.py.backup"
    print_success "Backed up app.py"
fi

echo ""

# Step 2: Copy new files
print_info "Step 2: Copying new portfolio files..."

# Core files
FILES_TO_COPY=(
    "portfolio_data_model.py"
    "multi_account_scanner.py"
    "waf_portfolio_integration.py"
)

for file in "${FILES_TO_COPY[@]}"; do
    if [ -f "$file" ]; then
        cp "$file" "$PROJECT_DIR/"
        print_success "Copied $file"
    else
        print_warning "$file not found in current directory"
    fi
done

echo ""

# Step 3: Replace PDF generator
print_info "Step 3: Replacing PDF generator..."

if [ -f "pdf_report_generator_MULTI_ACCOUNT.py" ]; then
    cp "pdf_report_generator_MULTI_ACCOUNT.py" "$PROJECT_DIR/pdf_report_generator.py"
    print_success "Replaced pdf_report_generator.py with multi-account version"
else
    print_error "pdf_report_generator_MULTI_ACCOUNT.py not found!"
    print_warning "You'll need to manually copy this file"
fi

echo ""

# Step 4: Check Python dependencies
print_info "Step 4: Checking Python dependencies..."

python3 -c "import boto3" 2>/dev/null
if [ $? -eq 0 ]; then
    print_success "boto3 is installed"
else
    print_warning "boto3 not found. Install with: pip install boto3"
fi

python3 -c "import reportlab" 2>/dev/null
if [ $? -eq 0 ]; then
    print_success "reportlab is installed"
else
    print_warning "reportlab not found. Install with: pip install reportlab"
fi

python3 -c "import streamlit" 2>/dev/null
if [ $? -eq 0 ]; then
    print_success "streamlit is installed"
else
    print_warning "streamlit not found. Install with: pip install streamlit"
fi

echo ""

# Step 5: Create integration notes
print_info "Step 5: Creating integration notes..."

cat > "$PROJECT_DIR/PORTFOLIO_INTEGRATION_NOTES.md" << 'EOF'
# Portfolio Integration Notes

## Files Added:
1. portfolio_data_model.py - Data structures and utilities
2. multi_account_scanner.py - Multi-account AWS scanner
3. waf_portfolio_integration.py - Streamlit UI integration
4. pdf_report_generator.py - Updated (auto-detects portfolios)

## Next Steps:

### 1. Add Import to Your Main File

In your `app.py` or `waf_review_module.py`, add:

```python
from waf_portfolio_integration import (
    render_assessment_type_selector,
    render_portfolio_workflow,
    is_portfolio_assessment
)
```

### 2. Add UI Toggle

In your assessment creation section, add:

```python
assessment_type = render_assessment_type_selector()

if assessment_type == "Multi-Account Portfolio":
    render_portfolio_workflow()
else:
    # Your existing single-account code
    pass
```

### 3. Update Scan Handler

In your AWS scan section:

```python
if is_portfolio_assessment(assessment):
    from waf_portfolio_integration import handle_portfolio_scan
    handle_portfolio_scan(assessment)
else:
    # Your existing scan code
    run_single_account_scan(assessment)
```

### 4. Test

1. Run: `streamlit run app.py`
2. Select "Multi-Account Portfolio"
3. Create portfolio with 2 accounts
4. Export PDF

## Rollback

If you need to rollback, your original files are backed up in:
`backups/portfolio_deployment_YYYYMMDD_HHMMSS/`

To restore:
```bash
cp backups/portfolio_deployment_YYYYMMDD_HHMMSS/*.backup .
```

## Support

See:
- MULTI_ACCOUNT_DEPLOYMENT_GUIDE.md - Complete guide
- MULTI_ACCOUNT_QUICK_REF.md - Quick reference
- app_integration_example.py - Full integration example
EOF

print_success "Created PORTFOLIO_INTEGRATION_NOTES.md"
echo ""

# Step 6: Summary
print_success "=========================================="
print_success "Deployment Complete!"
print_success "=========================================="
echo ""

echo -e "${GREEN}Files copied:${NC}"
echo "  ✓ portfolio_data_model.py"
echo "  ✓ multi_account_scanner.py"
echo "  ✓ waf_portfolio_integration.py"
echo "  ✓ pdf_report_generator.py (updated)"
echo ""

echo -e "${GREEN}Backups created in:${NC}"
echo "  📁 $BACKUP_DIR/"
echo ""

echo -e "${YELLOW}Next Steps:${NC}"
echo "  1. Review: $PROJECT_DIR/PORTFOLIO_INTEGRATION_NOTES.md"
echo "  2. Add imports to your main file (see notes)"
echo "  3. Add UI toggle for portfolio selection (see notes)"
echo "  4. Test: streamlit run $PROJECT_DIR/app.py"
echo ""

echo -e "${BLUE}Documentation:${NC}"
echo "  📖 MULTI_ACCOUNT_DEPLOYMENT_GUIDE.md - Complete guide"
echo "  ⚡ MULTI_ACCOUNT_QUICK_REF.md - Quick reference"
echo "  📝 app_integration_example.py - Full example"
echo ""

print_info "Ready to integrate! Follow the steps in PORTFOLIO_INTEGRATION_NOTES.md"
echo ""

# Optional: Open integration notes
read -p "Open integration notes now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if command -v code &> /dev/null; then
        code "$PROJECT_DIR/PORTFOLIO_INTEGRATION_NOTES.md"
    elif command -v nano &> /dev/null; then
        nano "$PROJECT_DIR/PORTFOLIO_INTEGRATION_NOTES.md"
    else
        cat "$PROJECT_DIR/PORTFOLIO_INTEGRATION_NOTES.md"
    fi
fi

print_success "Deployment script complete!"
