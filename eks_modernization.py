"""
EKS & Container Modernization Module
Comprehensive AI-Powered Kubernetes Modernization Platform

Features:
- Technology comparison matrices with AI recommendations
- Implementation guides for Karpenter, Service Mesh, GitOps
- CI/CD maturity assessment with actionable roadmap
- Cost-benefit analysis for modernization initiatives
- AI-powered personalized recommendations
"""

import streamlit as st
import json
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, field

# ============================================================================
# COMPREHENSIVE TECHNOLOGY CATALOG
# ============================================================================

EKS_TECHNOLOGY_CATALOG = {
    "autoscaling": {
        "name": "Node Autoscaling",
        "icon": "📈",
        "description": "Automatically adjust cluster capacity based on workload demands",
        "technologies": {
            "karpenter": {
                "name": "Karpenter",
                "vendor": "AWS",
                "maturity": "Production Ready",
                "complexity": "Medium",
                "cost_impact": "20-50% savings",
                "description": "Next-gen node provisioning - provisions right-sized nodes in seconds",
                "key_features": [
                    "Sub-minute node provisioning",
                    "Automatic right-sizing based on pod requirements",
                    "Spot instance integration with interruption handling",
                    "Consolidation to reduce cluster costs",
                    "No node groups required",
                    "Custom provisioner configurations"
                ],
                "best_for": [
                    "Dynamic/variable workloads",
                    "Cost optimization focus",
                    "Mixed instance type requirements",
                    "Spot instance utilization"
                ],
                "considerations": [
                    "Requires careful provisioner configuration",
                    "Learning curve for teams familiar with Cluster Autoscaler",
                    "AWS-specific (though working on multi-cloud)"
                ],
                "implementation_steps": [
                    "Install Karpenter using Helm",
                    "Configure IAM roles for Karpenter controller",
                    "Create Provisioner CRD with instance requirements",
                    "Define NodePool with constraints (instance types, zones, capacity type)",
                    "Configure pod disruption budgets for graceful scaling",
                    "Set up consolidation policies",
                    "Test with sample workloads before production migration",
                    "Gradually migrate from Cluster Autoscaler"
                ],
                "aws_services": ["EC2", "EC2 Spot", "IAM", "SQS (for spot interruption)"],
                "estimated_effort": "2-4 weeks",
                "roi_timeline": "1-2 months"
            },
            "cluster_autoscaler": {
                "name": "Cluster Autoscaler",
                "vendor": "Kubernetes SIG",
                "maturity": "Stable",
                "complexity": "Low",
                "cost_impact": "10-30% savings",
                "description": "Traditional node group-based autoscaling",
                "key_features": [
                    "Node group-based scaling",
                    "Well-documented and widely adopted",
                    "Works with managed node groups",
                    "Predictable behavior"
                ],
                "best_for": [
                    "Teams new to Kubernetes",
                    "Simple, predictable workloads",
                    "Existing node group investments"
                ],
                "considerations": [
                    "Slower scaling (minutes vs seconds)",
                    "Requires pre-defined node groups",
                    "Less optimal bin-packing"
                ],
                "implementation_steps": [
                    "Create managed node groups with appropriate sizes",
                    "Deploy Cluster Autoscaler via Helm",
                    "Configure IAM permissions for ASG management",
                    "Set scaling policies and thresholds",
                    "Test scaling behavior"
                ],
                "aws_services": ["EC2 Auto Scaling", "IAM"],
                "estimated_effort": "1-2 weeks",
                "roi_timeline": "Immediate"
            }
        },
        "comparison_criteria": [
            {"criterion": "Provisioning Speed", "karpenter": "Seconds", "cluster_autoscaler": "Minutes"},
            {"criterion": "Right-sizing", "karpenter": "Automatic per-pod", "cluster_autoscaler": "Fixed node groups"},
            {"criterion": "Spot Support", "karpenter": "Native with interruption handling", "cluster_autoscaler": "Requires separate setup"},
            {"criterion": "Complexity", "karpenter": "Medium", "cluster_autoscaler": "Low"},
            {"criterion": "Cost Savings", "karpenter": "20-50%", "cluster_autoscaler": "10-30%"},
            {"criterion": "Multi-AZ", "karpenter": "Automatic", "cluster_autoscaler": "Per node group"},
            {"criterion": "Learning Curve", "karpenter": "Steeper", "cluster_autoscaler": "Gentle"}
        ]
    },
    "service_mesh": {
        "name": "Service Mesh",
        "icon": "🕸️",
        "description": "Manage service-to-service communication with observability and security",
        "technologies": {
            "istio": {
                "name": "Istio",
                "vendor": "Google/IBM/Lyft",
                "maturity": "Production Ready",
                "complexity": "High",
                "cost_impact": "Operational overhead offset by observability gains",
                "description": "Feature-rich service mesh with comprehensive traffic management",
                "key_features": [
                    "Advanced traffic management (canary, blue-green, A/B)",
                    "Mutual TLS (mTLS) for all service communication",
                    "Rich observability (metrics, logs, traces)",
                    "Policy enforcement",
                    "Multi-cluster support"
                ],
                "best_for": [
                    "Large microservices deployments",
                    "Complex traffic routing requirements",
                    "Strong security/compliance needs",
                    "Teams with dedicated platform engineers"
                ],
                "considerations": [
                    "Significant resource overhead (sidecars)",
                    "Complex configuration and debugging",
                    "Steep learning curve"
                ],
                "implementation_steps": [
                    "Plan namespace injection strategy",
                    "Install Istio control plane (istiod)",
                    "Configure sidecar injection",
                    "Deploy Kiali for visualization",
                    "Configure traffic policies gradually",
                    "Enable mTLS in permissive mode first",
                    "Migrate to strict mTLS",
                    "Set up monitoring dashboards"
                ],
                "aws_services": ["EKS", "CloudWatch", "X-Ray integration"],
                "estimated_effort": "4-8 weeks",
                "roi_timeline": "3-6 months"
            },
            "aws_app_mesh": {
                "name": "AWS App Mesh",
                "vendor": "AWS",
                "maturity": "Production Ready",
                "complexity": "Medium",
                "cost_impact": "Free (pay for resources)",
                "description": "AWS-native service mesh with deep AWS integration",
                "key_features": [
                    "Native AWS integration",
                    "Works with ECS, EKS, EC2",
                    "X-Ray integration for tracing",
                    "CloudWatch metrics",
                    "AWS-managed control plane"
                ],
                "best_for": [
                    "AWS-centric environments",
                    "Mixed ECS/EKS workloads",
                    "Teams wanting managed service"
                ],
                "considerations": [
                    "AWS lock-in",
                    "Fewer features than Istio",
                    "Limited community resources"
                ],
                "implementation_steps": [
                    "Create App Mesh resources (mesh, virtual nodes)",
                    "Deploy App Mesh controller",
                    "Configure Envoy sidecar injection",
                    "Define virtual services and routes",
                    "Enable X-Ray tracing",
                    "Configure CloudWatch integration"
                ],
                "aws_services": ["App Mesh", "X-Ray", "CloudWatch", "Cloud Map"],
                "estimated_effort": "2-4 weeks",
                "roi_timeline": "1-3 months"
            },
            "linkerd": {
                "name": "Linkerd",
                "vendor": "Buoyant",
                "maturity": "Production Ready",
                "complexity": "Low",
                "cost_impact": "Minimal overhead",
                "description": "Lightweight, security-focused service mesh",
                "key_features": [
                    "Ultra-lightweight (Rust-based proxy)",
                    "Simple installation and operation",
                    "Automatic mTLS",
                    "Built-in dashboard",
                    "CNCF graduated project"
                ],
                "best_for": [
                    "Teams prioritizing simplicity",
                    "Security-focused deployments",
                    "Resource-constrained environments"
                ],
                "considerations": [
                    "Fewer advanced features",
                    "Smaller ecosystem",
                    "Limited traffic management options"
                ],
                "implementation_steps": [
                    "Install Linkerd CLI",
                    "Run pre-installation checks",
                    "Install control plane",
                    "Inject sidecars into workloads",
                    "Enable mTLS",
                    "Deploy Linkerd dashboard"
                ],
                "aws_services": ["EKS"],
                "estimated_effort": "1-2 weeks",
                "roi_timeline": "Immediate"
            }
        },
        "comparison_criteria": [
            {"criterion": "Complexity", "istio": "High", "aws_app_mesh": "Medium", "linkerd": "Low"},
            {"criterion": "Resource Overhead", "istio": "High", "aws_app_mesh": "Medium", "linkerd": "Low"},
            {"criterion": "Feature Richness", "istio": "Highest", "aws_app_mesh": "Medium", "linkerd": "Focused"},
            {"criterion": "AWS Integration", "istio": "Manual", "aws_app_mesh": "Native", "linkerd": "Manual"},
            {"criterion": "Learning Curve", "istio": "Steep", "aws_app_mesh": "Moderate", "linkerd": "Gentle"},
            {"criterion": "Multi-cluster", "istio": "Advanced", "aws_app_mesh": "Supported", "linkerd": "Supported"}
        ]
    },
    "gitops": {
        "name": "GitOps & Continuous Delivery",
        "icon": "🔄",
        "description": "Declarative, Git-centric continuous delivery for Kubernetes",
        "technologies": {
            "argocd": {
                "name": "ArgoCD",
                "vendor": "Intuit/CNCF",
                "maturity": "Production Ready",
                "complexity": "Medium",
                "cost_impact": "Free",
                "description": "Declarative GitOps CD tool with powerful UI",
                "key_features": [
                    "Intuitive web UI",
                    "Application-centric view",
                    "SSO integration",
                    "Multi-cluster support",
                    "Sync windows and waves",
                    "ApplicationSets for multi-tenancy"
                ],
                "best_for": [
                    "Teams wanting visual CD management",
                    "Multi-cluster deployments",
                    "Organizations with many applications"
                ],
                "implementation_steps": [
                    "Install ArgoCD in dedicated namespace",
                    "Configure SSO/OIDC integration",
                    "Set up Git repository connections",
                    "Create Application manifests",
                    "Configure sync policies (auto/manual)",
                    "Set up notifications",
                    "Implement RBAC policies",
                    "Create ApplicationSets for patterns"
                ],
                "aws_services": ["EKS", "Secrets Manager", "IAM (IRSA)"],
                "estimated_effort": "2-3 weeks",
                "roi_timeline": "Immediate"
            },
            "flux": {
                "name": "Flux CD",
                "vendor": "Weaveworks/CNCF",
                "maturity": "Production Ready",
                "complexity": "Medium",
                "cost_impact": "Free",
                "description": "Kubernetes-native GitOps toolkit",
                "key_features": [
                    "Native Kubernetes resources",
                    "Helm and Kustomize support",
                    "Image automation",
                    "Multi-tenancy support",
                    "Notification controller"
                ],
                "best_for": [
                    "Teams preferring CLI-first approach",
                    "Heavy Helm users",
                    "Automated image updates"
                ],
                "implementation_steps": [
                    "Bootstrap Flux with flux bootstrap",
                    "Configure Git source repositories",
                    "Create Kustomization resources",
                    "Set up HelmReleases",
                    "Configure image automation",
                    "Set up alerting"
                ],
                "aws_services": ["EKS", "ECR", "Secrets Manager"],
                "estimated_effort": "2-3 weeks",
                "roi_timeline": "Immediate"
            }
        },
        "comparison_criteria": [
            {"criterion": "UI Experience", "argocd": "Rich Web UI", "flux": "CLI-focused"},
            {"criterion": "Learning Curve", "argocd": "Moderate", "flux": "Moderate"},
            {"criterion": "Multi-cluster", "argocd": "App of Apps pattern", "flux": "Native"},
            {"criterion": "Image Automation", "argocd": "Via Image Updater", "flux": "Built-in"},
            {"criterion": "Helm Support", "argocd": "Good", "flux": "Excellent"}
        ]
    },
    "observability": {
        "name": "Observability Stack",
        "icon": "📊",
        "description": "Comprehensive monitoring, logging, and tracing for Kubernetes",
        "technologies": {
            "prometheus_grafana": {
                "name": "Prometheus + Grafana",
                "vendor": "CNCF",
                "maturity": "Production Ready",
                "complexity": "Medium",
                "cost_impact": "Infrastructure costs only",
                "description": "Industry-standard open-source monitoring stack",
                "key_features": [
                    "Powerful PromQL query language",
                    "Rich ecosystem of exporters",
                    "Grafana for visualization",
                    "AlertManager for alerting",
                    "Wide community support"
                ],
                "best_for": [
                    "Teams wanting full control",
                    "Cost-conscious organizations",
                    "Custom metrics requirements"
                ],
                "implementation_steps": [
                    "Deploy kube-prometheus-stack via Helm",
                    "Configure persistent storage",
                    "Set up ServiceMonitors for applications",
                    "Create Grafana dashboards",
                    "Configure AlertManager rules",
                    "Set up Thanos for long-term storage (optional)"
                ],
                "aws_services": ["EBS", "S3 (for Thanos)"],
                "estimated_effort": "2-4 weeks",
                "roi_timeline": "Immediate"
            },
            "aws_cloudwatch": {
                "name": "CloudWatch Container Insights",
                "vendor": "AWS",
                "maturity": "Production Ready",
                "complexity": "Low",
                "cost_impact": "Pay per metric/log",
                "description": "AWS-native container monitoring",
                "key_features": [
                    "Zero configuration",
                    "AWS-native integration",
                    "Automatic dashboards",
                    "Container map visualization",
                    "Performance log insights"
                ],
                "best_for": [
                    "AWS-centric teams",
                    "Quick setup requirements",
                    "Integrated billing/monitoring"
                ],
                "implementation_steps": [
                    "Enable Container Insights add-on",
                    "Deploy CloudWatch agent",
                    "Configure log groups",
                    "Set up alarms",
                    "Create custom dashboards"
                ],
                "aws_services": ["CloudWatch", "CloudWatch Logs", "X-Ray"],
                "estimated_effort": "1 week",
                "roi_timeline": "Immediate"
            },
            "datadog": {
                "name": "Datadog",
                "vendor": "Datadog",
                "maturity": "Production Ready",
                "complexity": "Low",
                "cost_impact": "$15-23/host/month",
                "description": "Enterprise APM and monitoring platform",
                "key_features": [
                    "Unified platform (metrics, logs, traces, APM)",
                    "AI-powered anomaly detection",
                    "Extensive integrations",
                    "Real-time dashboards",
                    "SLO tracking"
                ],
                "best_for": [
                    "Enterprise requirements",
                    "Teams wanting managed solution",
                    "Complex microservices"
                ],
                "implementation_steps": [
                    "Deploy Datadog Operator",
                    "Configure API and app keys",
                    "Enable APM tracing",
                    "Set up log collection",
                    "Create monitors and dashboards"
                ],
                "aws_services": ["EKS", "AWS integrations"],
                "estimated_effort": "1-2 weeks",
                "roi_timeline": "Immediate"
            }
        },
        "comparison_criteria": [
            {"criterion": "Cost", "prometheus_grafana": "Infrastructure only", "aws_cloudwatch": "Per metric/log", "datadog": "$15-23/host/mo"},
            {"criterion": "Setup Complexity", "prometheus_grafana": "Medium", "aws_cloudwatch": "Low", "datadog": "Low"},
            {"criterion": "Customization", "prometheus_grafana": "High", "aws_cloudwatch": "Medium", "datadog": "High"},
            {"criterion": "AI/ML Features", "prometheus_grafana": "Limited", "aws_cloudwatch": "Anomaly Detection", "datadog": "Advanced"},
            {"criterion": "Vendor Lock-in", "prometheus_grafana": "None", "aws_cloudwatch": "AWS", "datadog": "Datadog"}
        ]
    },
    "security": {
        "name": "Security & Policy",
        "icon": "🔒",
        "description": "Kubernetes security, policy enforcement, and compliance",
        "technologies": {
            "opa_gatekeeper": {
                "name": "OPA Gatekeeper",
                "vendor": "CNCF",
                "maturity": "Production Ready",
                "complexity": "Medium",
                "cost_impact": "Free",
                "description": "Policy engine for Kubernetes admission control",
                "key_features": [
                    "Rego policy language",
                    "Admission webhook enforcement",
                    "Audit existing resources",
                    "Constraint templates library",
                    "Mutation support"
                ],
                "best_for": [
                    "Policy-as-code requirements",
                    "Multi-tenant clusters",
                    "Compliance enforcement"
                ]
            },
            "kyverno": {
                "name": "Kyverno",
                "vendor": "Nirmata/CNCF",
                "maturity": "Production Ready",
                "complexity": "Low",
                "cost_impact": "Free",
                "description": "Kubernetes-native policy engine using YAML",
                "key_features": [
                    "YAML-based policies (no Rego)",
                    "Validate, mutate, generate resources",
                    "Easy to learn and use",
                    "Policy reports"
                ],
                "best_for": [
                    "Teams not wanting to learn Rego",
                    "Quick policy implementation",
                    "Resource generation needs"
                ]
            },
            "falco": {
                "name": "Falco",
                "vendor": "Sysdig/CNCF",
                "maturity": "Production Ready",
                "complexity": "Medium",
                "cost_impact": "Free",
                "description": "Runtime security and threat detection",
                "key_features": [
                    "Runtime threat detection",
                    "Syscall monitoring",
                    "Container behavior analysis",
                    "Integration with alerting systems"
                ],
                "best_for": [
                    "Runtime security monitoring",
                    "Threat detection",
                    "Compliance auditing"
                ]
            }
        }
    }
}

