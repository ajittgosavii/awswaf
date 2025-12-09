"""
PDF Report Generator Module
Generate comprehensive WAF assessment reports in PDF format

Features:
- Executive summary with key metrics
- Detailed pillar assessments
- Findings with remediation steps
- Resource inventory
- Remediation roadmap
- Professional formatting
"""

from io import BytesIO
from datetime import datetime
from typing import Dict, List, Any

# ============================================================================
# PDF GENERATION
# ============================================================================

def generate_comprehensive_waf_report(assessment) -> bytes:
    """Generate comprehensive PDF report from assessment"""
    
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
            PageBreak, HRFlowable, ListFlowable, ListItem
        )
    except ImportError:
        raise ImportError("reportlab is required for PDF generation")
    
    buffer = BytesIO()
    
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=1*inch,
        bottomMargin=0.75*inch
    )
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    styles.add(ParagraphStyle(
        name='MainTitle',
        parent=styles['Title'],
        fontSize=28,
        textColor=colors.HexColor('#232F3E'),
        spaceAfter=20
    ))
    
    styles.add(ParagraphStyle(
        name='SubTitle',
        parent=styles['Normal'],
        fontSize=14,
        textColor=colors.HexColor('#FF9900'),
        spaceAfter=30
    ))
    
    styles.add(ParagraphStyle(
        name='SectionHeader',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#232F3E'),
        spaceBefore=25,
        spaceAfter=15,
        borderWidth=0,
        borderPadding=0
    ))
    
    styles.add(ParagraphStyle(
        name='SubSection',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#37475A'),
        spaceBefore=15,
        spaceAfter=10
    ))
    
    styles.add(ParagraphStyle(
        name='BodyText',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_JUSTIFY,
        spaceAfter=8
    ))
    
    styles.add(ParagraphStyle(
        name='FindingTitle',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#1976D2'),
        fontName='Helvetica-Bold',
        spaceAfter=5
    ))
    
    elements = []
    
    # =========================================================================
    # COVER PAGE
    # =========================================================================
    
    elements.append(Spacer(1, 2*inch))
    elements.append(Paragraph("AWS Well-Architected", styles['MainTitle']))
    elements.append(Paragraph("Framework Review Report", styles['MainTitle']))
    elements.append(Spacer(1, 0.5*inch))
    elements.append(Paragraph("AI-Powered Architecture Assessment", styles['SubTitle']))
    elements.append(Spacer(1, 0.5*inch))
    
    # Assessment info
    elements.append(Paragraph(f"Assessment Date: {assessment.timestamp.strftime('%B %d, %Y')}", styles['BodyText']))
    elements.append(Paragraph(f"Assessment ID: {assessment.assessment_id}", styles['BodyText']))
    elements.append(Paragraph(f"Regions Scanned: {', '.join(assessment.regions_scanned)}", styles['BodyText']))
    
    elements.append(Spacer(1, 1*inch))
    
    # Score display
    score_color = colors.HexColor('#388E3C') if assessment.overall_score >= 80 else \
                  colors.HexColor('#FBC02D') if assessment.overall_score >= 60 else \
                  colors.HexColor('#D32F2F')
    
    elements.append(Paragraph(
        f"<font size='48' color='{score_color}'><b>{assessment.overall_score}</b></font>",
        ParagraphStyle('ScoreStyle', parent=styles['Title'], alignment=TA_CENTER)
    ))
    elements.append(Paragraph("Overall WAF Score", styles['SubTitle']))
    elements.append(Paragraph(f"Risk Level: <b>{assessment.overall_risk}</b>", styles['BodyText']))
    
    elements.append(PageBreak())
    
    # =========================================================================
    # EXECUTIVE SUMMARY
    # =========================================================================
    
    elements.append(Paragraph("Executive Summary", styles['SectionHeader']))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#FF9900')))
    elements.append(Spacer(1, 15))
    
    # Key metrics
    critical_count = sum(1 for f in assessment.findings if f.severity == 'CRITICAL')
    high_count = sum(1 for f in assessment.findings if f.severity == 'HIGH')
    medium_count = sum(1 for f in assessment.findings if f.severity == 'MEDIUM')
    
    summary = f"""This Well-Architected Framework Review provides a comprehensive assessment of your AWS environment 
    against the six pillars of the AWS Well-Architected Framework. The assessment identified 
    <b>{len(assessment.findings)} findings</b>, including <b>{critical_count} critical</b> and 
    <b>{high_count} high</b> severity issues requiring immediate attention.
    
    Your overall WAF score is <b>{assessment.overall_score}/100</b>, indicating a <b>{assessment.overall_risk}</b> 
    risk level. The assessment covers Security, Reliability, Performance Efficiency, Cost Optimization, 
    Operational Excellence, and Sustainability pillars."""
    
    elements.append(Paragraph(summary, styles['BodyText']))
    elements.append(Spacer(1, 20))
    
    # Summary metrics table
    metrics_data = [
        ['Metric', 'Value', 'Status'],
        ['Overall Score', f'{assessment.overall_score}/100', assessment.overall_risk],
        ['Total Findings', str(len(assessment.findings)), ''],
        ['Critical Issues', str(critical_count), 'Immediate Action' if critical_count > 0 else 'None'],
        ['High Issues', str(high_count), 'Urgent' if high_count > 0 else 'None'],
        ['Medium Issues', str(medium_count), 'Plan' if medium_count > 0 else 'None'],
        ['Potential Savings', f'${assessment.savings_opportunities:,.0f}/mo', ''],
    ]
    
    table = Table(metrics_data, colWidths=[2.5*inch, 1.5*inch, 2*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#232F3E')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F5F5F5')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
    ]))
    elements.append(table)
    
    elements.append(PageBreak())
    
    # =========================================================================
    # PILLAR SCORES
    # =========================================================================
    
    elements.append(Paragraph("Pillar Assessment Scores", styles['SectionHeader']))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#FF9900')))
    elements.append(Spacer(1, 15))
    
    pillar_data = [['Pillar', 'Score', 'Critical', 'High', 'Medium', 'Status']]
    
    for pillar_name, ps in assessment.pillar_scores.items():
        if ps.score >= 80:
            status = 'Good'
        elif ps.score >= 60:
            status = 'Needs Work'
        else:
            status = 'At Risk'
        
        pillar_data.append([
            pillar_name,
            f'{ps.score}/100',
            str(ps.critical_count),
            str(ps.high_count),
            str(ps.medium_count),
            status
        ])
    
    pillar_table = Table(pillar_data, colWidths=[2*inch, 0.8*inch, 0.7*inch, 0.7*inch, 0.8*inch, 1*inch])
    pillar_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#232F3E')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
    ]))
    elements.append(pillar_table)
    
    elements.append(PageBreak())
    
    # =========================================================================
    # DETAILED FINDINGS
    # =========================================================================
    
    elements.append(Paragraph("Detailed Findings", styles['SectionHeader']))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#FF9900')))
    elements.append(Spacer(1, 15))
    
    severity_colors = {
        'CRITICAL': colors.HexColor('#D32F2F'),
        'HIGH': colors.HexColor('#F57C00'),
        'MEDIUM': colors.HexColor('#FBC02D'),
        'LOW': colors.HexColor('#388E3C')
    }
    
    for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
        sev_findings = [f for f in assessment.findings if f.severity == severity]
        if not sev_findings:
            continue
        
        elements.append(Paragraph(
            f"<font color='{severity_colors[severity]}'><b>{severity} Findings ({len(sev_findings)})</b></font>",
            styles['SubSection']
        ))
        
        for finding in sev_findings[:10]:  # Limit to 10 per severity
            elements.append(Paragraph(finding.title, styles['FindingTitle']))
            elements.append(Paragraph(f"<b>Pillar:</b> {finding.pillar} | <b>Service:</b> {finding.source_service}", styles['BodyText']))
            elements.append(Paragraph(f"<b>Description:</b> {finding.description}", styles['BodyText']))
            
            if finding.affected_resources:
                resources = ', '.join(finding.affected_resources[:5])
                elements.append(Paragraph(f"<b>Affected Resources:</b> {resources}", styles['BodyText']))
            
            if finding.recommendation:
                elements.append(Paragraph(f"<b>Recommendation:</b> {finding.recommendation}", styles['BodyText']))
            
            if finding.remediation_steps:
                elements.append(Paragraph("<b>Remediation Steps:</b>", styles['BodyText']))
                for i, step in enumerate(finding.remediation_steps[:5], 1):
                    elements.append(Paragraph(f"  {i}. {step}", styles['BodyText']))
            
            if finding.estimated_savings > 0:
                elements.append(Paragraph(f"<b>Potential Savings:</b> ${finding.estimated_savings:,.0f}/month", styles['BodyText']))
            
            elements.append(Spacer(1, 10))
        
        if len(sev_findings) > 10:
            elements.append(Paragraph(f"<i>... and {len(sev_findings) - 10} more {severity} findings</i>", styles['BodyText']))
        
        elements.append(Spacer(1, 15))
    
    elements.append(PageBreak())
    
    # =========================================================================
    # RESOURCE INVENTORY
    # =========================================================================
    
    elements.append(Paragraph("Resource Inventory", styles['SectionHeader']))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#FF9900')))
    elements.append(Spacer(1, 15))
    
    inv = assessment.inventory
    
    # Compute resources
    elements.append(Paragraph("Compute Resources", styles['SubSection']))
    compute_data = [
        ['Resource Type', 'Count', 'Details'],
        ['EC2 Instances', str(inv.ec2_instances), f'{inv.ec2_running} running'],
        ['Lambda Functions', str(inv.lambda_functions), ''],
        ['EKS Clusters', str(inv.eks_clusters), ''],
        ['ECS Clusters', str(inv.ecs_clusters), ''],
    ]
    
    compute_table = Table(compute_data, colWidths=[2.5*inch, 1.5*inch, 2*inch])
    compute_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#37475A')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
    ]))
    elements.append(compute_table)
    elements.append(Spacer(1, 15))
    
    # Storage resources
    elements.append(Paragraph("Storage & Database", styles['SubSection']))
    storage_data = [
        ['Resource Type', 'Count', 'Details'],
        ['S3 Buckets', str(inv.s3_buckets), f'{inv.s3_public} public'],
        ['EBS Volumes', str(inv.ebs_volumes), f'{inv.ebs_unattached} unattached'],
        ['RDS Instances', str(inv.rds_instances), f'{inv.rds_multi_az} Multi-AZ'],
    ]
    
    storage_table = Table(storage_data, colWidths=[2.5*inch, 1.5*inch, 2*inch])
    storage_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#37475A')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
    ]))
    elements.append(storage_table)
    elements.append(Spacer(1, 15))
    
    # Security resources
    elements.append(Paragraph("Security & IAM", styles['SubSection']))
    security_data = [
        ['Resource Type', 'Count', 'Details'],
        ['IAM Users', str(inv.iam_users), f'{inv.iam_users_no_mfa} without MFA'],
        ['IAM Roles', str(inv.iam_roles), ''],
        ['Security Groups', str(inv.security_groups), ''],
        ['VPCs', str(inv.vpcs), ''],
    ]
    
    security_table = Table(security_data, colWidths=[2.5*inch, 1.5*inch, 2*inch])
    security_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#37475A')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
    ]))
    elements.append(security_table)
    
    elements.append(PageBreak())
    
    # =========================================================================
    # REMEDIATION ROADMAP
    # =========================================================================
    
    elements.append(Paragraph("Remediation Roadmap", styles['SectionHeader']))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#FF9900')))
    elements.append(Spacer(1, 15))
    
    elements.append(Paragraph("Immediate Actions (0-30 days)", styles['SubSection']))
    immediate = [f for f in assessment.findings if f.severity in ['CRITICAL', 'HIGH'] and f.effort == 'Low']
    for finding in immediate[:5]:
        elements.append(Paragraph(f"• <b>{finding.title}</b>: {finding.recommendation[:100]}", styles['BodyText']))
    
    elements.append(Spacer(1, 10))
    
    elements.append(Paragraph("Short-term Actions (30-90 days)", styles['SubSection']))
    short_term = [f for f in assessment.findings if f.severity in ['HIGH', 'MEDIUM'] and f.effort == 'Medium']
    for finding in short_term[:5]:
        elements.append(Paragraph(f"• <b>{finding.title}</b>: {finding.recommendation[:100]}", styles['BodyText']))
    
    elements.append(Spacer(1, 10))
    
    elements.append(Paragraph("Medium-term Actions (90+ days)", styles['SubSection']))
    medium_term = [f for f in assessment.findings if f.effort == 'High']
    for finding in medium_term[:5]:
        elements.append(Paragraph(f"• <b>{finding.title}</b>: {finding.recommendation[:100]}", styles['BodyText']))
    
    # =========================================================================
    # COST OPTIMIZATION
    # =========================================================================
    
    if assessment.savings_opportunities > 0:
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("Cost Optimization Summary", styles['SectionHeader']))
        elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#FF9900')))
        elements.append(Spacer(1, 15))
        
        elements.append(Paragraph(
            f"Total Monthly Savings Potential: <b>${assessment.savings_opportunities:,.0f}</b>",
            styles['BodyText']
        ))
        elements.append(Paragraph(
            f"Total Annual Savings Potential: <b>${assessment.savings_opportunities * 12:,.0f}</b>",
            styles['BodyText']
        ))
        
        elements.append(Spacer(1, 10))
        
        savings_findings = [f for f in assessment.findings if f.estimated_savings > 0]
        savings_findings.sort(key=lambda x: x.estimated_savings, reverse=True)
        
        for finding in savings_findings[:5]:
            elements.append(Paragraph(
                f"• {finding.title}: <b>${finding.estimated_savings:,.0f}/month</b>",
                styles['BodyText']
            ))
    
    # Build PDF
    doc.build(elements)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes

# Export
__all__ = ['generate_comprehensive_waf_report']
