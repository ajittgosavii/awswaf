"""
EKS & Cloud Native Modernization Module - Enterprise Edition
AI-Powered Kubernetes Transformation Journey

This module provides comprehensive guidance for container and Kubernetes adoption,
including AI-powered recommendations, building blocks, and best practices.

Features:
- AI-powered modernization assessment
- Container readiness evaluation
- EKS architecture design
- Building blocks library (Karpenter, Service Mesh, GitOps, etc.)
- Implementation roadmap generation
- Cost optimization
- Security hardening
- Production best practices
"""

import streamlit as st
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

# ============================================================================
# DATA MODELS
# ============================================================================

class MaturityLevel(Enum):
    """EKS/Cloud Native maturity levels"""
    BEGINNING = ("Beginning Journey", "🌱", "Just starting with containers")
    INTERMEDIATE = ("Intermediate", "🌿", "Running containers in production")
    ADVANCED = ("Advanced", "🌳", "Cloud-native with GitOps, service mesh")
    EXPERT = ("Expert", "🏆", "Platform engineering, multi-cluster")

class BuildingBlockCategory(Enum):
    """Categories of EKS building blocks"""
    COMPUTE = "Compute & Scaling"
    NETWORKING = "Networking & Service Mesh"
    SECURITY = "Security & Compliance"
    OBSERVABILITY = "Observability & Monitoring"
    GITOPS = "GitOps & Automation"
    STORAGE = "Storage & Databases"
    COST = "Cost Optimization"

@dataclass
class BuildingBlock:
    """EKS/K8s building block"""
    name: str
    category: BuildingBlockCategory
    description: str
    maturity_required: MaturityLevel
    aws_services: List[str]
    oss_tools: List[str]
    implementation_time: str
    complexity: str  # Low, Medium, High
    prerequisites: List[str]
    benefits: List[str]
    best_practices: List[str]
    cost_impact: str
    reference_architecture: str

# ============================================================================
# BUILDING BLOCKS LIBRARY
# ============================================================================

