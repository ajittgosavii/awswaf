"""
EKS & Container Modernization Module - Enhanced
Comprehensive AI-Powered Kubernetes Modernization Platform

Focus Areas:
- Organizational challenges (sizing, technology selection, architecture decisions)
- Best architectural patterns and reference architectures
- Transformation roadmap and implementation strategies
- Cost-benefit analysis for modernization initiatives
- AI-powered personalized recommendations
"""

import streamlit as st
import json
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, field

# ============================================================================
# ORGANIZATIONAL CHALLENGES FRAMEWORK
# ============================================================================

MODERNIZATION_CHALLENGES = {
    "sizing_capacity": {
        "name": "Sizing & Capacity Planning",
        "icon": "📊",
        "severity": "High",
        "frequency": "85% of organizations",
        "description": "Determining the right cluster size, node types, and capacity requirements",
        "common_issues": [
            "Over-provisioning leading to 30-50% wasted resources",
            "Under-provisioning causing performance degradation",
            "Inability to predict peak load requirements",
            "Lack of visibility into actual resource utilization",
            "Difficulty in forecasting growth patterns"
        ],
        "symptoms": [
            "Consistently low CPU/memory utilization (<40%)",
            "Frequent node scaling events",
            "Application performance issues during peaks",
            "Unexpected cost overruns",
            "Manual intervention required for scaling"
        ],
        "solutions": {
            "short_term": {
                "actions": [
                    "Enable AWS Compute Optimizer for right-sizing recommendations",
                    "Implement comprehensive monitoring with Container Insights",
                    "Deploy metrics-server and vertical pod autoscaler (VPA)",
                    "Analyze pod resource requests vs actual usage",
                    "Set up cost allocation tags by team/application"
                ],
                "tools": ["AWS Compute Optimizer", "Container Insights", "Kubecost", "Prometheus"],
                "timeline": "1-2 weeks",
                "expected_outcome": "15-25% immediate cost reduction"
            },
            "long_term": {
                "actions": [
                    "Implement Karpenter for intelligent node provisioning",
                    "Deploy cluster-proportional-autoscaler for system components",
                    "Create capacity planning dashboards with historical trends",
                    "Establish pod resource quotas and limit ranges",
                    "Implement predictive scaling using machine learning"
                ],
                "tools": ["Karpenter", "Prometheus + Thanos", "AI/ML forecasting", "Custom operators"],
                "timeline": "2-3 months",
                "expected_outcome": "30-50% optimization + automated management"
            }
        },
        "best_practices": [
            "Start with 60% capacity buffer, gradually optimize",
            "Use pod disruption budgets to protect critical workloads",
            "Implement multi-tier autoscaling (pod → node → cluster)",
            "Regular capacity reviews every quarter",
            "Build capacity models based on business metrics"
        ],
        "cost_impact": "30-50% of total EKS costs"
    },
    
    "technology_selection": {
        "name": "Technology Stack Selection",
        "icon": "🔧",
        "severity": "Critical",
        "frequency": "90% of organizations",
        "description": "Choosing the right tools and technologies from the overwhelming Kubernetes ecosystem",
        "common_issues": [
            "Analysis paralysis from too many options",
            "Vendor lock-in concerns with managed services",
            "Incompatible tool combinations",
            "Technical debt from early technology choices",
            "Team skill gaps with selected technologies"
        ],
        "decision_framework": {
            "criteria": [
                {
                    "name": "Team Expertise",
                    "weight": "25%",
                    "considerations": [
                        "Current team skills and experience",
                        "Learning curve and training requirements",
                        "Community support and documentation",
                        "Hiring availability for specialists"
                    ]
                },
                {
                    "name": "Operational Complexity",
                    "weight": "30%",
                    "considerations": [
                        "Day-2 operations burden",
                        "Maintenance and upgrade overhead",
                        "Troubleshooting and debugging ease",
                        "Integration with existing tools"
                    ]
                },
                {
                    "name": "Business Requirements",
                    "weight": "25%",
                    "considerations": [
                        "Performance requirements",
                        "Security and compliance needs",
                        "Multi-cloud/hybrid requirements",
                        "Vendor neutrality importance"
                    ]
                },
                {
                    "name": "Total Cost of Ownership",
                    "weight": "20%",
                    "considerations": [
                        "Licensing costs",
                        "Infrastructure overhead",
                        "Team size requirements",
                        "Support and enterprise features"
                    ]
                }
            ]
        },
        "technology_maturity_model": {
            "level_1_basic": {
                "name": "Foundation (Months 0-3)",
                "focus": "Core Kubernetes + AWS Native Services",
                "recommended_stack": [
                    "EKS Managed Control Plane",
                    "Cluster Autoscaler (simple autoscaling)",
                    "AWS Load Balancer Controller",
                    "EBS CSI Driver for storage",
                    "Container Insights for monitoring",
                    "kubectl + Helm for deployments"
                ],
                "rationale": "Minimize complexity, leverage AWS integration, low learning curve",
                "team_size": "2-3 engineers"
            },
            "level_2_intermediate": {
                "name": "Scale & Optimize (Months 3-9)",
                "focus": "Operational Excellence + Cost Optimization",
                "recommended_stack": [
                    "Karpenter (advanced autoscaling)",
                    "Prometheus + Grafana (observability)",
                    "FluxCD or ArgoCD (GitOps)",
                    "External Secrets Operator",
                    "Cert-manager for TLS",
                    "Kyverno or OPA for policies"
                ],
                "rationale": "Proven tools, active communities, production-ready",
                "team_size": "4-6 engineers"
            },
            "level_3_advanced": {
                "name": "Innovation & Governance (Months 9+)",
                "focus": "Advanced Patterns + Multi-Cluster",
                "recommended_stack": [
                    "Service Mesh (Istio/Linkerd)",
                    "Multi-cluster management",
                    "Advanced security (Falco, Trivy)",
                    "Custom operators",
                    "FinOps automation",
                    "Chaos engineering"
                ],
                "rationale": "Microservices at scale, complex requirements, mature team",
                "team_size": "8+ engineers with specialized roles"
            }
        },
        "common_mistakes": [
            "Adopting service mesh too early (before microservices maturity)",
            "Over-engineering for current scale",
            "Choosing tools based on hype rather than needs",
            "Ignoring operational burden of tool choices",
            "Not considering team skill development timeline"
        ]
    },
    
    "architecture_patterns": {
        "name": "Architecture & Design Decisions",
        "icon": "🏗️",
        "severity": "Critical",
        "frequency": "78% of organizations",
        "description": "Designing the right architecture for workloads, networking, security, and operations",
        "common_issues": [
            "Monolithic architecture migrated to containers without decomposition",
            "Improper network segmentation and security boundaries",
            "Inadequate disaster recovery and high availability design",
            "Poor secret management and credential handling",
            "Insufficient observability and troubleshooting capabilities"
        ],
        "architecture_layers": {
            "workload_architecture": {
                "name": "Workload Architecture",
                "patterns": [
                    {
                        "pattern": "Microservices with Sidecar Pattern",
                        "use_case": "Complex applications requiring service mesh",
                        "pros": ["Fine-grained control", "Rich observability", "Traffic management"],
                        "cons": ["Resource overhead", "Increased complexity"],
                        "best_for": "Large teams, 50+ services"
                    },
                    {
                        "pattern": "Modular Monolith",
                        "use_case": "Mid-size applications transitioning to microservices",
                        "pros": ["Simpler operations", "Lower overhead", "Easier debugging"],
                        "cons": ["Limited independent scaling", "Deployment coupling"],
                        "best_for": "Teams under 20, growing applications"
                    },
                    {
                        "pattern": "Serverless Hybrid (EKS + Lambda)",
                        "use_case": "Event-driven workloads with variable load",
                        "pros": ["Cost efficient", "Auto-scaling", "No server management"],
                        "cons": ["Cold start latency", "Limited execution time"],
                        "best_for": "Batch processing, APIs with variable traffic"
                    }
                ]
            },
            "network_architecture": {
                "name": "Network Architecture",
                "key_decisions": [
                    {
                        "decision": "IP Address Management",
                        "options": [
                            {
                                "option": "AWS VPC CNI (Native)",
                                "pros": ["Native AWS integration", "Direct pod networking", "Simple security groups"],
                                "cons": ["IP address exhaustion", "ENI limits"],
                                "recommendation": "Default choice for most workloads"
                            },
                            {
                                "option": "Calico",
                                "pros": ["Network policies", "No IP exhaustion", "On-premises consistency"],
                                "cons": ["Additional complexity", "Encapsulation overhead"],
                                "recommendation": "For IP-constrained environments or network policy requirements"
                            }
                        ]
                    },
                    {
                        "decision": "Ingress Strategy",
                        "options": [
                            {
                                "option": "AWS Load Balancer Controller",
                                "pros": ["Native AWS integration", "Automatic ALB/NLB provisioning", "WAF integration"],
                                "cons": ["AWS-specific", "Load balancer costs"],
                                "recommendation": "Primary choice for AWS-native applications"
                            },
                            {
                                "option": "NGINX Ingress + NLB",
                                "pros": ["Vendor neutral", "Advanced routing", "Lower cost"],
                                "cons": ["Manual management", "Additional configuration"],
                                "recommendation": "For multi-cloud or advanced routing requirements"
                            }
                        ]
                    }
                ]
            },
            "security_architecture": {
                "name": "Security Architecture",
                "layers": [
                    {
                        "layer": "Cluster Security",
                        "controls": [
                            "Private API endpoint with bastion host or VPN",
                            "Pod security standards (restricted profile)",
                            "Network policies for pod-to-pod communication",
                            "IRSA (IAM Roles for Service Accounts) for least privilege",
                            "Encryption at rest (EBS, EFS) and in transit (TLS)"
                        ]
                    },
                    {
                        "layer": "Workload Security",
                        "controls": [
                            "Container image scanning (ECR, Trivy)",
                            "Runtime security monitoring (Falco, GuardDuty)",
                            "Secret management (External Secrets Operator + Secrets Manager)",
                            "Resource quotas and limit ranges",
                            "Security context constraints"
                        ]
                    },
                    {
                        "layer": "Identity & Access",
                        "controls": [
                            "RBAC with least privilege principle",
                            "AWS SSO integration for human access",
                            "Service accounts with IRSA for workload access",
                            "Audit logging to CloudWatch/S3",
                            "MFA enforcement for cluster admin access"
                        ]
                    }
                ]
            }
        }
    },
    
    "operational_readiness": {
        "name": "Operational Readiness",
        "icon": "⚙️",
        "severity": "High",
        "frequency": "82% of organizations",
        "description": "Preparing teams and processes for production Kubernetes operations",
        "readiness_dimensions": {
            "observability": {
                "name": "Observability & Monitoring",
                "requirements": [
                    "Centralized logging (CloudWatch Container Insights or EFK)",
                    "Metrics collection (Prometheus + Grafana)",
                    "Distributed tracing (X-Ray or Jaeger)",
                    "Application performance monitoring",
                    "Cost visibility and allocation"
                ],
                "kpis": [
                    "Mean time to detect (MTTD) < 5 minutes",
                    "Mean time to resolve (MTTR) < 30 minutes",
                    "Service availability > 99.9%",
                    "Alert noise ratio < 5%"
                ]
            },
            "incident_management": {
                "name": "Incident Management",
                "requirements": [
                    "Runbook automation for common scenarios",
                    "On-call rotation and escalation procedures",
                    "Post-incident review process",
                    "Chaos engineering practices",
                    "Disaster recovery drills"
                ],
                "tools": ["PagerDuty/OpsGenie", "Incident.io", "AWS Systems Manager", "Chaos Mesh"]
            },
            "change_management": {
                "name": "Change Management",
                "requirements": [
                    "GitOps workflow (ArgoCD/FluxCD)",
                    "Progressive delivery (canary/blue-green)",
                    "Automated testing pipeline",
                    "Change approval process",
                    "Rollback procedures"
                ],
                "success_criteria": [
                    "100% of changes tracked in Git",
                    "Zero manual kubectl applies in production",
                    "Automated validation before production",
                    "Rollback capability for all changes"
                ]
            }
        }
    }
}

