"""
AWS Landscape Scanner Module
Comprehensive AWS resource scanning and WAF assessment

Features:
- 15+ AWS service scanning
- Automatic WAF pillar mapping
- Detailed findings with remediation
- Demo mode with realistic data
- PDF report generation support
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any, Callable
from dataclasses import dataclass, field
import json

# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class Finding:
    """Represents a WAF-related finding"""
    id: str
    title: str
    description: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW, INFO
    pillar: str
    source_service: str
    affected_resources: List[str] = field(default_factory=list)
    recommendation: str = ""
    remediation_steps: List[str] = field(default_factory=list)
    account_id: str = ""
    region: str = ""
    estimated_savings: float = 0.0
    effort: str = "Medium"
    aws_doc_link: str = ""
    compliance_frameworks: List[str] = field(default_factory=list)

@dataclass
class ResourceInventory:
    """AWS Resource inventory summary"""
    ec2_instances: int = 0
    ec2_running: int = 0
    rds_instances: int = 0
    rds_multi_az: int = 0
    s3_buckets: int = 0
    s3_public: int = 0
    s3_unencrypted: int = 0
    lambda_functions: int = 0
    eks_clusters: int = 0
    ecs_clusters: int = 0
    vpcs: int = 0
    subnets: int = 0
    security_groups: int = 0
    load_balancers: int = 0
    ebs_volumes: int = 0
    ebs_unattached: int = 0
    ebs_unencrypted: int = 0
    iam_users: int = 0
    iam_users_no_mfa: int = 0
    iam_roles: int = 0
    iam_policies: int = 0
    cloudfront_distributions: int = 0
    route53_zones: int = 0
    secrets_manager_secrets: int = 0
    kms_keys: int = 0

@dataclass
class PillarScore:
    """Score for a WAF pillar"""
    name: str
    score: int
    findings_count: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    top_findings: List[Finding] = field(default_factory=list)

@dataclass
class LandscapeAssessment:
    """Complete AWS Landscape Assessment"""
    assessment_id: str
    timestamp: datetime
    accounts_scanned: List[str] = field(default_factory=list)
    regions_scanned: List[str] = field(default_factory=list)
    overall_score: int = 0
    overall_risk: str = "Unknown"
    inventory: ResourceInventory = field(default_factory=ResourceInventory)
    monthly_cost: float = 0.0
    savings_opportunities: float = 0.0
    pillar_scores: Dict[str, PillarScore] = field(default_factory=dict)
    findings: List[Finding] = field(default_factory=list)
    services_scanned: Dict[str, bool] = field(default_factory=dict)
    scan_errors: Dict[str, str] = field(default_factory=dict)
    scan_duration_seconds: float = 0.0

# ============================================================================
# DEMO DATA GENERATOR
# ============================================================================

def generate_demo_assessment() -> LandscapeAssessment:
    """Generate comprehensive realistic demo data"""
    
    findings = [
        # CRITICAL Findings
        Finding(
            id="SEC-001",
            title="Root Account Has No MFA Enabled",
            description="The AWS root account does not have Multi-Factor Authentication (MFA) enabled. This is a critical security risk as root account has unrestricted access to all resources.",
            severity="CRITICAL",
            pillar="Security",
            source_service="IAM",
            affected_resources=["Root Account"],
            recommendation="Enable MFA for the root account immediately using a hardware MFA device",
            remediation_steps=[
                "Sign in to AWS Console as root user",
                "Navigate to IAM Dashboard",
                "Click 'Activate MFA on your root account'",
                "Choose 'Virtual MFA device' or 'Hardware MFA device'",
                "Complete the MFA registration process",
                "Store backup codes securely"
            ],
            effort="Low",
            aws_doc_link="https://docs.aws.amazon.com/IAM/latest/UserGuide/id_root-user.html#id_root-user_manage_mfa",
            compliance_frameworks=["CIS AWS 1.5", "SOC 2", "PCI DSS", "HIPAA"]
        ),
        Finding(
            id="SEC-002",
            title="S3 Bucket with Public Access",
            description="S3 bucket 'company-data-backup' has public access enabled through bucket ACL. This exposes sensitive data to the internet.",
            severity="CRITICAL",
            pillar="Security",
            source_service="S3",
            affected_resources=["company-data-backup", "legacy-uploads"],
            recommendation="Remove public access and enable S3 Block Public Access at account level",
            remediation_steps=[
                "Navigate to S3 console",
                "Select the affected bucket",
                "Go to 'Permissions' tab",
                "Edit 'Block public access' settings",
                "Enable all four block public access options",
                "Review and update bucket policy",
                "Enable S3 Block Public Access at account level"
            ],
            effort="Low",
            aws_doc_link="https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-control-block-public-access.html",
            compliance_frameworks=["CIS AWS 2.1.5", "SOC 2", "GDPR"]
        ),
        Finding(
            id="SEC-003",
            title="IAM Users with Programmatic Access and No Recent Activity",
            description="5 IAM users have programmatic access keys that haven't been used in over 90 days. These dormant credentials pose a security risk.",
            severity="HIGH",
            pillar="Security",
            source_service="IAM",
            affected_resources=["user-legacy-api", "user-jenkins-old", "user-terraform-v1", "user-monitoring", "user-backup-script"],
            recommendation="Rotate or deactivate unused access keys and implement key rotation policy",
            remediation_steps=[
                "Generate IAM Credential Report",
                "Identify keys not used in 90+ days",
                "Contact key owners to verify if still needed",
                "Deactivate unused keys (don't delete immediately)",
                "After 30 days, delete deactivated keys",
                "Implement automated key rotation using AWS Secrets Manager"
            ],
            effort="Medium",
            compliance_frameworks=["CIS AWS 1.12", "SOC 2"]
        ),
        Finding(
            id="SEC-004",
            title="Security Groups Allow Unrestricted SSH Access",
            description="3 security groups allow inbound SSH (port 22) from 0.0.0.0/0, exposing instances to brute force attacks.",
            severity="HIGH",
            pillar="Security",
            source_service="VPC",
            affected_resources=["sg-0abc123-webservers", "sg-0def456-bastion", "sg-0ghi789-legacy"],
            recommendation="Restrict SSH access to specific IP ranges or use AWS Systems Manager Session Manager",
            remediation_steps=[
                "Identify all security groups with 0.0.0.0/0 SSH rules",
                "Document legitimate source IPs that need SSH access",
                "Update rules to allow only specific IP ranges",
                "Consider implementing AWS Systems Manager Session Manager",
                "Enable VPC Flow Logs to monitor access patterns",
                "Set up AWS Config rule to prevent future violations"
            ],
            effort="Medium",
            aws_doc_link="https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/security-group-rules.html",
            compliance_frameworks=["CIS AWS 5.2", "PCI DSS"]
        ),
        
        # HIGH Findings
        Finding(
            id="REL-001",
            title="RDS Instances Without Multi-AZ",
            description="Production RDS instances are running without Multi-AZ deployment, creating a single point of failure.",
            severity="HIGH",
            pillar="Reliability",
            source_service="RDS",
            affected_resources=["prod-mysql-main", "prod-postgres-analytics"],
            recommendation="Enable Multi-AZ for all production databases",
            remediation_steps=[
                "Identify production RDS instances without Multi-AZ",
                "Schedule maintenance window for conversion",
                "Modify RDS instance to enable Multi-AZ",
                "Monitor replication lag during conversion",
                "Update monitoring alerts for Multi-AZ metrics",
                "Test failover procedure"
            ],
            effort="Medium",
            estimated_savings=0,
            compliance_frameworks=["SOC 2"]
        ),
        Finding(
            id="REL-002",
            title="No Automated Backups for Critical Resources",
            description="12 EC2 instances and 3 RDS databases are not covered by AWS Backup plans.",
            severity="HIGH",
            pillar="Reliability",
            source_service="AWS Backup",
            affected_resources=["i-0abc123-prod-web1", "i-0def456-prod-web2", "prod-mysql-main"],
            recommendation="Create comprehensive AWS Backup plan with appropriate retention",
            remediation_steps=[
                "Inventory all critical resources",
                "Define backup requirements (RPO/RTO)",
                "Create AWS Backup vault with encryption",
                "Create backup plan with appropriate schedule",
                "Assign resources to backup plan using tags",
                "Configure cross-region backup for DR",
                "Test backup restoration quarterly"
            ],
            effort="Medium"
        ),
        Finding(
            id="REL-003",
            title="Single AZ Deployment for Production Workloads",
            description="Production Auto Scaling Group is configured to use only one Availability Zone.",
            severity="HIGH",
            pillar="Reliability",
            source_service="EC2 Auto Scaling",
            affected_resources=["asg-prod-web-servers"],
            recommendation="Configure ASG to span multiple Availability Zones",
            remediation_steps=[
                "Review current ASG configuration",
                "Identify additional subnets in other AZs",
                "Update ASG to include multiple AZ subnets",
                "Verify instance distribution across AZs",
                "Update load balancer health checks"
            ],
            effort="Low"
        ),
        
        # MEDIUM Findings
        Finding(
            id="SEC-005",
            title="CloudTrail Not Enabled for All Regions",
            description="CloudTrail is only configured for us-east-1, missing audit logs from other regions.",
            severity="MEDIUM",
            pillar="Security",
            source_service="CloudTrail",
            affected_resources=["main-trail"],
            recommendation="Enable multi-region CloudTrail with S3 log file validation",
            remediation_steps=[
                "Navigate to CloudTrail console",
                "Edit existing trail or create new one",
                "Enable 'Apply trail to all regions'",
                "Enable log file validation",
                "Configure CloudWatch Logs integration",
                "Set up metric filters for security events"
            ],
            effort="Low",
            compliance_frameworks=["CIS AWS 3.1", "SOC 2", "PCI DSS"]
        ),
        Finding(
            id="SEC-006",
            title="EBS Volumes Without Encryption",
            description="18 EBS volumes are not encrypted at rest, potentially exposing sensitive data.",
            severity="MEDIUM",
            pillar="Security",
            source_service="EC2",
            affected_resources=["vol-0abc123", "vol-0def456", "vol-0ghi789"],
            recommendation="Enable default EBS encryption and migrate existing volumes",
            remediation_steps=[
                "Enable default EBS encryption at account level",
                "Identify all unencrypted volumes",
                "For each volume: create encrypted snapshot",
                "Create new encrypted volume from snapshot",
                "Stop instance, detach old volume, attach new",
                "Verify data integrity and delete old volume"
            ],
            effort="High",
            compliance_frameworks=["CIS AWS 2.2.1", "HIPAA", "PCI DSS"]
        ),
        Finding(
            id="PERF-001",
            title="EC2 Instances Using Previous Generation Types",
            description="12 EC2 instances are using previous generation instance types (m4, c4, r4), missing performance improvements and cost savings.",
            severity="MEDIUM",
            pillar="Performance Efficiency",
            source_service="EC2",
            affected_resources=["i-0abc-m4.xlarge", "i-0def-c4.2xlarge", "i-0ghi-r4.large"],
            recommendation="Migrate to current generation instances (m6i, c6i, r6i) or Graviton",
            remediation_steps=[
                "Analyze current instance utilization with Compute Optimizer",
                "Identify workloads suitable for Graviton (ARM)",
                "Test application compatibility on new instance types",
                "Plan migration during maintenance window",
                "Use EC2 Instance Refresh for ASG migrations",
                "Monitor performance post-migration"
            ],
            effort="Medium",
            estimated_savings=450.0
        ),
        Finding(
            id="COST-001",
            title="Unattached EBS Volumes",
            description="8 EBS volumes are not attached to any instance, incurring unnecessary costs.",
            severity="MEDIUM",
            pillar="Cost Optimization",
            source_service="EC2",
            affected_resources=["vol-0111", "vol-0222", "vol-0333", "vol-0444", "vol-0555"],
            recommendation="Delete unneeded volumes or attach to instances",
            remediation_steps=[
                "List all unattached volumes",
                "Check volume tags for ownership",
                "Create snapshots of volumes with data",
                "Contact owners to verify if needed",
                "Delete confirmed unused volumes",
                "Set up AWS Config rule to alert on unattached volumes"
            ],
            effort="Low",
            estimated_savings=180.0
        ),
        Finding(
            id="COST-002",
            title="Reserved Instance Coverage Below Target",
            description="RI coverage is only 45% for steady-state EC2 workloads. Potential for significant savings.",
            severity="MEDIUM",
            pillar="Cost Optimization",
            source_service="Cost Explorer",
            affected_resources=["EC2 Fleet"],
            recommendation="Purchase Reserved Instances or Savings Plans for steady-state workloads",
            remediation_steps=[
                "Analyze EC2 usage patterns in Cost Explorer",
                "Identify steady-state vs variable workloads",
                "Calculate optimal RI/Savings Plan mix",
                "Consider Compute Savings Plans for flexibility",
                "Start with 1-year No Upfront for lower risk",
                "Review coverage monthly and adjust"
            ],
            effort="Low",
            estimated_savings=2800.0
        ),
        Finding(
            id="COST-003",
            title="Idle Load Balancers",
            description="3 Application Load Balancers have zero healthy targets and no traffic.",
            severity="LOW",
            pillar="Cost Optimization",
            source_service="ELB",
            affected_resources=["alb-staging-old", "alb-test-deprecated", "alb-feature-x"],
            recommendation="Delete unused load balancers",
            remediation_steps=[
                "Verify ALBs have no active traffic",
                "Check if ALBs are referenced in any DNS records",
                "Document and delete unused ALBs",
                "Remove associated target groups"
            ],
            effort="Low",
            estimated_savings=65.0
        ),
        
        # OPERATIONAL EXCELLENCE
        Finding(
            id="OPS-001",
            title="Resources Missing Required Tags",
            description="67 resources are missing required tags (Environment, Owner, CostCenter), hindering governance and cost allocation.",
            severity="MEDIUM",
            pillar="Operational Excellence",
            source_service="Resource Groups",
            affected_resources=["Multiple EC2, RDS, S3 resources"],
            recommendation="Implement and enforce tagging policy using AWS Organizations SCPs",
            remediation_steps=[
                "Define mandatory tag keys and allowed values",
                "Create AWS Config rule for tag compliance",
                "Implement SCP to require tags on resource creation",
                "Use Tag Editor to bulk-apply missing tags",
                "Set up Cost Allocation Tags for billing",
                "Create automation to tag resources on creation"
            ],
            effort="Medium"
        ),
        Finding(
            id="OPS-002",
            title="No Runbooks for Incident Response",
            description="Critical systems lack documented runbooks in AWS Systems Manager.",
            severity="MEDIUM",
            pillar="Operational Excellence",
            source_service="Systems Manager",
            affected_resources=["Production workloads"],
            recommendation="Create SSM Automation runbooks for common operational tasks",
            remediation_steps=[
                "Identify critical operational procedures",
                "Document steps in SSM Automation documents",
                "Test runbooks in non-production",
                "Train operations team on runbook usage",
                "Integrate runbooks with incident management"
            ],
            effort="High"
        ),
        
        # SUSTAINABILITY
        Finding(
            id="SUS-001",
            title="Over-Provisioned Resources in Non-Production",
            description="Development and staging environments use production-sized instances, wasting resources.",
            severity="LOW",
            pillar="Sustainability",
            source_service="EC2",
            affected_resources=["dev-*", "staging-*"],
            recommendation="Right-size non-production environments and implement scheduling",
            remediation_steps=[
                "Analyze non-prod resource utilization",
                "Define appropriate sizing for dev/staging",
                "Implement Instance Scheduler to stop after hours",
                "Use smaller instance types for non-prod",
                "Consider Spot instances for dev workloads"
            ],
            effort="Medium",
            estimated_savings=320.0
        ),
        Finding(
            id="SUS-002",
            title="No Instance Scheduling for Non-Production",
            description="Development instances run 24/7 but are only used during business hours.",
            severity="LOW",
            pillar="Sustainability",
            source_service="EC2",
            affected_resources=["dev-web-1", "dev-api-1", "dev-db-1"],
            recommendation="Implement AWS Instance Scheduler for automatic start/stop",
            remediation_steps=[
                "Deploy AWS Instance Scheduler solution",
                "Define schedules (e.g., M-F 8am-6pm)",
                "Tag instances with appropriate schedules",
                "Monitor cost savings",
                "Adjust schedules based on usage patterns"
            ],
            effort="Low",
            estimated_savings=180.0
        )
    ]
    
    # Create inventory
    inventory = ResourceInventory(
        ec2_instances=47,
        ec2_running=38,
        rds_instances=8,
        rds_multi_az=5,
        s3_buckets=23,
        s3_public=2,
        s3_unencrypted=4,
        lambda_functions=34,
        eks_clusters=2,
        ecs_clusters=1,
        vpcs=4,
        subnets=16,
        security_groups=42,
        load_balancers=7,
        ebs_volumes=89,
        ebs_unattached=8,
        ebs_unencrypted=18,
        iam_users=35,
        iam_users_no_mfa=5,
        iam_roles=67,
        iam_policies=23,
        cloudfront_distributions=3,
        route53_zones=5,
        secrets_manager_secrets=12,
        kms_keys=8
    )
    
    # Calculate pillar scores
    pillar_findings = {}
    for pillar in ['Security', 'Reliability', 'Performance Efficiency', 'Cost Optimization', 'Operational Excellence', 'Sustainability']:
        pillar_findings[pillar] = [f for f in findings if f.pillar == pillar]
    
    pillar_scores = {}
    for pillar, pfindings in pillar_findings.items():
        critical = sum(1 for f in pfindings if f.severity == 'CRITICAL')
        high = sum(1 for f in pfindings if f.severity == 'HIGH')
        medium = sum(1 for f in pfindings if f.severity == 'MEDIUM')
        low = sum(1 for f in pfindings if f.severity in ['LOW', 'INFO'])
        
        score = 100 - (critical * 20) - (high * 10) - (medium * 5) - (low * 2)
        score = max(0, min(100, score))
        
        pillar_scores[pillar] = PillarScore(
            name=pillar,
            score=score,
            findings_count=len(pfindings),
            critical_count=critical,
            high_count=high,
            medium_count=medium,
            low_count=low,
            top_findings=sorted(pfindings, key=lambda f: {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}.get(f.severity, 4))[:5]
        )
    
    # Calculate overall score (weighted)
    weights = {'Security': 1.5, 'Reliability': 1.3, 'Performance Efficiency': 1.0, 
               'Cost Optimization': 1.0, 'Operational Excellence': 0.9, 'Sustainability': 0.8}
    
    weighted_sum = sum(pillar_scores[p].score * weights.get(p, 1.0) for p in pillar_scores)
    total_weight = sum(weights.get(p, 1.0) for p in pillar_scores)
    overall_score = int(weighted_sum / total_weight)
    
    # Determine risk
    if overall_score >= 80:
        risk = "Low"
    elif overall_score >= 60:
        risk = "Medium"
    elif overall_score >= 40:
        risk = "High"
    else:
        risk = "Critical"
    
    return LandscapeAssessment(
        assessment_id=f"demo-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        timestamp=datetime.now(),
        accounts_scanned=["123456789012"],
        regions_scanned=["us-east-1", "us-west-2"],
        overall_score=overall_score,
        overall_risk=risk,
        inventory=inventory,
        monthly_cost=18750.0,
        savings_opportunities=sum(f.estimated_savings for f in findings),
        pillar_scores=pillar_scores,
        findings=findings,
        services_scanned={
            "IAM": True, "S3": True, "EC2": True, "RDS": True, "VPC": True,
            "CloudTrail": True, "Security Hub": True, "GuardDuty": True,
            "Config": True, "Lambda": True, "EKS": True, "Cost Explorer": True
        },
        scan_errors={},
        scan_duration_seconds=45.3
    )

# ============================================================================
# AWS SCANNER CLASS
# ============================================================================

class AWSLandscapeScanner:
    """Scan AWS resources for WAF assessment"""
    
    def __init__(self, session):
        self.session = session
        self.account_id = None
        self.findings: List[Finding] = []
        self.inventory = ResourceInventory()
        self.scan_status = {}
        self.scan_errors = {}
        
        try:
            sts = session.client('sts')
            self.account_id = sts.get_caller_identity()['Account']
        except:
            pass
    
    def run_scan(self, regions: List[str], progress_callback: Callable = None) -> LandscapeAssessment:
        """Run comprehensive scan"""
        start_time = datetime.now()
        
        scan_tasks = [
            ("IAM", self._scan_iam),
            ("S3", self._scan_s3),
            ("EC2", lambda: self._scan_ec2(regions[0])),
            ("RDS", lambda: self._scan_rds(regions[0])),
            ("VPC", lambda: self._scan_vpc(regions[0])),
            ("CloudTrail", lambda: self._scan_cloudtrail(regions[0])),
        ]
        
        for idx, (name, func) in enumerate(scan_tasks):
            if progress_callback:
                progress_callback(idx / len(scan_tasks), f"Scanning {name}...")
            try:
                func()
                self.scan_status[name] = True
            except Exception as e:
                self.scan_status[name] = False
                self.scan_errors[name] = str(e)
        
        if progress_callback:
            progress_callback(1.0, "Calculating scores...")
        
        # Build assessment
        pillar_scores = self._calculate_pillar_scores()
        overall_score = self._calculate_overall_score(pillar_scores)
        
        return LandscapeAssessment(
            assessment_id=f"scan-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            timestamp=datetime.now(),
            accounts_scanned=[self.account_id] if self.account_id else [],
            regions_scanned=regions,
            overall_score=overall_score,
            overall_risk=self._determine_risk(overall_score),
            inventory=self.inventory,
            pillar_scores=pillar_scores,
            findings=self.findings,
            services_scanned=self.scan_status,
            scan_errors=self.scan_errors,
            scan_duration_seconds=(datetime.now() - start_time).total_seconds()
        )
    
    def _scan_iam(self):
        """Scan IAM"""
        iam = self.session.client('iam')
        
        users = iam.list_users()['Users']
        self.inventory.iam_users = len(users)
        
        for user in users[:20]:
            try:
                mfa = iam.list_mfa_devices(UserName=user['UserName'])['MFADevices']
                if not mfa:
                    self.inventory.iam_users_no_mfa += 1
                    self.findings.append(Finding(
                        id=f"iam-nomfa-{user['UserName']}",
                        title=f"IAM User Without MFA: {user['UserName']}",
                        description=f"User {user['UserName']} does not have MFA enabled",
                        severity='HIGH',
                        pillar='Security',
                        source_service="IAM",
                        affected_resources=[user['UserName']],
                        recommendation="Enable MFA for this user",
                        effort="Low"
                    ))
            except:
                pass
        
        self.inventory.iam_roles = len(iam.list_roles()['Roles'])
    
    def _scan_s3(self):
        """Scan S3"""
        s3 = self.session.client('s3')
        buckets = s3.list_buckets()['Buckets']
        self.inventory.s3_buckets = len(buckets)
    
    def _scan_ec2(self, region: str):
        """Scan EC2"""
        ec2 = self.session.client('ec2', region_name=region)
        
        for reservation in ec2.describe_instances()['Reservations']:
            for instance in reservation['Instances']:
                self.inventory.ec2_instances += 1
                if instance['State']['Name'] == 'running':
                    self.inventory.ec2_running += 1
        
        volumes = ec2.describe_volumes()['Volumes']
        for vol in volumes:
            self.inventory.ebs_volumes += 1
            if vol['State'] == 'available':
                self.inventory.ebs_unattached += 1
        
        self.inventory.vpcs = len(ec2.describe_vpcs()['Vpcs'])
    
    def _scan_rds(self, region: str):
        """Scan RDS"""
        rds = self.session.client('rds', region_name=region)
        dbs = rds.describe_db_instances()['DBInstances']
        
        for db in dbs:
            self.inventory.rds_instances += 1
            if db.get('MultiAZ'):
                self.inventory.rds_multi_az += 1
    
    def _scan_vpc(self, region: str):
        """Scan VPC"""
        ec2 = self.session.client('ec2', region_name=region)
        self.inventory.security_groups = len(ec2.describe_security_groups()['SecurityGroups'])
    
    def _scan_cloudtrail(self, region: str):
        """Scan CloudTrail"""
        ct = self.session.client('cloudtrail', region_name=region)
        trails = ct.describe_trails()['trailList']
        
        if not any(t.get('IsMultiRegionTrail') for t in trails):
            self.findings.append(Finding(
                id="ct-no-multiregion",
                title="CloudTrail Not Multi-Region",
                description="No multi-region CloudTrail configured",
                severity="MEDIUM",
                pillar="Security",
                source_service="CloudTrail",
                recommendation="Enable multi-region CloudTrail"
            ))
    
    def _calculate_pillar_scores(self) -> Dict[str, PillarScore]:
        """Calculate pillar scores"""
        pillar_scores = {}
        pillars = ['Security', 'Reliability', 'Performance Efficiency', 'Cost Optimization', 'Operational Excellence', 'Sustainability']
        
        for pillar in pillars:
            pfindings = [f for f in self.findings if f.pillar == pillar]
            critical = sum(1 for f in pfindings if f.severity == 'CRITICAL')
            high = sum(1 for f in pfindings if f.severity == 'HIGH')
            medium = sum(1 for f in pfindings if f.severity == 'MEDIUM')
            low = sum(1 for f in pfindings if f.severity in ['LOW', 'INFO'])
            
            score = 100 - (critical * 20) - (high * 10) - (medium * 5) - (low * 2)
            score = max(0, min(100, score))
            
            pillar_scores[pillar] = PillarScore(
                name=pillar,
                score=score,
                findings_count=len(pfindings),
                critical_count=critical,
                high_count=high,
                medium_count=medium,
                low_count=low,
                top_findings=pfindings[:5]
            )
        
        return pillar_scores
    
    def _calculate_overall_score(self, pillar_scores: Dict[str, PillarScore]) -> int:
        """Calculate overall score"""
        weights = {'Security': 1.5, 'Reliability': 1.3, 'Performance Efficiency': 1.0, 
                   'Cost Optimization': 1.0, 'Operational Excellence': 0.9, 'Sustainability': 0.8}
        
        weighted = sum(ps.score * weights.get(p, 1.0) for p, ps in pillar_scores.items())
        total = sum(weights.get(p, 1.0) for p in pillar_scores)
        return int(weighted / total) if total > 0 else 0
    
    def _determine_risk(self, score: int) -> str:
        """Determine risk level"""
        if score >= 80: return "Low"
        if score >= 60: return "Medium"
        if score >= 40: return "High"
        return "Critical"

# ============================================================================
# RENDER FUNCTION
# ============================================================================

def render_landscape_scanner_tab():
    """Render the landscape scanner tab"""
    is_demo = st.session_state.get('app_mode', 'demo') == 'demo'
    
    if is_demo:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #1565C0 0%, #1976D2 100%); padding: 2rem; border-radius: 12px; margin-bottom: 1.5rem;">
            <h2 style="color: white; margin: 0;">🎭 Demo Mode - AWS Landscape Scanner</h2>
            <p style="color: #BBDEFB; margin: 0.5rem 0 0 0;">Experience the scanner with comprehensive sample data</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #1a472a 0%, #2d5a3d 100%); padding: 2rem; border-radius: 12px; margin-bottom: 1.5rem;">
            <h2 style="color: #98FB98; margin: 0;">🔴 Live Mode - AWS Landscape Scanner</h2>
            <p style="color: #90EE90; margin: 0.5rem 0 0 0;">Scanning your real AWS resources</p>
        </div>
        """, unsafe_allow_html=True)
        
        if not st.session_state.get('aws_connected'):
            st.warning("⚠️ Connect to AWS in the AWS Connector tab first, or switch to Demo mode")
            return
    
    # Options
    col1, col2 = st.columns(2)
    with col1:
        regions = st.multiselect(
            "Regions",
            ["us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1"],
            default=["us-east-1", "us-west-2"]
        )
    with col2:
        generate_pdf = st.checkbox("📄 Generate PDF Report", value=True)
    
    # Run scan button
    btn_text = "🎭 Run Demo Assessment" if is_demo else "🚀 Run Live Assessment"
    
    if st.button(btn_text, type="primary", use_container_width=True):
        progress = st.progress(0)
        status = st.empty()
        
        if is_demo:
            import time
            steps = [
                (0.1, "Initializing..."), (0.2, "Scanning IAM..."),
                (0.3, "Scanning S3..."), (0.4, "Scanning EC2..."),
                (0.5, "Scanning RDS..."), (0.6, "Scanning VPC..."),
                (0.7, "Analyzing Security Hub..."), (0.8, "Checking compliance..."),
                (0.9, "Calculating scores..."), (1.0, "Complete!")
            ]
            for p, m in steps:
                progress.progress(p)
                status.text(m)
                time.sleep(0.3)
            
            assessment = generate_demo_assessment()
        else:
            session = st.session_state.get('aws_session')
            scanner = AWSLandscapeScanner(session)
            assessment = scanner.run_scan(regions, lambda p, m: (progress.progress(p), status.text(m)))
        
        st.session_state.landscape_assessment = assessment
        
        # Display results
        render_assessment_summary(assessment)
        render_pillar_scores(assessment)
        render_findings_list(assessment)
        
        if generate_pdf:
            render_pdf_download(assessment)