BUILDING_BLOCKS = {
    # COMPUTE & SCALING
    "karpenter": BuildingBlock(
        name="Karpenter",
        category=BuildingBlockCategory.COMPUTE,
        description="Just-in-time, right-sized compute provisioning. Replaces Cluster Autoscaler with intelligent, cost-optimized node provisioning.",
        maturity_required=MaturityLevel.INTERMEDIATE,
        aws_services=["EKS", "EC2", "Spot Instances"],
        oss_tools=["Karpenter"],
        implementation_time="1-2 weeks",
        complexity="Medium",
        prerequisites=["EKS cluster", "IAM roles configured", "Node requirements defined"],
        benefits=[
            "60-80% cost reduction vs fixed node groups",
            "Sub-minute scaling (vs 3-5 min with Cluster Autoscaler)",
            "Automatic rightsizing based on actual pod requirements",
            "Native Spot instance support with fallback",
            "Consolidation of underutilized nodes"
        ],
        best_practices=[
            "Start with non-production clusters for testing",
            "Define NodePools for different workload types (compute, memory, GPU)",
            "Set appropriate consolidation policies (5-10 min empty node TTL)",
            "Use Spot instances with on-demand fallback (80% spot, 20% on-demand)",
            "Monitor consolidation events and disruptions",
            "Set node limits per NodePool to prevent runaway costs",
            "Use topology spread constraints for HA"
        ],
        cost_impact="High savings (60-80% reduction)",
        reference_architecture="https://karpenter.sh/docs/getting-started/"
    ),
    
    "fargate": BuildingBlock(
        name="AWS Fargate for EKS",
        category=BuildingBlockCategory.COMPUTE,
        description="Serverless compute for EKS - no node management required. Ideal for batch jobs, CI/CD, and workloads with variable traffic.",
        maturity_required=MaturityLevel.BEGINNING,
        aws_services=["EKS", "Fargate"],
        oss_tools=[],
        implementation_time="1 week",
        complexity="Low",
        prerequisites=["EKS cluster", "Fargate profiles defined"],
        benefits=[
            "Zero node management overhead",
            "Automatic scaling",
            "Pay only for pod resources",
            "Improved security isolation",
            "Ideal for batch/CI workloads"
        ],
        best_practices=[
            "Use for CI/CD runners (save 70% vs always-on nodes)",
            "Batch processing and cron jobs",
            "Development environments",
            "Not recommended for stateful workloads or GPU",
            "Configure appropriate resource requests/limits",
            "Use for workloads that can tolerate 30-60s cold start"
        ],
        cost_impact="Medium (20-30% premium vs EC2, but savings on ops)",
        reference_architecture="https://docs.aws.amazon.com/eks/latest/userguide/fargate.html"
    ),
    
    # NETWORKING & SERVICE MESH
    "istio": BuildingBlock(
        name="Istio Service Mesh",
        category=BuildingBlockCategory.NETWORKING,
        description="Complete service mesh with traffic management, security, and observability. Industry-standard, production-proven.",
        maturity_required=MaturityLevel.ADVANCED,
        aws_services=["EKS", "NLB"],
        oss_tools=["Istio", "Envoy"],
        implementation_time="3-4 weeks",
        complexity="High",
        prerequisites=["EKS cluster", "CNI configured", "Observability stack"],
        benefits=[
            "Automatic mTLS between services",
            "Advanced traffic routing (canary, A/B testing)",
            "Distributed tracing",
            "Circuit breaking and retries",
            "Zero-trust security",
            "Multi-cluster service discovery"
        ],
        best_practices=[
            "Start with ambient mesh mode (no sidecars) for easier adoption",
            "Enable strict mTLS after testing",
            "Use virtual services for traffic management",
            "Implement gradual rollout (canary 10% → 50% → 100%)",
            "Monitor control plane resource usage",
            "Use Kiali for visualization",
            "Limit sidecar resource overhead (100m CPU, 128Mi memory per sidecar)"
        ],
        cost_impact="Medium overhead (10-15% CPU/memory for sidecars)",
        reference_architecture="https://istio.io/latest/docs/setup/install/"
    ),
    
    "app_mesh": BuildingBlock(
        name="AWS App Mesh",
        category=BuildingBlockCategory.NETWORKING,
        description="AWS-managed service mesh alternative to Istio. Simpler to operate, integrated with AWS services.",
        maturity_required=MaturityLevel.INTERMEDIATE,
        aws_services=["EKS", "App Mesh", "Cloud Map", "X-Ray"],
        oss_tools=["Envoy"],
        implementation_time="2-3 weeks",
        complexity="Medium",
        prerequisites=["EKS cluster", "AWS Cloud Map"],
        benefits=[
            "AWS-managed control plane (zero ops)",
            "Native AWS integration (CloudWatch, X-Ray)",
            "Lower operational overhead vs Istio",
            "Automatic mTLS",
            "Works with EC2, ECS, and EKS"
        ],
        best_practices=[
            "Use for AWS-native environments",
            "Leverage Cloud Map for service discovery",
            "Enable X-Ray tracing from day 1",
            "Use virtual gateways for ingress",
            "Implement gradual deployment strategies",
            "Monitor via CloudWatch Container Insights"
        ],
        cost_impact="Low (managed service, pay for resources only)",
        reference_architecture="https://docs.aws.amazon.com/app-mesh/"
    ),
    
    "cilium": BuildingBlock(
        name="Cilium CNI + Network Policies",
        category=BuildingBlockCategory.NETWORKING,
        description="eBPF-based networking with advanced network policies, observability, and performance. Next-gen CNI.",
        maturity_required=MaturityLevel.ADVANCED,
        aws_services=["EKS", "VPC"],
        oss_tools=["Cilium", "Hubble"],
        implementation_time="2 weeks",
        complexity="High",
        prerequisites=["EKS 1.28+", "Linux kernel 5.10+"],
        benefits=[
            "10-15% better network performance vs AWS VPC CNI",
            "Advanced network policies (L7, DNS-based)",
            "Built-in network observability (Hubble)",
            "Transparent encryption",
            "Multi-cluster connectivity",
            "Service mesh capabilities without sidecars"
        ],
        best_practices=[
            "Use Cilium for greenfield clusters",
            "Enable Hubble for network visibility",
            "Implement L7 network policies",
            "Use BGP for multi-cluster",
            "Monitor via Hubble UI and Grafana",
            "Test thoroughly before production migration"
        ],
        cost_impact="Neutral (better performance, slightly more complex)",
        reference_architecture="https://docs.cilium.io/en/stable/gettingstarted/k8s-install-default/"
    ),
    
    # GITOPS & AUTOMATION
    "argocd": BuildingBlock(
        name="ArgoCD GitOps",
        category=BuildingBlockCategory.GITOPS,
        description="Declarative GitOps continuous delivery. Industry standard for Kubernetes deployments.",
        maturity_required=MaturityLevel.INTERMEDIATE,
        aws_services=["EKS", "CodeCommit/GitHub"],
        oss_tools=["ArgoCD", "Kustomize", "Helm"],
        implementation_time="2 weeks",
        complexity="Medium",
        prerequisites=["EKS cluster", "Git repository", "RBAC configured"],
        benefits=[
            "Git as single source of truth",
            "Automated sync and drift detection",
            "Easy rollbacks",
            "Multi-cluster management",
            "Self-healing applications",
            "Audit trail for all changes"
        ],
        best_practices=[
            "Use ApplicationSets for multi-environment",
            "Implement progressive delivery with Argo Rollouts",
            "Enable auto-sync with prune for non-prod",
            "Manual sync for production (with approval)",
            "Use Kustomize for environment-specific configs",
            "Implement RBAC per team/namespace",
            "Monitor sync status and health",
            "Use webhook notifications (Slack/Teams)"
        ],
        cost_impact="Low (small operational overhead)",
        reference_architecture="https://argo-cd.readthedocs.io/en/stable/"
    ),
    
    "flux": BuildingBlock(
        name="Flux GitOps",
        category=BuildingBlockCategory.GITOPS,
        description="CNCF graduated GitOps operator. Lightweight, GitOps-native approach.",
        maturity_required=MaturityLevel.INTERMEDIATE,
        aws_services=["EKS", "CodeCommit/GitHub"],
        oss_tools=["Flux", "Kustomize", "Helm"],
        implementation_time="1-2 weeks",
        complexity="Medium",
        prerequisites=["EKS cluster", "Git repository"],
        benefits=[
            "Lower resource footprint vs ArgoCD",
            "Native Kubernetes approach",
            "Image automation",
            "Multi-tenancy support",
            "Notification system"
        ],
        best_practices=[
            "Use Flux for resource-constrained environments",
            "Implement image update automation",
            "Use Kustomize for overlays",
            "Monitor via Flux CLI and metrics",
            "Implement alerts for sync failures"
        ],
        cost_impact="Low",
        reference_architecture="https://fluxcd.io/docs/"
    ),
    
    # OBSERVABILITY
    "prometheus_stack": BuildingBlock(
        name="Prometheus + Grafana Stack",
        category=BuildingBlockCategory.OBSERVABILITY,
        description="Complete observability stack with metrics, alerts, and dashboards. Industry standard.",
        maturity_required=MaturityLevel.INTERMEDIATE,
        aws_services=["EKS", "AMP", "AMG"],
        oss_tools=["Prometheus", "Grafana", "AlertManager", "Thanos"],
        implementation_time="2-3 weeks",
        complexity="Medium",
        prerequisites=["EKS cluster", "Persistent storage"],
        benefits=[
            "Comprehensive metrics collection",
            "Flexible alerting",
            "Rich visualization",
            "Long-term storage with Thanos",
            "Standard for Kubernetes monitoring"
        ],
        best_practices=[
            "Use kube-prometheus-stack Helm chart",
            "Configure appropriate retention (15-30 days local)",
            "Implement Thanos for long-term storage (90+ days)",
            "Set up critical alerts (OOMKilled, CrashLoopBackOff, NodeNotReady)",
            "Create dashboards per team",
            "Use recording rules for expensive queries",
            "Monitor Prometheus itself (disk, memory)",
            "Consider AWS AMP/AMG for managed option"
        ],
        cost_impact="Medium (storage and compute for monitoring)",
        reference_architecture="https://prometheus.io/docs/introduction/overview/"
    ),
    
    "datadog": BuildingBlock(
        name="Datadog Observability",
        category=BuildingBlockCategory.OBSERVABILITY,
        description="Unified observability platform (metrics, logs, traces, RUM). Best for comprehensive monitoring.",
        maturity_required=MaturityLevel.INTERMEDIATE,
        aws_services=["EKS"],
        oss_tools=["Datadog Agent"],
        implementation_time="1 week",
        complexity="Low",
        prerequisites=["EKS cluster", "Datadog account"],
        benefits=[
            "Unified platform (no tool sprawl)",
            "Out-of-box dashboards",
            "APM with distributed tracing",
            "Log management",
            "Real User Monitoring",
            "Excellent support"
        ],
        best_practices=[
            "Use Datadog Operator for agent deployment",
            "Enable APM for critical services",
            "Set up log pipelines",
            "Create SLO monitors",
            "Use tagging strategy (env, team, service)",
            "Set budget alerts"
        ],
        cost_impact="High (SaaS pricing, but saves ops time)",
        reference_architecture="https://docs.datadoghq.com/containers/kubernetes/"
    ),
    
    # SECURITY
    "pod_security": BuildingBlock(
        name="Pod Security Standards",
        category=BuildingBlockCategory.SECURITY,
        description="Enforce pod security best practices. Essential for production clusters.",
        maturity_required=MaturityLevel.BEGINNING,
        aws_services=["EKS"],
        oss_tools=["Pod Security Admission", "OPA Gatekeeper"],
        implementation_time="1 week",
        complexity="Low",
        prerequisites=["EKS 1.25+"],
        benefits=[
            "Prevent insecure pod configurations",
            "No privileged containers",
            "Read-only root filesystem",
            "Non-root users",
            "Drop unnecessary capabilities"
        ],
        best_practices=[
            "Start with 'audit' mode, move to 'enforce'",
            "Use 'restricted' profile for apps, 'baseline' for system",
            "Never use 'privileged' mode unless absolutely required",
            "Enforce read-only root filesystem",
            "Drop ALL capabilities, add only what's needed",
            "Set runAsNonRoot: true",
            "Use security contexts on every pod"
        ],
        cost_impact="Zero (built-in)",
        reference_architecture="https://kubernetes.io/docs/concepts/security/pod-security-standards/"
    ),
    
    "secrets_management": BuildingBlock(
        name="AWS Secrets Manager + ESO",
        category=BuildingBlockCategory.SECURITY,
        description="External secrets management integrated with Kubernetes. Keep secrets out of Git.",
        maturity_required=MaturityLevel.INTERMEDIATE,
        aws_services=["Secrets Manager", "Parameter Store", "KMS"],
        oss_tools=["External Secrets Operator"],
        implementation_time="1 week",
        complexity="Low",
        prerequisites=["EKS cluster", "IAM roles for service accounts"],
        benefits=[
            "Secrets never in Git",
            "Centralized secret management",
            "Automatic rotation",
            "Audit trail",
            "Multi-environment support"
        ],
        best_practices=[
            "Use IRSA for authentication",
            "Enable automatic rotation",
            "One secret per application",
            "Use SecretStore per namespace/team",
            "Monitor sync failures",
            "Implement least privilege IAM"
        ],
        cost_impact="Low (AWS Secrets Manager pricing)",
        reference_architecture="https://external-secrets.io/"
    ),
    
    # COST OPTIMIZATION
    "spot_instances": BuildingBlock(
        name="Spot Instances Strategy",
        category=BuildingBlockCategory.COST,
        description="Use Spot instances for 60-80% cost savings. Essential for cost-optimized EKS.",
        maturity_required=MaturityLevel.INTERMEDIATE,
        aws_services=["EC2 Spot", "EKS"],
        oss_tools=["Karpenter", "cluster-autoscaler"],
        implementation_time="1 week",
        complexity="Medium",
        prerequisites=["Workload analysis", "Interruption handling"],
        benefits=[
            "60-80% cost reduction",
            "Same performance as on-demand",
            "Diversification across instance families",
            "2-minute interruption notice"
        ],
        best_practices=[
            "Use Karpenter for intelligent Spot management",
            "Diversify across 8-10 instance types",
            "Handle interruptions gracefully (PodDisruptionBudgets)",
            "Use on-demand for critical workloads (databases, stateful)",
            "Target 80% Spot, 20% on-demand",
            "Monitor Spot interruption rates",
            "Use Spot Instance Advisor for selection"
        ],
        cost_impact="Huge savings (60-80% reduction)",
        reference_architecture="https://aws.amazon.com/ec2/spot/"
    ),
    
    "kubecost": BuildingBlock(
        name="Kubecost",
        category=BuildingBlockCategory.COST,
        description="Kubernetes cost monitoring and optimization. Essential for FinOps.",
        maturity_required=MaturityLevel.INTERMEDIATE,
        aws_services=["EKS", "Cost Explorer"],
        oss_tools=["Kubecost", "OpenCost"],
        implementation_time="1 week",
        complexity="Low",
        prerequisites=["EKS cluster", "Prometheus"],
        benefits=[
            "Per-namespace/pod/label cost visibility",
            "Right-sizing recommendations",
            "Showback/chargeback",
            "Spot savings tracking",
            "Budget alerts"
        ],
        best_practices=[
            "Install on all clusters",
            "Set up cost allocation tags",
            "Create per-team dashboards",
            "Implement budget alerts",
            "Review right-sizing recommendations weekly",
            "Track savings from optimizations"
        ],
        cost_impact="Enables savings (tool cost < savings)",
        reference_architecture="https://www.kubecost.com/"
    )
}

