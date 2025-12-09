"""
AWS Well-Architected Framework Advisor - Enterprise Edition
AI-Powered Architecture Review & Risk Assessment Platform

Version: 2.2.0 - Now with Firebase Authentication
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
# FIREBASE AUTHENTICATION - NEW
# ============================================================================

# Firebase Authentication Module Import
try:
    from firebase_auth_module import (
        firebase_manager,
        check_authentication,
        render_login_page,
        render_admin_user_management,
        render_user_profile_sidebar,
        has_permission,
        UserRole
    )
    FIREBASE_AVAILABLE = True
except ImportError as e:
    FIREBASE_AVAILABLE = False
    st.warning(f"⚠️ Firebase authentication not available: {str(e)}")

# Firebase Initialization
def initialize_firebase():
    """Initialize Firebase on first run"""
    if not FIREBASE_AVAILABLE:
        st.session_state.firebase_initialized = False
        st.session_state.auth_disabled = True
        return
    
    if 'firebase_initialized' not in st.session_state:
        try:
            # Get Firebase config from Streamlit secrets
            if not hasattr(st, 'secrets') or 'firebase' not in st.secrets:
                st.session_state.firebase_initialized = False
                st.session_state.auth_disabled = True
                st.warning("⚠️ Firebase not configured. Running in non-authenticated mode.")
                return
            
            # Get Firebase config - web_config is optional for server-side only auth
            config = {
                'service_account_key': dict(st.secrets['firebase']['service_account_key'])
            }
            
            # Add web_config only if present (needed for client-side auth like Google Sign-In)
            if 'web_config' in st.secrets['firebase']:
                config['web_config'] = dict(st.secrets['firebase']['web_config'])
            
            success, message = firebase_manager.initialize_firebase(config)
            
            if success:
                st.session_state.firebase_initialized = True
                st.session_state.auth_disabled = False
            else:
                st.error(f"🔥 Firebase initialization failed: {message}")
                st.info("""
                **Firebase Setup Required:**
                1. Complete Firebase setup (see FIREBASE_SETUP_GUIDE.md)
                2. Add Firebase credentials to .streamlit/secrets.toml
                3. Restart the app
                
                The app will run in non-authenticated mode for now.
                """)
                st.session_state.firebase_initialized = False
                st.session_state.auth_disabled = True
                
        except Exception as e:
            st.error(f"❌ Firebase configuration error: {str(e)}")
            st.info("Running in non-authenticated mode. Add Firebase credentials to enable authentication.")
            st.session_state.firebase_initialized = False
            st.session_state.auth_disabled = True

# Initialize Firebase
initialize_firebase()

# Check Authentication (if enabled)
if not st.session_state.get('auth_disabled', False) and FIREBASE_AVAILABLE:
    if not check_authentication():
        render_login_page()
        st.stop()

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
    from eks_modernization_module import render_eks_modernization_tab
    MODULE_STATUS['EKS & Modernization'] = True
except Exception as e:
    MODULE_STATUS['EKS & Modernization'] = False
    MODULE_ERRORS['eks_modernization'] = str(e)

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

# WAF Review Module
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
    .user-profile {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 1rem;
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
# AWS CREDENTIALS AUTO-LOADING
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
        'aws_auto_loaded': False,
        # Authentication state (initialized by firebase_auth_module if available)
        'authenticated': False,
        'user_uid': None,
        'user_email': None,
        'user_name': None,
        'user_role': 'viewer'
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
# SIDEBAR - ENHANCED WITH USER PROFILE
# ============================================================================

def render_sidebar():
    """Render sidebar with user profile"""
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0;">
            <img src="data:image/jpeg;base64,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" 
                 width="80" style="margin-bottom: 0.5rem;">
            <h3 style="color: #FF9900; margin: 0.5rem 0 0 0; font-size: 1rem; font-weight: 700;">Well-Architected Advisor</h3>
            <p style="color: #232F3E; font-size: 0.85rem; margin: 0; font-weight: 600;">Enterprise Edition v2.2</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # User Profile - NEW
        if FIREBASE_AVAILABLE and st.session_state.get('authenticated'):
            render_user_profile_sidebar()
        elif not st.session_state.get('auth_disabled', False):
            st.info("🔐 Authenticated")
        
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
        st.markdown("### ⚡ Quick Actions")
        if st.button("🔄 Reset Session", use_container_width=True):
            for key in list(st.session_state.keys()):
                if key not in ['authenticated', 'user_uid', 'user_email', 'user_name', 'user_role', 'firebase_initialized']:
                    del st.session_state[key]
            st.rerun()

# ============================================================================
# DASHBOARD
# ============================================================================

def render_executive_dashboard():
    """Render executive dashboard"""
    # Welcome message with user name if authenticated
    if st.session_state.get('authenticated'):
        user_name = st.session_state.get('user_name', 'User')
        user_role = st.session_state.get('user_role', 'viewer')
        role_icon = {'admin': '👑', 'user': '👤', 'viewer': '👁️'}.get(user_role, '👤')
        st.markdown(f"### Welcome back, {user_name}! {role_icon}")
    else:
        st.markdown("### Executive Dashboard")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card"><div class="metric-value">92</div><div class="metric-label">WAF Score</div></div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card"><div class="metric-value">3</div><div class="metric-label">Critical Issues</div></div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card"><div class="metric-value">$2.4M</div><div class="metric-label">Est. Annual Savings</div></div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card"><div class="metric-value">15</div><div class="metric-label">Workloads</div></div>', unsafe_allow_html=True)
    
    st.markdown("")
    
    # Quick Stats
    st.markdown("#### 📊 Assessment Overview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        st.markdown("**Last Assessment**")
        st.markdown("- Date: December 8, 2025")
        st.markdown("- Workload: Production API")
        st.markdown("- Score: 92/100")
        st.markdown("- Status: ✅ Passed")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        st.markdown("**Key Findings**")
        st.markdown("- 🔴 3 Critical")
        st.markdown("- 🟠 8 High")
        st.markdown("- 🟡 12 Medium")
        st.markdown("- 🟢 5 Low")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Role-specific information
    if FIREBASE_AVAILABLE and st.session_state.get('authenticated'):
        user_role = st.session_state.get('user_role', 'viewer')
        
        st.markdown("---")
        st.markdown("#### 🎯 Your Access Level")
        
        if user_role == 'admin':
            st.info("""
            👑 **Admin Access**
            - Full access to all features
            - Can create and manage users
            - View all assessments across the organization
            - Manage system settings
            """)
        elif user_role == 'user':
            st.info("""
            👤 **User Access**
            - Run AWS assessments
            - View and export your own reports
            - Access all tools and features
            - Create and manage your assessments
            """)
        else:  # viewer
            st.info("""
            👁️ **Viewer Access**
            - Read-only access
            - View architecture patterns
            - Access documentation
            - Contact admin for elevated permissions
            """)

# ============================================================================
# MAIN APPLICATION - ENHANCED WITH ROLE-BASED ACCESS
# ============================================================================

def main():
    """Main application with role-based access control"""
    init_session_state()
    render_sidebar()
    
    is_demo = st.session_state.get('app_mode', 'demo') == 'demo'
    mode_badge = "🎭 Demo" if is_demo else "🔴 Live"
    mode_color = "#1565C0" if is_demo else "#2E7D32"
    
    # Get user role
    user_role = st.session_state.get('user_role', 'viewer')
    auth_disabled = st.session_state.get('auth_disabled', False)
    
    # If auth is disabled, give full access
    if auth_disabled:
        user_role = 'admin'
    
    st.markdown(f'<div class="main-header"><div style="display: flex; justify-content: space-between; align-items: center;"><div><h1>🏗️ AWS Well-Architected Framework Advisor</h1><p>Enterprise AI-Powered Architecture Review Platform</p></div><div style="background: {mode_color}; padding: 0.5rem 1rem; border-radius: 20px; color: white; font-weight: 600;">{mode_badge}</div></div></div>', unsafe_allow_html=True)
    
    # Create tabs based on user role
    if user_role == 'admin' or user_role == UserRole.ADMIN if FIREBASE_AVAILABLE else False:
        # Admin sees all tabs including User Management
        tabs = st.tabs([
            "📊 Dashboard",
            "🏗️ WAF Assessment Hub",
            "📤 Architecture & Migration",
            "🏛️ Architecture Patterns",
            "🚀 EKS & Modernization",
            "👥 User Management"
        ])
        
        with tabs[0]:
            render_executive_dashboard()
        
        with tabs[1]:  # WAF Assessment Hub
            if MODULE_STATUS.get('WAF Review'):
                if has_permission("run_aws_scans") if FIREBASE_AVAILABLE and not auth_disabled else True:
                    render_waf_review_tab()
                else:
                    st.warning("⚠️ You don't have permission to run AWS scans")
            else:
                st.error("❌ WAF Assessment Hub Not Loaded")
                st.info("""
                💡 To enable WAF Assessment Hub:
                
                ```
                # 1. Ensure waf_review_module.py is in your project directory
                # 2. Check the error below for details
                ```
                """)
                with st.expander("🔍 Error Details"):
                    st.code(MODULE_ERRORS.get('waf_review_module', 'Module not found'))
        
        with tabs[2]:  # Architecture & Migration
            render_architecture_migration_tab()
        
        with tabs[3]:  # Architecture Patterns
            if MODULE_STATUS.get('Architecture Patterns'):
                render_architecture_patterns_tab()
            else:
                st.error("❌ Architecture Patterns Module Not Loaded")
                st.info("""
                💡 To enable Architecture Patterns:
                
                ```
                # 1. Ensure architecture_patterns.py is in your project directory
                # 2. Check the error below for details
                ```
                """)
                with st.expander("🔍 Error Details"):
                    st.code(MODULE_ERRORS.get('architecture_patterns', 'Module not found'))
        
        with tabs[4]:  # EKS & Modernization
            if MODULE_STATUS.get('EKS & Modernization'):
                if has_permission("run_aws_scans") if FIREBASE_AVAILABLE and not auth_disabled else True:
                    render_eks_modernization_tab()
                else:
                    st.warning("⚠️ You don't have permission to access this feature")
            else:
                st.error("❌ EKS & Modernization Module Not Loaded")
                st.info("""
                💡 To enable EKS & Modernization Hub:
                
                ```
                # 1. Ensure eks_modernization_module.py is in your project directory
                # 2. Check the error below for details
                ```
                """)
                with st.expander("🔍 Error Details"):
                    st.code(MODULE_ERRORS.get('eks_modernization', 'Module not found'))
        
        with tabs[5]:  # User Management (Admin Only)
            if FIREBASE_AVAILABLE and not auth_disabled:
                render_admin_user_management()
            else:
                st.info("""
                👥 **User Management**
                
                Firebase authentication is not configured. 
                
                To enable user management:
                1. Complete Firebase setup (see FIREBASE_SETUP_GUIDE.md)
                2. Add firebase_auth_module.py to your project
                3. Configure .streamlit/secrets.toml with Firebase credentials
                4. Restart the app
                """)
    
    elif user_role == 'user' or user_role == UserRole.USER if FIREBASE_AVAILABLE else False:
        # Regular users see standard tabs (no User Management)
        tabs = st.tabs([
            "📊 Dashboard",
            "🏗️ WAF Assessment Hub",
            "📤 Architecture & Migration",
            "🏛️ Architecture Patterns",
            "🚀 EKS & Modernization"
        ])
        
        with tabs[0]:
            render_executive_dashboard()
        
        with tabs[1]:
            if MODULE_STATUS.get('WAF Review'):
                if has_permission("run_aws_scans") if FIREBASE_AVAILABLE else True:
                    render_waf_review_tab()
                else:
                    st.warning("⚠️ You don't have permission to run AWS scans")
            else:
                st.error("❌ WAF Assessment Hub Not Loaded")
                with st.expander("🔍 Error Details"):
                    st.code(MODULE_ERRORS.get('waf_review_module', 'Module not found'))
        
        with tabs[2]:
            render_architecture_migration_tab()
        
        with tabs[3]:
            if MODULE_STATUS.get('Architecture Patterns'):
                render_architecture_patterns_tab()
            else:
                st.error("❌ Architecture Patterns Module Not Loaded")
        
        with tabs[4]:
            if MODULE_STATUS.get('EKS & Modernization'):
                render_eks_modernization_tab()
            else:
                st.error("❌ EKS & Modernization Module Not Loaded")
    
    else:  # viewer or default
        # Viewers see limited tabs
        tabs = st.tabs([
            "📊 Dashboard",
            "🏛️ Architecture Patterns"
        ])
        
        with tabs[0]:
            render_executive_dashboard()
            if not auth_disabled:
                st.info("👁️ You have viewer access. Contact your administrator for additional permissions.")
        
        with tabs[1]:
            if MODULE_STATUS.get('Architecture Patterns'):
                render_architecture_patterns_tab()
            else:
                st.error("❌ Architecture Patterns Module Not Loaded")
    
    st.markdown('<div class="app-footer">AWS Well-Architected Framework Advisor | Enterprise Edition v2.2 | Powered by Claude AI & Firebase 🔐</div>', unsafe_allow_html=True)

# ============================================================================
# ARCHITECTURE & MIGRATION TAB
# ============================================================================

def render_architecture_migration_tab():
    """
    Consolidated Architecture Review + Migration Planning + DR Strategy
    This integrates three related workflows into one cohesive experience
    """
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 2rem; border-radius: 12px; margin-bottom: 2rem;">
        <h2 style="color: white; margin: 0;">📤 Architecture & Migration Planning</h2>
        <p style="color: white; opacity: 0.9; margin: 0.5rem 0 0 0;">
            Complete architecture assessment, migration planning, and DR strategy in one place
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sub-navigation for this consolidated tab
    arch_tabs = st.tabs([
        "🏗️ Architecture Review",
        "🔄 Migration Planning",
        "🛡️ DR & Business Continuity"
    ])
    
    with arch_tabs[0]:
        # Original architecture review functionality
        render_architecture_review_content()
    
    with arch_tabs[1]:
        # Migration planning (previously separate tab)
        render_migration_planning()
    
    with arch_tabs[2]:
        # DR strategy (previously part of separate tab)
        render_dr_strategy()

def render_architecture_review_content():
    """Original architecture review functionality"""
    st.markdown("### 🏗️ Architecture Review")
    
    st.markdown("""
    Comprehensive architecture assessment covering:
    - Current state analysis
    - Target architecture design
    - Gap analysis and recommendations
    - Implementation roadmap
    """)
    
    # Simplified architecture review form
    with st.form("architecture_review"):
        st.markdown("#### Current Architecture")
        
        col1, col2 = st.columns(2)
        
        with col1:
            workload_name = st.text_input("Workload Name")
            architecture_type = st.selectbox(
                "Architecture Type",
                ["Monolithic", "N-Tier", "Microservices", "Serverless", "Event-Driven", "Hybrid"]
            )
        
        with col2:
            deployment_model = st.selectbox(
                "Deployment Model",
                ["On-Premises", "Hybrid", "Cloud-Native", "Multi-Cloud"]
            )
            tech_stack = st.multiselect(
                "Technology Stack",
                ["Containers", "Serverless", "VMs", "Databases", "APIs", "Message Queues"]
            )
        
        architecture_notes = st.text_area(
            "Architecture Notes",
            placeholder="Describe key components, data flows, and integration points...",
            height=120
        )
        
        submitted = st.form_submit_button("📊 Generate Architecture Assessment", type="primary", use_container_width=True)
        
        if submitted:
            with st.spinner("Analyzing architecture..."):
                st.success("✅ Architecture assessment complete!")
                
                st.markdown("### 📋 Assessment Summary")
                
                st.info(f"""
                **Workload:** {workload_name or 'Not specified'}
                **Architecture:** {architecture_type}
                **Deployment:** {deployment_model}
                **Stack:** {', '.join(tech_stack) if tech_stack else 'Not specified'}
                """)
                
                st.markdown("**Key Recommendations:**")
                st.markdown("""
                1. ✅ Consider microservices decomposition
                2. ✅ Implement API gateway pattern
                3. ✅ Add caching layer
                4. ✅ Improve monitoring and observability
                5. ✅ Implement circuit breaker pattern
                """)

def render_migration_planning():
    """Migration planning functionality"""
    st.markdown("### 🔄 Migration Planning")
    
    st.markdown("""
    Plan your migration to AWS using the **6 R's strategy**:
    - **Rehost** (Lift & Shift)
    - **Replatform** (Lift & Reshape)
    - **Refactor** (Re-architect)
    - **Repurchase** (Replace)
    - **Retain** (Keep as-is)
    - **Retire** (Decommission)
    """)
    
    col_m1, col_m2 = st.columns(2)
    
    with col_m1:
        st.markdown("**Current Environment**")
        
        col_env1, col_env2 = st.columns(2)
        
        with col_env1:
            workload_name = st.text_input("Workload Name", key="migration_workload")
            current_platform = st.selectbox(
                "Current Platform",
                ["On-Premises", "Colocation", "Other Cloud", "Hybrid"]
            )
        
        with col_env2:
            workload_type = st.selectbox(
                "Workload Type",
                ["Web Application", "Database", "API Service", "Batch Processing", "Analytics"]
            )
        
        complexity = st.select_slider(
            "Complexity Level",
            options=["Simple", "Moderate", "Complex", "Very Complex"],
            value="Moderate"
        )
        
        dependencies = st.text_area(
            "Key Dependencies",
            placeholder="List critical dependencies (databases, APIs, services)...",
            height=100
        )
    
    with col_m2:
        st.markdown("**Migration Strategy**")
        
        strategy = st.radio(
            "Recommended Strategy",
            [
                "🚀 Rehost (Lift & Shift)",
                "🔧 Replatform (Lift & Reshape)",
                "🏗️ Refactor (Re-architect)",
                "🔄 Repurchase (Replace)",
                "🏠 Retain (Keep as-is)",
                "❌ Retire (Decommission)"
            ]
        )
        
        timeline = st.selectbox(
            "Target Timeline",
            ["1-3 months", "3-6 months", "6-12 months", "12+ months"]
        )
    
    if st.button("📊 Generate Migration Plan", type="primary", use_container_width=True):
        with st.spinner("Generating migration plan..."):
            st.success("✅ Migration plan generated!")
            
            st.markdown("### 📋 Migration Plan Summary")
            
            st.info(f"""
            **Workload:** {workload_name or 'Not specified'}
            **Strategy:** {strategy}
            **Timeline:** {timeline}
            **Complexity:** {complexity}
            """)
            
            st.markdown("**Recommended Next Steps:**")
            st.markdown("""
            1. ✅ Complete detailed application discovery
            2. ✅ Identify dependencies and data flows
            3. ✅ Design target AWS architecture
            4. ✅ Create migration runbook
            5. ✅ Set up pilot environment
            6. ✅ Execute pilot migration
            7. ✅ Validate and optimize
            8. ✅ Plan production cutover
            """)

def render_dr_strategy():
    """DR strategy planning"""
    st.markdown("### 🛡️ Disaster Recovery & Business Continuity")
    
    st.markdown("""
    Plan your DR strategy with AWS:
    - Define RTO (Recovery Time Objective) and RPO (Recovery Point Objective)
    - Choose appropriate DR approach
    - Implement backup and restore procedures
    - Test and validate DR plan
    """)
    
    col_dr1, col_dr2 = st.columns(2)
    
    with col_dr1:
        st.markdown("**Recovery Requirements**")
        
        rto_hours = st.slider(
            "RTO (Recovery Time Objective)",
            min_value=0,
            max_value=72,
            value=4,
            format="%d hours"
        )
        
        rpo_minutes = st.slider(
            "RPO (Recovery Point Objective)",
            min_value=0,
            max_value=1440,
            value=60,
            format="%d minutes"
        )
        
        critical_systems = st.multiselect(
            "Critical Systems",
            ["Database", "Application Servers", "API Gateway", "File Storage", "Analytics"]
        )
    
    with col_dr2:
        st.markdown("**DR Approach**")
        
        dr_approach = st.radio(
            "Recommended Approach",
            [
                "🔥 Hot Standby (Active-Active)",
                "🌡️ Warm Standby (Active-Passive)",
                "❄️ Cold Standby (Backup & Restore)",
                "💾 Backup Only"
            ]
        )
        
        st.markdown("**Cost vs Recovery Time:**")
        if "Hot" in dr_approach:
            st.warning("💰 High cost, fastest recovery")
        elif "Warm" in dr_approach:
            st.info("💵 Medium cost, moderate recovery")
        else:
            st.success("💲 Low cost, longer recovery")
    
    if st.button("📊 Generate DR Plan", type="primary", use_container_width=True):
        with st.spinner("Creating DR plan..."):
            st.success("✅ DR plan created!")
            
            st.markdown("### 📋 DR Plan Summary")
            
            st.info(f"""
            **RTO:** {rto_hours} hours
            **RPO:** {rpo_minutes} minutes
            **Approach:** {dr_approach}
            **Critical Systems:** {len(critical_systems)} identified
            """)
            
            st.markdown("**Implementation Steps:**")
            st.markdown("""
            1. ✅ Set up cross-region replication
            2. ✅ Configure automated backups
            3. ✅ Implement monitoring and alerts
            4. ✅ Create runbooks for failover
            5. ✅ Schedule DR testing
            6. ✅ Document recovery procedures
            """)
    
    # DR Testing
    st.markdown("---")
    st.markdown("### 🧪 DR Testing")
    
    col_t1, col_t2 = st.columns(2)
    
    with col_t1:
        st.markdown("**Testing Checklist:**")
        st.checkbox("✅ Document DR procedures", value=True)
        st.checkbox("✅ Validate backup integrity", value=True)
        st.checkbox("✅ Test failover process", value=False)
        st.checkbox("✅ Verify RTO/RPO targets", value=False)
        st.checkbox("✅ Test communication plans", value=False)
        st.checkbox("✅ Update runbooks", value=False)
    
    with col_t2:
        st.markdown("**Last Test Results:**")
        st.success("✅ Backup restore successful")
        st.success("✅ RTO achieved: 2.5 hours (target: < 4 hours)")
        st.warning("⚠️ RPO missed: 75 minutes (target: < 60 min)")
        st.info("💡 Recommendation: Increase backup frequency")

# ============================================================================
# RUN APPLICATION
# ============================================================================

if __name__ == "__main__":
    main()