# ============================================================================
# ARCHITECTURAL PATTERNS & REFERENCE ARCHITECTURES
# ============================================================================

REFERENCE_ARCHITECTURES = {
    "high_availability_multi_az": {
        "name": "High Availability Multi-AZ Architecture",
        "icon": "🏢",
        "complexity": "Medium",
        "use_case": "Production workloads requiring 99.99% availability",
        "description": "Enterprise-grade HA architecture with multi-AZ distribution and automated failover",
        "components": {
            "control_plane": {
                "configuration": "EKS managed across 3 AZs",
                "rationale": "AWS manages HA and failover automatically",
                "cost": "~$0.10/hour ($73/month)"
            },
            "data_plane": {
                "configuration": [
                    "3 managed node groups, one per AZ",
                    "Mixed instance types with priorities",
                    "Auto Scaling Groups with termination policies",
                    "Pod anti-affinity for critical workloads"
                ],
                "rationale": "Ensures application availability during AZ failure",
                "cost_optimization": "Use Karpenter to optimize instance selection across AZs"
            },
            "networking": {
                "configuration": [
                    "VPC with private subnets in 3 AZs",
                    "NAT Gateway in each AZ (HA)",
                    "Application Load Balancer with cross-zone load balancing",
                    "Network Load Balancer for internal services"
                ],
                "rationale": "Eliminates single points of failure in network path"
            },
            "storage": {
                "configuration": [
                    "EBS volumes with gp3 storage class",
                    "EFS for shared storage (automatically multi-AZ)",
                    "Regular EBS snapshots to S3"
                ],
                "rationale": "Persistent storage survives AZ failures"
            },
            "resilience_features": [
                "Pod Disruption Budgets (PDB) for all critical services",
                "Topology spread constraints for even distribution",
                "Health checks and automatic pod restart",
                "Horizontal Pod Autoscaler for demand changes",
                "Cluster Autoscaler or Karpenter for node scaling"
            ]
        },
        "implementation_steps": [
            {
                "phase": "Phase 1: Foundation (Week 1-2)",
                "tasks": [
                    "Create VPC with 3 public + 3 private subnets",
                    "Deploy EKS cluster with private endpoint",
                    "Configure managed node groups in each AZ",
                    "Install AWS Load Balancer Controller",
                    "Set up Container Insights monitoring"
                ]
            },
            {
                "phase": "Phase 2: Resilience (Week 3-4)",
                "tasks": [
                    "Configure Pod Disruption Budgets",
                    "Implement topology spread constraints",
                    "Set up Horizontal Pod Autoscalers",
                    "Deploy cluster-proportional-autoscaler",
                    "Configure pod anti-affinity rules"
                ]
            },
            {
                "phase": "Phase 3: Validation (Week 5-6)",
                "tasks": [
                    "Chaos engineering - simulate AZ failure",
                    "Load testing across zones",
                    "Validate failover times",
                    "Document runbooks",
                    "Train operations team"
                ]
            }
        ],
        "estimated_cost": {
            "control_plane": "$73/month",
            "nodes": "$500-2000/month (depends on workload)",
            "nat_gateways": "$96/month (3 x $32)",
            "load_balancers": "$50-100/month",
            "total": "$719-2269/month base + workload"
        },
        "availability_target": "99.99% (52 minutes downtime/year)"
    },
    
    "cost_optimized_spot_heavy": {
        "name": "Cost-Optimized Spot-Heavy Architecture",
        "icon": "💰",
        "complexity": "Medium-High",
        "use_case": "Fault-tolerant workloads prioritizing cost savings",
        "description": "Aggressive cost optimization using Spot instances with intelligent diversification",
        "target_savings": "60-80% compared to on-demand",
        "components": {
            "node_strategy": {
                "configuration": [
                    "10-20% on-demand for critical system components",
                    "80-90% Spot instances with Karpenter",
                    "Multiple instance families (c5, c6, m5, m6, r5, r6)",
                    "Both x86 and Graviton (arm64) instances"
                ],
                "spot_interruption_handling": [
                    "Karpenter automatic rebalancing",
                    "2-minute interruption warning handling",
                    "Graceful pod termination (terminationGracePeriodSeconds)",
                    "Pod Disruption Budgets to control drain rate"
                ]
            },
            "workload_patterns": {
                "critical_workloads": {
                    "description": "Control plane, auth services, monitoring",
                    "strategy": "On-demand instances with pod anti-affinity",
                    "percentage": "10-15% of total capacity"
                },
                "production_workloads": {
                    "description": "Application pods with multiple replicas",
                    "strategy": "70% Spot + 30% on-demand mix",
                    "percentage": "60-70% of total capacity"
                },
                "batch_workloads": {
                    "description": "Jobs, cron jobs, data processing",
                    "strategy": "100% Spot instances",
                    "percentage": "15-20% of total capacity"
                }
            },
            "karpenter_provisioner": {
                "configuration": """
apiVersion: karpenter.sh/v1beta1
kind: NodePool
metadata:
  name: cost-optimized
spec:
  template:
    spec:
      requirements:
        - key: karpenter.sh/capacity-type
          operator: In
          values: ["spot", "on-demand"]
        - key: kubernetes.io/arch
          operator: In
          values: ["amd64", "arm64"]
        - key: karpenter.k8s.aws/instance-category
          operator: In
          values: ["c", "m", "r"]
        - key: karpenter.k8s.aws/instance-generation
          operator: Gt
          values: ["5"]
      nodeClassRef:
        name: default
  disruption:
    consolidationPolicy: WhenUnderutilized
    consolidateAfter: 30s
    expireAfter: 720h # 30 days
  weight: 10
---
apiVersion: karpenter.sh/v1beta1
kind: NodePool
metadata:
  name: on-demand-critical
spec:
  template:
    spec:
      requirements:
        - key: karpenter.sh/capacity-type
          operator: In
          values: ["on-demand"]
      nodeClassRef:
        name: default
  weight: 100
                """
            }
        },
        "cost_breakdown": {
            "on_demand_baseline": "$1000/month",
            "with_spot_optimization": "$250-400/month",
            "savings": "60-75%",
            "risk_mitigation_cost": "$50/month (monitoring, automation)"
        },
        "risk_mitigation": [
            "Diversification across 10+ instance types",
            "Multi-AZ distribution",
            "Automatic capacity rebalancing",
            "Application-level resilience (multiple replicas)",
            "Monitoring and alerting for interruption rates"
        ]
    },
    
    "microservices_service_mesh": {
        "name": "Microservices with Service Mesh",
        "icon": "🕸️",
        "complexity": "High",
        "use_case": "Large-scale microservices requiring advanced traffic management",
        "description": "Enterprise microservices architecture with Istio service mesh for traffic control and observability",
        "prerequisites": [
            "50+ microservices",
            "Multiple teams",
            "Complex routing requirements",
            "Dedicated platform team (3+ engineers)"
        ],
        "architecture_layers": {
            "service_mesh": {
                "technology": "Istio",
                "components": [
                    "Istiod (control plane) - manages configuration",
                    "Envoy sidecars - data plane proxy in each pod",
                    "Ingress Gateway - entry point for external traffic",
                    "Egress Gateway - controlled external access"
                ],
                "features": [
                    "Automatic mTLS between all services",
                    "Advanced traffic routing (canary, A/B testing)",
                    "Circuit breaking and retries",
                    "Distributed tracing integration",
                    "Request metrics and logging"
                ]
            },
            "observability_stack": {
                "metrics": "Prometheus + Grafana + Kiali",
                "tracing": "Jaeger or AWS X-Ray",
                "logging": "CloudWatch Container Insights",
                "service_map": "Kiali for visualization"
            },
            "deployment_patterns": [
                {
                    "pattern": "Canary Deployment",
                    "description": "Gradual traffic shift to new version",
                    "configuration": "Istio VirtualService with weight-based routing",
                    "use_case": "Risk mitigation for production releases"
                },
                {
                    "pattern": "Circuit Breaking",
                    "description": "Prevent cascading failures",
                    "configuration": "DestinationRule with connection pool settings",
                    "use_case": "Protecting downstream services"
                },
                {
                    "pattern": "A/B Testing",
                    "description": "Route traffic based on headers/cookies",
                    "configuration": "VirtualService with header-based matching",
                    "use_case": "Feature testing and experimentation"
                }
            ]
        },
        "resource_overhead": {
            "cpu": "10-15% additional (Envoy sidecars)",
            "memory": "50-100MB per pod (sidecar)",
            "latency": "1-2ms per hop (sidecar processing)",
            "recommendation": "Budget 20% additional capacity"
        },
        "implementation_timeline": {
            "phase_1": "2-3 months (pilot with 5-10 services)",
            "phase_2": "3-6 months (full rollout)",
            "phase_3": "Ongoing (advanced features)",
            "team_investment": "1-2 full-time platform engineers"
        }
    },
    
    "hybrid_serverless": {
        "name": "Hybrid EKS + Serverless",
        "icon": "⚡",
        "complexity": "Medium",
        "use_case": "Mixed workloads - containers for stateful, Lambda for event-driven",
        "description": "Optimal cost-performance by combining EKS for long-running services with Lambda for event processing",
        "architecture_split": {
            "eks_workloads": [
                "API servers (always-on)",
                "Databases and stateful services",
                "WebSocket connections",
                "Long-running batch jobs",
                "Services requiring complex dependencies"
            ],
            "lambda_workloads": [
                "Event processors (SQS, SNS, EventBridge)",
                "Scheduled tasks",
                "Webhook handlers",
                "Image/video processing",
                "Simple REST APIs with low traffic"
            ]
        },
        "integration_patterns": {
            "eks_to_lambda": {
                "method": "Direct invocation via AWS SDK",
                "use_case": "Offload heavy processing from API",
                "example": "Image upload → EKS API → Lambda for resize → S3"
            },
            "lambda_to_eks": {
                "method": "HTTP calls to EKS services via ALB",
                "use_case": "Event triggers that need stateful processing",
                "example": "S3 event → Lambda → EKS service for business logic"
            },
            "shared_data": {
                "method": "SQS queues, S3 buckets, DynamoDB",
                "use_case": "Asynchronous communication",
                "example": "EKS produces to SQS → Lambda consumers process"
            }
        },
        "cost_optimization": {
            "savings": "40-60% vs all-EKS",
            "eks_cost": "$500/month (baseline services)",
            "lambda_cost": "$50-200/month (variable load)",
            "data_transfer": "$20-50/month (VPC endpoints reduce cost)"
        }
    }
}