# ============================================================================
# AI-POWERED ASSESSMENT
# ============================================================================

def get_ai_modernization_recommendations(assessment_data: Dict) -> Dict:
    """
    Get AI-powered recommendations for EKS modernization based on current state.
    Uses Claude API for intelligent, context-aware recommendations.
    """
    
    if not ANTHROPIC_AVAILABLE:
        return {
            "error": "Anthropic API not available",
            "recommendations": []
        }
    
    try:
        api_key = st.secrets.get("ANTHROPIC_API_KEY")
        if not api_key:
            return {
                "error": "ANTHROPIC_API_KEY not configured",
                "recommendations": []
            }
        
        client = anthropic.Anthropic(api_key=api_key)
        
        # Build comprehensive prompt
        prompt = f"""You are an expert AWS Solutions Architect and Kubernetes consultant specializing in EKS and cloud-native modernization.

Analyze this organization's current state and provide detailed, actionable recommendations for their EKS modernization journey.

CURRENT STATE:
- Organization: {assessment_data.get('organization', 'Unknown')}
- Current Platform: {assessment_data.get('current_platform', 'Unknown')}
- Workload Types: {', '.join(assessment_data.get('workload_types', []))}
- Team Size: {assessment_data.get('team_size', 'Unknown')}
- Cloud Experience: {assessment_data.get('cloud_experience', 'Unknown')}
- Kubernetes Experience: {assessment_data.get('k8s_experience', 'Unknown')}
- Current Challenges: {', '.join(assessment_data.get('challenges', []))}
- Goals: {', '.join(assessment_data.get('goals', []))}
- Timeline: {assessment_data.get('timeline', 'Unknown')}
- Budget Constraints: {assessment_data.get('budget', 'Unknown')}

Provide comprehensive recommendations in the following JSON format:

{{
  "maturity_level": "Beginning/Intermediate/Advanced/Expert",
  "recommended_approach": "Brief description of recommended approach",
  "phase_1_immediate": [
    {{
      "building_block": "name",
      "priority": "Critical/High/Medium",
      "rationale": "Why this first",
      "timeline": "X weeks",
      "quick_wins": ["specific benefit 1", "specific benefit 2"]
    }}
  ],
  "phase_2_foundation": [
    {{
      "building_block": "name",
      "priority": "Critical/High/Medium",
      "rationale": "Why after phase 1",
      "timeline": "X weeks"
    }}
  ],
  "phase_3_optimization": [
    {{
      "building_block": "name",
      "priority": "High/Medium",
      "rationale": "Why for optimization",
      "timeline": "X weeks"
    }}
  ],
  "cost_optimization_potential": "Estimated % savings and dollar amount",
  "risk_areas": ["risk 1", "risk 2"],
  "success_metrics": ["metric 1", "metric 2"],
  "estimated_roi": "ROI analysis",
  "team_upskilling_needed": ["skill 1", "skill 2"]
}}

Focus on:
1. Practical, achievable recommendations
2. Risk mitigation strategies
3. Cost optimization opportunities
4. Team capability building
5. Quick wins vs long-term investments

Be specific with building block names (Karpenter, Istio, ArgoCD, etc.)"""

        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=3000,
            temperature=0.7,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        # Parse response
        response_text = message.content[0].text
        
        # Extract JSON from response
        import re
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if json_match:
            recommendations = json.loads(json_match.group())
            recommendations['full_analysis'] = response_text
            return recommendations
        else:
            return {
                "error": "Could not parse AI response",
                "raw_response": response_text
            }
            
    except Exception as e:
        return {
            "error": str(e),
            "recommendations": []
        }

