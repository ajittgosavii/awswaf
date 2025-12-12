"""
Multi-Account WAF PDF Report Generator
Generate comprehensive PDF reports for single and multi-account AWS assessments

Features:
- Executive summary with multi-account overview
- Per-account detailed analysis
- Aggregated findings across accounts
- Cross-account security analysis
- Compliance framework mapping
- Cost optimization recommendations
- Visual charts and graphs
- Professional AWS branding
"""

from io import BytesIO
from datetime import datetime
from typing import Dict, List, Any, Optional
from collections import defaultdict

# ============================================================================
# MULTI-ACCOUNT PDF REPORT GENERATOR
# ============================================================================

def generate_multiaccount_waf_report(
    assessments: List[Dict],
    accounts_config: List[Dict],
    report_type: str = "comprehensive"
) -> bytes:
    """
    Generate comprehensive multi-account PDF report
    
    Args:
        assessments: List of assessment results, one per account
        accounts_config: List of account configurations
        report_type: 'executive', 'comprehensive', or 'technical'
    
    Returns:
        PDF file as bytes
    """
    
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
            PageBreak, HRFlowable, ListFlowable, ListItem, KeepTogether
        )
        from reportlab.graphics.shapes import Drawing
        from reportlab.graphics.charts.piecharts import Pie
        from reportlab.graphics.charts.barcharts import VerticalBarChart, HorizontalBarChart
        from reportlab.graphics.charts.legends import Legend
    except ImportError:
        raise ImportError("reportlab is required for PDF generation")
    
    buffer = BytesIO()
    
    # Document setup
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=1*inch,
        bottomMargin=0.75*inch,
        title="AWS Multi-Account Well-Architected Framework Assessment",
        author="AWS WAF Advisor",
        subject="Multi-Account Assessment Report"
    )
    
    # Initialize story (content)
    story = []
    
    # Custom styles
    styles = _create_custom_styles()
    
    # Aggregate data across accounts
    aggregated_data = _aggregate_assessment_data(assessments, accounts_config)
    
    # Build report based on type
    if report_type == "executive":
        story = _build_executive_report(story, styles, aggregated_data, accounts_config)
    elif report_type == "technical":
        story = _build_technical_report(story, styles, aggregated_data, accounts_config, assessments)
    else:  # comprehensive
        story = _build_comprehensive_report(story, styles, aggregated_data, accounts_config, assessments)
    
    # Build PDF
    doc.build(story)
    
    # Return PDF bytes
    buffer.seek(0)
    return buffer.getvalue()


def _create_custom_styles():
    """Create custom paragraph styles for the report"""
    styles = getSampleStyleSheet()
    
    # AWS Brand Colors
    AWS_ORANGE = colors.HexColor('#FF9900')
    AWS_DARK_BLUE = colors.HexColor('#232F3E')
    AWS_LIGHT_BLUE = colors.HexColor('#37475A')
    AWS_SQUID_INK = colors.HexColor('#161E2D')
    
    # Main Title
    styles.add(ParagraphStyle(
        name='AWSTitleStyle',
        parent=styles['Title'],
        fontSize=28,
        textColor=AWS_DARK_BLUE,
        spaceAfter=10,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    ))
    
    # Subtitle
    styles.add(ParagraphStyle(
        name='AWSSubTitle',
        parent=styles['Normal'],
        fontSize=16,
        textColor=AWS_ORANGE,
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica'
    ))
    
    # Section Header
    styles.add(ParagraphStyle(
        name='AWSSectionHeader',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=AWS_DARK_BLUE,
        spaceBefore=25,
        spaceAfter=15,
        fontName='Helvetica-Bold',
        borderWidth=2,
        borderColor=AWS_ORANGE,
        borderPadding=8
    ))
    
    # Subsection
    styles.add(ParagraphStyle(
        name='AWSSubSection',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=AWS_LIGHT_BLUE,
        spaceBefore=15,
        spaceAfter=10,
        fontName='Helvetica-Bold'
    ))
    
    # Body Text
    styles.add(ParagraphStyle(
        name='AWSBody',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_JUSTIFY,
        spaceAfter=8,
        leading=14
    ))
    
    # Finding Critical
    styles.add(ParagraphStyle(
        name='FindingCritical',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#DC2626'),
        fontName='Helvetica-Bold',
        spaceAfter=6
    ))
    
    # Finding High
    styles.add(ParagraphStyle(
        name='FindingHigh',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#EA580C'),
        fontName='Helvetica-Bold',
        spaceAfter=6
    ))
    
    # Finding Medium
    styles.add(ParagraphStyle(
        name='FindingMedium',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#F59E0B'),
        fontName='Helvetica-Bold',
        spaceAfter=6
    ))
    
    # Account Name
    styles.add(ParagraphStyle(
        name='AccountName',
        parent=styles['Normal'],
        fontSize=12,
        textColor=AWS_DARK_BLUE,
        fontName='Helvetica-Bold',
        spaceAfter=8,
        leftIndent=20
    ))
    
    return styles


