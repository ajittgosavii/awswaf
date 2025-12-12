# Portfolio Integration Guide

## Deployment Complete! 

The following files are now in your project:
- portfolio_data_model.py
- multi_account_scanner.py  
- waf_portfolio_integration.py
- pdf_report_generator.py (UPDATED)

Backups saved in: backups\portfolio_deployment_2-12205-_004300

## Next Steps:

### 1. Add Imports to Your Main File

Open `app.py` or `waf_review_module.py` and add these imports at the top:

```python
from waf_portfolio_integration import (
    render_assessment_type_selector,
    render_portfolio_workflow,
    is_portfolio_assessment
)
```

### 2. Add UI Toggle

Find your assessment creation section and add:

```python
# Add assessment type selector
assessment_type = render_assessment_type_selector()

if assessment_type == "Multi-Account Portfolio":
    render_portfolio_workflow()
else:
    # Your existing single-account code
    pass
```

### 3. Test Locally

```bash
streamlit run app.py
```

Test both:
- Single Account (should work as before)
- Multi-Account Portfolio (new feature)

### 4. Deploy

```bash
git add .
git commit -m "Add multi-account portfolio support"
git push origin main
```

## Documentation

See:
- DEPLOYMENT_CHECKLIST.md - Step-by-step guide
- WINDOWS_DEPLOYMENT_GUIDE.md - Windows-specific help
- MULTI_ACCOUNT_DEPLOYMENT_GUIDE.md - Complete reference

## Rollback

If needed, restore from backup:
```bash
copy "backups\portfolio_deployment_2-12205-_004300\*.backup" .
```

## Support

Check the documentation files for help!
