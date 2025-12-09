"""
AWS Well-Architected Framework Advisor - Enterprise Edition
AI-Powered Architecture Review & Risk Assessment Platform

Version: 2.0.0
Author: Enterprise Cloud Architecture Team
"""

import streamlit as st
import json
import base64
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any, Tuple
import os
import hashlib

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="AWS Well-Architected Advisor | Enterprise",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://docs.aws.amazon.com/wellarchitected/',
        'Report a bug': None,
        'About': """
        ## AWS Well-Architected Framework Advisor
        **Enterprise Edition v2.0.0**
        
        AI-Powered Architecture Review Platform
        
        Built with Claude AI by Anthropic
        """
    }
)

# ============================================================================
# MODULE IMPORTS
# ============================================================================

MODULE_STATUS = {}
MODULE_ERRORS = {}
IMPORT_WARNINGS = []

# Core libraries
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError as e:
    ANTHROPIC_AVAILABLE = False
    MODULE_ERRORS['anthropic'] = str(e)
    IMPORT_WARNINGS.append("AI analysis features disabled - install anthropic package")

try:
    import boto3
    from botocore.config import Config
    from botocore.exceptions import ClientError, NoCredentialsError
    BOTO3_AVAILABLE = True
except ImportError as e:
    BOTO3_AVAILABLE = False
    MODULE_ERRORS['boto3'] = str(e)
    IMPORT_WARNINGS.append("AWS connectivity disabled - install boto3 package")

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

# ============================================================================
# ENTERPRISE STYLES
# ============================================================================

