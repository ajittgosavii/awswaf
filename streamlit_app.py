"""
AWS Well-Architected Framework Advisor
Enterprise-Grade AI-Powered Architecture Review Platform

This is the main application file that orchestrates all modules.
Modules are imported from the root directory for Streamlit Cloud compatibility.
"""

import streamlit as st
import json
import base64
from datetime import datetime
from typing import Optional, Dict, List, Any
import os

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="AWS Well-Architected Advisor",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# MODULE IMPORTS (from root directory)
# ============================================================================

MODULE_STATUS = {}
MODULE_ERRORS = {}

# Import Anthropic
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError as e:
    ANTHROPIC_AVAILABLE = False
    MODULE_ERRORS['anthropic'] = str(e)

# Import boto3
try:
    import boto3
    from botocore.config import Config
    from botocore.exceptions import ClientError
    BOTO3_AVAILABLE = True
except ImportError as e:
    BOTO3_AVAILABLE = False
    MODULE_ERRORS['boto3'] = str(e)

# Import AWS Connector
try:
    from aws_connector import (
        render_aws_connector_tab,
        get_aws_session,
        AWSCredentials,
        get_aws_credentials_from_secrets
    )
    MODULE_STATUS['AWS Connector'] = True
except Exception as e:
    MODULE_STATUS['AWS Connector'] = False
    MODULE_ERRORS['aws_connector'] = str(e)

# Import Landscape Scanner
try:
    from landscape_scanner import (
        render_landscape_scanner_tab,
        AWSLandscapeScanner,
        generate_demo_assessment
    )
    MODULE_STATUS['Landscape Scanner'] = True
except Exception as e:
    MODULE_STATUS['Landscape Scanner'] = False
    MODULE_ERRORS['landscape_scanner'] = str(e)

# Import EKS Modernization
try:
    from eks_modernization import render_eks_modernization_tab
    MODULE_STATUS['EKS & Modernization'] = True
except Exception as e:
    MODULE_STATUS['EKS & Modernization'] = False
    MODULE_ERRORS['eks_modernization'] = str(e)

# Import FinOps
try:
    from finops_module import render_finops_tab
    MODULE_STATUS['FinOps'] = True
except Exception as e:
    MODULE_STATUS['FinOps'] = False
    MODULE_ERRORS['finops_module'] = str(e)

# Import Compliance
try:
    from compliance_module import render_compliance_tab
    MODULE_STATUS['Compliance'] = True
except Exception as e:
    MODULE_STATUS['Compliance'] = False
    MODULE_ERRORS['compliance_module'] = str(e)

# Import Migration & DR
try:
    from migration_dr_module import render_migration_dr_tab
    MODULE_STATUS['Migration & DR'] = True
except Exception as e:
    MODULE_STATUS['Migration & DR'] = False
    MODULE_ERRORS['migration_dr_module'] = str(e)

# Import PDF Generator
try:
    from pdf_report_generator import generate_comprehensive_waf_report
    MODULE_STATUS['PDF Reports'] = True
except Exception as e:
    MODULE_STATUS['PDF Reports'] = False
    MODULE_ERRORS['pdf_report_generator'] = str(e)

# ============================================================================
# STYLES
# ============================================================================

