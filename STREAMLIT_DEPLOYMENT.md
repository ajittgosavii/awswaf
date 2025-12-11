# 🚀 AWS WAF Advisor - Streamlit Cloud Deployment Guide
## Deploy in 30 Minutes - $0/month

---

## ⚡ Quick Start

### What You Get
- ✅ **FREE** Streamlit Cloud hosting
- ✅ Multi-account scanning (unlimited accounts)
- ✅ Multi-region scanning (all AWS regions)
- ✅ Parallel scanning (5 accounts, 10 regions)
- ✅ Auto-deployment from GitHub
- ✅ HTTPS included

### What You Need
- GitHub account (free)
- Streamlit Cloud account (free)
- AWS account(s) with IAM permissions
- Anthropic API key

---

## 📦 Step 1: Push to GitHub (5 minutes)

```bash
# In your project directory
git add .
git commit -m "Add multi-account support"
git push origin main
```

**Important:** Make sure `.gitignore` includes:
```
.streamlit/secrets.toml
*.pyc
__pycache__/
```

---

## 🌐 Step 2: Deploy to Streamlit Cloud (10 minutes)

### 2.1 Create App
1. Go to https://share.streamlit.io
2. Click "New app"
3. Select your repository
4. Main file: `streamlit_app.py`
5. Click "Deploy"

### 2.2 Configure Secrets

Click "Advanced settings" → "Secrets", then paste:

```toml
# Anthropic API Key
ANTHROPIC_API_KEY = "sk-ant-your-key-here"

# Hub Account Credentials
[aws]
access_key_id = "AKIA..."
secret_access_key = "your-secret-key"
default_region = "us-east-1"
```

**That's it for single-account mode!** Your app works now.

---

## 🌐 Step 3: Add Multi-Account Support (15 minutes)

### 3.1 Generate External IDs

For **each** account you want to scan:

```bash
openssl rand -base64 32
```

Save each output - you'll need them!

### 3.2 Create Cross-Account Roles

In **each spoke account**, run:

#### Create Trust Policy (`trust-policy.json`):
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {
      "AWS": "arn:aws:iam::YOUR_HUB_ACCOUNT_ID:root"
    },
    "Action": "sts:AssumeRole",
    "Condition": {
      "StringEquals": {
        "sts:ExternalId": "YOUR_EXTERNAL_ID_FOR_THIS_ACCOUNT"
      }
    }
  }]
}
```

Replace:
- `YOUR_HUB_ACCOUNT_ID` = Your hub AWS account ID
- `YOUR_EXTERNAL_ID_FOR_THIS_ACCOUNT` = The external ID you generated

#### Create the Role:
```bash
# Create role
aws iam create-role \
  --role-name WAFAdvisorCrossAccountRole \
  --assume-role-policy-document file://trust-policy.json

# Attach read-only access
aws iam attach-role-policy \
  --role-name WAFAdvisorCrossAccountRole \
  --policy-arn arn:aws:iam::aws:policy/ReadOnlyAccess
```

### 3.3 Add Accounts to Streamlit Secrets

In Streamlit Cloud → Settings → Secrets, **add** this section:

```toml
# Multi-Account Configuration
[accounts]

[[accounts.list]]
account_id = "123456789012"
account_name = "Production"
environment = "production"
role_arn = "arn:aws:iam::123456789012:role/WAFAdvisorCrossAccountRole"
external_id = "paste-external-id-for-this-account"
regions = ["us-east-1", "us-west-2"]
priority = "high"

[[accounts.list]]
account_id = "234567890123"
account_name = "Development"
environment = "development"
role_arn = "arn:aws:iam::234567890123:role/WAFAdvisorCrossAccountRole"
external_id = "paste-external-id-for-this-account"
regions = ["us-east-1"]
priority = "medium"
```

Click "Save" - app restarts automatically.

---

## ✅ Step 4: Test (5 minutes)

### Single Account Mode
1. Open your app: `https://your-app.streamlit.app`
2. Go to "AWS Connector" tab
3. Should show "✅ Connected to AWS"
4. Select regions
5. Run scan

### Multi-Account Mode
1. In "AWS Connector" tab
2. Select "🌐 Multi-Account" mode
3. You'll see your configured accounts
4. Select accounts to scan
5. Click "🚀 Scan Selected Accounts"

---

## 🔧 Common Issues & Solutions

### Issue: "Access Denied" when scanning accounts

**Cause:** External ID mismatch or role not created

**Fix:**
1. Verify external ID matches in both:
   - Streamlit secrets
   - IAM role trust policy
2. Test role assumption:
```bash
aws sts assume-role \
  --role-arn arn:aws:iam::ACCOUNT_ID:role/WAFAdvisorCrossAccountRole \
  --role-session-name test \
  --external-id YOUR_EXTERNAL_ID
```

### Issue: "No accounts configured"

**Cause:** Secrets not formatted correctly

**Fix:**
1. Check TOML formatting in Streamlit secrets
2. Each account must be `[[accounts.list]]` (double brackets)
3. Save and wait for app to restart

