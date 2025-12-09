"""
Compliance & Governance Module
Comprehensive Regulatory Compliance Assessment Platform

Features:
- Multi-framework compliance assessment
- Control mapping across frameworks
- Gap analysis with remediation guidance
- Continuous compliance monitoring
- Audit-ready reporting
"""

import streamlit as st
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, field
import json

# ============================================================================
# COMPLIANCE FRAMEWORKS
# ============================================================================

COMPLIANCE_FRAMEWORKS = {
    "soc2": {
        "name": "SOC 2",
        "icon": "🔐",
        "description": "Service Organization Control 2 - Trust Services Criteria",
        "categories": ["Security", "Availability", "Processing Integrity", "Confidentiality", "Privacy"],
        "aws_artifacts": ["SOC 2 Type II Report"],
        "key_controls": [
            {"id": "CC6.1", "name": "Logical Access Controls", "description": "Access to systems is controlled"},
            {"id": "CC6.6", "name": "System Operations", "description": "Security events are logged and monitored"},
            {"id": "CC7.2", "name": "System Monitoring", "description": "System anomalies are identified"},
            {"id": "CC8.1", "name": "Change Management", "description": "Changes are authorized and tested"}
        ]
    },
    "hipaa": {
        "name": "HIPAA",
        "icon": "🏥",
        "description": "Health Insurance Portability and Accountability Act",
        "categories": ["Administrative Safeguards", "Physical Safeguards", "Technical Safeguards"],
        "aws_artifacts": ["HIPAA BAA", "HIPAA Whitepaper"],
        "key_controls": [
            {"id": "164.312(a)(1)", "name": "Access Control", "description": "Unique user identification"},
            {"id": "164.312(b)", "name": "Audit Controls", "description": "Hardware/software recording mechanisms"},
            {"id": "164.312(c)(1)", "name": "Integrity", "description": "Protect ePHI from alteration"},
            {"id": "164.312(e)(1)", "name": "Transmission Security", "description": "Protect ePHI during transmission"}
        ]
    },
    "pci_dss": {
        "name": "PCI DSS",
        "icon": "💳",
        "description": "Payment Card Industry Data Security Standard v4.0",
        "categories": ["Build Secure Network", "Protect Cardholder Data", "Vulnerability Management", 
                      "Access Control", "Monitor Networks", "Security Policies"],
        "aws_artifacts": ["PCI DSS AOC", "PCI DSS Responsibility Summary"],
        "key_controls": [
            {"id": "Req 1", "name": "Firewall Configuration", "description": "Install and maintain network security controls"},
            {"id": "Req 3", "name": "Protect Stored Data", "description": "Protect stored account data"},
            {"id": "Req 7", "name": "Access Restriction", "description": "Restrict access by business need to know"},
            {"id": "Req 10", "name": "Logging", "description": "Log and monitor all access to system components"}
        ]
    },
    "gdpr": {
        "name": "GDPR",
        "icon": "🇪🇺",
        "description": "General Data Protection Regulation",
        "categories": ["Data Processing", "Data Subject Rights", "Security Measures", "Data Transfers"],
        "aws_artifacts": ["GDPR DPA", "GDPR Whitepaper"],
        "key_controls": [
            {"id": "Art 5", "name": "Data Processing Principles", "description": "Lawfulness, fairness, transparency"},
            {"id": "Art 17", "name": "Right to Erasure", "description": "Right to be forgotten"},
            {"id": "Art 32", "name": "Security of Processing", "description": "Appropriate technical measures"},
            {"id": "Art 33", "name": "Breach Notification", "description": "72-hour notification requirement"}
        ]
    },
    "iso27001": {
        "name": "ISO 27001",
        "icon": "📋",
        "description": "Information Security Management System",
        "categories": ["Organizational", "People", "Physical", "Technological"],
        "aws_artifacts": ["ISO 27001 Certificate"],
        "key_controls": [
            {"id": "A.5", "name": "Information Security Policies", "description": "Management direction"},
            {"id": "A.8", "name": "Asset Management", "description": "Inventory and classification"},
            {"id": "A.9", "name": "Access Control", "description": "Limit access to information"},
            {"id": "A.12", "name": "Operations Security", "description": "Correct and secure operations"}
        ]
    },
    "cis_aws": {
        "name": "CIS AWS Foundations",
        "icon": "🔧",
        "description": "CIS Amazon Web Services Foundations Benchmark v2.0",
        "categories": ["Identity and Access Management", "Storage", "Logging", "Monitoring", "Networking"],
        "aws_artifacts": ["Security Hub CIS Standard"],
        "key_controls": [
            {"id": "1.4", "name": "Root Account MFA", "description": "Ensure MFA is enabled for root account"},
            {"id": "2.1.1", "name": "S3 Block Public Access", "description": "Ensure S3 block public access is enabled"},
            {"id": "3.1", "name": "CloudTrail Enabled", "description": "Ensure CloudTrail is enabled in all regions"},
            {"id": "4.1", "name": "Security Group SSH", "description": "Ensure no SG allows 0.0.0.0/0 to SSH"}
        ]
    },
    "nist_csf": {
        "name": "NIST CSF",
        "icon": "🔬",
        "description": "NIST Cybersecurity Framework",
        "categories": ["Identify", "Protect", "Detect", "Respond", "Recover"],
        "aws_artifacts": ["NIST Whitepaper"],
        "key_controls": [
            {"id": "ID.AM", "name": "Asset Management", "description": "Data, systems, and capabilities managed"},
            {"id": "PR.AC", "name": "Access Control", "description": "Access to assets is managed"},
            {"id": "DE.CM", "name": "Continuous Monitoring", "description": "Systems are monitored"},
            {"id": "RS.RP", "name": "Response Planning", "description": "Response processes executed"}
        ]
    },
    "fedramp": {
        "name": "FedRAMP",
        "icon": "🏛️",
        "description": "Federal Risk and Authorization Management Program",
        "categories": ["Access Control", "Audit", "Configuration Management", "Incident Response", "System Protection"],
        "aws_artifacts": ["FedRAMP Package"],
        "key_controls": [
            {"id": "AC-2", "name": "Account Management", "description": "Manage information system accounts"},
            {"id": "AU-2", "name": "Audit Events", "description": "Organization-defined auditable events"},
            {"id": "CM-2", "name": "Baseline Configuration", "description": "Develop and maintain configurations"},
            {"id": "SC-7", "name": "Boundary Protection", "description": "Monitor and control communications"}
        ]
    }
}