st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #232F3E 0%, #37475A 100%);
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .main-header h1 { color: #FF9900; margin: 0; font-size: 2.2rem; }
    .main-header p { color: #FF9900; margin: 0.5rem 0 0 0; opacity: 0.9; }
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .metric-value { font-size: 2.5rem; font-weight: 700; color: #232F3E; }
    .metric-label { color: #666; font-size: 0.9rem; }
    .module-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid #FF9900;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# WAF PILLARS
# ============================================================================

WAF_PILLARS = {
    "operational_excellence": {"name": "Operational Excellence", "icon": "⚙️", "color": "#FF9900"},
    "security": {"name": "Security", "icon": "🔒", "color": "#D32F2F"},
    "reliability": {"name": "Reliability", "icon": "🛡️", "color": "#1976D2"},
    "performance": {"name": "Performance Efficiency", "icon": "⚡", "color": "#7B1FA2"},
    "cost": {"name": "Cost Optimization", "icon": "💰", "color": "#388E3C"},
    "sustainability": {"name": "Sustainability", "icon": "🌱", "color": "#00897B"}
}

# ============================================================================
# SESSION STATE & HELPERS
# ============================================================================

def get_api_key() -> Optional[str]:
    """Get Anthropic API key from secrets or session"""
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
    return anthropic.Anthropic(api_key=api_key)

def init_session_state():
    """Initialize session state"""
    defaults = {
        'anthropic_api_key': get_api_key(),
        'aws_connected': False,
        'aws_session': None,
        'app_mode': 'demo',
        'analysis_results': None,
        'landscape_assessment': None,
        'organization_context': ''
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# ============================================================================
# SIDEBAR
# ============================================================================

def render_sidebar():
    """Render sidebar"""
    with st.sidebar:
        st.image("https://a0.awsstatic.com/libra-css/images/logos/aws_smile-header-desktop-en-white_59x35.png", width=80)
        
        # Mode Toggle
        st.markdown("### 🎮 Mode")
        mode = st.radio(
            "Select Mode",
            ["🎭 Demo", "🔴 Live"],
            index=0 if st.session_state.get('app_mode', 'demo') == 'demo' else 1,
            horizontal=True
        )
        st.session_state.app_mode = 'demo' if '🎭' in mode else 'live'
        
        if st.session_state.app_mode == 'demo':
            st.info("📋 Demo mode - sample data")
        else:
            st.warning("🔴 Live mode - real AWS")
        
        st.markdown("---")
        
        # API Key Status
        st.markdown("### ⚙️ Configuration")
        if get_api_key():
            st.success("✓ API Key configured")
        else:
            api_key = st.text_input("Anthropic API Key", type="password")
            if api_key:
                st.session_state.anthropic_api_key = api_key
                st.rerun()
        
        # AWS Status
        st.markdown("### 🔐 AWS Connection")
        if st.session_state.app_mode == 'demo':
            st.caption("Not required in Demo mode")
        elif st.session_state.get('aws_connected'):
            st.success("✓ AWS Connected")
        else:
            st.warning("Configure in AWS Connector tab")
        
        st.markdown("---")
        
        # Module Status
        st.markdown("### 📦 Modules")
        loaded = sum(MODULE_STATUS.values())
        total = len(MODULE_STATUS)
        
        if loaded == total:
            st.success(f"✅ All {total} modules loaded")
        else:
            st.warning(f"⚠️ {loaded}/{total} modules")
            with st.expander("View Details"):
                for name, status in MODULE_STATUS.items():
                    st.markdown(f"{'✅' if status else '❌'} {name}")
                if MODULE_ERRORS:
                    st.markdown("**Errors:**")
                    for mod, err in MODULE_ERRORS.items():
                        st.code(f"{mod}: {err[:50]}...")
        
        st.markdown("---")
        
        # Organization Context
        st.markdown("### 🏢 Context")
        org_context = st.text_area(
            "Organization Context",
            value=st.session_state.get('organization_context', ''),
            placeholder="Industry, compliance needs, tech stack...",
            height=80
        )
        st.session_state.organization_context = org_context

# ============================================================================
# ARCHITECTURE REVIEW TAB
# ============================================================================

def render_architecture_review_tab():
    """Render architecture upload and review tab"""
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1565C0 0%, #1976D2 100%); padding: 2rem; border-radius: 12px; margin-bottom: 1.5rem;">
        <h2 style="color: white; margin: 0;">📤 Architecture Review</h2>
        <p style="color: #BBDEFB; margin: 0.5rem 0 0 0;">Upload your architecture for AI-powered WAF analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    input_method = st.radio(
        "Input Method",
        ["🖼️ Architecture Diagram", "📝 CloudFormation/Terraform", "✏️ Text Description", "📊 AWS Config Export"],
        horizontal=True
    )
    
    architecture_data = None
    
    if "Diagram" in input_method:
        uploaded = st.file_uploader("Upload diagram", type=['png', 'jpg', 'jpeg', 'gif', 'webp'])
        if uploaded:
            st.image(uploaded, caption="Uploaded Architecture", use_container_width=True)
            architecture_data = f"[Architecture diagram uploaded: {uploaded.name}]"
            st.session_state['uploaded_image'] = {
                'data': base64.b64encode(uploaded.read()).decode('utf-8'),
                'type': uploaded.type
            }
    elif "CloudFormation" in input_method:
        code = st.text_area("Paste IaC code", height=300, placeholder="CloudFormation YAML/JSON or Terraform...")
        if code:
            architecture_data = code
    elif "Text" in input_method:
        desc = st.text_area("Describe architecture", height=300, placeholder="Services, data flows, security...")
        if desc:
            architecture_data = desc
    else:
        uploaded_json = st.file_uploader("Upload JSON", type=['json'])
        if uploaded_json:
            architecture_data = uploaded_json.read().decode('utf-8')
    
    context = st.text_area("Additional Context", placeholder="Compliance requirements, traffic patterns...", height=100)
    
    if st.button("🔍 Analyze Architecture", type="primary", use_container_width=True):
        if not architecture_data:
            st.warning("Please provide architecture information")
            return
        
        client = get_anthropic_client()
        if not client:
            st.error("Configure Anthropic API key in sidebar")
            return
        
        with st.spinner("Analyzing with Claude AI..."):
            results = analyze_architecture_with_ai(client, architecture_data, context)
        
        if results:
            st.session_state.analysis_results = results
            st.success("✅ Analysis complete! View in WAF Results tab")

def analyze_architecture_with_ai(client, architecture: str, context: str) -> Dict:
    """Comprehensive AI analysis of architecture"""
    prompt = f"""You are an AWS Well-Architected Framework expert. Perform a comprehensive analysis.

ARCHITECTURE:
{architecture}

CONTEXT: {context if context else 'None provided'}

Provide detailed JSON response:
{{
    "executive_summary": "3-4 sentence overview",
    "overall_score": 0-100,
    "overall_risk": "Critical|High|Medium|Low",
    "pillar_assessments": {{
        "Security": {{
            "score": 0-100,
            "risk_level": "Critical|High|Medium|Low",
            "current_state": "Detailed description of current security posture",
            "strengths": ["strength1", "strength2"],
            "gaps": ["gap1", "gap2"],
            "findings": [
                {{
                    "title": "Finding title",
                    "severity": "Critical|High|Medium|Low",
                    "description": "Detailed description",
                    "affected_resources": ["resource1"],
                    "business_impact": "Impact description",
                    "recommendation": "Detailed recommendation",
                    "implementation_steps": ["step1", "step2", "step3"],
                    "effort": "Low|Medium|High",
                    "aws_services": ["service1", "service2"]
                }}
            ]
        }},
        "Reliability": {{ ... same structure ... }},
        "Performance Efficiency": {{ ... same structure ... }},
        "Cost Optimization": {{ ... same structure ... }},
        "Operational Excellence": {{ ... same structure ... }},
        "Sustainability": {{ ... same structure ... }}
    }},
    "cross_cutting_concerns": [
        {{
            "title": "Concern title",
            "description": "Description",
            "affected_pillars": ["Security", "Reliability"],
            "recommendation": "Recommendation"
        }}
    ],
    "remediation_roadmap": {{
        "immediate": ["action1", "action2"],
        "short_term": ["action1", "action2"],
        "medium_term": ["action1", "action2"],
        "long_term": ["action1", "action2"]
    }},
    "estimated_savings": {{
        "monthly": 0,
        "annual": 0,
        "opportunities": ["opportunity1", "opportunity2"]
    }},
    "architecture_recommendations": [
        {{
            "title": "Recommendation",
            "current_state": "Current",
            "target_state": "Target",
            "benefits": ["benefit1"],
            "implementation_complexity": "Low|Medium|High"
        }}
    ]
}}

Be thorough, specific, and actionable. Include AWS service names and best practices."""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=8000,
            messages=[{"role": "user", "content": prompt}]
        )
        
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
    """Render comprehensive WAF results"""
    results = st.session_state.get('analysis_results')
    assessment = st.session_state.get('landscape_assessment')
    
    if not results and not assessment:
        st.info("📋 No results yet. Run an analysis from AWS Scanner or Architecture Review tab.")
        return
    
    # Use whichever data is available
    if results:
        render_ai_analysis_results(results)
    
    if assessment:
        render_assessment_results(assessment)

def render_ai_analysis_results(results: Dict):
    """Render AI analysis results"""
    st.markdown("### 📊 AI-Powered WAF Analysis Results")
    
    # Executive Summary
    st.markdown(f"**Executive Summary:** {results.get('executive_summary', 'N/A')}")
    
    # Overall Metrics
    col1, col2, col3, col4 = st.columns(4)
    score = results.get('overall_score', 0)
    risk = results.get('overall_risk', 'Unknown')
    
    with col1:
        color = "#388E3C" if score >= 80 else "#FBC02D" if score >= 60 else "#D32F2F"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color: {color};">{score}</div>
            <div class="metric-label">WAF Score</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.metric("Risk Level", risk)
    with col3:
        pillar_count = len(results.get('pillar_assessments', {}))
        st.metric("Pillars Analyzed", pillar_count)
    with col4:
        findings_count = sum(len(p.get('findings', [])) for p in results.get('pillar_assessments', {}).values())
        st.metric("Total Findings", findings_count)
    
    # Pillar Details
    st.markdown("### 📈 Pillar Assessments")
    
    for pillar_name, assessment in results.get('pillar_assessments', {}).items():
        pillar_info = next((p for p in WAF_PILLARS.values() if p['name'] == pillar_name), None)
        icon = pillar_info['icon'] if pillar_info else '📊'
        
        with st.expander(f"{icon} {pillar_name} - Score: {assessment.get('score', 'N/A')}/100"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**✅ Strengths:**")
                for s in assessment.get('strengths', []):
                    st.markdown(f"- {s}")
            
            with col2:
                st.markdown("**⚠️ Gaps:**")
                for g in assessment.get('gaps', []):
                    st.markdown(f"- {g}")
            
            st.markdown("**📋 Findings:**")
            for finding in assessment.get('findings', []):
                severity_colors = {'Critical': '🔴', 'High': '🟠', 'Medium': '🟡', 'Low': '🟢'}
                sev = finding.get('severity', 'Medium')
                
                with st.container():
                    st.markdown(f"{severity_colors.get(sev, '⚪')} **{finding.get('title', 'Finding')}** ({sev})")
                    st.markdown(f"_{finding.get('description', '')}_")
                    
                    if finding.get('recommendation'):
                        st.success(f"💡 **Recommendation:** {finding['recommendation']}")
                    
                    if finding.get('implementation_steps'):
                        with st.expander("Implementation Steps"):
                            for i, step in enumerate(finding['implementation_steps'], 1):
                                st.markdown(f"{i}. {step}")
    
    # Remediation Roadmap
    roadmap = results.get('remediation_roadmap', {})
    if roadmap:
        st.markdown("### 🗺️ Remediation Roadmap")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("**🚨 Immediate (0-30 days)**")
            for item in roadmap.get('immediate', []):
                st.markdown(f"- {item}")
        
        with col2:
            st.markdown("**⚡ Short-term (1-3 months)**")
            for item in roadmap.get('short_term', []):
                st.markdown(f"- {item}")
        
        with col3:
            st.markdown("**📅 Medium-term (3-6 months)**")
            for item in roadmap.get('medium_term', []):
                st.markdown(f"- {item}")
        
        with col4:
            st.markdown("**🎯 Long-term (6-12 months)**")
            for item in roadmap.get('long_term', []):
                st.markdown(f"- {item}")

def render_assessment_results(assessment):
    """Render scanner assessment results"""
    st.markdown("### 📊 AWS Scanner Results")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("WAF Score", assessment.overall_score)
    with col2:
        st.metric("Risk Level", assessment.overall_risk)
    with col3:
        st.metric("Findings", len(assessment.findings))
    with col4:
        critical = sum(1 for f in assessment.findings if f.severity == 'CRITICAL')
        st.metric("Critical", critical)
    
    # Findings list
    st.markdown("### 🚨 Findings")
    for finding in assessment.findings[:15]:
        sev_icon = {'CRITICAL': '🔴', 'HIGH': '🟠', 'MEDIUM': '🟡', 'LOW': '🟢'}.get(finding.severity, '⚪')
        with st.expander(f"{sev_icon} {finding.title}"):
            st.markdown(f"**Pillar:** {finding.pillar}")
            st.markdown(f"**Description:** {finding.description}")
            if finding.recommendation:
                st.success(f"💡 {finding.recommendation}")

# ============================================================================
# KNOWLEDGE BASE TAB
# ============================================================================

def render_knowledge_base_tab():
    """Render knowledge base"""
    st.markdown("### 📚 AWS Well-Architected Framework Knowledge Base")
    
    for key, pillar in WAF_PILLARS.items():
        with st.expander(f"{pillar['icon']} {pillar['name']}"):
            st.markdown(f"[📖 AWS Documentation](https://docs.aws.amazon.com/wellarchitected/latest/framework/{key.replace('_', '-')}.html)")

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main application"""
    init_session_state()
    render_sidebar()
    
    # Header
    is_demo = st.session_state.get('app_mode', 'demo') == 'demo'
    mode_badge = "🎭 Demo" if is_demo else "🔴 Live"
    mode_color = "#1565C0" if is_demo else "#2E7D32"
    
    st.markdown(f"""
    <div class="main-header">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h1>🏗️ AWS Well-Architected Framework Advisor</h1>
                <p>AI-Powered Architecture Review & Risk Assessment</p>
            </div>
            <div style="background: {mode_color}; padding: 0.5rem 1rem; border-radius: 20px; color: white; font-weight: 600;">
                {mode_badge}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Tabs
    tab_names = [
        "🎯 AWS Scanner",
        "📤 Architecture Review",
        "📊 WAF Results",
        "🚀 EKS & Modernization",
        "💰 FinOps",
        "📋 Compliance",
        "🔄 Migration & DR",
        "📚 Knowledge Base"
    ]
    
    tabs = st.tabs(tab_names)
    
    with tabs[0]:
        if MODULE_STATUS.get('Landscape Scanner'):
            render_landscape_scanner_tab()
        else:
            st.error(f"Module not loaded: {MODULE_ERRORS.get('landscape_scanner', 'Unknown error')}")
    
    with tabs[1]:
        render_architecture_review_tab()
    
    with tabs[2]:
        render_waf_results_tab()
    
    with tabs[3]:
        if MODULE_STATUS.get('EKS & Modernization'):
            render_eks_modernization_tab()
        else:
            st.error(f"Module not loaded: {MODULE_ERRORS.get('eks_modernization', 'Unknown error')}")
    
    with tabs[4]:
        if MODULE_STATUS.get('FinOps'):
            render_finops_tab()
        else:
            st.error(f"Module not loaded: {MODULE_ERRORS.get('finops_module', 'Unknown error')}")
    
    with tabs[5]:
        if MODULE_STATUS.get('Compliance'):
            render_compliance_tab()
        else:
            st.error(f"Module not loaded: {MODULE_ERRORS.get('compliance_module', 'Unknown error')}")
    
    with tabs[6]:
        if MODULE_STATUS.get('Migration & DR'):
            render_migration_dr_tab()
        else:
            st.error(f"Module not loaded: {MODULE_ERRORS.get('migration_dr_module', 'Unknown error')}")
    
    with tabs[7]:
        render_knowledge_base_tab()

if __name__ == "__main__":
    main()