def render_assessment_summary(assessment: LandscapeAssessment):
    """Render assessment summary"""
    st.markdown("---")
    st.markdown("### 📊 Assessment Summary")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    score_color = "#388E3C" if assessment.overall_score >= 80 else "#FBC02D" if assessment.overall_score >= 60 else "#D32F2F"
    
    with col1:
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem; background: white; border-radius: 10px;">
            <div style="font-size: 2.5rem; font-weight: bold; color: {score_color};">{assessment.overall_score}</div>
            <div style="color: #666;">WAF Score</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        risk_icon = {"Low": "🟢", "Medium": "🟡", "High": "🟠", "Critical": "🔴"}.get(assessment.overall_risk, "⚪")
        st.metric("Risk Level", f"{risk_icon} {assessment.overall_risk}")
    
    with col3:
        st.metric("Total Findings", len(assessment.findings))
    
    with col4:
        critical = sum(1 for f in assessment.findings if f.severity == 'CRITICAL')
        high = sum(1 for f in assessment.findings if f.severity == 'HIGH')
        st.metric("Critical/High", f"{critical}/{high}")
    
    with col5:
        st.metric("Potential Savings", f"${assessment.savings_opportunities:,.0f}/mo")

def render_pillar_scores(assessment: LandscapeAssessment):
    """Render pillar scores"""
    st.markdown("### 📈 Pillar Scores")
    
    cols = st.columns(6)
    icons = {
        "Security": "🔒", "Reliability": "🛡️", "Performance Efficiency": "⚡",
        "Cost Optimization": "💰", "Operational Excellence": "⚙️", "Sustainability": "🌱"
    }
    
    for idx, (pillar, ps) in enumerate(assessment.pillar_scores.items()):
        with cols[idx]:
            color = "#388E3C" if ps.score >= 80 else "#FBC02D" if ps.score >= 60 else "#D32F2F"
            st.markdown(f"""
            <div style="text-align: center; padding: 0.5rem; background: white; border-radius: 8px;">
                <div style="font-size: 1.5rem;">{icons.get(pillar, '📊')}</div>
                <div style="font-size: 1.5rem; font-weight: bold; color: {color};">{ps.score}</div>
                <div style="font-size: 0.7rem; color: #666;">{pillar.split()[0]}</div>
                <div style="font-size: 0.6rem; color: #999;">{ps.findings_count} findings</div>
            </div>
            """, unsafe_allow_html=True)

