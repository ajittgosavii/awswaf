# 🚀 QUICK START - 5 Minutes to Deploy!

## What You're Getting
✅ Multi-account AWS scanning
✅ All AWS regions support  
✅ FREE Streamlit Cloud hosting
✅ 30-minute setup, $0/month cost

---

## 3 Simple Steps

### 1️⃣ Push to GitHub (2 min)
```bash
git add .
git commit -m "Deploy WAF Advisor"
git push origin main
```

### 2️⃣ Deploy to Streamlit (3 min)
1. Go to https://share.streamlit.io
2. Click "New app"
3. Select your repository
4. Click "Deploy"

### 3️⃣ Add Secrets (5 min)
In Streamlit Cloud dashboard → Settings → Secrets:

```toml
ANTHROPIC_API_KEY = "sk-ant-your-key"

[aws]
access_key_id = "AKIA..."
secret_access_key = "your-secret"
default_region = "us-east-1"
```

**Done! Your app is live! 🎉**

---

## Want Multi-Account?

### Step A: Generate External ID
```bash
openssl rand -base64 32
```

### Step B: Create Role in Each Account
```bash
aws iam create-role \
  --role-name WAFAdvisorCrossAccountRole \
  --assume-role-policy-document file://trust-policy.json

aws iam attach-role-policy \
  --role-name WAFAdvisorCrossAccountRole \
  --policy-arn arn:aws:iam::aws:policy/ReadOnlyAccess
```

**trust-policy.json:**
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"AWS": "arn:aws:iam::YOUR_HUB_ACCOUNT:root"},
    "Action": "sts:AssumeRole",
    "Condition": {
      "StringEquals": {"sts:ExternalId": "YOUR_EXTERNAL_ID"}
    }
  }]
}
```

### Step C: Add to Secrets
```toml
[accounts]
[[accounts.list]]
account_id = "123456789012"
account_name = "Production"
role_arn = "arn:aws:iam::123456789012:role/WAFAdvisorCrossAccountRole"
external_id = "your-external-id"
regions = ["us-east-1", "us-west-2"]
priority = "high"
```

---

## Files You Got

**New Files (Multi-Account):**
- `multi_account_manager.py` - Core logic
- `config_loader.py` - Secrets loader
- `STREAMLIT_DEPLOYMENT.md` - Full guide
- `QUICK_START.md` - This file

**Updated Files:**
- `aws_connector.py` - Now has multi-account mode
- `requirements.txt` - Added pyyaml
- `.streamlit/secrets.toml.template` - Multi-account config

**Original Files:** All kept intact!

---

## Cost: $0/month 🎉

**Streamlit Cloud Free Tier:**
- Unlimited public apps
- 1 GB RAM (enough for 10 accounts)
- Auto-deployment from GitHub
- HTTPS included

**Want private apps?** Upgrade to Team ($250/month)

---

## Need Help?

**Full Guide:** See `STREAMLIT_DEPLOYMENT.md`

**Troubleshooting:**
- External ID mismatch? Check both sides match
- Access denied? Test with `aws sts assume-role`
- Secrets error? Check TOML formatting

**Test Locally First:**
```bash
cp .streamlit/secrets.toml.template .streamlit/secrets.toml
# Edit with your values
streamlit run streamlit_app.py
```

---

## What's Next?

1. ✅ Deploy (done!)
2. ✅ Test single account
3. ✅ Add more accounts
4. ✅ Scan regularly
5. ✅ Fix findings

**You're production-ready! 🚀**

---

**Questions?** See STREAMLIT_DEPLOYMENT.md or open an issue.

**Version:** 3.0.0  
**Setup Time:** 30 minutes  
**Cost:** $0/month