def generate_implementation_roadmap(recommendations: Dict, assessment_data: Dict) -> str:
    """Generate detailed implementation roadmap based on AI recommendations"""
    
    if not ANTHROPIC_AVAILABLE or not recommendations.get('phase_1_immediate'):
        return "AI recommendations not available"
    
    try:
        api_key = st.secrets.get("ANTHROPIC_API_KEY")
        client = anthropic.Anthropic(api_key=api_key)
        
        prompt = f"""Based on these modernization recommendations, create a detailed, week-by-week implementation roadmap.

RECOMMENDATIONS:
{json.dumps(recommendations, indent=2)}

CONSTRAINTS:
- Team Size: {assessment_data.get('team_size', 'Unknown')}
- Timeline: {assessment_data.get('timeline', 'Unknown')}
- Budget: {assessment_data.get('budget', 'Unknown')}

Create a roadmap with:
1. Week-by-week breakdown
2. Parallel vs sequential activities
3. Resource requirements per week
4. Success criteria per phase
5. Risk mitigation steps
6. Testing and validation gates

Format as a clear, actionable markdown document."""

        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            temperature=0.7,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return message.content[0].text
        
    except Exception as e:
        return f"Error generating roadmap: {str(e)}"

# ============================================================================
# UI RENDERING FUNCTIONS
# ============================================================================

def render_eks_modernization_tab():
    """
    Main rendering function for EKS & Modernization tab
    Comprehensive cloud-native transformation hub
    """
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 2rem; border-radius: 12px; margin-bottom: 2rem;">
        <h2 style="color: white; margin: 0;">🚀 EKS & Cloud Native Modernization</h2>
        <p style="color: white; opacity: 0.9; margin: 0.5rem 0 0 0;">
            AI-powered Kubernetes transformation journey with proven building blocks and best practices
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'eks_assessments' not in st.session_state:
        st.session_state.eks_assessments = {}
    
    # Main sub-tabs
    tabs = st.tabs([
        "🎯 Start Assessment",
        "🧱 Building Blocks",
        "📚 Best Practices",
        "💰 Cost Calculator",
        "🏗️ Reference Architectures"
    ])
    
    with tabs[0]:
        render_modernization_assessment()
    
    with tabs[1]:
        render_building_blocks_library()
    
    with tabs[2]:
        render_best_practices()
    
    with tabs[3]:
        render_cost_calculator()
    
    with tabs[4]:
        render_reference_architectures()