st.markdown("""
<style>
    /* Main Header */
    .main-header {
        background: linear-gradient(135deg, #232F3E 0%, #37475A 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .main-header h1 { 
        color: #FF9900; 
        margin: 0; 
        font-size: 1.8rem;
        font-weight: 700;
    }
    .main-header p { 
        color: #FFFFFF; 
        margin: 0.3rem 0 0 0; 
        opacity: 0.9;
        font-size: 0.95rem;
    }
    
    /* Metric Cards */
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 1.2rem;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.08);
        border: 1px solid #e0e0e0;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.12);
    }
    .metric-value { 
        font-size: 2.2rem; 
        font-weight: 700; 
        color: #232F3E;
        line-height: 1.2;
    }
    .metric-label { 
        color: #666; 
        font-size: 0.85rem;
        margin-top: 0.3rem;
    }
    
    /* Dashboard Cards */
    .dashboard-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid #FF9900;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .dashboard-card h3 {
        color: #232F3E;
        margin: 0 0 1rem 0;
        font-size: 1.1rem;
    }
    
    /* Pillar Cards */
    .pillar-card {
        background: white;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
        border: 1px solid #e0e0e0;
        transition: all 0.2s;
    }
    .pillar-card:hover {
        border-color: #FF9900;
        box-shadow: 0 2px 8px rgba(255,153,0,0.2);
    }
    
    /* Status Badges */
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .status-success { background: #E8F5E9; color: #2E7D32; }
    .status-warning { background: #FFF3E0; color: #E65100; }
    .status-danger { background: #FFEBEE; color: #C62828; }
    
    /* Finding Cards */
    .finding-critical { border-left: 4px solid #D32F2F; }
    .finding-high { border-left: 4px solid #F57C00; }
    .finding-medium { border-left: 4px solid #FBC02D; }
    .finding-low { border-left: 4px solid #388E3C; }
    
    /* Footer */
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
# WAF PILLARS CONFIGURATION
# ============================================================================

WAF_PILLARS = {
    "security": {
        "name": "Security",
        "icon": "🔒",
        "color": "#D32F2F",
        "weight": 1.5,
        "description": "Protect information, systems, and assets through risk assessments and mitigation strategies",
        "focus_areas": ["Identity and access management", "Detection controls", "Infrastructure protection", "Data protection", "Incident response"]
    },
    "reliability": {
        "name": "Reliability",
        "icon": "🛡️",
        "color": "#1976D2",
        "weight": 1.3,
        "description": "Ensure workloads perform their intended functions correctly and consistently",
        "focus_areas": ["Foundations", "Workload architecture", "Change management", "Failure management"]
    },
    "performance": {
        "name": "Performance Efficiency",
        "icon": "⚡",
        "color": "#7B1FA2",
        "weight": 1.0,
        "description": "Use computing resources efficiently to meet requirements",
        "focus_areas": ["Selection", "Review", "Monitoring", "Tradeoffs"]
    },
    "cost": {
        "name": "Cost Optimization",
        "icon": "💰",
        "color": "#388E3C",
        "weight": 1.0,
        "description": "Avoid unnecessary costs and optimize spending",
        "focus_areas": ["Practice cloud financial management", "Expenditure awareness", "Cost-effective resources", "Optimize over time"]
    },
    "operational_excellence": {
        "name": "Operational Excellence",
        "icon": "⚙️",
        "color": "#FF9900",
        "weight": 0.9,
        "description": "Run and monitor systems to deliver business value",
        "focus_areas": ["Organization", "Prepare", "Operate", "Evolve"]
    },
    "sustainability": {
        "name": "Sustainability",
        "icon": "🌱",
        "color": "#00897B",
        "weight": 0.8,
        "description": "Minimize environmental impacts of running cloud workloads",
        "focus_areas": ["Region selection", "User behavior patterns", "Software patterns", "Data patterns", "Hardware patterns"]
    }
}

# ============================================================================
# SESSION STATE MANAGEMENT
# ============================================================================

def init_session_state():
    """Initialize all session state variables"""
    defaults = {
        'anthropic_api_key': None,
        'aws_credentials': None,
        'aws_session': None,
        'aws_connected': False,
        'aws_identity': None,
        'app_mode': 'demo',
        'landscape_assessment': None,
        'analysis_results': None,
        'assessment_history': [],
        'organization_context': '',
        'organization_name': '',
        'industry': '',
        'selected_frameworks': [],
        'ai_recommendations': [],
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    
    # Auto-load API key
    if not st.session_state.anthropic_api_key:
        st.session_state.anthropic_api_key = get_api_key()
    
    # Auto-load AWS credentials
    if not st.session_state.aws_credentials and MODULE_STATUS.get('AWS Connector'):
        try:
            creds, _ = get_aws_credentials_from_secrets()
            if creds:
                st.session_state.aws_credentials = creds
                session = get_aws_session(creds)
                if session:
                    success, msg, identity = test_aws_connection(session)
                    if success:
                        st.session_state.aws_session = session
                        st.session_state.aws_connected = True
                        st.session_state.aws_identity = identity
        except:
            pass

def get_api_key() -> Optional[str]:
    """Get Anthropic API key from various sources"""
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
    """Get configured Anthropic client"""
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
    """Render sidebar with configuration"""
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0;">
            <img src="https://a0.awsstatic.com/libra-css/images/logos/aws_smile-header-desktop-en-white_59x35.png" width="60">
            <h3 style="color: #FF9900; margin: 0.5rem 0 0 0; font-size: 1rem;">Well-Architected Advisor</h3>
            <p style="color: #666; font-size: 0.75rem; margin: 0;">Enterprise Edition v2.0</p>
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
                if st.session_state.get('aws_identity'):
                    st.caption(f"Account: {st.session_state.aws_identity.get('account', 'N/A')}")
            else:
                st.warning("⚠️ Configure AWS in connector tab")
        
        st.markdown("---")
        
        # Configuration Status
        st.markdown("### ⚙️ Configuration")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("🟢 AI" if get_api_key() else "🔴 AI")
        with col2:
            st.markdown("🟢 AWS" if st.session_state.get('aws_connected') else "🟡 AWS")
        
        if not get_api_key():
            with st.expander("🔑 Configure AI"):
                api_key = st.text_input("Anthropic API Key", type="password")
                if api_key:
                    st.session_state.anthropic_api_key = api_key
                    st.rerun()
        
        st.markdown("---")
        
        # Module Status
        st.markdown("### 📦 Modules")
        loaded = sum(MODULE_STATUS.values())
        total = len(MODULE_STATUS)
        st.markdown(f"{'✅' if loaded == total else '⚠️'} {loaded}/{total} loaded")
        
        with st.expander("Details"):
            for name, status in MODULE_STATUS.items():
                st.markdown(f"{'✅' if status else '❌'} {name}")
        
        st.markdown("---")
        
        # Organization Context
        st.markdown("### 🏢 Organization")
        org_name = st.text_input("Name", value=st.session_state.get('organization_name', ''), placeholder="Acme Corp")
        st.session_state.organization_name = org_name
        
        context = st.text_area("Context", value=st.session_state.get('organization_context', ''), placeholder="Industry, compliance needs...", height=60)
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
                Get AI-powered insights into your AWS architecture aligned with the Well-Architected Framework.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown('<div class="dashboard-card"><h3>📊 1. Run Assessment</h3><p>Scan your AWS environment or use demo mode.</p></div>', unsafe_allow_html=True)
            if st.button("Run Demo Assessment", use_container_width=True):
                if MODULE_STATUS.get('Landscape Scanner'):
                    st.session_state.landscape_assessment = generate_demo_assessment()
                    st.rerun()
        with col2:
            st.markdown('<div class="dashboard-card"><h3>📤 2. Upload Architecture</h3><p>Upload diagrams or IaC for AI review.</p></div>', unsafe_allow_html=True)
        with col3:
            st.markdown('<div class="dashboard-card"><h3>🔧 3. Connect AWS</h3><p>Connect your AWS account for live scanning.</p></div>', unsafe_allow_html=True)
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
            st.markdown(f'<div class="pillar-card"><div style="font-size: 1.5rem;">{pillar["icon"]}</div><div style="font-size: 1.8rem; font-weight: 700; color: {color};">{score}</div><div style="font-size: 0.75rem; color: #666;">{pillar["name"].split()[0]}</div><div style="font-size: 0.7rem; color: #999;">{findings} findings</div></div>', unsafe_allow_html=True)
    
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
        resources = [("EC2", inv.ec2_instances), ("S3", inv.s3_buckets), ("RDS", inv.rds_instances), ("Lambda", inv.lambda_functions), ("EBS", inv.ebs_volumes)]
        for name, count in resources:
            st.markdown(f"**{name}:** {count}")

# ============================================================================
# ARCHITECTURE REVIEW TAB
# ============================================================================

def render_architecture_review_tab():
    """Render architecture review tab"""
    st.markdown('<div style="background: linear-gradient(135deg, #1565C0 0%, #1976D2 100%); padding: 1.5rem 2rem; border-radius: 12px; margin-bottom: 1.5rem;"><h2 style="color: white; margin: 0;">📤 Architecture Review</h2><p style="color: #BBDEFB; margin: 0.3rem 0 0 0;">Upload your architecture for AI-powered WAF analysis</p></div>', unsafe_allow_html=True)
    
    input_method = st.radio("Input Method", ["🖼️ Architecture Diagram", "📝 CloudFormation/Terraform", "✏️ Text Description"], horizontal=True)
    
    architecture_data = None
    image_data = None
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if "Diagram" in input_method:
            uploaded = st.file_uploader("Upload diagram (PNG, JPG)", type=['png', 'jpg', 'jpeg', 'webp'])
            if uploaded:
                st.image(uploaded, use_container_width=True)
                image_data = {'data': base64.b64encode(uploaded.read()).decode('utf-8'), 'type': uploaded.type}
                uploaded.seek(0)
                architecture_data = f"[Architecture diagram: {uploaded.name}]"
        elif "CloudFormation" in input_method:
            code = st.text_area("Paste IaC code", height=300)
            if code:
                architecture_data = code
        else:
            desc = st.text_area("Describe your architecture", height=300)
            if desc:
                architecture_data = desc
    
    with col2:
        st.markdown("**Analysis Context**")
        workload_type = st.selectbox("Workload Type", ["General Purpose", "Web Application", "Data Analytics", "Serverless", "Container-based"])
        compliance_needs = st.multiselect("Compliance", ["SOC 2", "HIPAA", "PCI DSS", "GDPR"])
        additional_context = st.text_area("Additional Context", height=80)
    
    if st.button("🔍 Analyze Architecture", type="primary", use_container_width=True):
        if not architecture_data:
            st.warning("Please provide architecture information")
            return
        
        client = get_anthropic_client()
        if not client:
            st.error("Configure Anthropic API key in sidebar")
            return
        
        with st.spinner("Analyzing with Claude AI..."):
            results = analyze_architecture_with_ai(client, architecture_data, {'workload_type': workload_type, 'compliance': compliance_needs, 'context': additional_context}, image_data)
        
        if results:
            st.session_state.analysis_results = results
            st.success("✅ Analysis complete! View in WAF Results tab")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Score", f"{results.get('overall_score', 0)}/100")
            with col2:
                st.metric("Risk", results.get('overall_risk', 'Unknown'))
            with col3:
                findings = sum(len(p.get('findings', [])) for p in results.get('pillar_assessments', {}).values())
                st.metric("Findings", findings)

def analyze_architecture_with_ai(client, architecture: str, context: Dict, image_data: Optional[Dict] = None) -> Dict:
    """AI analysis of architecture"""
    prompt = f"""Perform a comprehensive AWS Well-Architected Framework review.

ARCHITECTURE: {architecture}
CONTEXT: Workload: {context.get('workload_type')}, Compliance: {context.get('compliance')}, Additional: {context.get('context')}

Return detailed JSON:
{{
    "executive_summary": "3-4 sentence assessment",
    "overall_score": 0-100,
    "overall_risk": "Critical|High|Medium|Low",
    "pillar_assessments": {{
        "Security": {{"score": 0-100, "risk_level": "...", "strengths": [...], "gaps": [...], "findings": [{{"title": "...", "severity": "Critical|High|Medium|Low", "description": "...", "recommendation": "...", "implementation_steps": [...], "effort": "Low|Medium|High"}}]}},
        "Reliability": {{...}},
        "Performance Efficiency": {{...}},
        "Cost Optimization": {{...}},
        "Operational Excellence": {{...}},
        "Sustainability": {{...}}
    }},
    "remediation_roadmap": {{"immediate": [...], "short_term": [...], "medium_term": [...], "long_term": [...]}},
    "estimated_savings": {{"monthly": 0, "annual": 0}}
}}

Be thorough and specific with AWS services and best practices."""

    try:
        messages = [{"role": "user", "content": prompt}]
        if image_data:
            messages = [{"role": "user", "content": [{"type": "image", "source": {"type": "base64", "media_type": image_data['type'], "data": image_data['data']}}, {"type": "text", "text": prompt}]}]
        
        response = client.messages.create(model="claude-sonnet-4-20250514", max_tokens=8000, messages=messages)
        
        import re
        text = response.content[0].text
        json_match = re.search(r'\{[\s\S]*\}', text)
        if json_match:
            return json.loads(json_match.group())
    except Exception as e:
        st.error(f"Analysis failed: {e}")
    return None

# ============================================================================
# WAF RESULTS TAB
# ============================================================================

def render_waf_results_tab():
    """Render WAF results"""
    results = st.session_state.get('analysis_results')
    assessment = st.session_state.get('landscape_assessment')
    
    if not results and not assessment:
        st.info("📋 No results. Run an assessment first.")
        if st.button("🎭 Generate Demo Assessment"):
            if MODULE_STATUS.get('Landscape Scanner'):
                st.session_state.landscape_assessment = generate_demo_assessment()
                st.rerun()
        return
    
    tabs = st.tabs(["📊 Overview", "📈 Pillars", "🚨 Findings", "🗺️ Roadmap", "📥 Export"])
    
    with tabs[0]:
        render_results_overview(results, assessment)
    with tabs[1]:
        render_pillar_details(results, assessment)
    with tabs[2]:
        render_all_findings(results, assessment)
    with tabs[3]:
        render_remediation_roadmap(results, assessment)
    with tabs[4]:
        render_export_options(results, assessment)

def render_results_overview(results, assessment):
    """Render overview"""
    st.markdown("### 📊 Assessment Overview")
    
    if results:
        score, risk = results.get('overall_score', 0), results.get('overall_risk', 'Unknown')
        summary = results.get('executive_summary', '')
    elif assessment:
        score, risk = assessment.overall_score, assessment.overall_risk
        summary = f"Assessment with {len(assessment.findings)} findings."
    else:
        return
    
    if summary:
        st.markdown(f'<div class="dashboard-card"><h3>📋 Executive Summary</h3><p>{summary}</p></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        color = "#388E3C" if score >= 80 else "#FBC02D" if score >= 60 else "#D32F2F"
        st.markdown(f'<div class="metric-card"><div class="metric-value" style="color: {color};">{score}</div><div class="metric-label">Overall Score</div></div>', unsafe_allow_html=True)
    with col2:
        st.metric("Risk Level", risk)
    with col3:
        if assessment:
            st.metric("Findings", len(assessment.findings))

def render_pillar_details(results, assessment):
    """Render pillar details"""
    st.markdown("### 📈 Pillar Assessments")
    
    pillar_data = {}
    if results:
        pillar_data = results.get('pillar_assessments', {})
    elif assessment:
        for pn, ps in assessment.pillar_scores.items():
            pillar_data[pn] = {'score': ps.score, 'findings': [{'title': f.title, 'severity': f.severity, 'description': f.description, 'recommendation': f.recommendation} for f in ps.top_findings]}
    
    for pillar_name, data in pillar_data.items():
        pillar_info = next((p for k, p in WAF_PILLARS.items() if p['name'] == pillar_name), None)
        icon = pillar_info['icon'] if pillar_info else '📊'
        score = data.get('score', 0)
        color = "#388E3C" if score >= 80 else "#FBC02D" if score >= 60 else "#D32F2F"
        
        with st.expander(f"{icon} {pillar_name} - Score: {score}/100", expanded=score < 60):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**✅ Strengths:**")
                for s in data.get('strengths', [])[:3]:
                    st.markdown(f"- {s}")
            with col2:
                st.markdown("**⚠️ Gaps:**")
                for g in data.get('gaps', [])[:3]:
                    st.markdown(f"- {g}")
            
            for finding in data.get('findings', [])[:5]:
                sev = finding.get('severity', 'Medium')
                sev_icon = {'Critical': '🔴', 'High': '🟠', 'Medium': '🟡', 'Low': '🟢', 'CRITICAL': '🔴', 'HIGH': '🟠', 'MEDIUM': '🟡', 'LOW': '🟢'}.get(sev, '⚪')
                st.markdown(f"**{sev_icon} {finding.get('title')}**")
                if finding.get('recommendation'):
                    st.success(f"💡 {finding['recommendation']}")

def render_all_findings(results, assessment):
    """Render all findings"""
    st.markdown("### 🚨 All Findings")
    
    all_findings = []
    if results:
        for pn, pd in results.get('pillar_assessments', {}).items():
            for f in pd.get('findings', []):
                f['pillar'] = pn
                all_findings.append(f)
    if assessment:
        for f in assessment.findings:
            all_findings.append({'title': f.title, 'description': f.description, 'severity': f.severity, 'pillar': f.pillar, 'recommendation': f.recommendation, 'effort': f.effort, 'estimated_savings': f.estimated_savings})
    
    if not all_findings:
        st.info("No findings")
        return
    
    severity_filter = st.multiselect("Severity Filter", ["CRITICAL", "HIGH", "MEDIUM", "LOW", "Critical", "High", "Medium", "Low"], default=["CRITICAL", "HIGH", "Critical", "High"])
    filtered = [f for f in all_findings if f.get('severity') in severity_filter] if severity_filter else all_findings
    filtered.sort(key=lambda f: {'CRITICAL': 0, 'Critical': 0, 'HIGH': 1, 'High': 1, 'MEDIUM': 2, 'Medium': 2}.get(f.get('severity', ''), 4))
    
    st.markdown(f"**Showing {len(filtered)} of {len(all_findings)} findings**")
    
    for f in filtered:
        sev = f.get('severity', 'Medium')
        sev_icon = {'CRITICAL': '🔴', 'Critical': '🔴', 'HIGH': '🟠', 'High': '🟠', 'MEDIUM': '🟡', 'Medium': '🟡', 'LOW': '🟢', 'Low': '🟢'}.get(sev, '⚪')
        with st.expander(f"{sev_icon} [{sev}] {f.get('title')} - {f.get('pillar', 'Unknown')}"):
            st.markdown(f"**Description:** {f.get('description', 'N/A')}")
            if f.get('recommendation'):
                st.success(f"💡 {f['recommendation']}")
            if f.get('implementation_steps'):
                for i, step in enumerate(f['implementation_steps'], 1):
                    st.markdown(f"{i}. {step}")

def render_remediation_roadmap(results, assessment):
    """Render roadmap"""
    st.markdown("### 🗺️ Remediation Roadmap")
    
    if results and results.get('remediation_roadmap'):
        roadmap = results['remediation_roadmap']
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 🚨 Immediate (0-7 days)")
            for item in roadmap.get('immediate', []):
                st.markdown(f"- {item}")
            st.markdown("#### ⚡ Short-term (8-30 days)")
            for item in roadmap.get('short_term', []):
                st.markdown(f"- {item}")
        with col2:
            st.markdown("#### 📅 Medium-term (1-3 months)")
            for item in roadmap.get('medium_term', []):
                st.markdown(f"- {item}")
            st.markdown("#### 🎯 Long-term (3-12 months)")
            for item in roadmap.get('long_term', []):
                st.markdown(f"- {item}")
    elif assessment:
        st.markdown("#### 🚨 Immediate (Critical & High, Low Effort)")
        for f in [f for f in assessment.findings if f.severity in ['CRITICAL', 'HIGH'] and f.effort == 'Low'][:5]:
            st.markdown(f"- **{f.title}**: {f.recommendation[:80]}")

def render_export_options(results, assessment):
    """Render export"""
    st.markdown("### 📥 Export Options")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if assessment and MODULE_STATUS.get('PDF Reports'):
            try:
                pdf_bytes = generate_comprehensive_waf_report(assessment)
                st.download_button("📄 Download PDF", pdf_bytes, file_name=f"WAF_Report_{datetime.now().strftime('%Y%m%d')}.pdf", mime="application/pdf", use_container_width=True)
            except Exception as e:
                st.error(f"PDF error: {e}")
    with col2:
        if results or assessment:
            export_data = {'export_date': datetime.now().isoformat(), 'ai_results': results, 'assessment_id': assessment.assessment_id if assessment else None}
            st.download_button("📊 Download JSON", json.dumps(export_data, indent=2, default=str), file_name=f"WAF_Export_{datetime.now().strftime('%Y%m%d')}.json", mime="application/json", use_container_width=True)
    with col3:
        if assessment and PANDAS_AVAILABLE:
            findings_list = [{'Title': f.title, 'Severity': f.severity, 'Pillar': f.pillar, 'Recommendation': f.recommendation} for f in assessment.findings]
            if findings_list:
                df = pd.DataFrame(findings_list)
                st.download_button("📋 Download CSV", df.to_csv(index=False), file_name=f"WAF_Findings_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv", use_container_width=True)

# ============================================================================
# KNOWLEDGE BASE TAB
# ============================================================================

def render_knowledge_base_tab():
    """Render knowledge base"""
    st.markdown('<div style="background: linear-gradient(135deg, #5E35B1 0%, #7E57C2 100%); padding: 1.5rem 2rem; border-radius: 12px; margin-bottom: 1.5rem;"><h2 style="color: white; margin: 0;">📚 Well-Architected Knowledge Base</h2></div>', unsafe_allow_html=True)
    
    tabs = st.tabs(["📖 WAF Pillars", "🔧 Best Practices", "🔗 Resources"])
    
    with tabs[0]:
        for key, pillar in WAF_PILLARS.items():
            with st.expander(f"{pillar['icon']} {pillar['name']}"):
                st.markdown(f"**Description:** {pillar['description']}")
                st.markdown("**Focus Areas:**")
                for area in pillar['focus_areas']:
                    st.markdown(f"- {area}")
                st.markdown(f"[📖 AWS Docs](https://docs.aws.amazon.com/wellarchitected/latest/framework/{key.replace('_', '-')}.html)")
    
    with tabs[1]:
        practices = {
            "Identity & Access": ["Use AWS Organizations", "Implement least privilege", "Enable MFA", "Use IAM roles"],
            "Data Protection": ["Encrypt at rest with KMS", "Use TLS 1.2+", "Enable S3 Block Public Access"],
            "Monitoring": ["Enable CloudTrail", "Use CloudWatch", "Enable GuardDuty"],
            "Cost": ["Use Reserved Instances", "Right-size resources", "Enable Cost Explorer"]
        }
        for cat, items in practices.items():
            st.markdown(f"**{cat}**")
            for item in items:
                st.markdown(f"- {item}")
    
    with tabs[2]:
        st.markdown("""
        **AWS Resources:**
        - [AWS Well-Architected Framework](https://docs.aws.amazon.com/wellarchitected/latest/framework/)
        - [AWS Well-Architected Tool](https://aws.amazon.com/well-architected-tool/)
        - [AWS Architecture Center](https://aws.amazon.com/architecture/)
        """)

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main application"""
    init_session_state()
    render_sidebar()
    
    is_demo = st.session_state.get('app_mode', 'demo') == 'demo'
    mode_badge = "🎭 Demo Mode" if is_demo else "🔴 Live Mode"
    mode_color = "#1565C0" if is_demo else "#2E7D32"
    
    st.markdown(f'<div class="main-header"><div style="display: flex; justify-content: space-between; align-items: center;"><div><h1>🏗️ AWS Well-Architected Framework Advisor</h1><p>Enterprise-Grade AI-Powered Architecture Review Platform</p></div><div style="background: {mode_color}; padding: 0.5rem 1rem; border-radius: 20px; color: white; font-weight: 600;">{mode_badge}</div></div></div>', unsafe_allow_html=True)
    
    tabs = st.tabs(["📊 Dashboard", "🎯 AWS Scanner", "📤 Architecture Review", "📈 WAF Results", "🚀 EKS & Modernization", "💰 FinOps", "📋 Compliance", "🔄 Migration & DR", "📚 Knowledge Base"])
    
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
    with tabs[4]:
        if MODULE_STATUS.get('EKS & Modernization'):
            render_eks_modernization_tab()
        else:
            st.error(f"Module error: {MODULE_ERRORS.get('eks_modernization', 'Unknown')}")
    with tabs[5]:
        if MODULE_STATUS.get('FinOps'):
            render_finops_tab()
        else:
            st.error(f"Module error: {MODULE_ERRORS.get('finops_module', 'Unknown')}")
    with tabs[6]:
        if MODULE_STATUS.get('Compliance'):
            render_compliance_tab()
        else:
            st.error(f"Module error: {MODULE_ERRORS.get('compliance_module', 'Unknown')}")
    with tabs[7]:
        if MODULE_STATUS.get('Migration & DR'):
            render_migration_dr_tab()
        else:
            st.error(f"Module error: {MODULE_ERRORS.get('migration_dr_module', 'Unknown')}")
    with tabs[8]:
        render_knowledge_base_tab()
    
    st.markdown('<div class="app-footer">AWS Well-Architected Framework Advisor | Enterprise Edition v2.0 | Powered by Claude AI</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