# ============================================================================
# TRANSFORMATION ROADMAP FRAMEWORK
# ============================================================================

TRANSFORMATION_ROADMAP = {
    "assessment_phase": {
        "name": "Assessment & Planning",
        "duration": "4-6 weeks",
        "icon": "🔍",
        "objectives": [
            "Understand current state and technical debt",
            "Identify key challenges and constraints",
            "Define success criteria and KPIs",
            "Build business case for modernization"
        ],
        "activities": {
            "week_1_2": {
                "name": "Current State Analysis",
                "tasks": [
                    "Inventory existing applications and infrastructure",
                    "Document dependencies and integrations",
                    "Assess team skills and gaps",
                    "Review current costs and utilization",
                    "Identify compliance and security requirements"
                ],
                "deliverables": [
                    "Application portfolio inventory",
                    "Current architecture diagrams",
                    "Skills assessment matrix",
                    "Cost baseline report"
                ]
            },
            "week_3_4": {
                "name": "Target State Design",
                "tasks": [
                    "Define reference architecture",
                    "Select technology stack",
                    "Design network and security architecture",
                    "Plan disaster recovery strategy",
                    "Estimate target state costs"
                ],
                "deliverables": [
                    "Target architecture blueprints",
                    "Technology selection matrix",
                    "Security and compliance framework",
                    "TCO analysis and ROI projection"
                ]
            },
            "week_5_6": {
                "name": "Roadmap Development",
                "tasks": [
                    "Prioritize applications for migration",
                    "Define migration waves",
                    "Identify quick wins",
                    "Create detailed project plan",
                    "Secure stakeholder buy-in"
                ],
                "deliverables": [
                    "Migration prioritization matrix (6R framework)",
                    "Wave-based migration plan",
                    "Resource allocation plan",
                    "Risk register and mitigation strategies"
                ]
            }
        },
        "key_questions": [
            "What business outcomes are we optimizing for?",
            "What are our cost, performance, and reliability targets?",
            "What level of risk can we accept during migration?",
            "What is our timeline and resource availability?",
            "How will we measure success?"
        ]
    },
    
    "foundation_phase": {
        "name": "Foundation & Pilot",
        "duration": "8-12 weeks",
        "icon": "🏗️",
        "objectives": [
            "Build production-ready EKS foundation",
            "Establish operational processes",
            "Migrate pilot applications",
            "Validate architecture decisions"
        ],
        "week_by_week": {
            "weeks_1_2": {
                "focus": "Infrastructure Foundation",
                "tasks": [
                    "Set up AWS Organizations structure",
                    "Create VPCs and networking (Hub-spoke or multi-VPC)",
                    "Deploy EKS cluster(s) with best practices",
                    "Configure IAM roles and IRSA",
                    "Set up monitoring and logging"
                ],
                "success_criteria": [
                    "EKS cluster operational in all AZs",
                    "Network connectivity validated",
                    "Monitoring dashboards live",
                    "Security baselines implemented"
                ]
            },
            "weeks_3_4": {
                "focus": "Platform Services",
                "tasks": [
                    "Deploy ingress controller",
                    "Set up cert-manager for TLS",
                    "Install External Secrets Operator",
                    "Configure autoscaling (HPA, VPA, Cluster Autoscaler)",
                    "Implement GitOps (ArgoCD/FluxCD)"
                ],
                "success_criteria": [
                    "All platform services operational",
                    "TLS certificates auto-renewing",
                    "GitOps workflow functional",
                    "Test application deployed successfully"
                ]
            },
            "weeks_5_8": {
                "focus": "Pilot Migration",
                "tasks": [
                    "Select 2-3 pilot applications",
                    "Containerize applications",
                    "Create Kubernetes manifests",
                    "Set up CI/CD pipelines",
                    "Migrate pilot applications"
                ],
                "success_criteria": [
                    "Pilot apps running in production",
                    "Performance meets SLAs",
                    "Team confident with workflows",
                    "Lessons learned documented"
                ]
            },
            "weeks_9_12": {
                "focus": "Optimization & Lessons",
                "tasks": [
                    "Tune resource requests/limits",
                    "Optimize costs with Karpenter/Spot",
                    "Enhance monitoring and alerting",
                    "Document runbooks",
                    "Conduct retrospective"
                ],
                "success_criteria": [
                    "Cost optimization targets met",
                    "Operations runbooks complete",
                    "Team training completed",
                    "Go/No-go decision for scale-out"
                ]
            }
        }
    },
    
    "scale_out_phase": {
        "name": "Scale-Out & Migration",
        "duration": "3-9 months (depends on portfolio size)",
        "icon": "📈",
        "objectives": [
            "Migrate application portfolio systematically",
            "Scale platform capabilities",
            "Achieve cost optimization targets",
            "Build operational maturity"
        ],
        "migration_waves": {
            "wave_1_quick_wins": {
                "duration": "Month 1-2",
                "criteria": [
                    "Stateless applications",
                    "Low business criticality",
                    "Simple architecture",
                    "No compliance requirements"
                ],
                "apps_count": "5-10 applications",
                "risk": "Low",
                "objective": "Build confidence and momentum"
            },
            "wave_2_mainstream": {
                "duration": "Month 2-5",
                "criteria": [
                    "Production workloads",
                    "Medium complexity",
                    "Standard architecture patterns",
                    "Moderate business impact"
                ],
                "apps_count": "20-30 applications",
                "risk": "Medium",
                "objective": "Migrate bulk of portfolio"
            },
            "wave_3_complex": {
                "duration": "Month 5-9",
                "criteria": [
                    "Stateful applications",
                    "High business criticality",
                    "Complex dependencies",
                    "Compliance requirements (PCI, HIPAA)"
                ],
                "apps_count": "5-15 applications",
                "risk": "High",
                "objective": "Complete migration with careful planning"
            }
        },
        "parallel_workstreams": [
            {
                "stream": "Application Migration",
                "team": "Application teams + Platform team",
                "cadence": "2-week sprints",
                "activities": ["Containerization", "Testing", "Cutover", "Validation"]
            },
            {
                "stream": "Platform Enhancement",
                "team": "Platform engineering team",
                "cadence": "Continuous",
                "activities": ["Add capabilities", "Scale infrastructure", "Optimize costs", "Security hardening"]
            },
            {
                "stream": "Operations Maturity",
                "team": "SRE team",
                "cadence": "Continuous",
                "activities": ["Runbook creation", "Chaos testing", "Incident drills", "Process improvement"]
            }
        ]
    },
    
    "optimization_phase": {
        "name": "Continuous Optimization",
        "duration": "Ongoing",
        "icon": "🎯",
        "objectives": [
            "Achieve and maintain cost targets",
            "Improve reliability and performance",
            "Enhance developer experience",
            "Drive innovation with new capabilities"
        ],
        "optimization_areas": {
            "cost_optimization": {
                "initiatives": [
                    "Karpenter adoption for 30-50% savings",
                    "Spot instance utilization (60-90% savings)",
                    "Right-sizing based on actual usage",
                    "Reserved Instances/Savings Plans for baseline",
                    "Idle resource cleanup automation"
                ],
                "target": "40-60% cost reduction vs initial deployment",
                "tools": ["Kubecost", "CloudHealth", "AWS Cost Optimizer"]
            },
            "reliability_optimization": {
                "initiatives": [
                    "Chaos engineering program",
                    "SLI/SLO definition and tracking",
                    "Automated remediation",
                    "Multi-region disaster recovery",
                    "Service mesh for advanced patterns"
                ],
                "target": "99.95%+ availability for critical services",
                "tools": ["Chaos Mesh", "Litmus", "Gremlin"]
            },
            "performance_optimization": {
                "initiatives": [
                    "Application profiling and tuning",
                    "Graviton migration (20-40% better price-performance)",
                    "CDN and edge optimization",
                    "Database query optimization",
                    "Caching strategies"
                ],
                "target": "50% latency reduction, 2x throughput",
                "tools": ["Datadog APM", "New Relic", "X-Ray"]
            },
            "developer_experience": {
                "initiatives": [
                    "Internal developer platform (IDP)",
                    "Self-service provisioning",
                    "Standardized templates",
                    "Automated testing and deployment",
                    "Developer documentation portal"
                ],
                "target": "10x faster deployment, 50% less tickets",
                "tools": ["Backstage", "Crossplane", "Port"]
            }
        },
        "governance_framework": {
            "review_cadence": {
                "daily": "Cost anomaly review, incident review",
                "weekly": "Capacity planning, performance trends",
                "monthly": "Cost optimization review, security posture",
                "quarterly": "Architecture review, roadmap planning"
            },
            "kpis": [
                "Cost per transaction",
                "Application availability (SLI/SLO)",
                "Mean time to deploy",
                "Mean time to recover",
                "Developer satisfaction score"
            ]
        }
    }
}