AWS_COMPLIANCE_SERVICES = {
    "security_hub": {
        "name": "AWS Security Hub",
        "description": "Centralized security findings and compliance checks",
        "supported_standards": ["CIS AWS", "PCI DSS", "NIST CSF", "AWS Best Practices"],
        "implementation": "Enable Security Hub and activate desired security standards"
    },
    "config": {
        "name": "AWS Config",
        "description": "Configuration compliance and change tracking",
        "supported_standards": ["Custom rules", "Conformance packs for SOC 2, HIPAA, PCI"],
        "implementation": "Enable Config, create rules, deploy conformance packs"
    },
    "audit_manager": {
        "name": "AWS Audit Manager",
        "description": "Automated evidence collection for audits",
        "supported_standards": ["SOC 2", "HIPAA", "PCI DSS", "GDPR", "NIST CSF", "ISO 27001"],
        "implementation": "Create assessment, select framework, collect evidence"
    },
    "cloudtrail": {
        "name": "AWS CloudTrail",
        "description": "API activity logging and audit trail",
        "supported_standards": ["All frameworks requiring audit logs"],
        "implementation": "Enable organization trail, enable log file validation"
    },
    "guardduty": {
        "name": "Amazon GuardDuty",
        "description": "Threat detection and continuous monitoring",
        "supported_standards": ["SOC 2", "PCI DSS", "NIST CSF"],
        "implementation": "Enable GuardDuty in all regions and accounts"
    },
    "macie": {
        "name": "Amazon Macie",
        "description": "Sensitive data discovery and protection",
        "supported_standards": ["GDPR", "HIPAA", "PCI DSS"],
        "implementation": "Enable Macie, create discovery jobs, review findings"
    },
    "inspector": {
        "name": "Amazon Inspector",
        "description": "Vulnerability management",
        "supported_standards": ["PCI DSS", "SOC 2", "NIST CSF"],
        "implementation": "Enable Inspector, configure scanning coverage"
    },
    "artifact": {
        "name": "AWS Artifact",
        "description": "Compliance reports and agreements",
        "supported_standards": ["All - contains AWS compliance documentation"],
        "implementation": "Download reports, execute agreements (BAA, DPA)"
    }
}