### Issue: App shows "Sleeping"

**Cause:** Free tier apps sleep after 7 days of inactivity

**Fix:**
- Visit the URL to wake it up (takes ~30 seconds)
- Or upgrade to Team plan ($250/month) for always-on

---

## 📊 Usage

### Scanning Single Account
1. Select "Single Account" mode
2. Choose regions
3. Click "Run Assessment"

### Scanning Multiple Accounts
1. Select "Multi-Account" mode
2. Check accounts to scan
3. Click "Scan Selected Accounts"
4. Results aggregated across all accounts

### Performance
- 1 account: ~5 minutes
- 5 accounts: ~12 minutes (parallel)
- 10 accounts: ~18 minutes (parallel)

---

## 💰 Cost

### Streamlit Cloud
- **Free Tier:** $0/month
  - 1 GB RAM
  - 1 CPU
  - Public apps
  - Apps sleep after 7 days

- **Team Tier:** $250/month (if needed)
  - 4 GB RAM
  - 4 CPUs
  - Private apps
  - No sleeping

### AWS Costs
- API calls: ~$0.01 per scan
- Data transfer: Minimal
- **Total:** $1-5/month for 100 scans

### Total: $0-5/month 🎉

Compare to full infrastructure: $800-1,100/month saved!

---

## 🔐 Security Best Practices

### External IDs
- ✅ Generate unique per account
- ✅ Use strong random strings (32+ characters)
- ✅ Never commit to Git
- ✅ Store only in Streamlit secrets

### IAM Roles
- ✅ Use read-only permissions
- ✅ Require external ID
- ✅ Limit to specific hub account
- ✅ Enable CloudTrail logging

### Credentials
- ✅ Rotate every 90 days
- ✅ Use IAM user (not root)
- ✅ Enable MFA (optional but recommended)
- ✅ Never commit to Git

---

## 📝 Adding New Accounts

### Quick Steps
1. Generate external ID: `openssl rand -base64 32`
2. Create IAM role in new account (see Step 3.2)
3. Add to Streamlit secrets (see Step 3.3)
4. Save - app restarts automatically
5. New account appears in UI

---

## 🎓 Tips & Tricks

### Testing Locally First
```bash
# Create .streamlit/secrets.toml (DO NOT commit!)
cp .streamlit/secrets.toml.template .streamlit/secrets.toml
nano .streamlit/secrets.toml  # Fill in your values

# Run locally
streamlit run streamlit_app.py

# Test thoroughly before pushing
```

### Monitoring
- Check Streamlit Cloud dashboard for errors
- Review scan results in app
- Monitor AWS CloudTrail for API calls

### Optimization
- Start with 2-3 accounts
- Test single region first
- Gradually add more accounts/regions
- Monitor memory usage

---

## 🔄 Updating Your App

### Code Changes
```bash
git add .
git commit -m "Update feature"
git push origin main
# Streamlit Cloud auto-deploys in ~2 minutes
```

### Configuration Changes
1. Streamlit Cloud → Settings → Secrets
2. Edit secrets
3. Click "Save"
4. App restarts automatically

---

## 🆘 Getting Help

### Documentation
- See `.streamlit/secrets.toml.template` for configuration examples
- Check README.md for feature documentation
- Review code comments for implementation details

### Testing
- Test role assumption with AWS CLI
- Check CloudTrail logs for access attempts
- Review Streamlit Cloud logs for errors

### Support
- GitHub Issues for bugs
- AWS documentation for IAM/STS
- Streamlit Community forum

---

## ✨ You're Done!

**Your WAF Advisor is now:**
- ✅ Deployed to Streamlit Cloud
- ✅ Accessible at your URL
- ✅ Ready for multi-account scanning
- ✅ Costing $0/month

**Next Steps:**
1. Share URL with your team
2. Add more accounts as needed
3. Schedule regular scans
4. Review findings
5. Improve security posture

---

## 📞 Quick Reference

### Essential Commands
```bash
# Generate external ID
openssl rand -base64 32

# Test role assumption
aws sts assume-role \
  --role-arn arn:aws:iam::ACCOUNT_ID:role/WAFAdvisorCrossAccountRole \
  --role-session-name test \
  --external-id EXTERNAL_ID

# Run locally
streamlit run streamlit_app.py
```

### Essential URLs
- **Streamlit Cloud:** https://share.streamlit.io
- **Your App:** https://your-app.streamlit.app
- **GitHub:** https://github.com/YOUR_USERNAME/waf-advisor

### Essential Files
- `streamlit_app.py` - Main application
- `multi_account_manager.py` - Multi-account logic
- `config_loader.py` - Secrets loader
- `requirements.txt` - Dependencies
- `.streamlit/secrets.toml.template` - Configuration template

---

**Congratulations! 🎉**

You've deployed an enterprise-grade AWS WAF assessment tool at **zero infrastructure cost**!

---

**Version:** 3.0.0  
**Last Updated:** December 11, 2025  
**Cost:** $0-5/month  
**Setup Time:** 30 minutes