# ============================================================================
# IMPLEMENTATION GUIDES
# ============================================================================

def render_challenges_assessment():
    """Render organizational challenges assessment"""
    st.markdown("## 🎯 Organizational Challenges & Solutions")
    
    for challenge_key, challenge in MODERNIZATION_CHALLENGES.items():
        with st.expander(f"{challenge['icon']} {challenge['name']} - {challenge['severity']} Priority"):
            st.markdown(f"**Affects:** {challenge['frequency']}")
            st.markdown(f"**Description:** {challenge['description']}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 🔴 Common Issues")
                for issue in challenge.get('common_issues', []):
                    st.markdown(f"• {issue}")
            
            with col2:
                if 'symptoms' in challenge:
                    st.markdown("### 📊 Symptoms")
                    for symptom in challenge['symptoms']:
                        st.markdown(f"• {symptom}")
            
            if 'solutions' in challenge:
                st.markdown("### 💡 Solutions")
                
                tab1, tab2 = st.tabs(["Quick Wins (1-2 weeks)", "Strategic (2-3 months)"])
                
                with tab1:
                    solution = challenge['solutions']['short_term']
                    st.markdown(f"**Timeline:** {solution['timeline']}")
                    st.markdown(f"**Expected Outcome:** {solution['expected_outcome']}")
                    st.markdown("**Actions:**")
                    for action in solution['actions']:
                        st.markdown(f"• {action}")
                    st.markdown(f"**Tools:** {', '.join(solution['tools'])}")
                
                with tab2:
                    solution = challenge['solutions']['long_term']
                    st.markdown(f"**Timeline:** {solution['timeline']}")
                    st.markdown(f"**Expected Outcome:** {solution['expected_outcome']}")
                    st.markdown("**Actions:**")
                    for action in solution['actions']:
                        st.markdown(f"• {action}")
                    st.markdown(f"**Tools:** {', '.join(solution['tools'])}")