def render_modernization_assessment():
    """
    AI-powered modernization assessment
    Analyzes current state and provides personalized recommendations
    """
    st.markdown("### 🎯 EKS Modernization Assessment")
    
    st.info("**Get AI-powered recommendations** for your Kubernetes transformation journey. This assessment takes 5-10 minutes.")
    
    # Assessment form
    with st.form("eks_assessment_form"):
        st.markdown("#### 📋 Current State")
        
        col1, col2 = st.columns(2)
        
        with col1:
            organization = st.text_input("Organization Name", placeholder="e.g., Acme Corp")
            
            current_platform = st.selectbox(
                "Current Platform",
                [
                    "On-premises VMs",
                    "EC2 instances",
                    "ECS/Fargate",
                    "Other Kubernetes (AKS, GKE, OpenShift)",
                    "Bare metal",
                    "Hybrid (mix of above)"
                ]
            )
            
            k8s_experience = st.select_slider(
                "Kubernetes Experience",
                options=["None", "Learning", "Production (< 1 year)", "Mature (1-3 years)", "Expert (3+ years)"],
                value="Learning"
            )
            
            team_size = st.selectbox(
                "Platform/DevOps Team Size",
                ["1-2 people", "3-5 people", "6-10 people", "11-20 people", "20+ people"]
            )
        
        with col2:
            cloud_experience = st.select_slider(
                "AWS Experience",
                options=["None", "Learning", "Intermediate", "Advanced", "Expert"],
                value="Intermediate"
            )
            
            timeline = st.selectbox(
                "Target Timeline",
                ["1-3 months", "3-6 months", "6-12 months", "12+ months"]
            )
            
            budget = st.selectbox(
                "Budget Approach",
                ["Cost optimization priority", "Balanced", "Feature-first, cost-conscious", "Unlimited budget"]
            )
        
        st.markdown("#### 🎯 Workloads & Goals")
        
        workload_types = st.multiselect(
            "Workload Types (select all that apply)",
            [
                "Web applications (APIs, microservices)",
                "Batch processing",
                "Data processing (Spark, ML training)",
                "Databases (PostgreSQL, MySQL, MongoDB)",
                "Message queues (Kafka, RabbitMQ)",
                "CI/CD pipelines",
                "Real-time streaming",
                "Machine Learning inference"
            ]
        )
        
        challenges = st.multiselect(
            "Current Challenges",
            [
                "High infrastructure costs",
                "Slow deployment cycles",
                "Scaling issues",
                "Poor observability",
                "Security/compliance concerns",
                "Team lacks K8s expertise",
                "Complex multi-environment management",
                "Service-to-service communication issues",
                "Vendor lock-in concerns"
            ]
        )
        
        goals = st.multiselect(
            "Primary Goals (top 3-5)",
            [
                "Reduce infrastructure costs by 50%+",
                "Improve deployment speed (< 10 min)",
                "Auto-scaling and resilience",
                "Modern observability (metrics, logs, traces)",
                "Zero-downtime deployments",
                "Multi-region/multi-cluster",
                "GitOps and automation",
                "Security hardening",
                "Service mesh capabilities",
                "Team capability building"
            ]
        )
        
        additional_context = st.text_area(
            "Additional Context (optional)",
            placeholder="Any specific requirements, constraints, or context that would help with recommendations...",
            height=100
        )
        
        submitted = st.form_submit_button("🤖 Get AI Recommendations", use_container_width=True, type="primary")
        
        if submitted:
            if not organization or not workload_types or not challenges or not goals:
                st.error("Please fill in all required fields")
            else:
                # Gather assessment data
                assessment_data = {
                    'organization': organization,
                    'current_platform': current_platform,
                    'k8s_experience': k8s_experience,
                    'team_size': team_size,
                    'cloud_experience': cloud_experience,
                    'timeline': timeline,
                    'budget': budget,
                    'workload_types': workload_types,
                    'challenges': challenges,
                    'goals': goals,
                    'additional_context': additional_context,
                    'created_at': datetime.now().isoformat()
                }
                
                # Get AI recommendations
                with st.spinner("🤖 AI is analyzing your requirements and generating personalized recommendations... This may take 20-30 seconds."):
                    recommendations = get_ai_modernization_recommendations(assessment_data)
                
                if 'error' in recommendations:
                    st.error(f"Error: {recommendations['error']}")
                else:
                    # Save assessment
                    assessment_id = datetime.now().strftime("%Y%m%d_%H%M%S")
                    st.session_state.eks_assessments[assessment_id] = {
                        'data': assessment_data,
                        'recommendations': recommendations
                    }
                    
                    st.success("✅ AI recommendations generated successfully!")
                    st.rerun()
    
    # Display existing assessments and recommendations
    if st.session_state.eks_assessments:
        st.markdown("---")
        st.markdown("### 📊 Your Assessments")
        
        for assessment_id, assessment in sorted(st.session_state.eks_assessments.items(), reverse=True):
            data = assessment['data']
            recommendations = assessment['recommendations']
            
            with st.expander(f"🎯 {data['organization']} - {assessment_id}", expanded=True):
                # Overview
                col_o1, col_o2, col_o3, col_o4 = st.columns(4)
                with col_o1:
                    st.metric("Maturity Level", recommendations.get('maturity_level', 'Unknown'))
                with col_o2:
                    st.metric("Timeline", data['timeline'])
                with col_o3:
                    st.metric("Team Size", data['team_size'])
                with col_o4:
                    cost_potential = recommendations.get('cost_optimization_potential', 'TBD')
                    st.metric("Cost Savings Potential", cost_potential)
                
                # Recommended Approach
                st.markdown("#### 🎯 Recommended Approach")
                st.info(recommendations.get('recommended_approach', 'No recommendation available'))
                
                # Phase-based recommendations
                rec_tabs = st.tabs(["⚡ Phase 1: Immediate", "🏗️ Phase 2: Foundation", "🚀 Phase 3: Optimization", "📊 Full Analysis"])
                
                with rec_tabs[0]:
                    st.markdown("**Quick Wins & Critical Setup (Weeks 1-4)**")
                    phase1 = recommendations.get('phase_1_immediate', [])
                    if phase1:
                        for item in phase1:
                            priority_color = {"Critical": "🔴", "High": "🟠", "Medium": "🟡"}.get(item.get('priority', 'Medium'), "🟡")
                            st.markdown(f"{priority_color} **{item.get('building_block', 'Unknown')}** ({item.get('priority', 'Medium')} Priority)")
                            st.markdown(f"*Timeline: {item.get('timeline', 'Unknown')}*")
                            st.markdown(f"**Why:** {item.get('rationale', 'No rationale provided')}")
                            if item.get('quick_wins'):
                                st.markdown("**Quick Wins:**")
                                for win in item['quick_wins']:
                                    st.markdown(f"- ✅ {win}")
                            st.markdown("---")
                    else:
                        st.info("No Phase 1 recommendations available")
                
                with rec_tabs[1]:
                    st.markdown("**Foundation & Scaling (Weeks 5-12)**")
                    phase2 = recommendations.get('phase_2_foundation', [])
                    if phase2:
                        for item in phase2:
                            priority_color = {"Critical": "🔴", "High": "🟠", "Medium": "🟡"}.get(item.get('priority', 'Medium'), "🟡")
                            st.markdown(f"{priority_color} **{item.get('building_block', 'Unknown')}** ({item.get('priority', 'Medium')} Priority)")
                            st.markdown(f"*Timeline: {item.get('timeline', 'Unknown')}*")
                            st.markdown(f"**Why:** {item.get('rationale', 'No rationale provided')}")
                            st.markdown("---")
                    else:
                        st.info("No Phase 2 recommendations available")
                
                with rec_tabs[2]:
                    st.markdown("**Advanced Features & Optimization (Weeks 13+)**")
                    phase3 = recommendations.get('phase_3_optimization', [])
                    if phase3:
                        for item in phase3:
                            priority_color = {"High": "🟠", "Medium": "🟡"}.get(item.get('priority', 'Medium'), "🟡")
                            st.markdown(f"{priority_color} **{item.get('building_block', 'Unknown')}** ({item.get('priority', 'Medium')} Priority)")
                            st.markdown(f"*Timeline: {item.get('timeline', 'Unknown')}*")
                            st.markdown(f"**Why:** {item.get('rationale', 'No rationale provided')}")
                            st.markdown("---")
                    else:
                        st.info("No Phase 3 recommendations available")
                
                with rec_tabs[3]:
                    st.markdown("**Complete AI Analysis**")
                    st.markdown(recommendations.get('full_analysis', 'No full analysis available'))
                
                # Additional sections
                col_add1, col_add2 = st.columns(2)
                
                with col_add1:
                    st.markdown("#### ⚠️ Risk Areas")
                    risks = recommendations.get('risk_areas', [])
                    if risks:
                        for risk in risks:
                            st.warning(f"⚠️ {risk}")
                    
                    st.markdown("#### 📈 Success Metrics")
                    metrics = recommendations.get('success_metrics', [])
                    if metrics:
                        for metric in metrics:
                            st.info(f"📊 {metric}")
                
                with col_add2:
                    st.markdown("#### 💰 Estimated ROI")
                    roi = recommendations.get('estimated_roi', 'Not calculated')
                    st.success(roi)
                    
                    st.markdown("#### 📚 Team Upskilling Needed")
                    skills = recommendations.get('team_upskilling_needed', [])
                    if skills:
                        for skill in skills:
                            st.caption(f"🎓 {skill}")
                
                # Generate Implementation Roadmap
                if st.button(f"📋 Generate Detailed Roadmap", key=f"roadmap_{assessment_id}", use_container_width=True):
                    with st.spinner("Generating detailed week-by-week roadmap..."):
                        roadmap = generate_implementation_roadmap(recommendations, data)
                        st.markdown("### 📋 Implementation Roadmap")
                        st.markdown(roadmap)

