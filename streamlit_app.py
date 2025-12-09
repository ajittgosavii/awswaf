"""
AWS Well-Architected Framework Advisor - Enterprise Edition
AI-Powered Architecture Review & Risk Assessment Platform

Version: 2.1.0
"""

import streamlit as st
import json
import base64
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any, Tuple
import os

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="AWS Well-Architected Advisor | Enterprise",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# MODULE IMPORTS
# ============================================================================

MODULE_STATUS = {}
MODULE_ERRORS = {}

# Core libraries
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError as e:
    ANTHROPIC_AVAILABLE = False
    MODULE_ERRORS['anthropic'] = str(e)

try:
    import boto3
    from botocore.config import Config
    from botocore.exceptions import ClientError, NoCredentialsError
    BOTO3_AVAILABLE = True
except ImportError as e:
    BOTO3_AVAILABLE = False
    MODULE_ERRORS['boto3'] = str(e)

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

# Module imports with fallbacks
try:
    from aws_connector import (
        render_aws_connector_tab,
        get_aws_session,
        AWSCredentials,
        get_aws_credentials_from_secrets,
        test_aws_connection
    )
    MODULE_STATUS['AWS Connector'] = True
except Exception as e:
    MODULE_STATUS['AWS Connector'] = False
    MODULE_ERRORS['aws_connector'] = str(e)

try:
    from landscape_scanner import (
        render_landscape_scanner_tab,
        AWSLandscapeScanner,
        generate_demo_assessment,
        Finding,
        LandscapeAssessment,
        ResourceInventory,
        PillarScore
    )
    MODULE_STATUS['Landscape Scanner'] = True
except Exception as e:
    MODULE_STATUS['Landscape Scanner'] = False
    MODULE_ERRORS['landscape_scanner'] = str(e)

try:
    from eks_modernization import render_eks_modernization_tab
    MODULE_STATUS['EKS & Modernization'] = True
except Exception as e:
    MODULE_STATUS['EKS & Modernization'] = False
    MODULE_ERRORS['eks_modernization'] = str(e)

try:
    from finops_module import render_finops_tab
    MODULE_STATUS['FinOps'] = True
except Exception as e:
    MODULE_STATUS['FinOps'] = False
    MODULE_ERRORS['finops_module'] = str(e)

try:
    from compliance_module import render_compliance_tab
    MODULE_STATUS['Compliance'] = True
except Exception as e:
    MODULE_STATUS['Compliance'] = False
    MODULE_ERRORS['compliance_module'] = str(e)

try:
    from migration_dr_module import render_migration_dr_tab
    MODULE_STATUS['Migration & DR'] = True
except Exception as e:
    MODULE_STATUS['Migration & DR'] = False
    MODULE_ERRORS['migration_dr_module'] = str(e)

try:
    from pdf_report_generator import generate_comprehensive_waf_report
    MODULE_STATUS['PDF Reports'] = True
except Exception as e:
    MODULE_STATUS['PDF Reports'] = False
    MODULE_ERRORS['pdf_report_generator'] = str(e)

try:
    from architecture_patterns import render_architecture_patterns_tab
    MODULE_STATUS['Architecture Patterns'] = True
except Exception as e:
    MODULE_STATUS['Architecture Patterns'] = False
    MODULE_ERRORS['architecture_patterns'] = str(e)

# WAF Review Module - NEW
try:
    from waf_review_module import render_waf_review_tab
    MODULE_STATUS['WAF Review'] = True
except Exception as e:
    MODULE_STATUS['WAF Review'] = False
    MODULE_ERRORS['waf_review_module'] = str(e)

# ============================================================================
# STYLES
# ============================================================================