# ============================================================================
# CONTROL MAPPING
# ============================================================================

CONTROL_CATEGORIES = {
    "access_control": {
        "name": "Access Control",
        "description": "User authentication, authorization, and access management",
        "aws_services": ["IAM", "SSO", "Organizations", "Cognito"],
        "key_practices": [
            "Implement least privilege access",
            "Use IAM roles instead of users where possible",
            "Enable MFA for all users",
            "Implement strong password policies",
            "Regular access reviews"
        ]
    },
    "data_protection": {
        "name": "Data Protection",
        "description": "Encryption, data classification, and protection",
        "aws_services": ["KMS", "Macie", "S3", "EBS", "RDS encryption"],
        "key_practices": [
            "Encrypt data at rest and in transit",
            "Implement data classification",
            "Use customer-managed KMS keys",
            "Enable versioning and object lock for critical data",
            "Implement data loss prevention"
        ]
    },
    "logging_monitoring": {
        "name": "Logging & Monitoring",
        "description": "Audit logging, monitoring, and alerting",
        "aws_services": ["CloudTrail", "CloudWatch", "VPC Flow Logs", "Config"],
        "key_practices": [
            "Enable CloudTrail in all regions",
            "Configure log file validation",
            "Set up centralized logging",
            "Create security metric filters and alarms",
            "Implement log retention policies"
        ]
    },
    "network_security": {
        "name": "Network Security",
        "description": "Network segmentation, firewalls, and protection",
        "aws_services": ["VPC", "Security Groups", "NACLs", "WAF", "Shield"],
        "key_practices": [
            "Implement network segmentation",
            "Use private subnets for sensitive workloads",
            "Restrict security group rules",
            "Enable VPC flow logs",
            "Deploy WAF for web applications"
        ]
    },
    "incident_response": {
        "name": "Incident Response",
        "description": "Security incident detection, response, and recovery",
        "aws_services": ["GuardDuty", "Security Hub", "Detective", "EventBridge"],
        "key_practices": [
            "Enable threat detection services",
            "Create incident response runbooks",
            "Automate response with Lambda",
            "Regular incident response testing",
            "Post-incident reviews"
        ]
    },
    "vulnerability_management": {
        "name": "Vulnerability Management",
        "description": "Vulnerability scanning, patching, and remediation",
        "aws_services": ["Inspector", "Systems Manager", "ECR scanning"],
        "key_practices": [
            "Enable continuous vulnerability scanning",
            "Implement automated patching",
            "Prioritize remediation by severity",
            "Track remediation SLAs",
            "Scan container images"
        ]
    }
}

# ============================================================================
# RENDER FUNCTIONS
# ============================================================================

def render_compliance_tab():
    """Render comprehensive compliance tab"""
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #4a148c 0%, #7b1fa2 100%); padding: 2rem; border-radius: 12px; margin-bottom: 1.5rem;">
        <h2 style="color: #E1BEE7; margin: 0;">📋 Compliance & Governance</h2>
        <p style="color: #CE93D8; margin: 0.5rem 0 0 0;">Multi-Framework Compliance Assessment Platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    tabs = st.tabs([
        "🎯 Framework Selection",
        "📊 Gap Analysis",
        "🔧 AWS Controls",
        "📋 Control Mapping",
        "📑 Audit Preparation"
    ])
    
    with tabs[0]:
        render_framework_selection()
    
    with tabs[1]:
        render_gap_analysis()
    
    with tabs[2]:
        render_aws_controls()
    
    with tabs[3]:
        render_control_mapping()
    
    with tabs[4]:
        render_audit_preparation()