def render_reference_architectures():
    """Render reference architectures"""
    st.markdown("## 🏗️ Reference Architectures & Patterns")
    
    arch_selection = st.selectbox(
        "Select Reference Architecture",
        options=list(REFERENCE_ARCHITECTURES.keys()),
        format_func=lambda x: f"{REFERENCE_ARCHITECTURES[x]['icon']} {REFERENCE_ARCHITECTURES[x]['name']}"
    )
    
    arch = REFERENCE_ARCHITECTURES[arch_selection]
    
    st.markdown(f"### {arch['icon']} {arch['name']}")
    st.markdown(f"**Complexity:** {arch['complexity']}")
    st.markdown(f"**Use Case:** {arch['use_case']}")
    st.markdown(f"**Description:** {arch['description']}")
    
    if 'target_savings' in arch:
        st.success(f"💰 **Target Savings:** {arch['target_savings']}")
    
    # Components
    st.markdown("### 📦 Architecture Components")
    for comp_key, comp_value in arch['components'].items():
        with st.expander(f"🔧 {comp_key.replace('_', ' ').title()}"):
            if isinstance(comp_value, dict):
                for key, value in comp_value.items():
                    if isinstance(value, list):
                        st.markdown(f"**{key.replace('_', ' ').title()}:**")
                        for item in value:
                            st.markdown(f"• {item}")
                    else:
                        st.markdown(f"**{key.replace('_', ' ').title()}:** {value}")
            elif isinstance(comp_value, list):
                for item in comp_value:
                    st.markdown(f"• {item}")
    
    # Implementation Steps
    if 'implementation_steps' in arch:
        st.markdown("### 📋 Implementation Steps")
        for step in arch['implementation_steps']:
            with st.expander(f"📍 {step['phase']}"):
                st.markdown("**Tasks:**")
                for task in step['tasks']:
                    st.markdown(f"• {task}")
    
    # Cost Breakdown
    if 'estimated_cost' in arch:
        st.markdown("### 💰 Estimated Monthly Cost")
        cost_data = arch['estimated_cost']
        for key, value in cost_data.items():
            st.markdown(f"**{key.replace('_', ' ').title()}:** {value}")