# ============================================================================
# CI/CD MATURITY MODEL
# ============================================================================

CICD_MATURITY_LEVELS = {
    "level_1": {
        "name": "Initial",
        "score_range": (0, 20),
        "characteristics": [
            "Manual deployments",
            "No version control for infrastructure",
            "Ad-hoc testing",
            "No deployment automation"
        ],
        "next_steps": [
            "Implement version control for all code",
            "Create basic CI pipeline with automated builds",
            "Introduce unit testing",
            "Document deployment procedures"
        ]
    },
    "level_2": {
        "name": "Managed",
        "score_range": (21, 40),
        "characteristics": [
            "Basic CI/CD pipeline exists",
            "Some automated testing",
            "Manual approval gates",
            "Environment-specific configurations"
        ],
        "next_steps": [
            "Increase test coverage",
            "Implement infrastructure as code",
            "Add integration testing",
            "Create staging environments"
        ]
    },
    "level_3": {
        "name": "Defined",
        "score_range": (41, 60),
        "characteristics": [
            "Standardized CI/CD processes",
            "Automated integration testing",
            "Infrastructure as Code",
            "Basic monitoring in place"
        ],
        "next_steps": [
            "Implement GitOps practices",
            "Add security scanning to pipeline",
            "Implement progressive delivery",
            "Enhance observability"
        ]
    },
    "level_4": {
        "name": "Quantitatively Managed",
        "score_range": (61, 80),
        "characteristics": [
            "Metrics-driven improvements",
            "Automated security scanning",
            "Progressive delivery (canary/blue-green)",
            "Comprehensive observability"
        ],
        "next_steps": [
            "Implement chaos engineering",
            "Add AI/ML for anomaly detection",
            "Full GitOps adoption",
            "Self-service platform"
        ]
    },
    "level_5": {
        "name": "Optimizing",
        "score_range": (81, 100),
        "characteristics": [
            "Continuous improvement culture",
            "Self-service developer platform",
            "Automated rollback and remediation",
            "Full observability and AIOps"
        ],
        "next_steps": [
            "Explore emerging technologies",
            "Share knowledge across organization",
            "Contribute to open source",
            "Mentor other teams"
        ]
    }
}