def render_building_blocks_library():
    """
    Comprehensive library of EKS building blocks with details
    """
    st.markdown("### 🧱 EKS Building Blocks Library")
    
    st.info("**Proven building blocks** for your EKS journey. Each has been battle-tested in production environments.")
    
    # Filter by category
    categories = list(BuildingBlockCategory)
    selected_category = st.selectbox(
        "Filter by Category",
        ["All"] + [cat.value for cat in categories]
    )
    
    # Filter by maturity level
    selected_maturity = st.selectbox(
        "Filter by Required Maturity",
        ["All"] + [level.value[0] for level in MaturityLevel]
    )
    
    # Display building blocks
    filtered_blocks = BUILDING_BLOCKS
    if selected_category != "All":
        filtered_blocks = {k: v for k, v in BUILDING_BLOCKS.items() 
                          if v.category.value == selected_category}
    
    if selected_maturity != "All":
        filtered_blocks = {k: v for k, v in filtered_blocks.items() 
                          if v.maturity_required.value[0] == selected_maturity}
    
    st.markdown(f"**Showing {len(filtered_blocks)} building blocks**")
    
    for block_id, block in filtered_blocks.items():
        with st.expander(f"{block.category.value} | {block.name} - {block.complexity} complexity"):
            col_b1, col_b2 = st.columns([2, 1])
            
            with col_b1:
                st.markdown(f"**{block.name}**")
                st.markdown(block.description)
                
                st.markdown("**📊 Quick Facts:**")
                st.markdown(f"- **Implementation Time:** {block.implementation_time}")
                st.markdown(f"- **Complexity:** {block.complexity}")
                st.markdown(f"- **Required Maturity:** {block.maturity_required.value[0]} {block.maturity_required.value[1]}")
                st.markdown(f"- **Cost Impact:** {block.cost_impact}")
            
            with col_b2:
                st.markdown("**🔧 Technology Stack:**")
                if block.aws_services:
                    st.caption("AWS Services:")
                    for service in block.aws_services:
                        st.caption(f"• {service}")
                
                if block.oss_tools:
                    st.caption("Open Source:")
                    for tool in block.oss_tools:
                        st.caption(f"• {tool}")
            
            st.markdown("---")
            
            col_det1, col_det2 = st.columns(2)
            
            with col_det1:
                st.markdown("**✅ Key Benefits:**")
                for benefit in block.benefits:
                    st.markdown(f"- {benefit}")
                
                st.markdown("**📋 Prerequisites:**")
                for prereq in block.prerequisites:
                    st.markdown(f"- {prereq}")
            
            with col_det2:
                st.markdown("**🎯 Best Practices:**")
                for practice in block.best_practices:
                    st.markdown(f"- {practice}")
            
            st.markdown("---")
            st.markdown(f"**📚 Reference:** [{block.reference_architecture}]({block.reference_architecture})")

def render_best_practices():
    """
    Comprehensive best practices for EKS
    """
    st.markdown("### 📚 EKS Best Practices Guide")
    
    practice_tabs = st.tabs([
        "🔐 Security",
        "💰 Cost Optimization",
        "⚡ Performance",
        "🛡️ Reliability",
        "📊 Observability"
    ])
    
    with practice_tabs[0]:
        st.markdown("#### 🔐 Security Best Practices")
        
        st.markdown("##### 1. Pod Security")
        st.code("""
# Enforce pod security standards
apiVersion: v1
kind: Namespace
metadata:
  name: production
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted

# Example secure pod
apiVersion: v1
kind: Pod
metadata:
  name: secure-app
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 2000
    seccompProfile:
      type: RuntimeDefault
  containers:
  - name: app
    image: myapp:1.0
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop:
        - ALL
    resources:
      limits:
        cpu: "1"
        memory: "1Gi"
      requests:
        cpu: "100m"
        memory: "128Mi"
        """, language="yaml")
        
        st.markdown("##### 2. RBAC & IAM")
        st.markdown("""
        **Key Principles:**
        - ✅ Use IRSA (IAM Roles for Service Accounts) - never use node IAM roles
        - ✅ Create namespace-specific service accounts
        - ✅ Follow least privilege principle
        - ✅ One IAM role per application/service
        - ✅ Use IAM policy conditions for fine-grained control
        - ✅ Regularly audit RBAC with kubectl auth can-i
        """)
        
        st.markdown("##### 3. Network Security")
        st.markdown("""
        **Implementation:**
        - ✅ Default deny-all network policies
        - ✅ Allow only necessary traffic (whitelist approach)
        - ✅ Use Calico/Cilium for L7 policies
        - ✅ Enable VPC flow logs
        - ✅ Use AWS Security Groups for Pods (where supported)
        - ✅ Implement egress filtering
        """)
        
        st.markdown("##### 4. Secrets Management")
        st.code("""
# External Secrets Operator with AWS Secrets Manager
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: app-secrets
  namespace: production
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-secrets-manager
    kind: SecretStore
  target:
    name: app-secrets
    creationPolicy: Owner
  data:
  - secretKey: database-password
    remoteRef:
      key: prod/db/password
        """, language="yaml")
    
    with practice_tabs[1]:
        st.markdown("#### 💰 Cost Optimization Best Practices")
        
        st.markdown("##### 1. Right-Sizing")
        st.markdown("""
        **Key Actions:**
        - ✅ Install Kubecost/OpenCost immediately
        - ✅ Set resource requests = actual usage (not limits)
        - ✅ Use VPA (Vertical Pod Autoscaler) for recommendations
        - ✅ Review and adjust weekly
        - ✅ Target 70-80% resource utilization
        
        **Common Over-provisioning:**
        - Requesting 1 CPU when using 100m → 90% waste
        - Requesting 2Gi memory when using 200Mi → 90% waste
        """)
        
        st.markdown("##### 2. Spot Instances")
        st.code("""
# Karpenter NodePool for Spot instances
apiVersion: karpenter.sh/v1beta1
kind: NodePool
metadata:
  name: default
spec:
  disruption:
    consolidationPolicy: WhenUnderutilized
    expireAfter: 720h # 30 days
  template:
    spec:
      requirements:
        - key: "karpenter.sh/capacity-type"
          operator: In
          values: ["spot", "on-demand"]
        - key: "kubernetes.io/arch"
          operator: In
          values: ["amd64"]
        - key: "karpenter.k8s.aws/instance-category"
          operator: In
          values: ["c", "m", "r"]
        - key: "karpenter.k8s.aws/instance-generation"
          operator: Gt
          values: ["4"]
      nodeClassRef:
        name: default
  limits:
    cpu: "1000"
    memory: "1000Gi"
  weight: 10
        """, language="yaml")
        
        st.markdown("##### 3. Cluster Consolidation")
        st.markdown("""
        **Strategies:**
        - ✅ Use namespaces instead of separate clusters (save 60-80%)
        - ✅ Share non-prod clusters across teams
        - ✅ Use Karpenter consolidation (automatic bin-packing)
        - ✅ Schedule batch jobs during off-peak hours
        - ✅ Use Fargate for CI/CD runners (no idle cost)
        """)
        
        st.markdown("##### 4. Savings Plans & RIs")
        st.markdown("""
        **Recommendations:**
        - ✅ Start with 1-year Compute Savings Plans (no EC2 commitment)
        - ✅ Cover 50-70% of baseline usage (not peak)
        - ✅ Let Spot cover the rest
        - ✅ Review quarterly and adjust
        - ✅ Use AWS Cost Explorer recommendations
        """)
    
    with practice_tabs[2]:
        st.markdown("#### ⚡ Performance Best Practices")
        
        st.markdown("##### 1. Resource Management")
        st.code("""
# Properly configured resources
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: app
        image: myapp:1.0
        resources:
          requests:  # What you actually need
            cpu: "250m"
            memory: "256Mi"
          limits:  # Maximum allowed
            cpu: "500m"  # 2x requests
            memory: "512Mi"  # 2x requests
        
        # Probes for health
        livenessProbe:
          httpGet:
            path: /healthz
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
        """, language="yaml")
        
        st.markdown("##### 2. HPA (Horizontal Pod Autoscaler)")
        st.code("""
# HPA based on CPU and custom metrics
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: web-app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: web-app
  minReplicas: 3
  maxReplicas: 100
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300  # 5 min cooldown
      policies:
      - type: Percent
        value: 50  # Scale down max 50% at a time
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
      - type: Percent
        value: 100  # Scale up 2x quickly
        periodSeconds: 15
        """, language="yaml")
        
        st.markdown("##### 3. Performance Tuning")
        st.markdown("""
        **Key Optimizations:**
        - ✅ Use topology spread constraints for even distribution
        - ✅ Configure PDB (PodDisruptionBudgets) for HA
        - ✅ Use node affinity for workload placement
        - ✅ Enable cluster autoscaler or Karpenter
        - ✅ Use local NVMe storage for I/O intensive workloads
        - ✅ Tune kernel parameters for high-throughput apps
        - ✅ Use Cilium CNI for 10-15% better network performance
        """)
    
    with practice_tabs[3]:
        st.markdown("#### 🛡️ Reliability Best Practices")
        
        st.markdown("##### 1. High Availability")
        st.markdown("""
        **Architecture:**
        - ✅ Multi-AZ cluster (3 AZs minimum)
        - ✅ Minimum 3 replicas for critical services
        - ✅ PodDisruptionBudgets (maxUnavailable: 1)
        - ✅ Topology spread constraints
        - ✅ Use ALB/NLB with cross-zone load balancing
        - ✅ Separate node groups per AZ
        """)
        
        st.markdown("##### 2. Disaster Recovery")
        st.code("""
# Velero backup configuration
apiVersion: velero.io/v1
kind: Schedule
metadata:
  name: daily-backup
  namespace: velero
spec:
  schedule: "0 1 * * *"  # 1 AM daily
  template:
    includedNamespaces:
    - production
    - staging
    excludedResources:
    - events
    - events.events.k8s.io
    storageLocation: default
    volumeSnapshotLocations:
    - default
    ttl: 720h  # 30 days retention
        """, language="yaml")
        
        st.markdown("##### 3. Chaos Engineering")
        st.markdown("""
        **Progressive Testing:**
        - ✅ Week 1: Test pod failures (kill random pods)
        - ✅ Week 2: Test node failures (drain/taint nodes)
        - ✅ Week 3: Test AZ failures (disable entire AZ)
        - ✅ Week 4: Test network issues (inject latency/packet loss)
        - ✅ Tools: Chaos Mesh, Litmus, AWS FIS
        """)
    
    with practice_tabs[4]:
        st.markdown("#### 📊 Observability Best Practices")
        
        st.markdown("##### 1. The Golden Signals")
        st.markdown("""
        **Monitor These 4 Metrics:**
        1. **Latency** - Request duration (p50, p95, p99)
        2. **Traffic** - Requests per second
        3. **Errors** - Error rate (%)
        4. **Saturation** - Resource utilization (CPU, memory, disk)
        
        **Implementation:**
        - ✅ Instrument all services with Prometheus metrics
        - ✅ Use service mesh (Istio/App Mesh) for automatic instrumentation
        - ✅ Export to Prometheus/CloudWatch
        - ✅ Create Grafana dashboards
        - ✅ Set up alerts on SLOs
        """)
        
        st.markdown("##### 2. Distributed Tracing")
        st.code("""
# OpenTelemetry collector configuration
apiVersion: v1
kind: ConfigMap
metadata:
  name: otel-collector-config
data:
  config.yaml: |
    receivers:
      otlp:
        protocols:
          grpc:
            endpoint: 0.0.0.0:4317
          http:
            endpoint: 0.0.0.0:4318
    
    processors:
      batch:
        timeout: 10s
        send_batch_size: 1024
      
      memory_limiter:
        check_interval: 5s
        limit_mib: 512
    
    exporters:
      awsxray:
        region: us-west-2
      
      prometheus:
        endpoint: "0.0.0.0:8889"
    
    service:
      pipelines:
        traces:
          receivers: [otlp]
          processors: [memory_limiter, batch]
          exporters: [awsxray]
        
        metrics:
          receivers: [otlp]
          processors: [memory_limiter, batch]
          exporters: [prometheus]
        """, language="yaml")
        
        st.markdown("##### 3. Log Aggregation")
        st.markdown("""
        **Best Practices:**
        - ✅ Use FluentBit (lighter than Fluentd)
        - ✅ Parse logs at source (not at destination)
        - ✅ Add Kubernetes metadata automatically
        - ✅ Set appropriate retention (7-30 days)
        - ✅ Use log sampling for high-volume services (1-10%)
        - ✅ Export to CloudWatch Logs or external SIEM
        - ✅ Create log-based metrics for alerting
        """)

def render_cost_calculator():
    """Cost calculator for EKS clusters"""
    st.markdown("### 💰 EKS Cost Calculator")
    
    st.info("**Estimate your EKS costs** and see potential savings with optimization")
    
    col_c1, col_c2 = st.columns(2)
    
    with col_c1:
        st.markdown("#### Current State")
        
        num_nodes = st.number_input("Number of nodes", min_value=1, max_value=1000, value=20)
        node_type = st.selectbox("Node instance type", [
            "t3.medium", "t3.large", "t3.xlarge",
            "m5.large", "m5.xlarge", "m5.2xlarge",
            "c5.large", "c5.xlarge", "c5.2xlarge",
            "r5.large", "r5.xlarge", "r5.2xlarge"
        ])
        
        utilization = st.slider("Average CPU utilization (%)", 0, 100, 30)
        hours_per_month = st.slider("Hours per month", 1, 730, 730)
    
    with col_c2:
        st.markdown("#### Optimizations")
        
        use_spot = st.checkbox("Use Spot instances (60-80% savings)", value=False)
        spot_percentage = st.slider("Spot instance %", 0, 100, 70) if use_spot else 0
        
        use_karpenter = st.checkbox("Use Karpenter (right-sizing)", value=False)
        use_fargate = st.checkbox("Use Fargate for batch jobs", value=False)
        
        rightsizing_savings = st.slider("Right-sizing savings (%)", 0, 80, 40) if use_karpenter else 0
    
    # Calculate costs
    pricing = {
        "t3.medium": 0.0416, "t3.large": 0.0832, "t3.xlarge": 0.1664,
        "m5.large": 0.096, "m5.xlarge": 0.192, "m5.2xlarge": 0.384,
        "c5.large": 0.085, "c5.xlarge": 0.170, "c5.2xlarge": 0.340,
        "r5.large": 0.126, "r5.xlarge": 0.252, "r5.2xlarge": 0.504
    }
    
    base_hourly = pricing.get(node_type, 0.1)
    base_monthly = base_hourly * num_nodes * hours_per_month
    
    # Apply optimizations
    optimized_cost = base_monthly
    savings_breakdown = []
    
    if use_spot:
        spot_savings = (base_monthly * spot_percentage / 100) * 0.70  # 70% average savings
        optimized_cost -= spot_savings
        savings_breakdown.append(("Spot Instances", spot_savings))
    
    if use_karpenter:
        rightsize_savings = (base_monthly * rightsizing_savings / 100)
        optimized_cost -= rightsize_savings
        savings_breakdown.append(("Karpenter Right-sizing", rightsize_savings))
    
    if use_fargate:
        fargate_savings = base_monthly * 0.15  # 15% savings on batch workloads
        optimized_cost -= fargate_savings
        savings_breakdown.append(("Fargate for Batch", fargate_savings))
    
    # EKS control plane cost
    eks_control_plane = 0.10 * hours_per_month  # $0.10/hour
    total_current = base_monthly + eks_control_plane
    total_optimized = optimized_cost + eks_control_plane
    total_savings = total_current - total_optimized
    savings_percentage = (total_savings / total_current * 100) if total_current > 0 else 0
    
    # Display results
    st.markdown("---")
    st.markdown("### 📊 Cost Analysis")
    
    col_r1, col_r2, col_r3, col_r4 = st.columns(4)
    
    with col_r1:
        st.metric("Current Monthly Cost", f"${total_current:,.2f}")
    with col_r2:
        st.metric("Optimized Cost", f"${total_optimized:,.2f}")
    with col_r3:
        st.metric("Monthly Savings", f"${total_savings:,.2f}", delta=f"-{savings_percentage:.1f}%")
    with col_r4:
        st.metric("Annual Savings", f"${total_savings * 12:,.2f}")
    
    if savings_breakdown:
        st.markdown("#### 💰 Savings Breakdown")
        for optimization, savings in savings_breakdown:
            st.success(f"✅ **{optimization}**: ${savings:,.2f}/month (${savings * 12:,.2f}/year)")
    
    # Recommendations
    st.markdown("---")
    st.markdown("### 🎯 Recommendations")
    
    if utilization < 50:
        st.warning(f"⚠️ **Low utilization ({utilization}%)** - Consider right-sizing with Karpenter to save ~40-60%")
    
    if not use_spot:
        estimated_spot_savings = base_monthly * 0.70 * 0.70  # 70% spot, 70% savings
        st.info(f"💡 **Enable Spot instances** - Potential savings: ${estimated_spot_savings:,.2f}/month")
    
    if not use_karpenter and utilization < 60:
        st.info("💡 **Implement Karpenter** - Automatic right-sizing could save 40-60% on compute")

def render_reference_architectures():
    """Reference architectures and patterns"""
    st.markdown("### 🏗️ Reference Architectures")
    
    st.info("**Production-ready architectures** used by leading companies")
    
    arch_tabs = st.tabs([
        "🌐 Multi-Tenant SaaS",
        "🔄 Microservices Platform",
        "📊 Data Processing",
        "🤖 ML/AI Workloads",
        "🎮 Gaming Backend"
    ])
    
    with arch_tabs[0]:
        st.markdown("#### 🌐 Multi-Tenant SaaS Architecture")
        
        st.markdown("""
        **Use Case:** B2B SaaS with 100+ customers, strict isolation requirements
        
        **Architecture:**
        - Single EKS cluster per region
        - Namespace per customer (or namespace per tier)
        - Network policies for isolation
        - RBAC per tenant
        - Resource quotas per namespace
        """)
        
        st.code("""
# Tenant namespace with quotas
apiVersion: v1
kind: Namespace
metadata:
  name: tenant-acme
  labels:
    tenant: acme
    tier: enterprise
---
apiVersion: v1
kind: ResourceQuota
metadata:
  name: tenant-quota
  namespace: tenant-acme
spec:
  hard:
    requests.cpu: "50"
    requests.memory: "100Gi"
    pods: "100"
    services: "20"
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: tenant-isolation
  namespace: tenant-acme
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          tenant: acme
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          tenant: acme
        """, language="yaml")
        
        st.markdown("""
        **Building Blocks Used:**
        - ✅ Karpenter for auto-scaling
        - ✅ Istio for traffic management and mTLS
        - ✅ ArgoCD for multi-tenant GitOps
        - ✅ Prometheus + Grafana per tenant
        - ✅ External Secrets for tenant credentials
        
        **Estimated Costs:** $5,000-15,000/month for 100 tenants
        """)
    
    with arch_tabs[1]:
        st.markdown("#### 🔄 Microservices Platform")
        
        st.markdown("""
        **Use Case:** 50+ microservices, high throughput, service mesh required
        
        **Architecture:**
        - Multi-cluster (prod, staging, dev)
        - Istio service mesh
        - API Gateway (Kong/Ambassador)
        - Distributed tracing
        - Centralized logging
        """)
        
        st.markdown("""
        **Building Blocks Used:**
        - ✅ Istio for service mesh
        - ✅ ArgoCD for GitOps
        - ✅ Karpenter for compute
        - ✅ Prometheus + Grafana + Jaeger
        - ✅ FluentBit → CloudWatch Logs
        
        **Estimated Costs:** $8,000-20,000/month
        """)
    
    with arch_tabs[2]:
        st.markdown("#### 📊 Data Processing Architecture")
        
        st.markdown("""
        **Use Case:** Spark/Flink workloads, batch processing, variable compute needs
        
        **Architecture:**
        - EKS with Karpenter
        - 80% Spot instances
        - Fargate for orchestration
        - S3 for data lake
        - Athena for queries
        """)
        
        st.markdown("""
        **Building Blocks Used:**
        - ✅ Karpenter with Spot instances
        - ✅ Fargate for Airflow/schedulers
        - ✅ Spark Operator on Kubernetes
        - ✅ Kubecost for cost tracking
        - ✅ S3 CSI driver for data access
        
        **Estimated Costs:** $3,000-10,000/month (70% savings vs fixed capacity)
        """)
    
    with arch_tabs[3]:
        st.markdown("#### 🤖 ML/AI Workloads")
        
        st.markdown("""
        **Use Case:** Model training and inference, GPU workloads
        
        **Architecture:**
        - Separate node pools for CPU/GPU
        - Karpenter for GPU provisioning
        - Kubeflow for ML pipelines
        - Model serving with KServe
        - JupyterHub for data scientists
        """)
        
        st.markdown("""
        **Building Blocks Used:**
        - ✅ Karpenter with GPU instances (P3, P4, G5)
        - ✅ Kubeflow for ML workflows
        - ✅ KServe for model serving
        - ✅ Spot instances for training (60% savings)
        - ✅ Prometheus for GPU metrics
        
        **Estimated Costs:** $10,000-50,000/month depending on GPU usage
        """)
    
    with arch_tabs[4]:
        st.markdown("#### 🎮 Gaming Backend")
        
        st.markdown("""
        **Use Case:** Real-time multiplayer, low latency, auto-scaling
        
        **Architecture:**
        - Multi-region active-active
        - Agones for game server management
        - Redis for session state
        - Dedicated node pools per game
        - Global load balancing
        """)
        
        st.markdown("""
        **Building Blocks Used:**
        - ✅ Agones (Kubernetes for game servers)
        - ✅ Karpenter for rapid scaling
        - ✅ Spot instances for non-production matches
        - ✅ AWS Global Accelerator
        - ✅ ElastiCache for state
        
        **Estimated Costs:** $15,000-100,000/month depending on concurrent users
        """)