def render_framework_selection():
    """Render framework selection"""
    st.markdown("### 🎯 Select Applicable Compliance Frameworks")
    st.markdown("Choose the regulatory frameworks that apply to your organization")
    
    selected_frameworks = []
    
    cols = st.columns(4)
    
    for idx, (key, framework) in enumerate(COMPLIANCE_FRAMEWORKS.items()):
        with cols[idx % 4]:
            if st.checkbox(f"{framework['icon']} {framework['name']}", key=f"fw_{key}"):
                selected_frameworks.append(key)
            st.caption(framework['description'][:60] + "...")
    
    if selected_frameworks:
        st.session_state['selected_frameworks'] = selected_frameworks
        st.success(f"✅ Selected {len(selected_frameworks)} framework(s)")
        
        st.markdown("---")
        st.markdown("### 📋 Framework Details")
        
        for fw_key in selected_frameworks:
            fw = COMPLIANCE_FRAMEWORKS[fw_key]
            
            with st.expander(f"{fw['icon']} {fw['name']} - Details"):
                st.markdown(f"**Description:** {fw['description']}")
                
                st.markdown("**Categories:**")
                for cat in fw['categories']:
                    st.markdown(f"- {cat}")
                
                st.markdown("**AWS Artifacts Available:**")
                for artifact in fw['aws_artifacts']:
                    st.markdown(f"- 📄 {artifact}")
                
                st.markdown("**Key Controls:**")
                for ctrl in fw['key_controls']:
                    st.markdown(f"- **{ctrl['id']}**: {ctrl['name']} - {ctrl['description']}")
    else:
        st.info("Select at least one framework to proceed")

def render_gap_analysis():
    """Render gap analysis"""
    st.markdown("### 📊 Compliance Gap Analysis")
    
    if not st.session_state.get('selected_frameworks'):
        st.info("Select frameworks in the Framework Selection tab first")
        return
    
    st.markdown("Rate your current compliance posture for each control area")
    
    scores = {}
    
    col1, col2 = st.columns(2)
    
    control_areas = [
        ("Access Control", "access_control"),
        ("Data Protection", "data_protection"),
        ("Logging & Monitoring", "logging_monitoring"),
        ("Network Security", "network_security"),
        ("Incident Response", "incident_response"),
        ("Vulnerability Management", "vulnerability_management"),
        ("Change Management", "change_mgmt"),
        ("Business Continuity", "bc_dr")
    ]
    
    for idx, (name, key) in enumerate(control_areas):
        with [col1, col2][idx % 2]:
            scores[key] = st.slider(name, 0, 100, 60, key=f"gap_{key}")
    
    avg_score = sum(scores.values()) / len(scores)
    
    st.markdown("---")
    
    # Results
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        color = "#388E3C" if avg_score >= 80 else "#FBC02D" if avg_score >= 60 else "#D32F2F"
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem; background: white; border-radius: 10px;">
            <div style="font-size: 2.5rem; font-weight: bold; color: {color};">{avg_score:.0f}%</div>
            <div style="color: #666;">Compliance Score</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        gaps = len([k for k, v in scores.items() if v < 60])
        st.metric("Critical Gaps", gaps)
    
    with col3:
        frameworks = len(st.session_state.get('selected_frameworks', []))
        st.metric("Frameworks", frameworks)
    
    with col4:
        status = "Ready" if avg_score >= 80 else "In Progress" if avg_score >= 60 else "At Risk"
        st.metric("Audit Status", status)
    
    # Gap details
    st.markdown("### 🔍 Gap Details")
    
    gaps = [(k, v) for k, v in scores.items() if v < 70]
    gaps.sort(key=lambda x: x[1])
    
    for key, score in gaps:
        name = next((n for n, k in control_areas if k == key), key)
        severity = "🔴 Critical" if score < 40 else "🟠 High" if score < 60 else "🟡 Medium"
        
        with st.expander(f"{severity} {name} - {score}%"):
            if key in CONTROL_CATEGORIES:
                cat = CONTROL_CATEGORIES[key]
                st.markdown(f"**AWS Services to Use:** {', '.join(cat['aws_services'])}")
                st.markdown("**Recommended Practices:**")
                for practice in cat['key_practices']:
                    st.markdown(f"- {practice}")