# ============================================================================
# AI-POWERED ANALYSIS
# ============================================================================

def get_ai_recommendation(client, context: Dict) -> Optional[str]:
    """Get AI-powered recommendation based on context"""
    if not client:
        return None
    
    prompt = f"""You are an expert Kubernetes and AWS architect. Based on the following context, provide specific, actionable recommendations.

CONTEXT:
- Current technologies: {context.get('current_tech', 'Not specified')}
- Target technology: {context.get('target_tech', 'Not specified')}
- Team experience: {context.get('experience', 'Not specified')}
- Primary goals: {context.get('goals', 'Not specified')}
- Constraints: {context.get('constraints', 'None specified')}
- Organization context: {context.get('org_context', 'None provided')}

Provide a comprehensive recommendation including:
1. **Recommendation Summary** (2-3 sentences)
2. **Why This Approach** (3-4 bullet points)
3. **Implementation Roadmap** (phased approach with timelines)
4. **Potential Challenges** (and how to mitigate)
5. **Success Metrics** (how to measure success)
6. **AWS Services to Leverage** (specific services that help)
7. **Cost Considerations** (estimated costs and savings)

Be specific and practical. Include actual commands, configurations, or architecture patterns where helpful."""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    except Exception as e:
        return f"Error getting AI recommendation: {e}"

