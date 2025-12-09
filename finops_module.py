"""
FinOps Module - Enhanced with AWS-Specific Intelligence
Comprehensive Cloud Financial Management Platform

Features:
- AWS Cost Explorer integration and analysis
- Optimization recommendations with AI
- RI/Savings Plans advisor
- Waste detection and elimination
- FinOps maturity assessment
- Cost allocation and showback
- Real-time AWS cost tracking
- Carbon footprint analysis
- Anomaly detection and alerting
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

# ============================================================================
# AWS COST OPTIMIZATION FRAMEWORK
# ============================================================================

AWS_COST_CATEGORIES = {
    "compute": {
        "name": "Compute",
        "icon": "💻",
        "services": ["EC2", "Lambda", "ECS", "EKS", "Fargate", "Lightsail", "Batch"],
        "typical_percentage": 45,
        "optimization_potential": "20-40%",
        "aws_tools": ["AWS Compute Optimizer", "Cost Explorer", "Trusted Advisor"],
        "key_metrics": [
            "vCPU utilization",
            "Memory utilization",
            "Network throughput",
            "Storage IOPS"
        ]
    },
    "storage": {
        "name": "Storage",
        "icon": "💾",
        "services": ["S3", "EBS", "EFS", "FSx", "Glacier", "Storage Gateway", "Backup"],
        "typical_percentage": 15,
        "optimization_potential": "15-30%",
        "aws_tools": ["S3 Storage Class Analysis", "EBS Volume Analyzer", "Storage Lens"],
        "key_metrics": [
            "Storage utilization",
            "Access patterns",
            "Data transfer costs",
            "Snapshot costs"
        ]
    },
    "database": {
        "name": "Database",
        "icon": "🗄️",
        "services": ["RDS", "DynamoDB", "ElastiCache", "Redshift", "Neptune", "DocumentDB", "MemoryDB"],
        "typical_percentage": 20,
        "optimization_potential": "15-25%",
        "aws_tools": ["RDS Performance Insights", "DynamoDB Auto Scaling", "Redshift Advisor"],
        "key_metrics": [
            "Connection count",
            "Query performance",
            "Storage growth",
            "Read/Write capacity units"
        ]
    },
    "network": {
        "name": "Network & Content Delivery",
        "icon": "🌐",
        "services": ["Data Transfer", "CloudFront", "Route53", "VPC", "Direct Connect", "Global Accelerator", "Transit Gateway"],
        "typical_percentage": 10,
        "optimization_potential": "10-25%",
        "aws_tools": ["VPC Flow Logs", "Cost Explorer (Data Transfer)", "CloudFront Reports"],
        "key_metrics": [
            "Inter-AZ data transfer",
            "Inter-region data transfer",
            "Internet egress",
            "VPC endpoint usage"
        ]
    },
    "other": {
        "name": "Other Services",
        "icon": "📦",
        "services": ["Support", "Marketplace", "KMS", "Secrets Manager", "CloudWatch", "SNS", "SQS"],
        "typical_percentage": 10,
        "optimization_potential": "5-15%",
        "aws_tools": ["Cost Explorer", "AWS Cost Optimization Hub"],
        "key_metrics": [
            "API call volume",
            "Log retention",
            "Alarm count",
            "Secret rotation frequency"
        ]
    }
}

# ============================================================================
# AWS-SPECIFIC OPTIMIZATION STRATEGIES
# ============================================================================

AWS_OPTIMIZATION_STRATEGIES = [
    {
        "name": "Reserved Instances (EC2/RDS)",
        "category": "Commitment Discounts",
        "savings_potential": "30-72%",
        "effort": "Low",
        "risk": "Medium",
        "description": "Commit to 1 or 3 year terms for predictable workloads",
        "aws_service_coverage": ["EC2", "RDS", "ElastiCache", "Redshift", "OpenSearch"],
        "best_for": [
            "Steady-state production workloads",
            "Databases running 24/7",
            "Always-on applications",
            "Baseline capacity requirements"
        ],
        "implementation": [
            "Navigate to Cost Explorer > Reserved Instances > Recommendations",
            "Analyze 30-60 day usage patterns",
            "Identify instances running consistently (>80% time)",
            "Start with 1-year No Upfront for lower commitment",
            "Consider Convertible RIs for instance type flexibility",
            "Purchase RIs matching your usage pattern",
            "Monitor RI utilization in Cost Explorer (target >90%)"
        ],
        "aws_tools": [
            "Cost Explorer RI Recommendations",
            "AWS Cost Optimization Hub",
            "Trusted Advisor RI Optimization Checks"
        ],
        "gotchas": [
            "Regional RIs don't apply to zonal reservations",
            "Size flexibility only within instance family",
            "Convertible RIs have slightly lower discounts",
            "Unused RIs still incur charges"
        ],
        "monitoring": [
            "RI Coverage (% of usage covered)",
            "RI Utilization (% of purchased capacity used)",
            "Expiration dates and renewal planning",
            "Savings realized vs baseline"
        ]
    },
    {
        "name": "Savings Plans",
        "category": "Commitment Discounts",
        "savings_potential": "20-72%",
        "effort": "Low",
        "risk": "Low",
        "description": "Flexible commitment discount for compute usage across services",
        "aws_service_coverage": ["EC2", "Fargate", "Lambda", "SageMaker"],
        "types": {
            "compute_savings_plans": {
                "discount": "Up to 66%",
                "flexibility": "Highest - any region, instance family, size, OS, tenancy",
                "use_case": "Maximum flexibility for dynamic workloads"
            },
            "ec2_instance_savings_plans": {
                "discount": "Up to 72%",
                "flexibility": "Medium - within instance family in specific region",
                "use_case": "Predictable EC2 usage patterns"
            },
            "sagemaker_savings_plans": {
                "discount": "Up to 64%",
                "flexibility": "SageMaker specific",
                "use_case": "ML workloads"
            }
        },
        "implementation": [
            "Go to Cost Management > Savings Plans > Recommendations",
            "Choose Compute Savings Plans for maximum flexibility",
            "Review lookback period (7, 30, or 60 days)",
            "Start with 1-year No Upfront commitment",
            "Cover 60-70% of baseline usage (not 100%)",
            "Stack with RIs for additional savings",
            "Monitor coverage and adjust quarterly"
        ],
        "aws_tools": [
            "Savings Plans Recommendations",
            "Cost Explorer Savings Plans utilization report",
            "AWS Cost Optimization Hub"
        ],
        "best_practices": [
            "Start conservative - you can always add more",
            "Combine with Spot for variable load",
            "Use Compute SP for multi-service coverage",
            "Review recommendations monthly"
        ]
    },
    {
        "name": "Spot Instances",
        "category": "Alternative Pricing",
        "savings_potential": "60-90%",
        "effort": "Medium",
        "risk": "Medium",
        "description": "Use spare AWS capacity at steep discounts with interruption handling",
        "best_for": [
            "Fault-tolerant workloads",
            "Batch processing and ETL",
            "CI/CD pipelines",
            "Container workloads (EKS with Karpenter)",
            "Dev/Test environments",
            "Big data analytics"
        ],
        "aws_implementation_options": {
            "ec2_spot_fleets": {
                "description": "Maintain target capacity across Spot and On-Demand",
                "configuration": "Define instance types, AZs, and allocation strategy",
                "use_case": "General purpose Spot usage"
            },
            "auto_scaling_groups": {
                "description": "Mix Spot and On-Demand in ASGs",
                "configuration": "Set base On-Demand, use Spot for scale-out",
                "use_case": "Web applications with variable load"
            },
            "eks_karpenter": {
                "description": "Intelligent Kubernetes node provisioning",
                "configuration": "Karpenter automatically manages Spot diversification",
                "use_case": "Container workloads on EKS"
            },
            "batch_compute_environments": {
                "description": "AWS Batch managed Spot",
                "configuration": "Batch handles interruptions and retries",
                "use_case": "Batch processing workloads"
            }
        },
        "implementation": [
            "Identify fault-tolerant workloads via architecture review",
            "Use Spot Instance Advisor to check interruption rates",
            "Configure diversification (8-10 instance types minimum)",
            "Implement capacity-optimized or price-capacity-optimized allocation",
            "Set up 2-minute interruption notice handling",
            "Use EC2 Instance Rebalance Recommendations",
            "Test failure scenarios before production",
            "Monitor Spot interruption rates and savings"
        ],
        "aws_tools": [
            "Spot Instance Advisor",
            "EC2 Fleet",
            "Auto Scaling Groups with mixed instances",
            "Karpenter for EKS",
            "AWS Batch"
        ],
        "interruption_handling": {
            "warning_time": "2 minutes",
            "best_practices": [
                "Checkpoint work frequently",
                "Implement graceful shutdown",
                "Use multiple instance types and AZs",
                "Set up CloudWatch alarms for interruptions",
                "Use EC2 Instance Metadata Service for warnings"
            ]
        }
    },
    {
        "name": "Right-Sizing",
        "category": "Resource Optimization",
        "savings_potential": "10-40%",
        "effort": "Medium",
        "risk": "Low",
        "description": "Match instance sizes and types to actual workload requirements",
        "aws_tools_integration": {
            "compute_optimizer": {
                "features": [
                    "ML-powered recommendations",
                    "Historical utilization analysis",
                    "Performance risk assessment",
                    "Cost savings projections"
                ],
                "metrics_analyzed": [
                    "CPU utilization (14-day history)",
                    "Memory utilization (CloudWatch agent required)",
                    "Network in/out",
                    "EBS throughput and IOPS"
                ]
            },
            "cost_explorer": {
                "features": [
                    "Resource-level cost analysis",
                    "Utilization heat maps",
                    "Rightsizing recommendations"
                ]
            },
            "cloudwatch": {
                "features": [
                    "Real-time metrics",
                    "Custom metrics",
                    "Anomaly detection",
                    "Performance baselines"
                ]
            }
        },
        "implementation": [
            "Enable AWS Compute Optimizer (free service)",
            "Install CloudWatch agent for memory metrics",
            "Wait 14 days for sufficient data collection",
            "Review Compute Optimizer recommendations weekly",
            "Start with clearly over-provisioned instances (< 40% utilization)",
            "Test in non-production first",
            "Implement during maintenance windows",
            "Monitor performance for 7 days post-change",
            "Document baseline performance metrics"
        ],
        "decision_framework": {
            "downsize": "Sustained < 40% CPU + low memory",
            "upsize": "Frequent > 80% CPU or memory pressure",
            "change_family": "Workload characteristics changed (compute vs memory intensive)",
            "leave_as_is": "Right-sized or performance-critical with margin"
        },
        "best_practices": [
            "Establish performance baselines before changes",
            "Right-size in waves, not all at once",
            "Consider burstable instances (T-series) for variable workloads",
            "Use Auto Scaling for dynamic workloads instead of oversizing",
            "Review recommendations monthly, implement quarterly"
        ]
    },
    {
        "name": "Graviton Migration",
        "category": "Architecture Optimization",
        "savings_potential": "20-40%",
        "effort": "Medium",
        "risk": "Low",
        "description": "Move to ARM-based AWS Graviton processors for better price-performance",
        "graviton_benefits": {
            "cost_savings": "Up to 40% lower cost than comparable x86 instances",
            "performance": "Up to 40% better price-performance",
            "efficiency": "Up to 60% better energy efficiency",
            "services": ["EC2", "RDS", "EKS", "Lambda", "ECS"]
        },
        "compatibility": {
            "best_for": [
                "Linux-based workloads",
                "Open source software (nginx, MySQL, PostgreSQL)",
                "Containerized applications",
                "Java, Python, Go, Node.js applications",
                "Managed services (RDS, ElastiCache)"
            ],
            "requires_testing": [
                "Applications with compiled binaries",
                "Third-party software dependencies",
                "Legacy applications"
            ],
            "not_compatible": [
                "Windows workloads",
                "x86-only commercial software",
                "Applications requiring specific CPU features"
            ]
        },
        "implementation": [
            "Inventory current x86 EC2 instances",
            "Identify compatible Linux workloads",
            "Test application on Graviton in dev/test (t4g, m6g instances)",
            "Recompile code if needed (usually not required for interpreted languages)",
            "Update container images to multi-arch (amd64 + arm64)",
            "Migrate RDS databases to Graviton",
            "Update Lambda functions to arm64",
            "Monitor performance and costs",
            "Gradually roll out to production"
        ],
        "aws_graviton_instance_families": {
            "general_purpose": ["t4g", "m6g", "m6gd", "m7g"],
            "compute_optimized": ["c6g", "c6gd", "c6gn", "c7g"],
            "memory_optimized": ["r6g", "r6gd", "r7g", "x2gd"],
            "storage_optimized": ["im4gn", "is4gen"],
            "accelerated_computing": ["g5g"]
        }
    },
    {
        "name": "S3 Intelligent-Tiering & Lifecycle",
        "category": "Storage Optimization",
        "savings_potential": "20-95%",
        "effort": "Low",
        "risk": "Low",
        "description": "Automatically move S3 objects to cost-effective storage classes",
        "s3_storage_classes": {
            "s3_standard": {
                "cost": "$0.023/GB",
                "use_case": "Frequently accessed data",
                "retrieval": "Instant, no fees"
            },
            "s3_intelligent_tiering": {
                "cost": "$0.023/GB → $0.0125/GB (auto)",
                "use_case": "Unpredictable access patterns",
                "retrieval": "Instant, no fees",
                "monitoring_fee": "$0.0025 per 1000 objects"
            },
            "s3_standard_ia": {
                "cost": "$0.0125/GB",
                "use_case": "Infrequent access (< 1/month)",
                "retrieval": "$0.01/GB + per request fees",
                "minimum": "30 days, 128KB per object"
            },
            "s3_one_zone_ia": {
                "cost": "$0.01/GB",
                "use_case": "Infrequent, non-critical data",
                "retrieval": "$0.01/GB",
                "durability": "99.999999999% in single AZ"
            },
            "glacier_instant_retrieval": {
                "cost": "$0.004/GB",
                "use_case": "Archive with instant access",
                "retrieval": "$0.03/GB",
                "minimum": "90 days"
            },
            "glacier_flexible_retrieval": {
                "cost": "$0.0036/GB",
                "use_case": "Archive (mins-hours retrieval)",
                "retrieval": "Expedited/Standard/Bulk pricing",
                "minimum": "90 days"
            },
            "glacier_deep_archive": {
                "cost": "$0.00099/GB",
                "use_case": "Long-term archive (12hr retrieval)",
                "retrieval": "$0.02/GB",
                "minimum": "180 days"
            }
        },
        "implementation_strategy": {
            "intelligent_tiering": [
                "Enable S3 Intelligent-Tiering for buckets with unpredictable access",
                "Configure Archive Access tier (90 days)",
                "Configure Deep Archive Access tier (180 days)",
                "No lifecycle rules needed - fully automated"
            ],
            "lifecycle_policies": [
                "Analyze access patterns with S3 Storage Class Analysis",
                "Create lifecycle rules based on object age",
                "Transition to IA after 30 days",
                "Transition to Glacier after 90 days",
                "Transition to Deep Archive after 365 days",
                "Delete after retention period"
            ]
        },
        "aws_tools": [
            "S3 Storage Class Analysis",
            "S3 Storage Lens",
            "S3 Intelligent-Tiering",
            "S3 Lifecycle policies"
        ],
        "best_practices": [
            "Use Intelligent-Tiering for unknown patterns",
            "Enable Storage Class Analysis for 30 days before creating rules",
            "Consider retrieval costs in total cost calculation",
            "Use lifecycle rules for predictable patterns",
            "Monitor with S3 Storage Lens dashboards"
        ]
    },
    {
        "name": "Idle Resource Elimination",
        "category": "Waste Reduction",
        "savings_potential": "5-20%",
        "effort": "Low",
        "risk": "Low",
        "description": "Identify and remove unused AWS resources",
        "common_waste_areas": {
            "unattached_ebs": {
                "description": "EBS volumes not attached to instances",
                "typical_cost": "$50-500/month per account",
                "detection": "AWS Config rule: ec2-volume-inuse-check",
                "action": "Snapshot and delete after 7-day grace period"
            },
            "unused_elastic_ips": {
                "description": "EIPs not associated with running instances",
                "typical_cost": "$3.65/month per IP",
                "detection": "Cost Explorer or custom script",
                "action": "Release unused EIPs immediately"
            },
            "idle_load_balancers": {
                "description": "ALB/NLB with no traffic",
                "typical_cost": "$16-43/month per LB",
                "detection": "CloudWatch metrics: RequestCount, TargetConnectionCount",
                "action": "Delete LBs with < 100 requests/day"
            },
            "old_snapshots": {
                "description": "EBS snapshots beyond retention period",
                "typical_cost": "$0.05/GB-month",
                "detection": "Custom Lambda or AWS Backup lifecycle",
                "action": "Implement snapshot lifecycle policy"
            },
            "stopped_instances": {
                "description": "EC2 instances stopped long-term",
                "typical_cost": "EBS storage costs continue",
                "detection": "AWS Cost Explorer, Trusted Advisor",
                "action": "Convert to AMI and terminate, or restart"
            },
            "unused_nat_gateways": {
                "description": "NAT Gateways in unused VPCs",
                "typical_cost": "$32/month per NAT Gateway",
                "detection": "CloudWatch metrics: BytesOutToDestination",
                "action": "Delete unused NAT Gateways"
            },
            "orphaned_resources": {
                "description": "Resources from deleted stacks/apps",
                "typical_cost": "Varies",
                "detection": "Tag-based inventory, CloudFormation drift",
                "action": "Implement resource tagging policy"
            }
        },
        "implementation": [
            "Enable AWS Config for automated detection",
            "Set up Trusted Advisor checks",
            "Create CloudWatch dashboards for idle resources",
            "Implement tagging strategy (Owner, Environment, CostCenter)",
            "Schedule monthly waste cleanup reviews",
            "Automate cleanup with Lambda functions",
            "Set up SNS notifications for long-running resources"
        ],
        "aws_tools": [
            "AWS Trusted Advisor",
            "AWS Cost Explorer",
            "AWS Config Rules",
            "Cost Optimization Hub",
            "CloudWatch Metrics",
            "AWS Systems Manager Inventory"
        ],
        "automation_examples": {
            "lambda_ebs_cleanup": "Automated EBS volume cleanup after 7 days unattached",
            "lambda_snapshot_mgmt": "Delete snapshots older than retention policy",
            "eventbridge_unused_rds": "Alert on RDS instances with no connections for 7 days",
            "systems_manager_automation": "Stop non-production instances on schedule"
        }
    },
    {
        "name": "Instance Scheduler",
        "category": "Waste Reduction",
        "savings_potential": "40-70%",
        "effort": "Low",
        "risk": "Low",
        "description": "Automatically stop/start non-production resources on schedule",
        "use_cases": [
            "Dev/Test environments (nights and weekends)",
            "Demo and training systems",
            "Internal tools with business hours usage",
            "Batch processing windows"
        ],
        "aws_solution": {
            "name": "AWS Instance Scheduler",
            "deployment": "CloudFormation template",
            "features": [
                "Centralized scheduling across accounts",
                "Configurable time zones",
                "Holiday scheduling",
                "DynamoDB-based configuration",
                "SNS notifications",
                "Supports EC2, RDS, Auto Scaling Groups"
            ]
        },
        "implementation": [
            "Deploy Instance Scheduler CloudFormation stack",
            "Define schedules (e.g., office-hours: M-F 8am-6pm)",
            "Tag resources with Schedule tag",
            "Configure timezone appropriately",
            "Test with small subset before full rollout",
            "Set up CloudWatch alarms for scheduler failures",
            "Create override mechanism for exceptions",
            "Monitor savings in Cost Explorer"
        ],
        "example_schedules": {
            "office_hours": {
                "description": "Monday-Friday 8am-6pm",
                "savings": "65% reduction (113 hours/week savings)"
            },
            "business_hours": {
                "description": "Monday-Friday 7am-7pm",
                "savings": "55% reduction (108 hours/week savings)"
            },
            "weekdays_only": {
                "description": "Monday-Friday 24 hours, off weekends",
                "savings": "29% reduction (48 hours/week savings)"
            },
            "batch_window": {
                "description": "Daily 2am-6am only",
                "savings": "83% reduction (140 hours/week savings)"
            }
        },
        "alternatives": [
            "AWS Systems Manager (simpler, EC2 only)",
            "EventBridge + Lambda (custom solution)",
            "Third-party tools (CloudHealth, Spot.io)"
        ],
        "best_practices": [
            "Start with dev/test, not production",
            "Use SSM Parameter Store for scheduler configuration",
            "Implement tagging standards",
            "Create exceptions for always-on resources",
            "Monitor scheduler execution logs",
            "Communicate schedule to development teams"
        ]
    },
    {
        "name": "AWS Cost Optimization Hub",
        "category": "Centralized Optimization",
        "savings_potential": "15-30%",
        "effort": "Low",
        "risk": "Low",
        "description": "Centralized AWS service for discovering and tracking all cost optimization opportunities",
        "features": [
            "Aggregates recommendations from 8+ AWS services",
            "Unified dashboard for all cost optimization opportunities",
            "Prioritization by estimated savings",
            "Tracking of implemented recommendations",
            "Custom recommendation filters",
            "Multi-account support via Organizations"
        ],
        "included_recommendations": {
            "compute_optimizer": "EC2, Lambda, EBS, ECS on Fargate",
            "cost_explorer": "RDS idle instances, underutilized EC2",
            "s3_storage_lens": "S3 storage optimization",
            "redshift_advisor": "Redshift cluster optimization",
            "trusted_advisor": "Various best practice checks",
            "savings_plans": "Commitment discount opportunities"
        },
        "implementation": [
            "Navigate to Cost Management console",
            "Access Cost Optimization Hub",
            "Review estimated annual savings",
            "Filter by service, account, or savings amount",
            "Export recommendations for team review",
            "Mark recommendations as implemented",
            "Track savings realized over time",
            "Schedule monthly review meetings"
        ],
        "advantages": [
            "Free service - no additional cost",
            "Single pane of glass for all optimizations",
            "Automatic recommendation updates",
            "Integration with AWS Organizations",
            "Savings tracking and reporting"
        ]
    }
]

# ============================================================================
# AWS COST EXPLORER INTEGRATION
# ============================================================================

class AWSCostExplorerIntegration:
    """Real AWS Cost Explorer integration for live cost data"""
    
    @staticmethod
    def get_monthly_costs(session: Optional[boto3.Session] = None, months: int = 6) -> Dict:
        """Fetch actual monthly costs from AWS Cost Explorer"""
        try:
            if session is None:
                session = boto3.Session()
            
            ce_client = session.client('ce', region_name='us-east-1')
            
            end_date = datetime.now().date()
            start_date = (end_date - timedelta(days=30 * months))
            
            response = ce_client.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date.isoformat(),
                    'End': end_date.isoformat()
                },
                Granularity='MONTHLY',
                Metrics=['UnblendedCost', 'UsageQuantity'],
                GroupBy=[
                    {'Type': 'DIMENSION', 'Key': 'SERVICE'}
                ]
            )
            
            # Process and structure the data
            monthly_data = {}
            for result in response['ResultsByTime']:
                month = result['TimePeriod']['Start'][:7]  # YYYY-MM
                monthly_data[month] = {
                    'services': {},
                    'total': 0
                }
                
                for group in result['Groups']:
                    service = group['Keys'][0]
                    cost = float(group['Metrics']['UnblendedCost']['Amount'])
                    monthly_data[month]['services'][service] = cost
                    monthly_data[month]['total'] += cost
            
            return {
                'success': True,
                'data': monthly_data,
                'currency': 'USD'
            }
            
        except (ClientError, NoCredentialsError) as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Unable to fetch AWS cost data. Ensure Cost Explorer is enabled and credentials are configured.'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'An unexpected error occurred while fetching cost data.'
            }
    
    @staticmethod
    def get_service_breakdown(session: Optional[boto3.Session] = None, days: int = 30) -> Dict:
        """Get cost breakdown by AWS service for the last N days"""
        try:
            if session is None:
                session = boto3.Session()
            
            ce_client = session.client('ce', region_name='us-east-1')
            
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days)
            
            response = ce_client.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date.isoformat(),
                    'End': end_date.isoformat()
                },
                Granularity='MONTHLY',
                Metrics=['UnblendedCost'],
                GroupBy=[
                    {'Type': 'DIMENSION', 'Key': 'SERVICE'}
                ]
            )
            
            service_costs = {}
            for result in response['ResultsByTime']:
                for group in result['Groups']:
                    service = group['Keys'][0]
                    amount = float(group['Metrics']['UnblendedCost']['Amount'])
                    service_costs[service] = service_costs.get(service, 0) + amount
            
            # Sort by cost descending
            sorted_services = dict(sorted(service_costs.items(), key=lambda x: x[1], reverse=True))
            
            return {
                'success': True,
                'services': sorted_services,
                'total': sum(sorted_services.values()),
                'period': f'Last {days} days'
            }
            
        except (ClientError, NoCredentialsError) as e:
            return {
                'success': False,
                'error': str(e)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def get_cost_forecast(session: Optional[boto3.Session] = None, days: int = 30) -> Dict:
        """Get AWS cost forecast"""
        try:
            if session is None:
                session = boto3.Session()
            
            ce_client = session.client('ce', region_name='us-east-1')
            
            start_date = datetime.now().date()
            end_date = start_date + timedelta(days=days)
            
            response = ce_client.get_cost_forecast(
                TimePeriod={
                    'Start': start_date.isoformat(),
                    'End': end_date.isoformat()
                },
                Metric='UNBLENDED_COST',
                Granularity='MONTHLY'
            )
            
            forecast = float(response['Total']['Amount'])
            
            return {
                'success': True,
                'forecast': forecast,
                'period': f'Next {days} days',
                'currency': 'USD'
            }
            
        except (ClientError, NoCredentialsError) as e:
            return {
                'success': False,
                'error': str(e)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def get_ri_coverage(session: Optional[boto3.Session] = None) -> Dict:
        """Get Reserved Instance coverage metrics"""
        try:
            if session is None:
                session = boto3.Session()
            
            ce_client = session.client('ce', region_name='us-east-1')
            
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=30)
            
            response = ce_client.get_reservation_coverage(
                TimePeriod={
                    'Start': start_date.isoformat(),
                    'End': end_date.isoformat()
                },
                Granularity='MONTHLY'
            )
            
            if response['CoveragesByTime']:
                coverage_data = response['CoveragesByTime'][0]['Total']
                coverage_pct = float(coverage_data.get('CoverageHours', {}).get('CoverageHoursPercentage', 0))
                on_demand_cost = float(coverage_data.get('OnDemandCost', 0))
                
                return {
                    'success': True,
                    'coverage_percentage': coverage_pct,
                    'on_demand_cost': on_demand_cost,
                    'message': f"{coverage_pct:.1f}% of usage covered by RIs/Savings Plans"
                }
            
            return {
                'success': False,
                'error': 'No coverage data available'
            }
            
        except (ClientError, NoCredentialsError) as e:
            return {
                'success': False,
                'error': str(e)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

# ============================================================================
# AWS CARBON FOOTPRINT DATA
# ============================================================================

AWS_CARBON_INTENSITY = {
    # gCO2eq per kWh by AWS region
    "us-east-1": {"name": "US East (N. Virginia)", "carbon_intensity": 415, "rating": "Medium"},
    "us-east-2": {"name": "US East (Ohio)", "carbon_intensity": 480, "rating": "Medium"},
    "us-west-1": {"name": "US West (N. California)", "carbon_intensity": 280, "rating": "Low"},
    "us-west-2": {"name": "US West (Oregon)", "carbon_intensity": 185, "rating": "Low"},
    "ca-central-1": {"name": "Canada (Central)", "carbon_intensity": 150, "rating": "Low"},
    "eu-west-1": {"name": "EU (Ireland)", "carbon_intensity": 320, "rating": "Medium"},
    "eu-west-2": {"name": "EU (London)", "carbon_intensity": 280, "rating": "Low"},
    "eu-west-3": {"name": "EU (Paris)", "carbon_intensity": 60, "rating": "Low"},
    "eu-central-1": {"name": "EU (Frankfurt)", "carbon_intensity": 380, "rating": "Medium"},
    "eu-north-1": {"name": "EU (Stockholm)", "carbon_intensity": 15, "rating": "Low"},
    "ap-northeast-1": {"name": "Asia Pacific (Tokyo)", "carbon_intensity": 480, "rating": "Medium"},
    "ap-northeast-2": {"name": "Asia Pacific (Seoul)", "carbon_intensity": 420, "rating": "Medium"},
    "ap-southeast-1": {"name": "Asia Pacific (Singapore)", "carbon_intensity": 520, "rating": "High"},
    "ap-southeast-2": {"name": "Asia Pacific (Sydney)", "carbon_intensity": 780, "rating": "High"},
    "ap-south-1": {"name": "Asia Pacific (Mumbai)", "carbon_intensity": 710, "rating": "High"},
    "sa-east-1": {"name": "South America (São Paulo)", "carbon_intensity": 85, "rating": "Low"}
}

# ============================================================================
# RENDERING FUNCTIONS
# ============================================================================

def render_finops_tab():
    """Main FinOps tab rendering function"""
    st.title("💰 AWS FinOps - Cloud Financial Management")
    
    # Top-level tabs
    main_tabs = st.tabs([
        "📊 Cost Dashboard",
        "🎯 Optimization Strategies",
        "🔍 Waste Detection",
        "💳 Commitment Discounts",
        "🌱 Sustainability",
        "📈 Forecasting"
    ])
    
    with main_tabs[0]:
        render_cost_dashboard()
    
    with main_tabs[1]:
        render_optimization_strategies()
    
    with main_tabs[2]:
        render_waste_detection()
    
    with main_tabs[3]:
        render_commitment_discounts()
    
    with main_tabs[4]:
        render_sustainability()
    
    with main_tabs[5]:
        render_forecasting()

def render_cost_dashboard():
    """Render AWS cost dashboard"""
    st.markdown("## 📊 AWS Cost Dashboard")
    
    st.info("💡 Connect your AWS account to see real-time cost data from Cost Explorer")
    
    # Connection status
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔌 Connect AWS Account", use_container_width=True):
            st.info("Configure AWS credentials in the Account Management section")
    
    # Try to fetch real data
    try:
        cost_data = AWSCostExplorerIntegration.get_monthly_costs()
        
        if cost_data.get('success'):
            st.success("✅ Successfully connected to AWS Cost Explorer")
            
            # Display cost breakdown
            monthly_data = cost_data['data']
            
            # Top services chart
            st.markdown("### 💰 Top AWS Services by Cost")
            # Implementation continues with real data...
            render_real_cost_data(monthly_data)
        else:
            st.warning("⚠️ Using demo data. Connect AWS for real-time insights.")
            render_demo_cost_data()
            
    except Exception as e:
        # Handle any AWS credential or connection errors
        st.warning("⚠️ AWS credentials not configured. Showing demo data.")
        st.caption("To see real data, configure AWS credentials in Streamlit secrets or environment variables")
        render_demo_cost_data()

def render_optimization_strategies():
    """Render AWS optimization strategies"""
    st.markdown("## 🎯 AWS Cost Optimization Strategies")
    
    st.markdown("""
    Comprehensive strategies to optimize your AWS costs across all services.
    Each strategy includes implementation steps, AWS tools, and expected savings.
    """)
    
    # Strategy selector
    selected_strategy = st.selectbox(
        "Select Optimization Strategy",
        options=range(len(AWS_OPTIMIZATION_STRATEGIES)),
        format_func=lambda x: f"{AWS_OPTIMIZATION_STRATEGIES[x]['name']} - {AWS_OPTIMIZATION_STRATEGIES[x]['savings_potential']} savings"
    )
    
    strategy = AWS_OPTIMIZATION_STRATEGIES[selected_strategy]
    
    # Display strategy details
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Savings Potential", strategy['savings_potential'])
    with col2:
        st.metric("Implementation Effort", strategy['effort'])
    with col3:
        st.metric("Risk Level", strategy['risk'])
    
    st.markdown(f"### {strategy['name']}")
    st.markdown(f"**Category:** {strategy['category']}")
    st.markdown(f"**Description:** {strategy['description']}")
    
    # Implementation steps
    with st.expander("📋 Implementation Steps", expanded=True):
        for i, step in enumerate(strategy['implementation'], 1):
            st.markdown(f"{i}. {step}")
    
    # AWS Tools
    if 'aws_tools' in strategy:
        with st.expander("🛠️ AWS Tools & Services"):
            for tool in strategy['aws_tools']:
                st.markdown(f"• {tool}")
    
    # Best practices
    if 'best_practices' in strategy:
        with st.expander("✅ Best Practices"):
            for practice in strategy['best_practices']:
                st.markdown(f"• {practice}")

def render_waste_detection():
    """Render waste detection and cleanup"""
    st.markdown("## 🔍 AWS Waste Detection")
    st.info("Identify and eliminate wasted spend across your AWS environment")
    
    # Waste categories
    waste_strategy = next(s for s in AWS_OPTIMIZATION_STRATEGIES if s['name'] == 'Idle Resource Elimination')
    
    st.markdown("### 🗑️ Common Waste Areas")
    
    for waste_key, waste_data in waste_strategy['common_waste_areas'].items():
        with st.expander(f"💰 {waste_data['description']} - ~{waste_data['typical_cost']}"):
            st.markdown(f"**Detection Method:** {waste_data['detection']}")
            st.markdown(f"**Recommended Action:** {waste_data['action']}")

def render_commitment_discounts():
    """Render RI and Savings Plans advisor"""
    st.markdown("## 💳 Commitment Discounts (RIs & Savings Plans)")
    
    st.markdown("""
    AWS offers significant discounts (up to 72%) through Reserved Instances and Savings Plans.
    Choose the right commitment strategy for your workload patterns.
    """)
    
    # Comparison table
    commitment_comparison = {
        "Feature": [
            "Discount",
            "Flexibility",
            "Commitment",
            "Instance Changes",
            "Region Changes",
            "Service Coverage",
            "Best For"
        ],
        "Reserved Instances": [
            "Up to 72%",
            "Low-Medium",
            "1 or 3 years",
            "Limited (size flex in family)",
            "No (Regional RIs)",
            "EC2, RDS, ElastiCache, etc.",
            "Predictable, steady workloads"
        ],
        "Compute Savings Plans": [
            "Up to 66%",
            "High",
            "1 or 3 years",
            "Yes (any instance type)",
            "Yes (any region)",
            "EC2, Fargate, Lambda",
            "Dynamic, multi-service workloads"
        ],
        "EC2 Instance Savings Plans": [
            "Up to 72%",
            "Medium",
            "1 or 3 years",
            "Yes (within family)",
            "No (specific region)",
            "EC2 only",
            "Predictable EC2 usage patterns"
        ]
    }
    
    import pandas as pd
    st.dataframe(pd.DataFrame(commitment_comparison), use_container_width=True)

def render_sustainability():
    """Render AWS sustainability and carbon tracking"""
    st.markdown("## 🌱 AWS Sustainability & Carbon Footprint")
    
    st.info("Track and optimize your AWS carbon footprint using AWS Customer Carbon Footprint Tool")
    
    st.markdown("### 🌍 AWS Region Carbon Intensity")
    st.markdown("Choose regions with lower carbon intensity for sustainability")
    
    # Display region carbon data
    import pandas as pd
    region_df = pd.DataFrame([
        {
            "Region": data['name'],
            "Carbon Intensity": f"{data['carbon_intensity']} gCO2eq/kWh",
            "Rating": f"{'🟢' if data['rating'] == 'Low' else '🟡' if data['rating'] == 'Medium' else '🔴'} {data['rating']}"
        }
        for region, data in AWS_CARBON_INTENSITY.items()
    ]).sort_values("Carbon Intensity")
    
    st.dataframe(region_df, use_container_width=True)
    
    st.markdown("### 💡 Sustainability Best Practices")
    st.markdown("""
    - **Use low-carbon regions** - Deploy in regions with renewable energy (EU North, CA Central)
    - **Optimize utilization** - Higher utilization = better energy efficiency
    - **Use Graviton instances** - 60% better energy efficiency than comparable x86 instances
    - **Implement auto-scaling** - Scale down during low demand periods
    - **Use managed services** - AWS operates at higher efficiency than self-managed
    - **Archive old data** - Move to Glacier Deep Archive for lower energy consumption
    """)

def render_forecasting():
    """Render AWS cost forecasting"""
    st.markdown("## 📈 AWS Cost Forecasting")
    
    st.info("View AWS cost forecasts and trends to plan your cloud budget")
    
    forecast_data = AWSCostExplorerIntegration.get_cost_forecast()
    
    if forecast_data['success']:
        st.success(f"**Forecasted Cost ({forecast_data['period']}):** ${forecast_data['forecast']:,.2f}")
    else:
        st.warning("Connect AWS to see real forecasts")

def render_real_cost_data(monthly_data):
    """Render real AWS cost data from Cost Explorer"""
    import pandas as pd
    import plotly.express as px
    
    # Extract latest month data
    latest_month = max(monthly_data.keys())
    services = monthly_data[latest_month]['services']
    total = monthly_data[latest_month]['total']
    
    # Top metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Current Month Cost", f"${total:,.2f}")
    with col2:
        # Calculate month-over-month change
        months = sorted(monthly_data.keys())
        if len(months) >= 2:
            prev_month = months[-2]
            prev_total = monthly_data[prev_month]['total']
            change = ((total - prev_total) / prev_total * 100) if prev_total > 0 else 0
            st.metric("Month-over-Month", f"{change:+.1f}%")
    with col3:
        # Top service
        top_service = max(services.items(), key=lambda x: x[1])
        st.metric("Top Service", f"{top_service[0]}: ${top_service[1]:,.2f}")
    
    # Services breakdown chart
    df = pd.DataFrame(list(services.items()), columns=['Service', 'Cost'])
    df = df.sort_values('Cost', ascending=False).head(10)
    
    fig = px.bar(df, x='Service', y='Cost', title='Top 10 AWS Services by Cost')
    st.plotly_chart(fig, use_container_width=True)
    
    # Cost trend over time
    trend_data = []
    for month in sorted(monthly_data.keys()):
        trend_data.append({
            'Month': month,
            'Total Cost': monthly_data[month]['total']
        })
    
    trend_df = pd.DataFrame(trend_data)
    fig2 = px.line(trend_df, x='Month', y='Total Cost', title='Cost Trend Over Time', markers=True)
    st.plotly_chart(fig2, use_container_width=True)

def render_demo_cost_data():
    """Render demo cost data when AWS is not connected"""
    import pandas as pd
    import plotly.express as px
    
    st.markdown("### 💰 Demo Cost Data")
    st.markdown("*This is sample data. Connect your AWS account for real insights.*")
    
    # Demo metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Monthly Cost", "$4,280", delta="+12%")
    with col2:
        st.metric("Top Service", "EC2: $1,250")
    with col3:
        st.metric("Savings Opportunity", "$1,200", delta="-28%")
    
    # Demo services
    demo_services = {
        "EC2": 1250,
        "RDS": 680,
        "S3": 420,
        "Data Transfer": 310,
        "Lambda": 180,
        "EKS": 150,
        "CloudWatch": 90,
        "VPC": 85,
        "EBS": 75,
        "Route 53": 40
    }
    
    df = pd.DataFrame(list(demo_services.items()), columns=['Service', 'Cost'])
    df = df.sort_values('Cost', ascending=False)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        fig = px.bar(df, x='Service', y='Cost', title='Monthly Cost by Service (Demo Data)',
                     color='Cost', color_continuous_scale='Blues')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Demo trend
    st.markdown("### 📈 Cost Trend (Demo)")
    trend_data = pd.DataFrame({
        'Month': ['Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
        'Cost': [3800, 3950, 4100, 4280, 4450]
    })
    fig2 = px.line(trend_data, x='Month', y='Cost', title='6-Month Cost Trend', markers=True)
    st.plotly_chart(fig2, use_container_width=True)
    
    st.info("💡 Configure AWS credentials to see your actual cost data and get personalized recommendations")


# Export main function
__all__ = ['render_finops_tab']