st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #232F3E 0%, #37475A 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .main-header h1 { color: #FF9900; margin: 0; font-size: 1.8rem; font-weight: 700; }
    .main-header p { color: #FFFFFF; margin: 0.3rem 0 0 0; opacity: 0.9; }
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 1.2rem;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.08);
        border: 1px solid #e0e0e0;
    }
    .metric-value { font-size: 2.2rem; font-weight: 700; color: #232F3E; }
    .metric-label { color: #666; font-size: 0.85rem; margin-top: 0.3rem; }
    .dashboard-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid #FF9900;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .pillar-card {
        background: white;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
        border: 1px solid #e0e0e0;
    }
    .finding-critical { border-left: 4px solid #D32F2F; }
    .finding-high { border-left: 4px solid #F57C00; }
    .finding-medium { border-left: 4px solid #FBC02D; }
    .finding-low { border-left: 4px solid #388E3C; }
    .status-connected { background: #E8F5E9; color: #2E7D32; padding: 0.5rem 1rem; border-radius: 8px; }
    .status-pending { background: #FFF3E0; color: #E65100; padding: 0.5rem 1rem; border-radius: 8px; }
    .app-footer {
        text-align: center;
        padding: 1rem;
        color: #666;
        font-size: 0.8rem;
        border-top: 1px solid #e0e0e0;
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# WAF PILLARS
# ============================================================================

WAF_PILLARS = {
    "security": {"name": "Security", "icon": "🔒", "color": "#D32F2F", "weight": 1.5},
    "reliability": {"name": "Reliability", "icon": "🛡️", "color": "#1976D2", "weight": 1.3},
    "performance": {"name": "Performance Efficiency", "icon": "⚡", "color": "#7B1FA2", "weight": 1.0},
    "cost": {"name": "Cost Optimization", "icon": "💰", "color": "#388E3C", "weight": 1.0},
    "operational_excellence": {"name": "Operational Excellence", "icon": "⚙️", "color": "#FF9900", "weight": 0.9},
    "sustainability": {"name": "Sustainability", "icon": "🌱", "color": "#00897B", "weight": 0.8}
}

# ============================================================================
# AWS CREDENTIALS AUTO-LOADING (ENHANCED)
# ============================================================================

def auto_load_aws_credentials() -> Tuple[bool, Optional[str], Optional[Dict]]:
    """
    Automatically load AWS credentials from Streamlit secrets.
    Returns: (success, message, identity_info)
    """
    if not BOTO3_AVAILABLE:
        return False, "boto3 not available", None
    
    try:
        # Check secrets availability
        if not hasattr(st, 'secrets'):
            return False, "No secrets configured", None
        
        secrets_keys = list(st.secrets.keys()) if st.secrets else []
        
        # Try multiple secret formats
        access_key = None
        secret_key = None
        region = 'us-east-1'
        
        # Format 1: [aws] section
        if 'aws' in st.secrets:
            aws_section = dict(st.secrets['aws'])
            access_key = (
                aws_section.get('access_key_id') or 
                aws_section.get('ACCESS_KEY_ID') or
                aws_section.get('aws_access_key_id') or
                aws_section.get('AWS_ACCESS_KEY_ID')
            )
            secret_key = (
                aws_section.get('secret_access_key') or 
                aws_section.get('SECRET_ACCESS_KEY') or
                aws_section.get('aws_secret_access_key') or
                aws_section.get('AWS_SECRET_ACCESS_KEY')
            )
            region = (
                aws_section.get('default_region') or 
                aws_section.get('region') or 
                aws_section.get('AWS_REGION') or
                aws_section.get('AWS_DEFAULT_REGION') or
                'us-east-1'
            )
        
        # Format 2: Flat keys
        if not access_key:
            access_key = st.secrets.get('AWS_ACCESS_KEY_ID')
            secret_key = st.secrets.get('AWS_SECRET_ACCESS_KEY')
            region = st.secrets.get('AWS_REGION', st.secrets.get('AWS_DEFAULT_REGION', 'us-east-1'))
        
        if not access_key or not secret_key:
            return False, "AWS credentials not found in secrets", None
        
        # Create session and test
        session = boto3.Session(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
        
        # Test connection
        sts = session.client('sts')
        identity = sts.get_caller_identity()
        
        # Store in session state
        st.session_state.aws_session = session
        st.session_state.aws_connected = True
        st.session_state.aws_region = region
        st.session_state.aws_identity = {
            'account': identity.get('Account'),
            'arn': identity.get('Arn'),
            'user_id': identity.get('UserId')
        }
        
        return True, f"Connected to account {identity.get('Account')}", st.session_state.aws_identity
        
    except ClientError as e:
        return False, f"AWS Error: {e.response['Error']['Message']}", None
    except Exception as e:
        return False, f"Error: {str(e)}", None

# ============================================================================
# SESSION STATE
# ============================================================================

def init_session_state():
    """Initialize session state with auto-loading"""
    defaults = {
        'anthropic_api_key': None,
        'aws_session': None,
        'aws_connected': False,
        'aws_identity': None,
        'aws_region': 'us-east-1',
        'app_mode': 'demo',
        'landscape_assessment': None,
        'analysis_results': None,
        'organization_context': '',
        'organization_name': '',
        'selected_pattern': 'microservices',
        'aws_auto_loaded': False
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    
    # Auto-load API key
    if not st.session_state.anthropic_api_key:
        st.session_state.anthropic_api_key = get_api_key()
    
    # Auto-load AWS credentials (only once)
    if not st.session_state.aws_auto_loaded and BOTO3_AVAILABLE:
        success, msg, identity = auto_load_aws_credentials()
        st.session_state.aws_auto_loaded = True
        if success:
            st.session_state.aws_connected = True

def get_api_key() -> Optional[str]:
    """Get Anthropic API key"""
    if st.session_state.get('anthropic_api_key'):
        return st.session_state.anthropic_api_key
    try:
        if hasattr(st, 'secrets'):
            if 'ANTHROPIC_API_KEY' in st.secrets:
                return st.secrets['ANTHROPIC_API_KEY']
            if 'anthropic' in st.secrets:
                return st.secrets['anthropic'].get('api_key')
    except:
        pass
    return os.environ.get('ANTHROPIC_API_KEY')

def get_anthropic_client():
    """Get Anthropic client"""
    if not ANTHROPIC_AVAILABLE:
        return None
    api_key = get_api_key()
    if not api_key:
        return None
    try:
        return anthropic.Anthropic(api_key=api_key)
    except:
        return None

# ============================================================================
# SIDEBAR
# ============================================================================

def render_sidebar():
    """Render sidebar"""
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0;">
            <img src="https://a0.awsstatic.com/libra-css/images/logos/aws_smile-header-desktop-en-white_59x35.png" width="60">
            <h3 style="color: #FF9900; margin: 0.5rem 0 0 0; font-size: 1rem;">Well-Architected Advisor</h3>
            <p style="color: #666; font-size: 0.75rem; margin: 0;">Enterprise Edition v2.1</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Mode Selection
        st.markdown("### 🎮 Operating Mode")
        mode = st.radio(
            "Select mode",
            ["🎭 Demo Mode", "🔴 Live Mode"],
            index=0 if st.session_state.get('app_mode', 'demo') == 'demo' else 1,
            horizontal=True
        )
        st.session_state.app_mode = 'demo' if 'Demo' in mode else 'live'
        
        if st.session_state.app_mode == 'demo':
            st.info("📋 Using sample data")
        else:
            if st.session_state.get('aws_connected'):
                st.success(f"✅ AWS Connected")
            else:
                st.warning("⚠️ AWS not connected")
        
        st.markdown("---")
        
        # Configuration Status
        st.markdown("### ⚙️ Configuration")
        
        # API Key Status
        if get_api_key():
            st.markdown('<div class="status-connected">✅ API Key configured</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-pending">⚠️ API Key needed</div>', unsafe_allow_html=True)
            with st.expander("🔑 Configure AI"):
                api_key = st.text_input("Anthropic API Key", type="password")
                if api_key:
                    st.session_state.anthropic_api_key = api_key
                    st.rerun()
        
        st.markdown("")
        
        # AWS Connection Status
        st.markdown("### 🔐 AWS Connection")
        
        if st.session_state.get('aws_connected'):
            identity = st.session_state.get('aws_identity', {})
            st.markdown(f"""
            <div class="status-connected">
                ✅ Connected<br>
                <small>Account: {identity.get('account', 'N/A')}</small><br>
                <small>Region: {st.session_state.get('aws_region', 'N/A')}</small>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🔄 Reconnect AWS"):
                st.session_state.aws_auto_loaded = False
                st.session_state.aws_connected = False
                st.rerun()
        else:
            st.markdown('<div class="status-pending">⚠️ Not connected</div>', unsafe_allow_html=True)
            
            if st.button("🔌 Connect to AWS"):
                success, msg, identity = auto_load_aws_credentials()
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
                    st.info("Configure AWS credentials in Streamlit secrets")
        
        st.markdown("---")
        
        # Module Status
        st.markdown("### 📦 Modules")
        loaded = sum(MODULE_STATUS.values())
        total = len(MODULE_STATUS)
        st.markdown(f"{'✅' if loaded == total else '⚠️'} {loaded}/{total} loaded")
        
        with st.expander("View Details"):
            for name, status in MODULE_STATUS.items():
                st.markdown(f"{'✅' if status else '❌'} {name}")
        
        st.markdown("---")
        
        # Organization Context
        st.markdown("### 🏢 Organization")
        org_name = st.text_input("Name", value=st.session_state.get('organization_name', ''))
        st.session_state.organization_name = org_name
        
        context = st.text_area("Context", value=st.session_state.get('organization_context', ''), height=60)
        st.session_state.organization_context = context
        
        st.markdown("---")
        
        # Quick Actions
        if st.button("📊 Quick Demo Assessment", use_container_width=True):
            if MODULE_STATUS.get('Landscape Scanner'):
                st.session_state.landscape_assessment = generate_demo_assessment()
                st.rerun()

# ============================================================================
# EXECUTIVE DASHBOARD
# ============================================================================

def render_executive_dashboard():
    """Render executive dashboard"""
    assessment = st.session_state.get('landscape_assessment')
    
    if not assessment:
        st.markdown("""
        <div style="text-align: center; padding: 3rem; background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%); border-radius: 12px;">
            <h2 style="color: #232F3E;">👋 Welcome to AWS Well-Architected Advisor</h2>
            <p style="color: #666; max-width: 600px; margin: 0 auto 2rem auto;">
                Enterprise-grade AI-powered architecture review platform with comprehensive implementation roadmaps, 
                cost analysis, and industry best practices.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown('<div class="dashboard-card"><h4>📊 1. Run Assessment</h4><p>Scan AWS or use demo</p></div>', unsafe_allow_html=True)
            if st.button("Run Demo", use_container_width=True):
                if MODULE_STATUS.get('Landscape Scanner'):
                    st.session_state.landscape_assessment = generate_demo_assessment()
                    st.rerun()
        with col2:
            st.markdown('<div class="dashboard-card"><h4>🏗️ 2. Architecture Patterns</h4><p>Best practices & roadmaps</p></div>', unsafe_allow_html=True)
        with col3:
            st.markdown('<div class="dashboard-card"><h4>💰 3. Cost Analysis</h4><p>TCO & optimization</p></div>', unsafe_allow_html=True)
        with col4:
            st.markdown('<div class="dashboard-card"><h4>📋 4. Compliance</h4><p>Multi-framework assessment</p></div>', unsafe_allow_html=True)
        return
    
    # Dashboard with data
    st.markdown("### 📊 Executive Dashboard")
    
    # Metrics row
    col1, col2, col3, col4, col5 = st.columns(5)
    
    score = assessment.overall_score
    score_color = "#388E3C" if score >= 80 else "#FBC02D" if score >= 60 else "#D32F2F"
    
    with col1:
        st.markdown(f'<div class="metric-card"><div class="metric-value" style="color: {score_color};">{score}</div><div class="metric-label">WAF Score</div></div>', unsafe_allow_html=True)
    with col2:
        risk_colors = {"Low": "#388E3C", "Medium": "#FBC02D", "High": "#F57C00", "Critical": "#D32F2F"}
        st.markdown(f'<div class="metric-card"><div class="metric-value" style="color: {risk_colors.get(assessment.overall_risk, "#666")}; font-size: 1.5rem;">{assessment.overall_risk}</div><div class="metric-label">Risk Level</div></div>', unsafe_allow_html=True)
    with col3:
        critical = sum(1 for f in assessment.findings if f.severity == 'CRITICAL')
        high = sum(1 for f in assessment.findings if f.severity == 'HIGH')
        st.markdown(f'<div class="metric-card"><div class="metric-value" style="color: #D32F2F;">{critical}<span style="font-size: 1rem; color: #666;"> / {high}</span></div><div class="metric-label">Critical / High</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{len(assessment.findings)}</div><div class="metric-label">Total Findings</div></div>', unsafe_allow_html=True)
    with col5:
        st.markdown(f'<div class="metric-card"><div class="metric-value" style="color: #388E3C;">${assessment.savings_opportunities:,.0f}</div><div class="metric-label">Monthly Savings</div></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Pillar Scores
    st.markdown("### 📈 Pillar Performance")
    cols = st.columns(6)
    for idx, (key, pillar) in enumerate(WAF_PILLARS.items()):
        with cols[idx]:
            ps = assessment.pillar_scores.get(pillar['name'])
            if ps:
                score = ps.score
                color = "#388E3C" if score >= 80 else "#FBC02D" if score >= 60 else "#D32F2F"
                findings = ps.findings_count
            else:
                score, color, findings = "-", "#666", 0
            st.markdown(f'<div class="pillar-card"><div style="font-size: 1.5rem;">{pillar["icon"]}</div><div style="font-size: 1.8rem; font-weight: 700; color: {color};">{score}</div><div style="font-size: 0.75rem; color: #666;">{pillar["name"].split()[0]}</div></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Priority findings
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("### 🚨 Priority Findings")
        priority_findings = sorted(assessment.findings, key=lambda f: {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}.get(f.severity, 4))[:5]
        for finding in priority_findings:
            sev_icon = {'CRITICAL': '🔴', 'HIGH': '🟠', 'MEDIUM': '🟡', 'LOW': '🟢'}.get(finding.severity, '⚪')
            st.markdown(f'<div class="dashboard-card finding-{finding.severity.lower()}"><strong>{sev_icon} {finding.title}</strong><p style="color: #666; margin: 0.3rem 0; font-size: 0.9rem;">{finding.description[:100]}...</p></div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 📦 Resources")
        inv = assessment.inventory
        resources = [("EC2", inv.ec2_instances), ("S3", inv.s3_buckets), ("RDS", inv.rds_instances), ("Lambda", inv.lambda_functions)]
        for name, count in resources:
            st.markdown(f"**{name}:** {count}")

# ============================================================================
# ARCHITECTURE REVIEW
# ============================================================================

def render_architecture_review_tab():
    """Render architecture review"""
    st.markdown('<div style="background: linear-gradient(135deg, #1565C0 0%, #1976D2 100%); padding: 1.5rem 2rem; border-radius: 12px; margin-bottom: 1.5rem;"><h2 style="color: white; margin: 0;">📤 Architecture Review</h2><p style="color: #BBDEFB; margin: 0;">AI-powered WAF analysis</p></div>', unsafe_allow_html=True)
    
    input_method = st.radio("Input Method", ["🖼️ Diagram", "📝 IaC", "✏️ Description"], horizontal=True)
    
    architecture_data = None
    image_data = None
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if "Diagram" in input_method:
            uploaded = st.file_uploader("Upload diagram", type=['png', 'jpg', 'jpeg', 'webp'])
            if uploaded:
                st.image(uploaded, use_container_width=True)
                image_data = {'data': base64.b64encode(uploaded.read()).decode('utf-8'), 'type': uploaded.type}
                uploaded.seek(0)
                architecture_data = f"[Diagram: {uploaded.name}]"
        elif "IaC" in input_method:
            code = st.text_area("CloudFormation/Terraform", height=300)
            if code:
                architecture_data = code
        else:
            desc = st.text_area("Describe architecture", height=300)
            if desc:
                architecture_data = desc
    
    with col2:
        workload_type = st.selectbox("Workload", ["General", "Web App", "Analytics", "Serverless", "Container"])
        compliance = st.multiselect("Compliance", ["SOC 2", "HIPAA", "PCI DSS", "GDPR"])
    
    if st.button("🔍 Analyze", type="primary", use_container_width=True):
        if not architecture_data:
            st.warning("Provide architecture information")
            return
        client = get_anthropic_client()
        if not client:
            st.error("Configure API key")
            return
        with st.spinner("Analyzing..."):
            results = analyze_architecture(client, architecture_data, {'workload': workload_type, 'compliance': compliance}, image_data)
        if results:
            st.session_state.analysis_results = results
            st.success("✅ Complete! View in WAF Results tab")

def analyze_architecture(client, architecture: str, context: Dict, image_data: Optional[Dict] = None) -> Dict:
    """AI architecture analysis"""
    prompt = f"""Analyze this AWS architecture against Well-Architected Framework:

ARCHITECTURE: {architecture}
CONTEXT: {context}

Return JSON with: executive_summary, overall_score (0-100), overall_risk, pillar_assessments (each with score, strengths, gaps, findings), remediation_roadmap (immediate/short_term/medium_term/long_term), estimated_savings.

Be specific with AWS services and best practices."""

    try:
        messages = [{"role": "user", "content": prompt}]
        if image_data:
            messages = [{"role": "user", "content": [
                {"type": "image", "source": {"type": "base64", "media_type": image_data['type'], "data": image_data['data']}},
                {"type": "text", "text": prompt}
            ]}]
        
        response = client.messages.create(model="claude-sonnet-4-20250514", max_tokens=8000, messages=messages)
        
        import re
        text = response.content[0].text
        json_match = re.search(r'\{[\s\S]*\}', text)
        if json_match:
            return json.loads(json_match.group())
    except Exception as e:
        st.error(f"Error: {e}")
    return None

# ============================================================================
# WAF RESULTS
# ============================================================================

def render_waf_results_tab():
    """Render WAF results"""
    results = st.session_state.get('analysis_results')
    assessment = st.session_state.get('landscape_assessment')
    
    if not results and not assessment:
        st.info("📋 No results. Run an assessment first.")
        if st.button("🎭 Generate Demo"):
            if MODULE_STATUS.get('Landscape Scanner'):
                st.session_state.landscape_assessment = generate_demo_assessment()
                st.rerun()
        return
    
    tabs = st.tabs(["📊 Overview", "📈 Pillars", "🚨 Findings", "🗺️ Roadmap", "📥 Export"])
    
    with tabs[0]:
        if results:
            st.markdown(f"**Executive Summary:** {results.get('executive_summary', '')}")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Score", f"{results.get('overall_score', 0)}/100")
            with col2:
                st.metric("Risk", results.get('overall_risk', 'Unknown'))
            with col3:
                findings = sum(len(p.get('findings', [])) for p in results.get('pillar_assessments', {}).values())
                st.metric("Findings", findings)
        elif assessment:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Score", f"{assessment.overall_score}/100")
            with col2:
                st.metric("Risk", assessment.overall_risk)
            with col3:
                st.metric("Findings", len(assessment.findings))
    
    with tabs[1]:
        if results:
            for pn, pd in results.get('pillar_assessments', {}).items():
                with st.expander(f"{pn} - Score: {pd.get('score', 0)}/100"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Strengths:**")
                        for s in pd.get('strengths', [])[:3]:
                            st.markdown(f"- {s}")
                    with col2:
                        st.markdown("**Gaps:**")
                        for g in pd.get('gaps', [])[:3]:
                            st.markdown(f"- {g}")
        elif assessment:
            for pn, ps in assessment.pillar_scores.items():
                with st.expander(f"{pn} - Score: {ps.score}/100"):
                    st.metric("Findings", ps.findings_count)
    
    with tabs[2]:
        if assessment:
            severity_filter = st.multiselect("Severity", ["CRITICAL", "HIGH", "MEDIUM", "LOW"], default=["CRITICAL", "HIGH"])
            filtered = [f for f in assessment.findings if f.severity in severity_filter]
            for f in filtered:
                sev_icon = {'CRITICAL': '🔴', 'HIGH': '🟠', 'MEDIUM': '🟡', 'LOW': '🟢'}.get(f.severity, '⚪')
                with st.expander(f"{sev_icon} {f.title}"):
                    st.markdown(f"**Description:** {f.description}")
                    if f.recommendation:
                        st.success(f"💡 {f.recommendation}")
                    if f.remediation_steps:
                        st.markdown("**Remediation:**")
                        for i, step in enumerate(f.remediation_steps, 1):
                            st.markdown(f"{i}. {step}")
    
    with tabs[3]:
        if results and results.get('remediation_roadmap'):
            roadmap = results['remediation_roadmap']
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### 🚨 Immediate")
                for item in roadmap.get('immediate', []):
                    st.markdown(f"- {item}")
                st.markdown("#### ⚡ Short-term")
                for item in roadmap.get('short_term', []):
                    st.markdown(f"- {item}")
            with col2:
                st.markdown("#### 📅 Medium-term")
                for item in roadmap.get('medium_term', []):
                    st.markdown(f"- {item}")
                st.markdown("#### 🎯 Long-term")
                for item in roadmap.get('long_term', []):
                    st.markdown(f"- {item}")
    
    with tabs[4]:
        col1, col2 = st.columns(2)
        with col1:
            if assessment and MODULE_STATUS.get('PDF Reports'):
                try:
                    pdf_bytes = generate_comprehensive_waf_report(assessment)
                    st.download_button("📄 Download PDF", pdf_bytes, file_name=f"WAF_Report_{datetime.now().strftime('%Y%m%d')}.pdf", mime="application/pdf", use_container_width=True)
                except Exception as e:
                    st.error(f"PDF error: {e}")
        with col2:
            if results or assessment:
                export_data = {'date': datetime.now().isoformat(), 'results': results, 'assessment_score': assessment.overall_score if assessment else None}
                st.download_button("📊 Download JSON", json.dumps(export_data, indent=2, default=str), file_name=f"WAF_Export_{datetime.now().strftime('%Y%m%d')}.json", mime="application/json", use_container_width=True)

# ============================================================================
# KNOWLEDGE BASE
# ============================================================================

def render_knowledge_base_tab():
    """Render knowledge base"""
    st.markdown('<div style="background: linear-gradient(135deg, #5E35B1 0%, #7E57C2 100%); padding: 1.5rem 2rem; border-radius: 12px; margin-bottom: 1.5rem;"><h2 style="color: white; margin: 0;">📚 Knowledge Base</h2></div>', unsafe_allow_html=True)
    
    tabs = st.tabs(["📖 WAF Pillars", "🔧 Best Practices", "🔗 Resources"])
    
    with tabs[0]:
        for key, pillar in WAF_PILLARS.items():
            with st.expander(f"{pillar['icon']} {pillar['name']}"):
                st.markdown(f"[📖 AWS Docs](https://docs.aws.amazon.com/wellarchitected/latest/framework/{key.replace('_', '-')}.html)")
    
    with tabs[1]:
        practices = {
            "Identity & Access": ["AWS Organizations", "Least privilege IAM", "Enable MFA", "Use IAM roles"],
            "Data Protection": ["KMS encryption", "TLS 1.2+", "S3 Block Public Access"],
            "Monitoring": ["CloudTrail", "CloudWatch", "GuardDuty"],
            "Cost": ["Reserved Instances", "Right-sizing", "Cost Explorer"]
        }
        for cat, items in practices.items():
            st.markdown(f"**{cat}:** {', '.join(items)}")
    
    with tabs[2]:
        st.markdown("""
        - [AWS Well-Architected Framework](https://docs.aws.amazon.com/wellarchitected/)
        - [AWS Architecture Center](https://aws.amazon.com/architecture/)
        - [AWS Solutions Library](https://aws.amazon.com/solutions/)
        """)

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main application"""
    init_session_state()
    render_sidebar()
    
    is_demo = st.session_state.get('app_mode', 'demo') == 'demo'
    mode_badge = "🎭 Demo" if is_demo else "🔴 Live"
    mode_color = "#1565C0" if is_demo else "#2E7D32"
    
    st.markdown(f'<div class="main-header"><div style="display: flex; justify-content: space-between; align-items: center;"><div><h1>🏗️ AWS Well-Architected Framework Advisor</h1><p>Enterprise AI-Powered Architecture Review Platform</p></div><div style="background: {mode_color}; padding: 0.5rem 1rem; border-radius: 20px; color: white; font-weight: 600;">{mode_badge}</div></div></div>', unsafe_allow_html=True)
    
    # Main tabs - now includes Architecture Patterns and WAF Review
    tabs = st.tabs([
        "📊 Dashboard",
        "🎯 AWS Scanner",
        "📤 Architecture Review",
        "📈 WAF Results",
        "🏗️ WAF Review",  # NEW TAB - Comprehensive Assessment
        "🏛️ Architecture Patterns",
        "🚀 EKS & Modernization",
        "💰 FinOps",
        "📋 Compliance",
        "🔄 Migration & DR",
        "📚 Knowledge Base"
    ])
    
    with tabs[0]:
        render_executive_dashboard()
    
    with tabs[1]:
        if MODULE_STATUS.get('Landscape Scanner'):
            render_landscape_scanner_tab()
        else:
            st.error(f"Module error: {MODULE_ERRORS.get('landscape_scanner', 'Unknown')}")
    
    with tabs[2]:
        render_architecture_review_tab()
    
    with tabs[3]:
        render_waf_results_tab()
    
    with tabs[4]:  # NEW TAB - WAF Review
        if MODULE_STATUS.get('WAF Review'):
            render_waf_review_tab()
        else:
            st.error(f"❌ WAF Review Module Not Loaded")
            st.info("💡 To enable WAF Review:")
            st.code("""
# 1. Ensure waf_review_module.py is in your project directory
# 2. Check the error below for details
            """)
            if 'waf_review_module' in MODULE_ERRORS:
                st.error(f"Error: {MODULE_ERRORS['waf_review_module']}")
    
    with tabs[5]:  # Architecture Patterns (was tabs[4])
        if MODULE_STATUS.get('Architecture Patterns'):
            render_architecture_patterns_tab()
        else:
            st.error(f"Module error: {MODULE_ERRORS.get('architecture_patterns', 'Unknown')}")
    
    with tabs[5]:  # Architecture Patterns (was tabs[4])
        if MODULE_STATUS.get('Architecture Patterns'):
            render_architecture_patterns_tab()
        else:
            st.error(f"Module error: {MODULE_ERRORS.get('architecture_patterns', 'Unknown')}")
    
    with tabs[6]:  # EKS & Modernization (was tabs[5])
        if MODULE_STATUS.get('EKS & Modernization'):
            render_eks_modernization_tab()
        else:
            st.error(f"Module error: {MODULE_ERRORS.get('eks_modernization', 'Unknown')}")
    
    with tabs[7]:  # FinOps (was tabs[6])
        if MODULE_STATUS.get('FinOps'):
            render_finops_tab()
        else:
            st.error(f"Module error: {MODULE_ERRORS.get('finops_module', 'Unknown')}")
    
    with tabs[8]:  # Compliance (was tabs[7])
        if MODULE_STATUS.get('Compliance'):
            render_compliance_tab()
        else:
            st.error(f"Module error: {MODULE_ERRORS.get('compliance_module', 'Unknown')}")
    
    with tabs[9]:  # Migration & DR (was tabs[8])
        if MODULE_STATUS.get('Migration & DR'):
            render_migration_dr_tab()
        else:
            st.error(f"Module error: {MODULE_ERRORS.get('migration_dr_module', 'Unknown')}")
    
    with tabs[10]:  # Knowledge Base (was tabs[9])
        render_knowledge_base_tab()
    
    st.markdown('<div class="app-footer">AWS Well-Architected Framework Advisor | Enterprise Edition v2.1 | Powered by Claude AI</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()