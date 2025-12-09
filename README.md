# AWS Well-Architected Framework Advisor
## Enterprise Edition v2.0.0

An AI-powered, enterprise-grade platform for comprehensive AWS architecture review aligned with the AWS Well-Architected Framework.

---

## 🎯 Features Overview

### 📊 Executive Dashboard
- Real-time WAF score visualization
- Risk level assessment (Critical/High/Medium/Low)
- Pillar performance breakdown
- Priority findings with quick actions
- Resource inventory summary

### 🎯 AWS Landscape Scanner
- **17 Detailed Findings** with remediation steps
- **6 WAF Pillars** fully assessed
- Compliance framework mapping (SOC 2, HIPAA, PCI DSS, GDPR)
- Cost savings estimates per finding
- AWS documentation links
- Demo mode with realistic sample data
- Live mode for real AWS scanning

### 📤 Architecture Review (AI-Powered)
- Upload architecture diagrams (PNG, JPG, WebP)
- Paste CloudFormation/Terraform code
- Text description analysis
- AI-powered assessment using Claude
- Workload-specific analysis
- Compliance requirement mapping

### 🚀 EKS & Container Modernization
- **5 Technology Categories**: Autoscaling, Service Mesh, GitOps, Observability, Security
- **Technology Comparisons**:
  - Karpenter vs Cluster Autoscaler
  - Istio vs AWS App Mesh vs Linkerd
  - ArgoCD vs Flux CD
  - Prometheus/Grafana vs CloudWatch vs Datadog
- **Detailed Implementation Guides** with actual commands
- **CI/CD Maturity Assessment** (5 levels)
- **AI-Powered Recommendations** personalized to your context

### 💰 FinOps & Cost Optimization
- **8 Optimization Strategies**: Reserved Instances, Savings Plans, Spot, Right-sizing, Graviton, Storage Tiering, Idle Cleanup, Scheduling
- Cost breakdown analysis by category
- AI-powered cost analysis
- Commitment discount advisor
- Waste detector
- FinOps maturity assessment (Crawl/Walk/Run)

### 📋 Compliance & Governance
- **8 Compliance Frameworks**: SOC 2, HIPAA, PCI DSS, GDPR, ISO 27001, FedRAMP, NIST CSF, CIS AWS
- Gap analysis with scoring
- Control mapping across frameworks
- AWS compliance services integration
- Audit preparation checklist

### 🔄 Migration & Disaster Recovery
- **7Rs Migration Strategies**: Rehost, Replatform, Repurchase, Refactor, Retire, Retain, Relocate
- **4 DR Patterns**: Backup & Restore, Pilot Light, Warm Standby, Active-Active
- RTO/RPO calculator
- Migration readiness assessment
- Implementation timelines

### 📚 Knowledge Base
- WAF pillar reference with focus areas
- Best practices by category
- Design principles
- External resource links

### 📥 Export Capabilities
- **PDF Reports**: Professional executive-ready reports
- **JSON Export**: Full assessment data for integration
- **CSV Export**: Findings spreadsheet for analysis

---

## 📦 Package Contents

```
aws-waf-advisor-enterprise/
├── streamlit_app.py          # Main application (922 lines)
├── landscape_scanner.py      # AWS scanner module (934 lines)
├── eks_modernization.py      # EKS & modernization (1,183 lines)
├── finops_module.py          # FinOps module (639 lines)
├── compliance_module.py      # Compliance module (513 lines)
├── migration_dr_module.py    # Migration & DR (727 lines)
├── aws_connector.py          # AWS connection (359 lines)
├── pdf_report_generator.py   # PDF reports (424 lines)
├── requirements.txt          # Dependencies
├── sample_architecture.json  # Sample test file
├── README.md                 # This file
└── .streamlit/
    ├── config.toml           # Streamlit theme
    └── secrets.toml.template # Secrets template
```

**Total: 5,701 lines of Python code**

---

## 🚀 Quick Start

### 1. Clone and Install

```bash
git clone <your-repo>
cd aws-waf-advisor-enterprise
pip install -r requirements.txt
```

### 2. Configure Secrets

Copy `.streamlit/secrets.toml.template` to `.streamlit/secrets.toml`:

```toml
# Anthropic API Key for AI features
ANTHROPIC_API_KEY = "sk-ant-..."

# AWS Credentials
[aws]
access_key_id = "AKIA..."
secret_access_key = "..."
default_region = "us-east-1"
```

### 3. Run Locally

```bash
streamlit run streamlit_app.py
```

---

## ☁️ Streamlit Cloud Deployment

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Deploy WAF Advisor"
git push origin main
```

### Step 2: Deploy on Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Select your repository
4. Main file: `streamlit_app.py`
5. Click "Deploy"

### Step 3: Configure Secrets
In Streamlit Cloud dashboard → Settings → Secrets:

```toml
ANTHROPIC_API_KEY = "sk-ant-api03-..."

[aws]
access_key_id = "AKIA..."
secret_access_key = "..."
default_region = "us-east-1"
```

---

## 🔧 Configuration Options

### Environment Variables
- `ANTHROPIC_API_KEY`: Claude AI API key
- `AWS_ACCESS_KEY_ID`: AWS access key
- `AWS_SECRET_ACCESS_KEY`: AWS secret key
- `AWS_REGION`: Default AWS region

### Streamlit Secrets Formats

**Format 1: Nested (Recommended)**
```toml
ANTHROPIC_API_KEY = "sk-ant-..."

[aws]
access_key_id = "AKIA..."
secret_access_key = "..."
default_region = "us-east-1"
```

**Format 2: Flat**
```toml
ANTHROPIC_API_KEY = "sk-ant-..."
AWS_ACCESS_KEY_ID = "AKIA..."
AWS_SECRET_ACCESS_KEY = "..."
AWS_REGION = "us-east-1"
```

---

## 📋 Requirements

### Python Packages
```
streamlit>=1.28.0
anthropic>=0.18.0
boto3>=1.34.0
botocore>=1.34.0
reportlab>=4.0.0
Pillow>=10.0.0
pandas>=2.0.0
python-dateutil>=2.8.0
```

### AWS Permissions (for Live Mode)
Recommended IAM policy for scanning:
- `ec2:Describe*`
- `s3:ListBuckets`, `s3:GetBucketAcl`
- `rds:DescribeDBInstances`
- `iam:ListUsers`, `iam:ListMFADevices`
- `cloudtrail:DescribeTrails`
- `vpc:Describe*`

---

## 🎭 Demo Mode vs Live Mode

### Demo Mode
- Uses comprehensive sample data
- No AWS credentials required
- Full functionality demonstration
- 17 realistic findings across all pillars

### Live Mode
- Connects to your AWS account
- Real-time resource scanning
- Actual findings from your environment
- Requires valid AWS credentials

---

## 📊 Assessment Metrics

### WAF Score Calculation
- **Security**: Weight 1.5x
- **Reliability**: Weight 1.3x
- **Performance**: Weight 1.0x
- **Cost Optimization**: Weight 1.0x
- **Operational Excellence**: Weight 0.9x
- **Sustainability**: Weight 0.8x

### Risk Levels
- **Low**: Score ≥ 80
- **Medium**: Score 60-79
- **High**: Score 40-59
- **Critical**: Score < 40

---

## 🔒 Security Considerations

1. **Never commit secrets** to version control
2. Use **Streamlit Secrets** for cloud deployment
3. Apply **least privilege** IAM permissions
4. Enable **MFA** on AWS accounts
5. Rotate credentials regularly

---

## 📈 Enterprise Features

- ✅ Multi-module architecture
- ✅ AI-powered analysis (Claude)
- ✅ Comprehensive WAF coverage
- ✅ Professional PDF reports
- ✅ Export capabilities (PDF, JSON, CSV)
- ✅ Demo mode for presentations
- ✅ Live AWS scanning
- ✅ Technology comparisons
- ✅ Implementation guides
- ✅ Compliance mapping
- ✅ Cost optimization
- ✅ Migration planning
- ✅ DR strategy

---

## 📞 Support

For issues or feature requests, please open a GitHub issue.

---

## 📄 License

Enterprise Edition - All rights reserved.

---

**Built with ❤️ using Claude AI by Anthropic**