# ============================================================================
# RENDER FUNCTIONS
# ============================================================================

def render_eks_modernization_tab():
    """Render comprehensive EKS modernization tab"""
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #0d47a1 0%, #1565c0 100%); padding: 2rem; border-radius: 12px; margin-bottom: 1.5rem;">
        <h2 style="color: #BBDEFB; margin: 0;">🚀 EKS & Container Modernization</h2>
        <p style="color: #90CAF9; margin: 0.5rem 0 0 0;">AI-Powered Kubernetes Modernization with Technology Comparisons</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sub-tabs for different areas
    sub_tabs = st.tabs([
        "🔧 Technology Comparisons",
        "📈 CI/CD Maturity",
        "🎯 AI Recommendations",
        "📋 Implementation Guides"
    ])
    
    with sub_tabs[0]:
        render_technology_comparisons()
    
    with sub_tabs[1]:
        render_cicd_maturity_assessment()
    
    with sub_tabs[2]:
        render_ai_recommendations()
    
    with sub_tabs[3]:
        render_implementation_guides()

def render_technology_comparisons():
    """Render technology comparison section"""
    st.markdown("### 🔧 Technology Comparison Matrix")
    st.markdown("Compare technologies and get AI-powered recommendations for your specific needs")
    
    # Technology category selection
    category = st.selectbox(
        "Select Technology Category",
        list(EKS_TECHNOLOGY_CATALOG.keys()),
        format_func=lambda x: f"{EKS_TECHNOLOGY_CATALOG[x]['icon']} {EKS_TECHNOLOGY_CATALOG[x]['name']}"
    )
    
    cat_data = EKS_TECHNOLOGY_CATALOG[category]
    
    st.markdown(f"### {cat_data['icon']} {cat_data['name']}")
    st.markdown(cat_data['description'])
    
    # Comparison table
    if 'comparison_criteria' in cat_data:
        st.markdown("#### 📊 Comparison Matrix")
        
        # Build comparison table
        techs = list(cat_data['technologies'].keys())
        
        comparison_data = []
        for criteria in cat_data['comparison_criteria']:
            row = {"Criterion": criteria['criterion']}
            for tech in techs:
                row[cat_data['technologies'][tech]['name']] = criteria.get(tech, 'N/A')
            comparison_data.append(row)
        
        st.table(comparison_data)
    
    # Detailed technology cards
    st.markdown("#### 📋 Technology Details")
    
    cols = st.columns(len(cat_data['technologies']))
    
    for idx, (tech_key, tech) in enumerate(cat_data['technologies'].items()):
        with cols[idx]:
            st.markdown(f"**{tech['name']}**")
            st.caption(f"by {tech['vendor']}")
            
            # Badges
            st.markdown(f"🏷️ {tech['maturity']} | ⚙️ {tech['complexity']} complexity")
            
            if tech.get('cost_impact'):
                st.markdown(f"💰 {tech['cost_impact']}")
            
            with st.expander("View Details"):
                st.markdown(f"**Description:** {tech['description']}")
                
                st.markdown("**Key Features:**")
                for feature in tech.get('key_features', [])[:5]:
                    st.markdown(f"- {feature}")
                
                st.markdown("**Best For:**")
                for use_case in tech.get('best_for', []):
                    st.markdown(f"- {use_case}")
                
                if tech.get('considerations'):
                    st.markdown("**Considerations:**")
                    for consideration in tech['considerations']:
                        st.markdown(f"- ⚠️ {consideration}")