def render_aws_controls():
    """Render AWS compliance controls"""
    st.markdown("### 🔧 AWS Compliance Services")
    st.markdown("AWS services to achieve and maintain compliance")
    
    for key, service in AWS_COMPLIANCE_SERVICES.items():
        with st.expander(f"📦 {service['name']}"):
            st.markdown(f"**Description:** {service['description']}")
            st.markdown(f"**Supported Standards:** {service['supported_standards']}")
            st.markdown(f"**Implementation:** {service['implementation']}")

def render_control_mapping():
    """Render control mapping across frameworks"""
    st.markdown("### 📋 Cross-Framework Control Mapping")
    st.markdown("See how controls map across different compliance frameworks")
    
    # Example mapping
    mapping_data = [
        {
            "control": "Multi-Factor Authentication",
            "soc2": "CC6.1",
            "pci_dss": "Req 8.3",
            "hipaa": "164.312(d)",
            "gdpr": "Art 32",
            "cis_aws": "1.4, 1.5",
            "aws_service": "IAM MFA, SSO"
        },
        {
            "control": "Encryption at Rest",
            "soc2": "CC6.7",
            "pci_dss": "Req 3.4",
            "hipaa": "164.312(a)(2)(iv)",
            "gdpr": "Art 32",
            "cis_aws": "2.1.1",
            "aws_service": "KMS, S3, EBS, RDS"
        },
        {
            "control": "Audit Logging",
            "soc2": "CC7.2",
            "pci_dss": "Req 10",
            "hipaa": "164.312(b)",
            "gdpr": "Art 30",
            "cis_aws": "3.1",
            "aws_service": "CloudTrail, Config"
        },
        {
            "control": "Access Reviews",
            "soc2": "CC6.2",
            "pci_dss": "Req 7.2",
            "hipaa": "164.308(a)(4)",
            "gdpr": "Art 5",
            "cis_aws": "1.16",
            "aws_service": "IAM Access Analyzer"
        }
    ]
    
    # Display as table
    import pandas as pd
    df = pd.DataFrame(mapping_data)
    st.dataframe(df, use_container_width=True)

def render_audit_preparation():
    """Render audit preparation guidance"""
    st.markdown("### 📑 Audit Preparation Checklist")
    
    checklist = [
        {"item": "Enable AWS Audit Manager", "status": False, "priority": "High"},
        {"item": "Select compliance framework in Audit Manager", "status": False, "priority": "High"},
        {"item": "Enable Security Hub with compliance standards", "status": False, "priority": "High"},
        {"item": "Configure centralized logging in CloudTrail", "status": False, "priority": "High"},
        {"item": "Enable Config with conformance packs", "status": False, "priority": "Medium"},
        {"item": "Download compliance artifacts from AWS Artifact", "status": False, "priority": "Medium"},
        {"item": "Execute BAA/DPA in AWS Artifact (if needed)", "status": False, "priority": "Medium"},
        {"item": "Document shared responsibility model", "status": False, "priority": "Medium"},
        {"item": "Create evidence collection schedule", "status": False, "priority": "Low"},
        {"item": "Prepare system description document", "status": False, "priority": "Low"},
    ]
    
    st.markdown("Track your audit preparation progress:")
    
    completed = 0
    for item in checklist:
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            if st.checkbox(item['item'], key=f"audit_{item['item'][:20]}"):
                completed += 1
        with col2:
            priority_colors = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}
            st.markdown(priority_colors.get(item['priority'], "⚪"))
        with col3:
            st.caption(item['priority'])
    
    st.markdown("---")
    progress = (completed / len(checklist)) * 100
    st.progress(progress / 100)
    st.markdown(f"**Progress:** {completed}/{len(checklist)} items ({progress:.0f}%)")

# Export
__all__ = ['render_compliance_tab']