def _aggregate_assessment_data(assessments: List[Dict], accounts_config: List[Dict]) -> Dict:
    """Aggregate data from multiple account assessments"""
    
    aggregated = {
        'total_accounts': len(assessments),
        'total_regions': 0,
        'total_resources': 0,
        'findings_by_severity': defaultdict(int),
        'findings_by_pillar': defaultdict(int),
        'compliance_status': defaultdict(int),
        'accounts_summary': [],
        'all_findings': [],
        'top_risks': [],
        'cost_optimization_total': 0,
        'security_score_avg': 0,
        'by_environment': defaultdict(lambda: {
            'count': 0,
            'resources': 0,
            'findings': 0
        })
    }
    
    security_scores = []
    
    for i, assessment in enumerate(assessments):
        account_config = accounts_config[i] if i < len(accounts_config) else {}
        
        # Basic metrics
        regions = assessment.get('regions_scanned', [])
        aggregated['total_regions'] += len(regions) if isinstance(regions, list) else 1
        
        resources = assessment.get('resources', {})
        resource_count = sum(len(v) if isinstance(v, list) else 0 for v in resources.values())
        aggregated['total_resources'] += resource_count
        
        # Findings by severity
        findings = assessment.get('findings', [])
        for finding in findings:
            severity = finding.get('severity', 'medium').lower()
            aggregated['findings_by_severity'][severity] += 1
            
            pillar = finding.get('pillar', 'operational_excellence')
            aggregated['findings_by_pillar'][pillar] += 1
            
            # Add to all findings with account context
            finding_with_context = finding.copy()
            finding_with_context['account_name'] = account_config.get('account_name', f'Account {i+1}')
            finding_with_context['account_id'] = account_config.get('account_id', 'unknown')
            aggregated['all_findings'].append(finding_with_context)
        
        # Compliance
        compliance = assessment.get('compliance', {})
        for framework, status in compliance.items():
            aggregated['compliance_status'][framework] = aggregated['compliance_status'].get(framework, 0) + (1 if status == 'compliant' else 0)
        
        # Security score
        pillar_scores = assessment.get('pillar_scores', {})
        security_score = pillar_scores.get('security', {}).get('score', 0)
        security_scores.append(security_score)
        
        # Cost optimization
        cost_savings = assessment.get('cost_optimization', {}).get('potential_savings', 0)
        aggregated['cost_optimization_total'] += cost_savings
        
        # Environment grouping
        environment = account_config.get('environment', 'unknown')
        aggregated['by_environment'][environment]['count'] += 1
        aggregated['by_environment'][environment]['resources'] += resource_count
        aggregated['by_environment'][environment]['findings'] += len(findings)
        
        # Account summary
        aggregated['accounts_summary'].append({
            'name': account_config.get('account_name', f'Account {i+1}'),
            'id': account_config.get('account_id', 'unknown'),
            'environment': environment,
            'regions': len(regions) if isinstance(regions, list) else 1,
            'resources': resource_count,
            'findings': len(findings),
            'critical_findings': sum(1 for f in findings if f.get('severity', '').lower() == 'critical'),
            'security_score': security_score
        })
    
    # Calculate averages
    aggregated['security_score_avg'] = sum(security_scores) / len(security_scores) if security_scores else 0
    
    # Identify top risks (critical and high severity findings)
    top_risks = sorted(
        [f for f in aggregated['all_findings'] if f.get('severity', '').lower() in ['critical', 'high']],
        key=lambda x: (0 if x.get('severity', '').lower() == 'critical' else 1, x.get('account_name', ''))
    )[:10]
    aggregated['top_risks'] = top_risks
    
    return aggregated


def _build_comprehensive_report(story, styles, data, accounts_config, assessments):
    """Build comprehensive multi-account report"""
    
    # Cover Page
    story.extend(_create_cover_page(styles, data))
    story.append(PageBreak())
    
    # Table of Contents
    story.extend(_create_table_of_contents(styles))
    story.append(PageBreak())
    
    # Executive Summary
    story.extend(_create_executive_summary(styles, data))
    story.append(PageBreak())
    
    # Multi-Account Overview
    story.extend(_create_multiaccount_overview(styles, data))
    story.append(PageBreak())
    
    # Security Posture
    story.extend(_create_security_posture_section(styles, data))
    story.append(PageBreak())
    
    # Findings Summary
    story.extend(_create_findings_summary(styles, data))
    story.append(PageBreak())
    
    # Per-Account Detailed Analysis
    for i, assessment in enumerate(assessments):
        account_config = accounts_config[i] if i < len(accounts_config) else {}
        story.extend(_create_account_detailed_section(styles, assessment, account_config))
        story.append(PageBreak())
    
    # Cross-Account Security Analysis
    story.extend(_create_cross_account_analysis(styles, data))
    story.append(PageBreak())
    
    # Compliance Summary
    story.extend(_create_compliance_section(styles, data))
    story.append(PageBreak())
    
    # Remediation Roadmap
    story.extend(_create_remediation_roadmap(styles, data))
    story.append(PageBreak())
    
    # Appendix
    story.extend(_create_appendix(styles, data))
    
    return story


def _build_executive_report(story, styles, data, accounts_config):
    """Build executive summary report (shorter, high-level)"""
    
    # Cover Page
    story.extend(_create_cover_page(styles, data))
    story.append(PageBreak())
    
    # Executive Summary
    story.extend(_create_executive_summary(styles, data))
    story.append(PageBreak())
    
    # Key Metrics
    story.extend(_create_key_metrics_section(styles, data))
    story.append(PageBreak())
    
    # Top Risks
    story.extend(_create_top_risks_section(styles, data))
    story.append(PageBreak())
    
    # Strategic Recommendations
    story.extend(_create_strategic_recommendations(styles, data))
    
    return story


def _build_technical_report(story, styles, data, accounts_config, assessments):
    """Build technical detailed report"""
    
    # Cover Page
    story.extend(_create_cover_page(styles, data))
    story.append(PageBreak())
    
    # Technical Overview
    story.append(Paragraph("Technical Assessment Report", styles['AWSTitleStyle']))
    story.append(Spacer(1, 20))
    
    # Detailed findings for each account
    for i, assessment in enumerate(assessments):
        account_config = accounts_config[i] if i < len(accounts_config) else {}
        story.extend(_create_technical_account_section(styles, assessment, account_config))
        story.append(PageBreak())
    
    # Resource inventory
    story.extend(_create_resource_inventory_section(styles, assessments, accounts_config))
    
    return story


# ============================================================================
# SECTION BUILDERS
# ============================================================================

def _create_cover_page(styles, data):
    """Create cover page"""
    from reportlab.lib import colors
    
    content = []
    
    # Logo/Title area
    content.append(Spacer(1, 2*inch))
    content.append(Paragraph("AWS Well-Architected", styles['AWSTitleStyle']))
    content.append(Paragraph("Framework Assessment", styles['AWSTitleStyle']))
    content.append(Spacer(1, 0.5*inch))
    content.append(Paragraph("Multi-Account Security & Compliance Report", styles['AWSSubTitle']))
    content.append(Spacer(1, 1.5*inch))
    
    # Key metrics box
    from reportlab.platypus import Table, TableStyle
    
    metrics_data = [
        ['', ''],
        ['Assessment Date:', datetime.now().strftime('%B %d, %Y')],
        ['Total Accounts:', str(data['total_accounts'])],
        ['Total Regions:', str(data['total_regions'])],
        ['Resources Assessed:', f"{data['total_resources']:,}"],
        ['Security Score:', f"{data['security_score_avg']:.1f}/100"],
        ['', '']
    ]
    
    metrics_table = Table(metrics_data, colWidths=[2.5*inch, 2.5*inch])
    metrics_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (0, -2), 'Helvetica-Bold'),
        ('FONTNAME', (1, 1), (1, -2), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -2), 12),
        ('TEXTCOLOR', (0, 1), (0, -2), colors.HexColor('#232F3E')),
        ('TEXTCOLOR', (1, 1), (1, -2), colors.HexColor('#FF9900')),
        ('BOX', (0, 1), (-1, -2), 2, colors.HexColor('#FF9900')),
        ('INNERGRID', (0, 1), (-1, -2), 0.5, colors.HexColor('#CCCCCC')),
        ('TOPPADDING', (0, 1), (-1, -2), 10),
        ('BOTTOMPADDING', (0, 1), (-1, -2), 10),
    ]))
    
    content.append(metrics_table)
    content.append(Spacer(1, 1*inch))
    
    # Confidentiality notice
    content.append(Paragraph(
        "CONFIDENTIAL - For Internal Use Only",
        styles['AWSBody']
    ))
    
    return content


def _create_table_of_contents(styles):
    """Create table of contents"""
    content = []
    
    content.append(Paragraph("Table of Contents", styles['AWSSectionHeader']))
    content.append(Spacer(1, 20))
    
    toc_items = [
        "1. Executive Summary",
        "2. Multi-Account Overview",
        "3. Security Posture Analysis",
        "4. Findings Summary",
        "5. Per-Account Detailed Analysis",
        "6. Cross-Account Security Analysis",
        "7. Compliance Framework Assessment",
        "8. Remediation Roadmap",
        "9. Appendix"
    ]
    
    for item in toc_items:
        content.append(Paragraph(item, styles['AWSBody']))
        content.append(Spacer(1, 10))
    
    return content


def _create_executive_summary(styles, data):
    """Create executive summary section"""
    from reportlab.lib import colors
    from reportlab.platypus import Table, TableStyle
    
    content = []
    
    content.append(Paragraph("Executive Summary", styles['AWSSectionHeader']))
    content.append(Spacer(1, 15))
    
    # Overview paragraph
    summary_text = f"""This comprehensive assessment evaluated {data['total_accounts']} AWS accounts across 
    {data['total_regions']} regions, analyzing {data['total_resources']:,} cloud resources against AWS Well-Architected 
    Framework best practices. The assessment identified {sum(data['findings_by_severity'].values())} findings across 
    all accounts, with {data['findings_by_severity'].get('critical', 0)} critical and 
    {data['findings_by_severity'].get('high', 0)} high-severity issues requiring immediate attention."""
    
    content.append(Paragraph(summary_text, styles['AWSBody']))
    content.append(Spacer(1, 20))
    
    # Key findings table
    content.append(Paragraph("Key Assessment Metrics", styles['AWSSubSection']))
    content.append(Spacer(1, 10))
    
    findings_data = [
        ['Metric', 'Count', 'Status'],
        ['Total Accounts Assessed', str(data['total_accounts']), '✓'],
        ['Regions Covered', str(data['total_regions']), '✓'],
        ['Resources Analyzed', f"{data['total_resources']:,}", '✓'],
        ['Critical Findings', str(data['findings_by_severity'].get('critical', 0)), 
         '⚠' if data['findings_by_severity'].get('critical', 0) > 0 else '✓'],
        ['High Priority Findings', str(data['findings_by_severity'].get('high', 0)),
         '⚠' if data['findings_by_severity'].get('high', 0) > 0 else '✓'],
        ['Average Security Score', f"{data['security_score_avg']:.1f}/100",
         '✓' if data['security_score_avg'] >= 70 else '⚠'],
        ['Estimated Cost Savings', f"${data['cost_optimization_total']:,.0f}/month", '✓']
    ]
    
    findings_table = Table(findings_data, colWidths=[3*inch, 1.5*inch, 1*inch])
    findings_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#232F3E')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('ALIGN', (2, 0), (2, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F7F7F7')]),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    content.append(findings_table)
    content.append(Spacer(1, 20))
    
    # Strategic insights
    content.append(Paragraph("Strategic Insights", styles['AWSSubSection']))
    content.append(Spacer(1, 10))
    
    insights = []
    
    if data['findings_by_severity'].get('critical', 0) > 0:
        insights.append(f"• Immediate attention required: {data['findings_by_severity']['critical']} critical security findings identified across accounts")
    
    if data['security_score_avg'] < 70:
        insights.append(f"• Security posture needs improvement: Current average score is {data['security_score_avg']:.1f}/100")
    else:
        insights.append(f"• Strong security posture: Average security score of {data['security_score_avg']:.1f}/100 across all accounts")
    
    if data['cost_optimization_total'] > 10000:
        insights.append(f"• Significant cost optimization opportunity: ${data['cost_optimization_total']:,.0f}/month in potential savings identified")
    
    insights.append(f"• Multi-account complexity: {data['total_accounts']} accounts require coordinated security governance")
    
    for insight in insights:
        content.append(Paragraph(insight, styles['AWSBody']))
    
    content.append(Spacer(1, 20))
    
    # Recommendations
    content.append(Paragraph("Executive Recommendations", styles['AWSSubSection']))
    content.append(Spacer(1, 10))
    
    recommendations = [
        "1. Prioritize remediation of all critical findings within 30 days",
        "2. Implement centralized security monitoring across all accounts",
        "3. Establish consistent tagging and resource management policies",
        "4. Review and optimize underutilized resources for cost savings",
        "5. Enhance compliance frameworks implementation across accounts"
    ]
    
    for rec in recommendations:
        content.append(Paragraph(rec, styles['AWSBody']))
        content.append(Spacer(1, 5))
    
    return content


def _create_multiaccount_overview(styles, data):
    """Create multi-account overview section"""
    from reportlab.lib import colors
    from reportlab.platypus import Table, TableStyle
    
    content = []
    
    content.append(Paragraph("Multi-Account Overview", styles['AWSSectionHeader']))
    content.append(Spacer(1, 15))
    
    # Environment breakdown
    content.append(Paragraph("Account Distribution by Environment", styles['AWSSubSection']))
    content.append(Spacer(1, 10))
    
    env_data = [['Environment', 'Accounts', 'Resources', 'Findings']]
    for env, stats in data['by_environment'].items():
        env_data.append([
            env.capitalize(),
            str(stats['count']),
            f"{stats['resources']:,}",
            str(stats['findings'])
        ])
    
    # Add totals row
    env_data.append([
        'Total',
        str(data['total_accounts']),
        f"{data['total_resources']:,}",
        str(sum(data['findings_by_severity'].values()))
    ])
    
    env_table = Table(env_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
    env_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#232F3E')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#F7F7F7')]),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#FFE5CC')),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    content.append(env_table)
    content.append(Spacer(1, 25))
    
    # Per-account summary
    content.append(Paragraph("Per-Account Summary", styles['AWSSubSection']))
    content.append(Spacer(1, 10))
    
    account_data = [['Account', 'Environment', 'Regions', 'Resources', 'Findings', 'Critical', 'Score']]
    for acc in data['accounts_summary']:
        account_data.append([
            acc['name'][:25],  # Truncate long names
            acc['environment'][:10],
            str(acc['regions']),
            str(acc['resources']),
            str(acc['findings']),
            str(acc['critical_findings']),
            f"{acc['security_score']:.0f}"
        ])
    
    account_table = Table(account_data, colWidths=[1.8*inch, 1*inch, 0.7*inch, 0.9*inch, 0.8*inch, 0.7*inch, 0.6*inch])
    account_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#232F3E')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F7F7F7')]),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    content.append(account_table)
    
    return content


def _create_security_posture_section(styles, data):
    """Create security posture analysis section"""
    from reportlab.lib import colors
    from reportlab.platypus import Table, TableStyle
    
    content = []
    
    content.append(Paragraph("Security Posture Analysis", styles['AWSSectionHeader']))
    content.append(Spacer(1, 15))
    
    # Security score analysis
    content.append(Paragraph("Security Score Distribution", styles['AWSSubSection']))
    content.append(Spacer(1, 10))
    
    # Categorize accounts by security score
    excellent = sum(1 for acc in data['accounts_summary'] if acc['security_score'] >= 90)
    good = sum(1 for acc in data['accounts_summary'] if 70 <= acc['security_score'] < 90)
    needs_improvement = sum(1 for acc in data['accounts_summary'] if 50 <= acc['security_score'] < 70)
    critical = sum(1 for acc in data['accounts_summary'] if acc['security_score'] < 50)
    
    score_data = [
        ['Score Range', 'Accounts', 'Percentage', 'Status'],
        ['90-100 (Excellent)', str(excellent), f"{excellent/data['total_accounts']*100:.1f}%", '✓ Excellent'],
        ['70-89 (Good)', str(good), f"{good/data['total_accounts']*100:.1f}%", '✓ Good'],
        ['50-69 (Needs Improvement)', str(needs_improvement), f"{needs_improvement/data['total_accounts']*100:.1f}%", '⚠ Review'],
        ['<50 (Critical)', str(critical), f"{critical/data['total_accounts']*100:.1f}%", '⚠ Urgent']
    ]
    
    score_table = Table(score_data, colWidths=[2.5*inch, 1*inch, 1.3*inch, 1.7*inch])
    score_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#232F3E')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F7F7F7')]),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    content.append(score_table)
    content.append(Spacer(1, 20))
    
    # Findings by severity
    content.append(Paragraph("Findings by Severity", styles['AWSSubSection']))
    content.append(Spacer(1, 10))
    
    severity_data = [['Severity', 'Count', 'Percentage']]
    total_findings = sum(data['findings_by_severity'].values())
    
    for severity in ['critical', 'high', 'medium', 'low']:
        count = data['findings_by_severity'].get(severity, 0)
        percentage = (count / total_findings * 100) if total_findings > 0 else 0
        severity_data.append([
            severity.capitalize(),
            str(count),
            f"{percentage:.1f}%"
        ])
    
    severity_table = Table(severity_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
    severity_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#232F3E')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F7F7F7')]),
        ('TEXTCOLOR', (0, 1), (0, 1), colors.HexColor('#DC2626')),
        ('TEXTCOLOR', (0, 2), (0, 2), colors.HexColor('#EA580C')),
        ('TEXTCOLOR', (0, 3), (0, 3), colors.HexColor('#F59E0B')),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    content.append(severity_table)
    
    return content


def _create_findings_summary(styles, data):
    """Create findings summary section"""
    content = []
    
    content.append(Paragraph("Findings Summary", styles['AWSSectionHeader']))
    content.append(Spacer(1, 15))
    
    # Top 10 critical/high findings
    content.append(Paragraph("Top Priority Findings", styles['AWSSubSection']))
    content.append(Spacer(1, 10))
    
    for i, finding in enumerate(data['top_risks'][:10], 1):
        severity = finding.get('severity', 'medium').lower()
        style_name = f'Finding{severity.capitalize()}'
        
        if severity == 'critical':
            icon = "🔴"
        elif severity == 'high':
            icon = "🟠"
        else:
            icon = "🟡"
        
        title = f"{icon} {i}. [{finding.get('account_name', 'Unknown')}] {finding.get('title', 'Unknown Finding')}"
        content.append(Paragraph(title, styles.get(style_name, styles['FindingHigh'])))
        
        description = finding.get('description', 'No description available')
        content.append(Paragraph(description[:200] + "..." if len(description) > 200 else description, styles['AWSBody']))
        content.append(Spacer(1, 10))
    
    return content


def _create_account_detailed_section(styles, assessment, account_config):
    """Create detailed section for a specific account"""
    from reportlab.lib import colors
    from reportlab.platypus import Table, TableStyle
    
    content = []
    
    account_name = account_config.get('account_name', 'Unknown Account')
    account_id = account_config.get('account_id', 'unknown')
    
    content.append(Paragraph(f"Account: {account_name}", styles['AWSSectionHeader']))
    content.append(Paragraph(f"Account ID: {account_id}", styles['AWSSubSection']))
    content.append(Spacer(1, 15))
    
    # Account metrics
    regions = assessment.get('regions_scanned', [])
    resources = assessment.get('resources', {})
    findings = assessment.get('findings', [])
    
    metrics_text = f"""This account was assessed across {len(regions) if isinstance(regions, list) else 1} region(s), 
    analyzing {sum(len(v) if isinstance(v, list) else 0 for v in resources.values())} resources. 
    The assessment identified {len(findings)} findings requiring attention."""
    
    content.append(Paragraph(metrics_text, styles['AWSBody']))
    content.append(Spacer(1, 15))
    
    # Resources table
    content.append(Paragraph("Resources Summary", styles['AWSSubSection']))
    content.append(Spacer(1, 10))
    
    resource_data = [['Service', 'Resources']]
    for service, items in resources.items():
        count = len(items) if isinstance(items, list) else 0
        if count > 0:
            resource_data.append([service, str(count)])
    
    if len(resource_data) > 1:
        resource_table = Table(resource_data, colWidths=[3*inch, 2*inch])
        resource_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#232F3E')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F7F7F7')]),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        content.append(resource_table)
    
    content.append(Spacer(1, 20))
    
    # Findings for this account
    content.append(Paragraph("Findings", styles['AWSSubSection']))
    content.append(Spacer(1, 10))
    
    if findings:
        for i, finding in enumerate(findings[:5], 1):  # Top 5 findings
            severity = finding.get('severity', 'medium').lower()
            title = f"{i}. [{severity.upper()}] {finding.get('title', 'Unknown Finding')}"
            content.append(Paragraph(title, styles.get(f'Finding{severity.capitalize()}', styles['AWSBody'])))
            content.append(Paragraph(finding.get('description', ''), styles['AWSBody']))
            content.append(Spacer(1, 8))
    else:
        content.append(Paragraph("No findings identified for this account.", styles['AWSBody']))
    
    return content


def _create_cross_account_analysis(styles, data):
    """Create cross-account security analysis"""
    content = []
    
    content.append(Paragraph("Cross-Account Security Analysis", styles['AWSSectionHeader']))
    content.append(Spacer(1, 15))
    
    content.append(Paragraph("Cross-Account Patterns", styles['AWSSubSection']))
    content.append(Spacer(1, 10))
    
    # Identify common issues across accounts
    common_issues = []
    if data['findings_by_severity'].get('critical', 0) > 0:
        common_issues.append("• Multiple accounts have critical security findings requiring immediate remediation")
    
    common_issues.append(f"• {data['total_accounts']} accounts require consistent security policy enforcement")
    common_issues.append("• Centralized logging and monitoring should be implemented across all accounts")
    
    for issue in common_issues:
        content.append(Paragraph(issue, styles['AWSBody']))
    
    content.append(Spacer(1, 15))
    
    content.append(Paragraph("Recommendations", styles['AWSSubSection']))
    content.append(Spacer(1, 10))
    
    recommendations = [
        "1. Implement AWS Organizations with Service Control Policies (SCPs) for centralized governance",
        "2. Enable AWS CloudTrail across all accounts with centralized logging",
        "3. Use AWS Security Hub for aggregated security findings",
        "4. Implement consistent tagging strategy across all accounts",
        "5. Establish AWS Control Tower for automated account provisioning and governance"
    ]
    
    for rec in recommendations:
        content.append(Paragraph(rec, styles['AWSBody']))
        content.append(Spacer(1, 5))
    
    return content


def _create_compliance_section(styles, data):
    """Create compliance framework section"""
    from reportlab.lib import colors
    from reportlab.platypus import Table, TableStyle
    
    content = []
    
    content.append(Paragraph("Compliance Framework Assessment", styles['AWSSectionHeader']))
    content.append(Spacer(1, 15))
    
    content.append(Paragraph("Compliance Status by Framework", styles['AWSSubSection']))
    content.append(Spacer(1, 10))
    
    # Compliance table
    compliance_data = [['Framework', 'Compliant Accounts', 'Status']]
    
    frameworks = {
        'SOC 2': data['compliance_status'].get('soc2', 0),
        'HIPAA': data['compliance_status'].get('hipaa', 0),
        'PCI DSS': data['compliance_status'].get('pci', 0),
        'GDPR': data['compliance_status'].get('gdpr', 0),
        'ISO 27001': data['compliance_status'].get('iso27001', 0)
    }
    
    for framework, compliant_count in frameworks.items():
        percentage = (compliant_count / data['total_accounts'] * 100) if data['total_accounts'] > 0 else 0
        status = '✓ Compliant' if percentage >= 80 else '⚠ Review Required'
        compliance_data.append([
            framework,
            f"{compliant_count}/{data['total_accounts']} ({percentage:.0f}%)",
            status
        ])
    
    compliance_table = Table(compliance_data, colWidths=[2*inch, 2.5*inch, 2*inch])
    compliance_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#232F3E')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F7F7F7')]),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    content.append(compliance_table)
    
    return content


def _create_remediation_roadmap(styles, data):
    """Create remediation roadmap"""
    from reportlab.lib import colors
    from reportlab.platypus import Table, TableStyle
    
    content = []
    
    content.append(Paragraph("Remediation Roadmap", styles['AWSSectionHeader']))
    content.append(Spacer(1, 15))
    
    content.append(Paragraph("Prioritized Action Plan", styles['AWSSubSection']))
    content.append(Spacer(1, 10))
    
    # Roadmap phases
    phases = [
        ['Phase', 'Timeline', 'Priority', 'Actions'],
        ['Immediate (0-30 days)', '30 days', 'Critical', 
         f"Address {data['findings_by_severity'].get('critical', 0)} critical findings"],
        ['Short-term (1-3 months)', '90 days', 'High',
         f"Remediate {data['findings_by_severity'].get('high', 0)} high-priority findings"],
        ['Medium-term (3-6 months)', '180 days', 'Medium',
         'Implement security automation and compliance controls'],
        ['Long-term (6-12 months)', '365 days', 'Optimization',
         'Continuous improvement and cost optimization']
    ]
    
    roadmap_table = Table(phases, colWidths=[1.5*inch, 1*inch, 1*inch, 3*inch])
    roadmap_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#232F3E')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F7F7F7')]),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    content.append(roadmap_table)
    
    return content


def _create_appendix(styles, data):
    """Create appendix with additional details"""
    content = []
    
    content.append(Paragraph("Appendix", styles['AWSSectionHeader']))
    content.append(Spacer(1, 15))
    
    content.append(Paragraph("A. Methodology", styles['AWSSubSection']))
    content.append(Spacer(1, 10))
    content.append(Paragraph(
        "This assessment was conducted using AWS Well-Architected Framework best practices, "
        "analyzing resources across multiple accounts and regions using automated scanning tools "
        "and manual verification of critical configurations.",
        styles['AWSBody']
    ))
    content.append(Spacer(1, 15))
    
    content.append(Paragraph("B. Scope", styles['AWSSubSection']))
    content.append(Spacer(1, 10))
    content.append(Paragraph(
        f"Assessment covered {data['total_accounts']} AWS accounts across {data['total_regions']} regions, "
        f"analyzing {data['total_resources']:,} resources across compute, storage, database, networking, "
        "and security services.",
        styles['AWSBody']
    ))
    content.append(Spacer(1, 15))
    
    content.append(Paragraph("C. Severity Definitions", styles['AWSSubSection']))
    content.append(Spacer(1, 10))
    
    severity_defs = [
        "• Critical: Immediate security risk or compliance violation requiring urgent remediation",
        "• High: Significant security risk or best practice deviation requiring prompt attention",
        "• Medium: Moderate security concern or optimization opportunity",
        "• Low: Minor improvement recommendation or informational finding"
    ]
    
    for sev_def in severity_defs:
        content.append(Paragraph(sev_def, styles['AWSBody']))
    
    return content


def _create_key_metrics_section(styles, data):
    """Create key metrics for executive report"""
    from reportlab.lib import colors
    from reportlab.platypus import Table, TableStyle
    
    content = []
    
    content.append(Paragraph("Key Performance Indicators", styles['AWSSectionHeader']))
    content.append(Spacer(1, 15))
    
    kpi_data = [
        ['Metric', 'Value', 'Target', 'Status'],
        ['Security Score', f"{data['security_score_avg']:.1f}/100", '> 80', 
         '✓' if data['security_score_avg'] >= 80 else '⚠'],
        ['Critical Findings', str(data['findings_by_severity'].get('critical', 0)), '0',
         '✓' if data['findings_by_severity'].get('critical', 0) == 0 else '⚠'],
        ['Cost Optimization', f"${data['cost_optimization_total']:,.0f}/mo", 'N/A', '✓'],
        ['Accounts Assessed', str(data['total_accounts']), 'All', '✓']
    ]
    
    kpi_table = Table(kpi_data, colWidths=[2.5*inch, 1.5*inch, 1*inch, 1*inch])
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#232F3E')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F7F7F7')]),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    
    content.append(kpi_table)
    
    return content


def _create_top_risks_section(styles, data):
    """Create top risks section for executive report"""
    content = []
    
    content.append(Paragraph("Top 5 Security Risks", styles['AWSSectionHeader']))
    content.append(Spacer(1, 15))
    
    for i, finding in enumerate(data['top_risks'][:5], 1):
        severity = finding.get('severity', 'medium').lower()
        icon = "🔴" if severity == 'critical' else "🟠"
        
        title = f"{icon} Risk #{i}: {finding.get('title', 'Unknown Risk')}"
        content.append(Paragraph(title, styles.get(f'Finding{severity.capitalize()}', styles['AWSBody'])))
        content.append(Paragraph(f"Account: {finding.get('account_name', 'Unknown')}", styles['AWSBody']))
        content.append(Paragraph(finding.get('description', '')[:150] + "...", styles['AWSBody']))
        content.append(Spacer(1, 15))
    
    return content


def _create_strategic_recommendations(styles, data):
    """Create strategic recommendations for executive report"""
    content = []
    
    content.append(Paragraph("Strategic Recommendations", styles['AWSSectionHeader']))
    content.append(Spacer(1, 15))
    
    recommendations = [
        {
            'title': '1. Immediate Security Remediation',
            'description': f'Address {data["findings_by_severity"].get("critical", 0)} critical findings within 30 days to eliminate immediate security risks.',
            'impact': 'High',
            'effort': 'Medium'
        },
        {
            'title': '2. Multi-Account Governance',
            'description': 'Implement AWS Organizations and Control Tower for centralized governance across all accounts.',
            'impact': 'High',
            'effort': 'High'
        },
        {
            'title': '3. Cost Optimization Initiative',
            'description': f'Realize ${data["cost_optimization_total"]:,.0f}/month in savings through resource rightsizing and optimization.',
            'impact': 'Medium',
            'effort': 'Low'
        },
        {
            'title': '4. Compliance Enhancement',
            'description': 'Strengthen compliance posture through automated controls and continuous monitoring.',
            'impact': 'High',
            'effort': 'Medium'
        },
        {
            'title': '5. Security Automation',
            'description': 'Deploy automated security response and remediation workflows across all accounts.',
            'impact': 'Medium',
            'effort': 'High'
        }
    ]
    
    for rec in recommendations:
        content.append(Paragraph(rec['title'], styles['AWSSubSection']))
        content.append(Paragraph(rec['description'], styles['AWSBody']))
        content.append(Paragraph(f"Impact: {rec['impact']} | Effort: {rec['effort']}", styles['AWSBody']))
        content.append(Spacer(1, 15))
    
    return content


def _create_technical_account_section(styles, assessment, account_config):
    """Create detailed technical section for an account"""
    content = []
    
    account_name = account_config.get('account_name', 'Unknown Account')
    
    content.append(Paragraph(f"Technical Analysis: {account_name}", styles['AWSSectionHeader']))
    content.append(Spacer(1, 15))
    
    # Detailed technical findings
    findings = assessment.get('findings', [])
    
    for finding in findings:
        content.append(Paragraph(f"Finding: {finding.get('title', 'Unknown')}", styles['AWSSubSection']))
        content.append(Paragraph(f"Severity: {finding.get('severity', 'unknown').upper()}", styles['AWSBody']))
        content.append(Paragraph(finding.get('description', ''), styles['AWSBody']))
        
        remediation = finding.get('remediation', 'No remediation steps available')
        content.append(Paragraph("Remediation:", styles['AWSBody']))
        content.append(Paragraph(remediation, styles['AWSBody']))
        content.append(Spacer(1, 15))
    
    return content


def _create_resource_inventory_section(styles, assessments, accounts_config):
    """Create resource inventory section"""
    from reportlab.lib import colors
    from reportlab.platypus import Table, TableStyle
    
    content = []
    
    content.append(Paragraph("Resource Inventory", styles['AWSSectionHeader']))
    content.append(Spacer(1, 15))
    
    # Aggregate resources by service type
    resource_totals = defaultdict(int)
    
    for assessment in assessments:
        resources = assessment.get('resources', {})
        for service, items in resources.items():
            count = len(items) if isinstance(items, list) else 0
            resource_totals[service] += count
    
    # Create table
    resource_data = [['Service', 'Total Resources']]
    for service, count in sorted(resource_totals.items(), key=lambda x: x[1], reverse=True):
        if count > 0:
            resource_data.append([service, str(count)])
    
    resource_table = Table(resource_data, colWidths=[4*inch, 2*inch])
    resource_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#232F3E')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F7F7F7')]),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    content.append(resource_table)
    
    return content


# ============================================================================
# SINGLE ACCOUNT REPORT (BACKWARD COMPATIBILITY)
# ============================================================================

def generate_waf_report(assessment, report_type: str = "comprehensive") -> bytes:
    """
    Generate single-account PDF report (backward compatible)
    
    Args:
        assessment: Single account assessment dict
        report_type: 'executive', 'comprehensive', or 'technical'
    
    Returns:
        PDF file as bytes
    """
    # Wrap single assessment in list format
    assessments = [assessment]
    accounts_config = [{
        'account_name': assessment.get('account_name', 'AWS Account'),
        'account_id': assessment.get('account_id', 'unknown'),
        'environment': 'production'
    }]
    
    return generate_multiaccount_waf_report(assessments, accounts_config, report_type)


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    'generate_multiaccount_waf_report',
    'generate_waf_report'
]