def render_cicd_maturity_assessment():
    """Render CI/CD maturity assessment"""
    st.markdown("### 📈 CI/CD Maturity Assessment")
    st.markdown("Assess your current CI/CD maturity and get a personalized improvement roadmap")
    
    col1, col2 = st.columns(2)
    
    assessment_scores = {}
    
    with col1:
        st.markdown("**Development Practices**")
        assessment_scores['version_control'] = st.select_slider(
            "Version Control",
            options=["None", "Basic Git", "Branching Strategy", "GitFlow/Trunk-based"],
            value="Basic Git"
        )
        assessment_scores['code_review'] = st.select_slider(
            "Code Review",
            options=["None", "Informal", "PR Reviews", "Automated + Manual"],
            value="PR Reviews"
        )
        assessment_scores['testing'] = st.select_slider(
            "Testing Strategy",
            options=["Manual", "Unit Tests", "Unit + Integration", "Full Pyramid + E2E"],
            value="Unit Tests"
        )
        assessment_scores['iac'] = st.select_slider(
            "Infrastructure as Code",
            options=["None", "Scripts", "Terraform/CloudFormation", "GitOps"],
            value="Scripts"
        )
    
    with col2:
        st.markdown("**Delivery Practices**")
        assessment_scores['ci'] = st.select_slider(
            "Continuous Integration",
            options=["Manual Builds", "Automated Builds", "Build + Test", "Full CI Pipeline"],
            value="Automated Builds"
        )
        assessment_scores['cd'] = st.select_slider(
            "Continuous Delivery",
            options=["Manual Deploy", "Scripted Deploy", "CD Pipeline", "GitOps"],
            value="Scripted Deploy"
        )
        assessment_scores['monitoring'] = st.select_slider(
            "Monitoring & Observability",
            options=["None", "Basic Logs", "Metrics + Logs", "Full Observability"],
            value="Basic Logs"
        )
        assessment_scores['security'] = st.select_slider(
            "Security Integration",
            options=["None", "Manual Scans", "CI Security Scans", "Shift-Left + Runtime"],
            value="Manual Scans"
        )
    
    # Calculate maturity score
    score_map = {
        "None": 0, "Manual": 0, "Manual Builds": 0, "Manual Deploy": 0,
        "Basic Git": 1, "Informal": 1, "Scripts": 1, "Basic Logs": 1, "Manual Scans": 1, "Scripted Deploy": 1,
        "Branching Strategy": 2, "PR Reviews": 2, "Unit Tests": 2, "Terraform/CloudFormation": 2, 
        "Automated Builds": 2, "CD Pipeline": 2, "Metrics + Logs": 2, "CI Security Scans": 2,
        "GitFlow/Trunk-based": 3, "Automated + Manual": 3, "Unit + Integration": 3, 
        "Build + Test": 3, "Full Observability": 3,
        "Full Pyramid + E2E": 4, "GitOps": 4, "Full CI Pipeline": 4, "Shift-Left + Runtime": 4
    }
    
    total_score = sum(score_map.get(v, 0) for v in assessment_scores.values())
    max_score = 32
    maturity_pct = int((total_score / max_score) * 100)
    
    # Determine level
    current_level = None
    for level_key, level in CICD_MATURITY_LEVELS.items():
        if level['score_range'][0] <= maturity_pct <= level['score_range'][1]:
            current_level = level
            break
    
    st.markdown("---")
    
    # Results
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        color = "#388E3C" if maturity_pct >= 70 else "#FBC02D" if maturity_pct >= 40 else "#D32F2F"
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem; background: white; border-radius: 10px;">
            <div style="font-size: 2.5rem; font-weight: bold; color: {color};">{maturity_pct}%</div>
            <div style="color: #666;">Maturity Score</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.metric("Current Level", current_level['name'] if current_level else "Unknown")
    
    with col3:
        next_level_pct = min(100, ((maturity_pct // 20) + 1) * 20)
        st.metric("Next Milestone", f"{next_level_pct}%")
    
    with col4:
        gap = next_level_pct - maturity_pct
        st.metric("Gap to Next Level", f"{gap} points")
    
    # Level details and recommendations
    if current_level:
        st.markdown(f"### 📊 Level: {current_level['name']}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Current Characteristics:**")
            for char in current_level['characteristics']:
                st.markdown(f"- {char}")
        
        with col2:
            st.markdown("**Recommended Next Steps:**")
            for step in current_level['next_steps']:
                st.markdown(f"- ✅ {step}")

def render_ai_recommendations():
    """Render AI-powered recommendations section"""
    st.markdown("### 🎯 AI-Powered Recommendations")
    st.markdown("Get personalized recommendations based on your specific context and goals")
    
    # Check for API key
    try:
        import anthropic
        api_key = st.session_state.get('anthropic_api_key')
        if not api_key:
            try:
                api_key = st.secrets.get('ANTHROPIC_API_KEY')
            except:
                pass
        
        if not api_key:
            st.warning("Configure Anthropic API key in sidebar for AI recommendations")
            client = None
        else:
            client = anthropic.Anthropic(api_key=api_key)
    except ImportError:
        st.error("Anthropic library not installed")
        client = None
    
    # Context inputs
    col1, col2 = st.columns(2)
    
    with col1:
        current_tech = st.multiselect(
            "Current Technologies",
            ["Cluster Autoscaler", "No Service Mesh", "Jenkins", "Manual Deployments", 
             "CloudWatch", "No Policy Engine", "Helm", "kubectl apply"],
            default=["Cluster Autoscaler", "No Service Mesh", "CloudWatch"]
        )
        
        target_tech = st.selectbox(
            "Technology to Implement",
            ["Karpenter", "Istio Service Mesh", "ArgoCD GitOps", "AWS App Mesh",
             "Prometheus/Grafana", "OPA Gatekeeper", "Linkerd", "Flux CD"]
        )
        
        experience = st.select_slider(
            "Team Kubernetes Experience",
            options=["Beginner", "Intermediate", "Advanced", "Expert"],
            value="Intermediate"
        )
    
    with col2:
        goals = st.multiselect(
            "Primary Goals",
            ["Cost Reduction", "Improved Reliability", "Faster Deployments",
             "Better Security", "Enhanced Observability", "Developer Productivity"],
            default=["Cost Reduction", "Faster Deployments"]
        )
        
        constraints = st.multiselect(
            "Constraints",
            ["Limited Budget", "Small Team", "Compliance Requirements",
             "Legacy Systems", "Multi-cloud Strategy", "Tight Timeline"],
            default=[]
        )
        
        timeline = st.selectbox(
            "Implementation Timeline",
            ["1-2 weeks", "1 month", "1-3 months", "3-6 months", "6+ months"],
            index=2
        )
    
    org_context = st.session_state.get('organization_context', '')
    
    if st.button("🤖 Get AI Recommendation", type="primary", use_container_width=True):
        if not client:
            st.error("AI client not available. Please configure API key.")
            return
        
        context = {
            'current_tech': ', '.join(current_tech),
            'target_tech': target_tech,
            'experience': experience,
            'goals': ', '.join(goals),
            'constraints': ', '.join(constraints) if constraints else 'None',
            'timeline': timeline,
            'org_context': org_context
        }
        
        with st.spinner(f"Generating personalized recommendation for {target_tech}..."):
            recommendation = get_ai_recommendation(client, context)
        
        if recommendation:
            st.markdown("### 🎯 AI Recommendation")
            st.markdown(recommendation)
            
            # Save to session for later reference
            if 'ai_recommendations' not in st.session_state:
                st.session_state.ai_recommendations = []
            st.session_state.ai_recommendations.append({
                'timestamp': datetime.now().isoformat(),
                'target': target_tech,
                'recommendation': recommendation
            })

def render_implementation_guides():
    """Render detailed implementation guides"""
    st.markdown("### 📋 Implementation Guides")
    st.markdown("Step-by-step guides for implementing key technologies")
    
    guide = st.selectbox(
        "Select Implementation Guide",
        ["Karpenter Migration", "ArgoCD GitOps Setup", "Service Mesh Implementation", 
         "Observability Stack", "Security Hardening"]
    )
    
    if guide == "Karpenter Migration":
        render_karpenter_guide()
    elif guide == "ArgoCD GitOps Setup":
        render_argocd_guide()
    elif guide == "Service Mesh Implementation":
        render_service_mesh_guide()
    elif guide == "Observability Stack":
        render_observability_guide()
    else:
        render_security_guide()

def render_karpenter_guide():
    """Detailed Karpenter implementation guide"""
    st.markdown("## 📈 Karpenter Migration Guide")
    
    st.markdown("""
    ### Overview
    Karpenter is a high-performance Kubernetes cluster autoscaler that automatically provisions 
    new nodes in response to unschedulable pods. Unlike Cluster Autoscaler, Karpenter:
    - Provisions nodes in seconds (not minutes)
    - Automatically selects optimal instance types
    - Handles Spot interruptions gracefully
    - Consolidates underutilized nodes
    """)
    
    with st.expander("📋 Prerequisites", expanded=True):
        st.markdown("""
        - EKS cluster version 1.21+
        - IAM OIDC provider configured
        - kubectl and Helm installed
        - AWS CLI configured
        """)
        
        st.code("""
# Verify EKS cluster
aws eks describe-cluster --name <cluster-name> --query 'cluster.version'

# Check OIDC provider
aws eks describe-cluster --name <cluster-name> \\
    --query 'cluster.identity.oidc.issuer'
        """, language="bash")
    
    with st.expander("🔧 Step 1: Create IAM Resources"):
        st.markdown("Create the IAM role and policies for Karpenter")
        
        st.code("""
# Create Karpenter controller policy
cat <<EOF > karpenter-controller-policy.json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "Karpenter",
            "Effect": "Allow",
            "Action": [
                "ec2:CreateFleet",
                "ec2:CreateLaunchTemplate",
                "ec2:CreateTags",
                "ec2:DeleteLaunchTemplate",
                "ec2:DescribeAvailabilityZones",
                "ec2:DescribeImages",
                "ec2:DescribeInstances",
                "ec2:DescribeInstanceTypeOfferings",
                "ec2:DescribeInstanceTypes",
                "ec2:DescribeLaunchTemplates",
                "ec2:DescribeSecurityGroups",
                "ec2:DescribeSpotPriceHistory",
                "ec2:DescribeSubnets",
                "ec2:RunInstances",
                "ec2:TerminateInstances",
                "iam:PassRole",
                "pricing:GetProducts",
                "ssm:GetParameter"
            ],
            "Resource": "*"
        }
    ]
}
EOF

# Create IAM role with IRSA
eksctl create iamserviceaccount \\
    --cluster=<cluster-name> \\
    --namespace=karpenter \\
    --name=karpenter \\
    --attach-policy-arn=arn:aws:iam::<account>:policy/KarpenterController \\
    --approve
        """, language="bash")
    
    with st.expander("🚀 Step 2: Install Karpenter"):
        st.code("""
# Add Karpenter Helm repo
helm repo add karpenter https://charts.karpenter.sh
helm repo update

# Install Karpenter
helm install karpenter karpenter/karpenter \\
    --namespace karpenter \\
    --create-namespace \\
    --set serviceAccount.annotations."eks\\.amazonaws\\.com/role-arn"=arn:aws:iam::<account>:role/KarpenterController \\
    --set controller.clusterName=<cluster-name> \\
    --set controller.clusterEndpoint=$(aws eks describe-cluster --name <cluster-name> --query 'cluster.endpoint' --output text) \\
    --wait
        """, language="bash")
    
    with st.expander("⚙️ Step 3: Configure NodePool"):
        st.markdown("Create a NodePool to define how Karpenter provisions nodes")
        
        st.code("""
apiVersion: karpenter.sh/v1beta1
kind: NodePool
metadata:
  name: default
spec:
  template:
    spec:
      requirements:
        - key: kubernetes.io/arch
          operator: In
          values: ["amd64", "arm64"]
        - key: karpenter.sh/capacity-type
          operator: In
          values: ["spot", "on-demand"]
        - key: karpenter.k8s.aws/instance-category
          operator: In
          values: ["c", "m", "r"]
        - key: karpenter.k8s.aws/instance-generation
          operator: Gt
          values: ["5"]
      nodeClassRef:
        name: default
  limits:
    cpu: 1000
  disruption:
    consolidationPolicy: WhenUnderutilized
    consolidateAfter: 30s
---
apiVersion: karpenter.k8s.aws/v1beta1
kind: EC2NodeClass
metadata:
  name: default
spec:
  amiFamily: AL2
  subnetSelectorTerms:
    - tags:
        karpenter.sh/discovery: <cluster-name>
  securityGroupSelectorTerms:
    - tags:
        karpenter.sh/discovery: <cluster-name>
  role: KarpenterNodeRole
        """, language="yaml")
    
    with st.expander("📊 Step 4: Verify and Monitor"):
        st.code("""
# Check Karpenter logs
kubectl logs -n karpenter -l app.kubernetes.io/name=karpenter -f

# Watch node provisioning
kubectl get nodes -w

# Check Karpenter metrics
kubectl get nodepools
kubectl get nodeclaims
        """, language="bash")
    
    with st.expander("🔄 Step 5: Migration from Cluster Autoscaler"):
        st.markdown("""
        **Gradual Migration Strategy:**
        1. Install Karpenter alongside Cluster Autoscaler
        2. Create NodePool for new workloads
        3. Cordon existing node groups
        4. Let pods migrate to Karpenter-provisioned nodes
        5. Delete old node groups
        6. Remove Cluster Autoscaler
        """)

def render_argocd_guide():
    """ArgoCD implementation guide"""
    st.markdown("## 🔄 ArgoCD GitOps Setup Guide")
    
    st.markdown("""
    ### Overview
    ArgoCD is a declarative GitOps continuous delivery tool for Kubernetes.
    """)
    
    with st.expander("🚀 Quick Start", expanded=True):
        st.code("""
# Install ArgoCD
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Get initial admin password
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d

# Access UI (port-forward)
kubectl port-forward svc/argocd-server -n argocd 8080:443
        """, language="bash")
    
    with st.expander("📋 Create Application"):
        st.code("""
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-app
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/your-org/your-repo
    targetRevision: HEAD
    path: kubernetes/
  destination:
    server: https://kubernetes.default.svc
    namespace: my-app
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
        """, language="yaml")

def render_service_mesh_guide():
    """Service mesh implementation guide"""
    st.markdown("## 🕸️ Service Mesh Implementation Guide")
    st.info("Select your preferred service mesh for detailed implementation guide")

def render_observability_guide():
    """Observability stack guide"""
    st.markdown("## 📊 Observability Stack Guide")
    st.info("Comprehensive monitoring, logging, and tracing setup")

def render_security_guide():
    """Security hardening guide"""
    st.markdown("## 🔒 Security Hardening Guide")
    st.info("EKS security best practices and implementation")

# Export
__all__ = ['render_eks_modernization_tab']