def render_transformation_roadmap():
    """Render transformation roadmap"""
    st.markdown("## 🗺️ Transformation Roadmap")
    
    # Roadmap overview
    st.markdown("""
    A structured approach to EKS modernization ensuring systematic migration with minimal risk.
    Each phase builds on the previous, with clear milestones and go/no-go decision points.
    """)
    
    # Phase selection
    phase_options = {
        "assessment_phase": "🔍 Assessment & Planning (4-6 weeks)",
        "foundation_phase": "🏗️ Foundation & Pilot (8-12 weeks)",
        "scale_out_phase": "📈 Scale-Out & Migration (3-9 months)",
        "optimization_phase": "🎯 Continuous Optimization (Ongoing)"
    }
    
    selected_phase = st.selectbox("Select Phase", options=list(phase_options.keys()),
                                   format_func=lambda x: phase_options[x])
    
    phase = TRANSFORMATION_ROADMAP[selected_phase]
    
    st.markdown(f"### {phase['icon']} {phase['name']}")
    st.markdown(f"**Duration:** {phase['duration']}")
    
    st.markdown("### 🎯 Objectives")
    for obj in phase['objectives']:
        st.markdown(f"• {obj}")
    
    # Phase-specific content
    if 'activities' in phase:
        st.markdown("### 📅 Weekly Activities")
        for week_key, week_data in phase['activities'].items():
            with st.expander(f"📍 {week_data['name']}"):
                st.markdown("**Tasks:**")
                for task in week_data['tasks']:
                    st.markdown(f"• {task}")
                st.markdown("**Deliverables:**")
                for deliverable in week_data['deliverables']:
                    st.markdown(f"✅ {deliverable}")
    
    if 'week_by_week' in phase:
        st.markdown("### 📅 Detailed Timeline")
        for week_key, week_data in phase['week_by_week'].items():
            with st.expander(f"📍 {week_key.replace('_', ' ').title()}: {week_data['focus']}"):
                st.markdown("**Tasks:**")
                for task in week_data['tasks']:
                    st.markdown(f"• {task}")
                st.markdown("**Success Criteria:**")
                for criteria in week_data['success_criteria']:
                    st.markdown(f"✅ {criteria}")
    
    if 'migration_waves' in phase:
        st.markdown("### 🌊 Migration Waves")
        for wave_key, wave_data in phase['migration_waves'].items():
            with st.expander(f"🌊 {wave_data.get('duration', 'Phase')}"):
                st.markdown(f"**Risk Level:** {wave_data.get('risk', 'N/A')}")
                st.markdown(f"**Objective:** {wave_data.get('objective', '')}")
                st.markdown(f"**Apps Count:** {wave_data.get('apps_count', 'N/A')}")
                st.markdown("**Selection Criteria:**")
                for criterion in wave_data.get('criteria', []):
                    st.markdown(f"• {criterion}")

