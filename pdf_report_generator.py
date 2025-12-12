"""
PDF Report Generator for WAF Assessments
Generates professional PDF reports using reportlab

Features:
- Cover page with branding
- Executive summary
- Pillar scores visualization
- Action items with priorities
- Detailed findings
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO
from datetime import datetime
from typing import Dict
import streamlit as st


def generate_waf_pdf_report(assessment: Dict) -> bytes:
    """Generate a comprehensive PDF report for the WAF assessment"""
    
    # Create PDF in memory
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18,
    )
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f77b4'),
        spaceAfter=30,
        alignment=TA_CENTER
    ))
    styles.add(ParagraphStyle(
        name='SectionHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=12,
        spaceBefore=12
    ))
    styles.add(ParagraphStyle(
        name='SubHeading',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=6
    ))
    
    # Cover Page
    title = Paragraph("AWS Well-Architected<br/>Framework Assessment", styles['CustomTitle'])
    elements.append(title)
    elements.append(Spacer(1, 0.5*inch))
    
    # Assessment info
    assessment_name = assessment.get('name', 'Unnamed Assessment')
    workload_name = assessment.get('workload_name', 'N/A')
    environment = assessment.get('environment', 'N/A')
    created_date = assessment.get('created_at', datetime.now().isoformat())[:10]
    
    info_data = [
        ['Assessment:', assessment_name],
        ['Workload:', workload_name],
        ['Environment:', environment],
        ['Date:', created_date],
        ['Overall Score:', f"{assessment.get('overall_score', 0)}/100"],
        ['Progress:', f"{assessment.get('progress', 0)}%"],
    ]
    
    info_table = Table(info_data, colWidths=[2*inch, 4*inch])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    
    elements.append(info_table)
    elements.append(Spacer(1, 0.5*inch))
    
    footer_text = Paragraph(
        f"<i>Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}<br/>"
        f"Powered by Claude AI & Firebase</i>",
        styles['Normal']
    )
    elements.append(Spacer(1, 2*inch))
    elements.append(footer_text)
    elements.append(PageBreak())
    
    # Executive Summary
    elements.append(Paragraph("Executive Summary", styles['SectionHeading']))
    elements.append(Spacer(1, 0.2*inch))
    
    overall_score = assessment.get('overall_score', 0)
    progress = assessment.get('progress', 0)
    total_responses = len(assessment.get('responses', {}))
    
    if overall_score >= 80:
        assessment_status = "Excellent"
        status_color = "green"
    elif overall_score >= 60:
        assessment_status = "Good"
        status_color = "blue"
    elif overall_score >= 40:
        assessment_status = "Needs Improvement"
        status_color = "orange"
    else:
        assessment_status = "Critical"
        status_color = "red"
    
    summary_text = f"""
    Your AWS architecture has been assessed using the Well-Architected Framework. 
    The assessment is <b>{progress:.0f}% complete</b> with <b>{total_responses} questions</b> answered 
    across all six pillars. Your overall score is <b>{overall_score}/100</b>, 
    indicating a <b><font color="{status_color}">{assessment_status}</font></b> architectural posture.
    """
    
    elements.append(Paragraph(summary_text, styles['Normal']))
    elements.append(Spacer(1, 0.3*inch))
    
    # Pillar Scores
    elements.append(Paragraph("Pillar Scores", styles['SectionHeading']))
    elements.append(Spacer(1, 0.2*inch))
    
    pillar_scores = assessment.get('scores', {})
    
    if pillar_scores:
        pillar_data = [['Pillar', 'Score', 'Status']]
        
        for pillar_name, score in pillar_scores.items():
            if score >= 80:
                status = "Excellent ✓"
            elif score >= 60:
                status = "Good"
            elif score >= 40:
                status = "Needs Improvement"
            else:
                status = "Critical ⚠"
            
            pillar_data.append([pillar_name, f"{score}/100", status])
        
        pillar_table = Table(pillar_data, colWidths=[3*inch, 1.5*inch, 2*inch])
        pillar_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('ALIGN', (2, 0), (2, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(pillar_table)
    else:
        elements.append(Paragraph("No pillar scores available.", styles['Normal']))
    
    elements.append(Spacer(1, 0.3*inch))
    
    # Action Items
    elements.append(PageBreak())
    elements.append(Paragraph("Action Items", styles['SectionHeading']))
    elements.append(Spacer(1, 0.2*inch))
    
    action_items = assessment.get('action_items', [])
    
    if action_items:
        sorted_items = sorted(action_items, key=lambda x: x.get('priority', 999))
        
        critical_items = [item for item in sorted_items if item.get('risk_level', '').upper() == 'CRITICAL']
        high_items = [item for item in sorted_items if item.get('risk_level', '').upper() == 'HIGH']
        medium_items = [item for item in sorted_items if item.get('risk_level', '').upper() == 'MEDIUM']
        
        if critical_items:
            elements.append(Paragraph("Critical Priority", styles['SubHeading']))
            for idx, item in enumerate(critical_items, 1):
                item_text = f"""
                <b>{idx}. {item.get('pillar', 'Unknown')}</b><br/>
                {item.get('title', 'No title')[:100]}...<br/>
                <i>Effort: {item.get('effort', 'Unknown')} | Cost: {item.get('cost', 'Unknown')}</i>
                """
                elements.append(Paragraph(item_text, styles['Normal']))
                elements.append(Spacer(1, 0.1*inch))
        
        if high_items:
            elements.append(Spacer(1, 0.2*inch))
            elements.append(Paragraph("High Priority", styles['SubHeading']))
            for idx, item in enumerate(high_items, 1):
                item_text = f"""
                <b>{idx}. {item.get('pillar', 'Unknown')}</b><br/>
                {item.get('title', 'No title')[:100]}...<br/>
                <i>Effort: {item.get('effort', 'Unknown')} | Cost: {item.get('cost', 'Unknown')}</i>
                """
                elements.append(Paragraph(item_text, styles['Normal']))
                elements.append(Spacer(1, 0.1*inch))
        
        if medium_items:
            elements.append(Spacer(1, 0.2*inch))
            elements.append(Paragraph("Medium Priority", styles['SubHeading']))
            for idx, item in enumerate(medium_items[:10], 1):
                item_text = f"""
                <b>{idx}. {item.get('pillar', 'Unknown')}</b><br/>
                {item.get('title', 'No title')[:100]}...<br/>
                <i>Effort: {item.get('effort', 'Unknown')} | Cost: {item.get('cost', 'Unknown')}</i>
                """
                elements.append(Paragraph(item_text, styles['Normal']))
                elements.append(Spacer(1, 0.1*inch))
            
            if len(medium_items) > 10:
                elements.append(Paragraph(
                    f"<i>... and {len(medium_items) - 10} more medium priority items</i>",
                    styles['Normal']
                ))
    
    else:
        elements.append(Paragraph(
            "No action items identified. Your architecture is well-optimized!",
            styles['Normal']
        ))
    
    # Conclusion
    elements.append(PageBreak())
    elements.append(Paragraph("Conclusion & Next Steps", styles['SectionHeading']))
    elements.append(Spacer(1, 0.2*inch))
    
    conclusion_text = f"""
    This assessment provides a comprehensive view of your AWS architecture's alignment 
    with the Well-Architected Framework. With an overall score of <b>{overall_score}/100</b>, 
    there are clear opportunities for improvement.
    <br/><br/>
    <b>Recommended Next Steps:</b><br/>
    1. Review and prioritize the critical action items<br/>
    2. Create a remediation roadmap with timelines<br/>
    3. Assign owners for each action item<br/>
    4. Schedule regular reassessments (quarterly recommended)<br/>
    5. Track progress using AWS Well-Architected Tool or this platform
    <br/><br/>
    <i>For detailed recommendations and AI-powered insights, visit the AI Insights tab in the application.</i>
    """
    
    elements.append(Paragraph(conclusion_text, styles['Normal']))
    
    # Build PDF
    doc.build(elements)
    
    # Get PDF bytes
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes