"""
FinOps Module
Comprehensive Cloud Financial Management Platform

Features:
- Cost analysis and breakdown
- Optimization recommendations with AI
- RI/Savings Plans advisor
- Waste detection and elimination
- FinOps maturity assessment
- Cost allocation and showback
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
import json

# ============================================================================
# FINOPS DATA STRUCTURES
# ============================================================================

COST_CATEGORIES = {
    "compute": {
        "name": "Compute",
        "icon": "💻",
        "services": ["EC2", "Lambda", "ECS", "EKS", "Fargate", "Lightsail", "Batch"],
        "typical_percentage": 45,
        "optimization_potential": "20-40%"
    },
    "storage": {
        "name": "Storage",
        "icon": "💾",
        "services": ["S3", "EBS", "EFS", "FSx", "Glacier", "Storage Gateway"],
        "typical_percentage": 15,
        "optimization_potential": "15-30%"
    },
    "database": {
        "name": "Database",
        "icon": "🗄️",
        "services": ["RDS", "DynamoDB", "ElastiCache", "Redshift", "Neptune", "DocumentDB"],
        "typical_percentage": 20,
        "optimization_potential": "15-25%"
    },
    "network": {
        "name": "Network",
        "icon": "🌐",
        "services": ["Data Transfer", "CloudFront", "Route53", "VPC", "Direct Connect", "Global Accelerator"],
        "typical_percentage": 10,
        "optimization_potential": "10-25%"
    },
    "other": {
        "name": "Other Services",
        "icon": "📦",
        "services": ["Support", "Marketplace", "KMS", "Secrets Manager", "CloudWatch"],
        "typical_percentage": 10,
        "optimization_potential": "5-15%"
    }
}

OPTIMIZATION_STRATEGIES = [
    {
        "name": "Reserved Instances",
        "category": "Commitment",
        "savings_potential": "30-72%",
        "effort": "Low",
        "risk": "Medium",
        "description": "Commit to 1 or 3 year terms for predictable workloads",
        "best_for": ["Steady-state workloads", "Production databases", "Always-on applications"],
        "implementation": [
            "Analyze 30-day EC2/RDS usage in Cost Explorer",
            "Identify instances running 24/7 with consistent utilization",
            "Start with 1-year No Upfront for lower risk",
            "Consider Convertible RIs for flexibility",
            "Purchase RIs matching your usage pattern"
        ],
        "aws_tools": ["Cost Explorer RI Recommendations", "AWS Cost Optimization Hub"]
    },
    {
        "name": "Savings Plans",
        "category": "Commitment",
        "savings_potential": "20-72%",
        "effort": "Low",
        "risk": "Low",
        "description": "Flexible commitment discount for compute usage",
        "best_for": ["Variable workloads", "Multi-service usage", "Organizations wanting flexibility"],
        "implementation": [
            "Review Savings Plans recommendations in Cost Explorer",
            "Choose Compute Savings Plans for maximum flexibility",
            "Start with 1-year No Upfront commitment",
            "Cover 60-70% of baseline usage",
            "Monitor coverage and adjust"
        ],
        "aws_tools": ["Savings Plans Recommendations", "Cost Optimization Hub"]
    },
    {
        "name": "Spot Instances",
        "category": "Pricing Model",
        "savings_potential": "60-90%",
        "effort": "Medium",
        "risk": "Medium",
        "description": "Use spare EC2 capacity at steep discounts",
        "best_for": ["Fault-tolerant workloads", "Batch processing", "CI/CD", "Dev/Test"],
        "implementation": [
            "Identify fault-tolerant workloads",
            "Configure Spot Fleet or ASG with Spot",
            "Use capacity-optimized allocation strategy",
            "Implement graceful shutdown handling",
            "Diversify across instance types and AZs"
        ],
        "aws_tools": ["Spot Instance Advisor", "EC2 Fleet", "Karpenter"]
    },
    {
        "name": "Right-sizing",
        "category": "Resource Optimization",
        "savings_potential": "10-40%",
        "effort": "Medium",
        "risk": "Low",
        "description": "Match instance sizes to actual utilization",
        "best_for": ["Over-provisioned resources", "Variable utilization patterns"],
        "implementation": [
            "Enable AWS Compute Optimizer",
            "Review right-sizing recommendations",
            "Start with clearly over-provisioned instances",
            "Monitor performance after changes",
            "Implement continuous right-sizing process"
        ],
        "aws_tools": ["Compute Optimizer", "CloudWatch", "Trusted Advisor"]
    },
    {
        "name": "Graviton Migration",
        "category": "Architecture",
        "savings_potential": "20-40%",
        "effort": "Medium",
        "risk": "Low",
        "description": "Move to ARM-based Graviton processors",
        "best_for": ["Linux workloads", "Containerized apps", "Open source software"],
        "implementation": [
            "Inventory current x86 workloads",
            "Test application compatibility on Graviton",
            "Start with dev/test environments",
            "Migrate containerized workloads first",
            "Update AMIs and launch templates"
        ],
        "aws_tools": ["EC2 Instance Types", "EKS", "Lambda"]
    },
    {
        "name": "Storage Tiering",
        "category": "Resource Optimization",
        "savings_potential": "20-60%",
        "effort": "Low",
        "risk": "Low",
        "description": "Move data to appropriate storage tiers",
        "best_for": ["Large S3 buckets", "Infrequent access data", "Archival requirements"],
        "implementation": [
            "Analyze S3 access patterns with Storage Class Analysis",
            "Create Lifecycle policies for automatic tiering",
            "Enable S3 Intelligent-Tiering for unpredictable access",
            "Move archives to Glacier Deep Archive",
            "Use EBS volume types appropriate for workload"
        ],
        "aws_tools": ["S3 Storage Class Analysis", "S3 Intelligent-Tiering", "Storage Lens"]
    },
    {
        "name": "Idle Resource Cleanup",
        "category": "Waste Elimination",
        "savings_potential": "5-20%",
        "effort": "Low",
        "risk": "Low",
        "description": "Remove unused resources",
        "best_for": ["Organizations with sprawl", "Post-project cleanup", "Cost governance"],
        "implementation": [
            "Identify unattached EBS volumes",
            "Find unused Elastic IPs",
            "Locate idle load balancers",
            "Delete old EBS snapshots",
            "Remove unused NAT Gateways"
        ],
        "aws_tools": ["Trusted Advisor", "Cost Explorer", "AWS Config"]
    },
    {
        "name": "Instance Scheduling",
        "category": "Waste Elimination",
        "savings_potential": "40-70%",
        "effort": "Low",
        "risk": "Low",
        "description": "Stop non-production resources after hours",
        "best_for": ["Dev/Test environments", "Demo systems", "Internal tools"],
        "implementation": [
            "Deploy AWS Instance Scheduler",
            "Define schedules (e.g., M-F 8am-6pm)",
            "Tag resources with schedule names",
            "Configure timezone appropriately",
            "Create exceptions for critical resources"
        ],
        "aws_tools": ["Instance Scheduler", "EventBridge", "Lambda"]
    }
]

FINOPS_MATURITY_DIMENSIONS = {
    "visibility": {
        "name": "Cost Visibility",
        "levels": {
            1: "No visibility into costs",
            2: "Monthly bills reviewed",
            3: "Cost Explorer used regularly",
            4: "Real-time dashboards available",
            5: "Anomaly detection in place"
        }
    },
    "allocation": {
        "name": "Cost Allocation",
        "levels": {
            1: "No cost allocation",
            2: "By AWS account only",
            3: "Tags used for allocation",
            4: "Full showback implemented",
            5: "Chargeback to business units"
        }
    },
    "optimization": {
        "name": "Optimization",
        "levels": {
            1: "No optimization activities",
            2: "Ad-hoc optimization",
            3: "Regular reviews and actions",
            4: "Automated optimization",
            5: "Continuous AI-driven optimization"
        }
    },
    "forecasting": {
        "name": "Forecasting",
        "levels": {
            1: "No forecasting",
            2: "Basic historical trending",
            3: "Monthly forecasts",
            4: "ML-based predictions",
            5: "Real-time forecast adjustments"
        }
    },
    "governance": {
        "name": "Governance",
        "levels": {
            1: "No governance",
            2: "Basic budgets in place",
            3: "Budget alerts configured",
            4: "Automated guardrails",
            5: "Policy-driven cost control"
        }
    },
    "culture": {
        "name": "FinOps Culture",
        "levels": {
            1: "Finance/Ops siloed",
            2: "Awareness beginning",
            3: "Cross-functional collaboration",
            4: "Engineers accountable for costs",
            5: "Cost optimization in DNA"
        }
    }
}

# ============================================================================
# AI ANALYSIS
# ============================================================================

def get_finops_ai_analysis(client, cost_data: Dict, context: str) -> Optional[str]:
    """Get AI-powered FinOps analysis"""
    if not client:
        return None
    
    prompt = f"""You are an AWS FinOps expert. Analyze the following cost data and provide actionable recommendations.

COST DATA:
{json.dumps(cost_data, indent=2)}

ORGANIZATION CONTEXT:
{context if context else 'Not provided'}

Provide comprehensive analysis including:

1. **Cost Analysis Summary**
   - Key observations about spending patterns
   - Comparison to industry benchmarks
   
2. **Top 5 Optimization Opportunities**
   - Specific recommendations with estimated savings
   - Implementation steps and effort level
   - Risk assessment for each
   
3. **Quick Wins (implement this week)**
   - Low-effort, immediate savings opportunities
   
4. **Strategic Recommendations (next quarter)**
   - Longer-term optimization strategies
   - Architecture changes for cost efficiency
   
5. **Commitment Strategy**
   - Reserved Instance recommendations
   - Savings Plans recommendations
   - Optimal commitment level
   
6. **Cost Governance Recommendations**
   - Tagging strategy
   - Budget and alert recommendations
   - Policy suggestions

Be specific with dollar amounts where possible. Include AWS service names and specific actions."""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    except Exception as e:
        return f"Error: {e}"

# ============================================================================
# RENDER FUNCTIONS
# ============================================================================

def render_finops_tab():
    """Render comprehensive FinOps tab"""
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1b5e20 0%, #2e7d32 100%); padding: 2rem; border-radius: 12px; margin-bottom: 1.5rem;">
        <h2 style="color: #C8E6C9; margin: 0;">💰 FinOps & Cost Optimization</h2>
        <p style="color: #A5D6A7; margin: 0.5rem 0 0 0;">AI-Powered Cloud Financial Management</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sub-tabs
    tabs = st.tabs([
        "📊 Cost Analysis",
        "💡 Optimization Strategies",
        "📈 Commitment Advisor",
        "🗑️ Waste Detector",
        "📉 FinOps Maturity"
    ])
    
    with tabs[0]:
        render_cost_analysis()
    
    with tabs[1]:
        render_optimization_strategies()
    
    with tabs[2]:
        render_commitment_advisor()
    
    with tabs[3]:
        render_waste_detector()
    
    with tabs[4]:
        render_finops_maturity()

def render_cost_analysis():
    """Render cost analysis section"""
    st.markdown("### 📊 Cost Analysis & Breakdown")
    
    st.info("💡 Enter your monthly costs by category for analysis")
    
    col1, col2 = st.columns(2)
    costs = {}
    
    with col1:
        st.markdown("**Core Services**")
        costs['compute'] = st.number_input("💻 Compute (EC2, Lambda, etc.)", min_value=0, value=8500, step=100)
        costs['storage'] = st.number_input("💾 Storage (S3, EBS, etc.)", min_value=0, value=2200, step=100)
        costs['database'] = st.number_input("🗄️ Database (RDS, DynamoDB)", min_value=0, value=3500, step=100)
    
    with col2:
        st.markdown("**Supporting Services**")
        costs['network'] = st.number_input("🌐 Network & Data Transfer", min_value=0, value=1800, step=100)
        costs['other'] = st.number_input("📦 Other Services", min_value=0, value=1200, step=100)
    
    total = sum(costs.values())
    
    st.markdown("---")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Monthly Spend", f"${total:,.0f}")
    with col2:
        st.metric("Annual Projection", f"${total * 12:,.0f}")
    with col3:
        # Estimate savings (25% typical)
        savings = total * 0.25
        st.metric("Potential Savings", f"${savings:,.0f}/mo", delta="-25%")
    with col4:
        st.metric("Annual Savings", f"${savings * 12:,.0f}")
    
    # Cost breakdown visualization
    st.markdown("### 📈 Cost Distribution")
    
    for cat_key, cat_data in COST_CATEGORIES.items():
        cost_val = costs.get(cat_key, 0)
        pct = (cost_val / total * 100) if total > 0 else 0
        typical = cat_data['typical_percentage']
        
        col1, col2, col3, col4 = st.columns([1, 2, 1, 1])
        with col1:
            st.markdown(f"{cat_data['icon']} **{cat_data['name']}**")
        with col2:
            st.progress(min(pct / 100, 1.0))
        with col3:
            st.markdown(f"${cost_val:,.0f} ({pct:.1f}%)")
        with col4:
            status = "🟢" if pct <= typical + 5 else "🟡" if pct <= typical + 15 else "🔴"
            st.markdown(f"{status} Typical: {typical}%")
    
    # AI Analysis
    st.markdown("---")
    st.markdown("### 🤖 AI-Powered Analysis")
    
    if st.button("🔍 Get AI Analysis", type="primary"):
        try:
            import anthropic
            api_key = st.session_state.get('anthropic_api_key')
            if not api_key:
                try:
                    api_key = st.secrets.get('ANTHROPIC_API_KEY')
                except:
                    pass
            
            if api_key:
                client = anthropic.Anthropic(api_key=api_key)
                context = st.session_state.get('organization_context', '')
                
                with st.spinner("Analyzing your costs..."):
                    analysis = get_finops_ai_analysis(client, costs, context)
                
                if analysis:
                    st.markdown(analysis)
            else:
                st.warning("Configure API key for AI analysis")
        except Exception as e:
            st.error(f"Error: {e}")

def render_optimization_strategies():
    """Render optimization strategies"""
    st.markdown("### 💡 Optimization Strategies")
    st.markdown("Proven strategies to reduce your AWS costs")
    
    # Filter by category
    categories = list(set(s['category'] for s in OPTIMIZATION_STRATEGIES))
    selected_cat = st.multiselect("Filter by Category", categories, default=categories)
    
    for strategy in OPTIMIZATION_STRATEGIES:
        if strategy['category'] not in selected_cat:
            continue
        
        with st.expander(f"💡 {strategy['name']} - Save {strategy['savings_potential']}"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Savings Potential", strategy['savings_potential'])
            with col2:
                effort_color = {"Low": "🟢", "Medium": "🟡", "High": "🔴"}.get(strategy['effort'], "⚪")
                st.metric("Effort", f"{effort_color} {strategy['effort']}")
            with col3:
                risk_color = {"Low": "🟢", "Medium": "🟡", "High": "🔴"}.get(strategy['risk'], "⚪")
                st.metric("Risk", f"{risk_color} {strategy['risk']}")
            
            st.markdown(f"**Description:** {strategy['description']}")
            
            st.markdown("**Best For:**")
            for item in strategy['best_for']:
                st.markdown(f"- {item}")
            
            st.markdown("**Implementation Steps:**")
            for i, step in enumerate(strategy['implementation'], 1):
                st.markdown(f"{i}. {step}")
            
            st.markdown(f"**AWS Tools:** {', '.join(strategy['aws_tools'])}")

def render_commitment_advisor():
    """Render commitment discount advisor"""
    st.markdown("### 📈 Commitment Discount Advisor")
    st.markdown("Optimize your Reserved Instance and Savings Plan strategy")
    
    col1, col2 = st.columns(2)
    
    with col1:
        monthly_ondemand = st.number_input("Current On-Demand Spend", min_value=0, value=10000, step=500)
        current_ri_coverage = st.slider("Current RI/SP Coverage %", 0, 100, 30)
        workload_stability = st.select_slider(
            "Workload Stability",
            options=["Highly Variable", "Somewhat Variable", "Stable", "Very Stable"],
            value="Stable"
        )
    
    with col2:
        commitment_preference = st.selectbox(
            "Commitment Preference",
            ["Maximum Savings", "Balanced", "Maximum Flexibility"]
        )
        term_preference = st.selectbox("Term Preference", ["1 Year", "3 Year", "Mix"])
        payment_preference = st.selectbox("Payment Preference", ["No Upfront", "Partial Upfront", "All Upfront"])
    
    if st.button("📊 Generate Recommendations"):
        st.markdown("---")
        st.markdown("### 📋 Recommendations")
        
        # Calculate recommendations based on inputs
        target_coverage = 70 if workload_stability in ["Stable", "Very Stable"] else 50
        additional_coverage = target_coverage - current_ri_coverage
        
        if additional_coverage > 0:
            additional_commitment = monthly_ondemand * (additional_coverage / 100)
            
            # Savings calculation
            if commitment_preference == "Maximum Savings":
                savings_rate = 0.40
                rec_type = "3-year All Upfront Reserved Instances"
            elif commitment_preference == "Balanced":
                savings_rate = 0.30
                rec_type = "1-year Compute Savings Plan"
            else:
                savings_rate = 0.22
                rec_type = "1-year No Upfront Compute Savings Plan"
            
            monthly_savings = additional_commitment * savings_rate
            annual_savings = monthly_savings * 12
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Target Coverage", f"{target_coverage}%")
            with col2:
                st.metric("Monthly Savings", f"${monthly_savings:,.0f}")
            with col3:
                st.metric("Annual Savings", f"${annual_savings:,.0f}")
            
            st.success(f"**Recommendation:** Purchase {rec_type} to cover additional ${additional_commitment:,.0f}/month")
            
            st.markdown("""
            **Next Steps:**
            1. Review Savings Plans recommendations in AWS Cost Explorer
            2. Analyze your specific usage patterns
            3. Start with a smaller commitment to test
            4. Monitor coverage and adjust quarterly
            """)
        else:
            st.info("Your current coverage appears adequate. Consider reviewing for optimization opportunities.")

def render_waste_detector():
    """Render waste detection section"""
    st.markdown("### 🗑️ Waste Detector")
    st.markdown("Identify and eliminate cloud waste")
    
    is_demo = st.session_state.get('app_mode', 'demo') == 'demo'
    
    if is_demo:
        # Demo waste data
        waste_items = [
            {"type": "Unattached EBS Volumes", "count": 8, "monthly_cost": 180, "action": "Delete or attach"},
            {"type": "Idle Elastic IPs", "count": 5, "monthly_cost": 18, "action": "Release unused EIPs"},
            {"type": "Unused Load Balancers", "count": 3, "monthly_cost": 65, "action": "Delete ALBs with no targets"},
            {"type": "Old EBS Snapshots (>90 days)", "count": 45, "monthly_cost": 95, "action": "Review and delete"},
            {"type": "Stopped Instances (>30 days)", "count": 6, "monthly_cost": 0, "action": "Terminate or restart"},
            {"type": "Unattached NAT Gateways", "count": 2, "monthly_cost": 90, "action": "Delete if unused"},
            {"type": "Oversized RDS Instances", "count": 2, "monthly_cost": 320, "action": "Right-size databases"},
        ]
        
        total_waste = sum(w['monthly_cost'] for w in waste_items)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Monthly Waste", f"${total_waste:,.0f}")
        with col2:
            st.metric("Annual Waste", f"${total_waste * 12:,.0f}")
        with col3:
            st.metric("Waste Items", sum(w['count'] for w in waste_items))
        
        st.markdown("---")
        
        for waste in waste_items:
            col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
            with col1:
                st.markdown(f"**{waste['type']}**")
            with col2:
                st.markdown(f"{waste['count']} items")
            with col3:
                st.markdown(f"${waste['monthly_cost']}/mo")
            with col4:
                st.caption(waste['action'])
    else:
        st.info("Connect to AWS to scan for waste in your account")

def render_finops_maturity():
    """Render FinOps maturity assessment"""
    st.markdown("### 📉 FinOps Maturity Assessment")
    st.markdown("Assess and improve your FinOps capabilities")
    
    scores = {}
    
    cols = st.columns(2)
    
    for idx, (dim_key, dim) in enumerate(FINOPS_MATURITY_DIMENSIONS.items()):
        with cols[idx % 2]:
            scores[dim_key] = st.select_slider(
                dim['name'],
                options=[1, 2, 3, 4, 5],
                value=2,
                format_func=lambda x, d=dim: f"L{x}: {d['levels'][x][:30]}..."
            )
    
    avg_score = sum(scores.values()) / len(scores)
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        phase = "Run" if avg_score >= 4 else "Walk" if avg_score >= 2.5 else "Crawl"
        st.metric("FinOps Phase", phase)
    with col2:
        st.metric("Average Maturity", f"{avg_score:.1f}/5")
    with col3:
        next_target = min(5, int(avg_score) + 1)
        st.metric("Next Target", f"Level {next_target}")
    
    # Recommendations
    st.markdown("### 📋 Improvement Recommendations")
    
    lowest_dims = sorted(scores.items(), key=lambda x: x[1])[:3]
    
    for dim_key, score in lowest_dims:
        dim = FINOPS_MATURITY_DIMENSIONS[dim_key]
        next_level = min(5, score + 1)
        
        st.markdown(f"**{dim['name']}** (Current: Level {score})")
        st.markdown(f"→ Target: {dim['levels'][next_level]}")

# Export
__all__ = ['render_finops_tab']