# ============================================================================
# MAIN RENDERING FUNCTION
# ============================================================================

def render_eks_modernization_tab():
    """Main rendering function for EKS modernization"""
    st.title("🐳 EKS & Container Modernization")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎯 Challenges & Solutions",
        "🏗️ Reference Architectures",
        "🗺️ Transformation Roadmap",
        "📚 Implementation Guides"
    ])
    
    with tab1:
        render_challenges_assessment()
    
    with tab2:
        render_reference_architectures()
    
    with tab3:
        render_transformation_roadmap()
    
    with tab4:
        st.markdown("## 📚 Detailed Implementation Guides")
        st.info("Select a guide for step-by-step implementation instructions")
        
        guide_options = [
            "Karpenter Setup Guide",
            "ArgoCD GitOps Guide",
            "Multi-AZ HA Setup",
            "Spot Instance Strategy",
            "Istio Service Mesh"
        ]
        
        selected_guide = st.selectbox("Select Implementation Guide", guide_options)
        
        if selected_guide == "Karpenter Setup Guide":
            render_karpenter_guide()
        elif selected_guide == "ArgoCD GitOps Guide":
            render_argocd_guide()
        # Add other guides as needed

def render_karpenter_guide():
    """Karpenter implementation guide"""
    st.markdown("## ⚡ Karpenter Setup Guide")
    
    st.markdown("""
    ### Overview
    Karpenter is a flexible, high-performance Kubernetes cluster autoscaler that helps
    improve application availability and cluster efficiency by rapidly launching
    right-sized compute resources in response to changing application load.
    
    ### Prerequisites
    - EKS cluster version 1.27+
    - kubectl and Helm installed
    - AWS CLI configured
    """)
    
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

# Export
__all__ = ['render_eks_modernization_tab']