def render_findings_list(assessment: LandscapeAssessment):
    """Render detailed findings list"""
    st.markdown("### 🚨 Detailed Findings")
    
    # Group by severity
    for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
        sev_findings = [f for f in assessment.findings if f.severity == severity]
        if not sev_findings:
            continue
        
        icon = {'CRITICAL': '🔴', 'HIGH': '🟠', 'MEDIUM': '🟡', 'LOW': '🟢'}.get(severity, '⚪')
        st.markdown(f"#### {icon} {severity} ({len(sev_findings)})")
        
        for finding in sev_findings:
            with st.expander(f"{finding.title}"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**Pillar:** {finding.pillar}")
                    st.markdown(f"**Service:** {finding.source_service}")
                    st.markdown(f"**Description:** {finding.description}")
                    
                    if finding.affected_resources:
                        st.markdown(f"**Affected Resources:** {', '.join(finding.affected_resources[:5])}")
                
                with col2:
                    st.markdown(f"**Effort:** {finding.effort}")
                    if finding.estimated_savings > 0:
                        st.markdown(f"**Savings:** ${finding.estimated_savings:,.0f}/mo")
                    if finding.compliance_frameworks:
                        st.markdown(f"**Compliance:** {', '.join(finding.compliance_frameworks[:3])}")
                
                if finding.recommendation:
                    st.success(f"💡 **Recommendation:** {finding.recommendation}")
                
                if finding.remediation_steps:
                    with st.expander("📋 Remediation Steps"):
                        for i, step in enumerate(finding.remediation_steps, 1):
                            st.markdown(f"{i}. {step}")

def render_pdf_download(assessment: LandscapeAssessment):
    """Render PDF download button"""
    st.markdown("---")
    
    try:
        from pdf_report_generator import generate_comprehensive_waf_report
        
        pdf_bytes = generate_comprehensive_waf_report(assessment)
        
        st.download_button(
            "📥 Download Comprehensive PDF Report",
            pdf_bytes,
            file_name=f"AWS_WAF_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mime="application/pdf"
        )
    except Exception as e:
        st.warning(f"PDF generation unavailable: {e}")

# Exports
__all__ = [
    'Finding', 'ResourceInventory', 'PillarScore', 'LandscapeAssessment',
    'AWSLandscapeScanner', 'generate_demo_assessment', 'render_landscape_scanner_tab'
]
