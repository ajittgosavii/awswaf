"""
Enhanced PDF Report Generator for WAF Assessments
Generates comprehensive PDF reports with AI Insights, Action Items, and Dashboard

Features:
- Cover page with branding
- Executive dashboard snapshot
- Pillar scores visualization  
- Comprehensive AI Insights (pillar-wise analysis)
- Detailed action items with priorities
- Risk summary and recommendations
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from io import BytesIO
from datetime import datetime
from typing import Dict
import streamlit as st


def generate_waf_pdf_report(assessment: Dict) -> bytes:
    """Generate a comprehensive PDF report for the WAF assessment with AI Insights"""
    
    # Create PDF in memory
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=36,
    )
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    styles.add(ParagraphStyle(
        name='CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f77b4'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    ))
    
    styles.add(ParagraphStyle(
        name='SectionHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    ))
    
    styles.add(ParagraphStyle(
        name='SubHeading',
        parent=styles['Heading3'],
        fontSize=13,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=8,
        spaceBefore=8,
        fontName='Helvetica-Bold'
    ))
    
    styles.add(ParagraphStyle(
        name='BodyText',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_JUSTIFY,
        spaceAfter=6
    ))
    
    styles.add(ParagraphStyle(
        name='BulletPoint',
        parent=styles['Normal'],
        fontSize=10,
        leftIndent=20,
        spaceAfter=4
    ))
    
    # =========================================================================
    # COVER PAGE
    # =========================================================================
    
    title = Paragraph(
        "AWS Well-Architected<br/>Framework Assessment<br/>Comprehensive Report",
        styles['CustomTitle']
    )
    elements.append(title)
    elements.append(Spacer(1, 0.3*inch))
    
    # Assessment info
    assessment_name = assessment.get('name', 'Unnamed Assessment')
    workload_name = assessment.get('workload_name', 'N/A')
    environment = assessment.get('environment', 'N/A')
    created_date = assessment.get('created_at', datetime.now().isoformat())[:10]
    
    info_data = [
        ['Assessment Name:', assessment_name],
        ['Workload:', workload_name],
        ['Environment:', environment],
        ['Date Generated:', datetime.now().strftime('%Y-%m-%d')],
        ['Assessment Date:', created_date],
        ['Overall Score:', f"{assessment.get('overall_score', 0):.0f}/100"],
        ['Completion:', f"{assessment.get('progress', 0):.0f}%"],
    ]
    
    info_table = Table(info_data, colWidths=[2.5*inch, 4*inch])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    elements.append(info_table)
    elements.append(Spacer(1, 0.5*inch))
    
    # Footer
    footer_text = Paragraph(
        f"<i>Report generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}<br/>"
        f"Powered by Claude AI & AWS Well-Architected Framework<br/>"
        f"AI-Enhanced Analysis | Automated Scanning | Compliance Mapping</i>",
        styles['Normal']
    )
    elements.append(Spacer(1, 1.5*inch))
    elements.append(footer_text)
    
    elements.append(PageBreak())
    
    # =========================================================================
    # EXECUTIVE DASHBOARD SNAPSHOT
    # =========================================================================
    
    elements.append(Paragraph("Executive Dashboard", styles['SectionHeading']))
    elements.append(Spacer(1, 0.15*inch))
    
    overall_score = assessment.get('overall_score', 0)
    progress = assessment.get('progress', 0)
    total_responses = len(assessment.get('responses', {}))
    action_items = assessment.get('action_items', [])
    
    # Determine status
    if overall_score >= 80:
        assessment_status = "Excellent"
        status_color = colors.green
    elif overall_score >= 60:
        assessment_status = "Good"
        status_color = colors.blue
    elif overall_score >= 40:
        assessment_status = "Needs Improvement"
        status_color = colors.orange
    else:
        assessment_status = "Critical Attention Required"
        status_color = colors.red
    
    # Key metrics table
    metrics_data = [
        ['Metric', 'Value', 'Status'],
        ['Overall Score', f'{overall_score:.0f}/100', assessment_status],
        ['Assessment Progress', f'{progress:.0f}%', f'{total_responses}/205 questions'],
        ['Action Items', str(len(action_items)), f'{len([i for i in action_items if i.get("risk_level", "").upper() == "CRITICAL"])} Critical'],
        ['Auto-Detected', str(len(assessment.get('auto_detected', {}))), f'{len(assessment.get("auto_detected", {}))/205*100:.0f}% coverage'],
    ]
    
    metrics_table = Table(metrics_data, colWidths=[2.5*inch, 1.5*inch, 2.5*inch])
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
    ]))
    
    elements.append(metrics_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Summary narrative
    summary_text = Paragraph(
        f"Your AWS architecture has been comprehensively assessed using the Well-Architected Framework. "
        f"The assessment is <b>{progress:.0f}% complete</b> with <b>{total_responses} questions</b> answered "
        f"across all six pillars. Your overall score of <b>{overall_score:.0f}/100</b> indicates "
        f"<b>{assessment_status}</b> architectural posture.",
        styles['BodyText']
    )
    elements.append(summary_text)
    elements.append(Spacer(1, 0.3*inch))
    
    # =========================================================================
    # PILLAR SCORES
    # =========================================================================
    
    elements.append(Paragraph("Pillar Scores Overview", styles['SectionHeading']))
    elements.append(Spacer(1, 0.15*inch))
    
    pillar_scores = assessment.get('scores', {})
    
    if pillar_scores:
        pillar_data = [['Pillar', 'Score', 'Rating', 'Status']]
        
        pillar_icons = {
            'Operational Excellence': '⚙️',
            'Security': '🔒',
            'Reliability': '🛡️',
            'Performance Efficiency': '⚡',
            'Cost Optimization': '💰',
            'Sustainability': '🌱'
        }
        
        for pillar_name, score in pillar_scores.items():
            if score >= 80:
                rating = "Excellent"
                status = "✓ Well-Architected"
            elif score >= 60:
                rating = "Good"
                status = "↗ Minor improvements"
            elif score >= 40:
                rating = "Fair"
                status = "⚠ Needs attention"
            else:
                rating = "Poor"
                status = "⚠ Critical gaps"
            
            icon = pillar_icons.get(pillar_name, '')
            pillar_data.append([f"{icon} {pillar_name}", f"{score:.0f}/100", rating, status])
        
        pillar_table = Table(pillar_data, colWidths=[2.5*inch, 1*inch, 1.2*inch, 1.8*inch])
        pillar_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2ecc71')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('ALIGN', (2, 0), (2, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        elements.append(pillar_table)
    else:
        elements.append(Paragraph("No pillar scores available yet.", styles['BodyText']))
    
    elements.append(PageBreak())
    
    # =========================================================================
    # AI INSIGHTS (if available)
    # =========================================================================
    
    # Check if AI insights are cached
    cache_key = f"ai_insights_{assessment.get('id', 'unknown')}"
    if cache_key in st.session_state:
        elements.append(Paragraph("AI-Powered Insights & Analysis", styles['SectionHeading']))
        elements.append(Spacer(1, 0.15*inch))
        
        insights = st.session_state[cache_key]
        
        # Check if insights contain error
        if 'error' not in insights:
            # Executive Summary from AI
            if 'executive_summary' in insights:
                elements.append(Paragraph("Executive Summary", styles['SubHeading']))
                exec_summary = insights['executive_summary'].replace('\n\n', '<br/><br/>')
                elements.append(Paragraph(exec_summary, styles['BodyText']))
                elements.append(Spacer(1, 0.15*inch))
            
            # Overall Assessment
            if 'overall_assessment' in insights:
                overall = insights['overall_assessment']
                
                if 'strengths' in overall:
                    elements.append(Paragraph("Key Strengths", styles['SubHeading']))
                    for strength in overall['strengths'][:5]:
                        elements.append(Paragraph(f"✓ {strength}", styles['BulletPoint']))
                    elements.append(Spacer(1, 0.1*inch))
                
                if 'weaknesses' in overall:
                    elements.append(Paragraph("Areas for Improvement", styles['SubHeading']))
                    for weakness in overall['weaknesses'][:5]:
                        elements.append(Paragraph(f"→ {weakness}", styles['BulletPoint']))
                    elements.append(Spacer(1, 0.15*inch))
            
            # Quick Wins
            if 'quick_wins' in insights:
                elements.append(PageBreak())
                elements.append(Paragraph("Quick Wins (Immediate Actions)", styles['SubHeading']))
                elements.append(Spacer(1, 0.1*inch))
                
                for idx, win in enumerate(insights['quick_wins'][:5], 1):
                    win_text = f"<b>{idx}. {win.get('title', 'Quick Win')}</b><br/>"
                    win_text += f"{win.get('description', '')} "
                    win_text += f"<i>(Impact: {win.get('impact', 'Unknown')}, Effort: {win.get('effort', 'Unknown')})</i>"
                    elements.append(Paragraph(win_text, styles['BodyText']))
                    elements.append(Spacer(1, 0.08*inch))
            
            # Pillar-wise Analysis (summarized)
            if 'pillar_analysis' in insights:
                elements.append(PageBreak())
                elements.append(Paragraph("Pillar-wise Deep Dive", styles['SectionHeading']))
                elements.append(Spacer(1, 0.15*inch))
                
                for pillar_name, analysis in list(insights['pillar_analysis'].items())[:6]:
                    elements.append(Paragraph(f"{pillar_name}", styles['SubHeading']))
                    
                    # Score and status
                    score_text = f"Score: {analysis.get('score', 0)}/100 - {analysis.get('status', 'Unknown')}"
                    elements.append(Paragraph(score_text, styles['BodyText']))
                    
                    # Top 2 recommendations only (to save space)
                    if 'recommendations' in analysis:
                        elements.append(Paragraph("Top Recommendations:", styles['Normal']))
                        for idx, rec in enumerate(analysis['recommendations'][:2], 1):
                            rec_text = f"{idx}. <b>{rec.get('title', 'Recommendation')}</b> "
                            rec_text += f"(Priority: {rec.get('priority', 'Unknown')})"
                            elements.append(Paragraph(rec_text, styles['BulletPoint']))
                    
                    elements.append(Spacer(1, 0.12*inch))
        else:
            elements.append(Paragraph(
                "AI Insights were not generated for this assessment. "
                "Generate insights in the application to include them in future reports.",
                styles['BodyText']
            ))
    else:
        elements.append(Paragraph("AI-Powered Insights", styles['SectionHeading']))
        elements.append(Paragraph(
            "AI Insights are available in the application but were not included in this report. "
            "To include AI insights, generate them in the AI Insights tab before exporting the PDF.",
            styles['BodyText']
        ))
    
    elements.append(PageBreak())
    
    # =========================================================================
    # DETAILED ACTION ITEMS
    # =========================================================================
    
    elements.append(Paragraph("Action Items & Recommendations", styles['SectionHeading']))
    elements.append(Spacer(1, 0.15*inch))
    
    if action_items:
        # Sort by priority and risk
        critical_items = [i for i in action_items if i.get('risk_level', '').upper() == 'CRITICAL']
        high_items = [i for i in action_items if i.get('risk_level', '').upper() == 'HIGH']
        medium_items = [i for i in action_items if i.get('risk_level', '').upper() == 'MEDIUM']
        
        # Summary
        summary_para = Paragraph(
            f"<b>Total Action Items: {len(action_items)}</b> | "
            f"🔴 Critical: {len(critical_items)} | "
            f"🟠 High: {len(high_items)} | "
            f"🟡 Medium: {len(medium_items)}",
            styles['BodyText']
        )
        elements.append(summary_para)
        elements.append(Spacer(1, 0.15*inch))
        
        # Critical Priority Items
        if critical_items:
            elements.append(Paragraph("Critical Priority (Immediate Action Required)", styles['SubHeading']))
            for idx, item in enumerate(critical_items[:10], 1):  # Limit to first 10
                item_text = f"<b>{idx}. [{item.get('pillar', 'Unknown')}] {item.get('title', 'Action Item')}</b><br/>"
                item_text += f"{item.get('description', 'No description')[:200]}...<br/>"
                item_text += f"<i>Priority: {item.get('priority', 'Unknown')} | "
                item_text += f"Effort: {item.get('effort', 'Unknown')} | "
                item_text += f"Cost: {item.get('cost', 'Unknown')}</i>"
                elements.append(Paragraph(item_text, styles['BodyText']))
                elements.append(Spacer(1, 0.1*inch))
            
            if len(critical_items) > 10:
                elements.append(Paragraph(
                    f"<i>... and {len(critical_items) - 10} more critical items</i>",
                    styles['BodyText']
                ))
            elements.append(Spacer(1, 0.15*inch))
        
        # High Priority Items
        if high_items:
            elements.append(Paragraph("High Priority", styles['SubHeading']))
            for idx, item in enumerate(high_items[:8], 1):  # Limit to first 8
                item_text = f"<b>{idx}. [{item.get('pillar', 'Unknown')}] {item.get('title', 'Action Item')}</b><br/>"
                item_text += f"{item.get('description', 'No description')[:150]}...<br/>"
                item_text += f"<i>Effort: {item.get('effort', 'Unknown')} | Cost: {item.get('cost', 'Unknown')}</i>"
                elements.append(Paragraph(item_text, styles['BodyText']))
                elements.append(Spacer(1, 0.08*inch))
            
            if len(high_items) > 8:
                elements.append(Paragraph(
                    f"<i>... and {len(high_items) - 8} more high priority items</i>",
                    styles['BodyText']
                ))
            elements.append(Spacer(1, 0.15*inch))
        
        # Medium Priority Items (summary only)
        if medium_items:
            elements.append(Paragraph("Medium Priority", styles['SubHeading']))
            elements.append(Paragraph(
                f"There are <b>{len(medium_items)} medium priority items</b> identified. "
                f"These should be addressed after critical and high priority items. "
                f"View the complete list in the application's Action Items tab.",
                styles['BodyText']
            ))
            
            # Show first 3 medium items
            for idx, item in enumerate(medium_items[:3], 1):
                item_text = f"{idx}. {item.get('title', 'Action Item')} ({item.get('pillar', 'Unknown')})"
                elements.append(Paragraph(item_text, styles['BulletPoint']))
            
            if len(medium_items) > 3:
                elements.append(Paragraph(
                    f"<i>... and {len(medium_items) - 3} more medium priority items</i>",
                    styles['BodyText']
                ))
    else:
        # No action items
        if progress >= 80:
            elements.append(Paragraph(
                "✓ <b>Excellent!</b> No action items required. Your architecture follows AWS Well-Architected "
                "best practices across all pillars. Continue monitoring and maintain current standards.",
                styles['BodyText']
            ))
        else:
            elements.append(Paragraph(
                f"Complete the assessment ({progress:.0f}% done) to generate prioritized action items and recommendations.",
                styles['BodyText']
            ))
    
    elements.append(PageBreak())
    
    # =========================================================================
    # CONCLUSION & NEXT STEPS
    # =========================================================================
    
    elements.append(Paragraph("Conclusion & Next Steps", styles['SectionHeading']))
    elements.append(Spacer(1, 0.15*inch))
    
    conclusion_text = f"""
This comprehensive assessment provides an in-depth view of your AWS architecture's alignment 
with the Well-Architected Framework. With an overall score of <b>{overall_score:.0f}/100</b> and 
<b>{progress:.0f}% completion</b>, the analysis identifies both strengths and opportunities for improvement.
<br/><br/>
<b>Key Highlights:</b><br/>
• Assessment includes {total_responses} questions across 6 pillars<br/>
• {len(assessment.get('auto_detected', {}))} questions auto-detected from AWS environment<br/>
• {len(action_items)} prioritized action items identified<br/>
• AI-powered insights provide detailed recommendations<br/>
<br/>
<b>Recommended Next Steps:</b><br/>
1. <b>Immediate:</b> Address all critical priority items within 2 weeks<br/>
2. <b>Short-term:</b> Create remediation plan for high priority items (1-3 months)<br/>
3. <b>Medium-term:</b> Implement medium priority improvements (3-6 months)<br/>
4. <b>Ongoing:</b> Schedule quarterly reassessments to track progress<br/>
5. <b>Continuous:</b> Enable automated scanning for real-time monitoring<br/>
<br/>
<b>Additional Resources:</b><br/>
• Full AI insights available in the application's AI Insights tab<br/>
• Detailed question-by-question analysis in Assessment tab<br/>
• Export action items to project management tools<br/>
• Schedule follow-up reviews with AWS Solutions Architects<br/>
<br/>
<i>For more detailed analysis and interactive insights, access the full report in the 
AWS Well-Architected Framework Advisor application.</i>
"""
    
    elements.append(Paragraph(conclusion_text, styles['BodyText']))
    
    elements.append(Spacer(1, 0.3*inch))
    
    # Footer disclaimer
    disclaimer = Paragraph(
        "<i><b>Note:</b> This report is generated automatically based on your responses and AI analysis. "
        "While comprehensive, it should be reviewed by qualified AWS Solutions Architects for critical workloads. "
        "AWS Well-Architected Framework is a trademark of Amazon Web Services, Inc.</i>",
        styles['Normal']
    )
    elements.append(disclaimer)
    
    # =========================================================================
    # BUILD PDF
    # =========================================================================
    
    doc.build(elements)
    
    # Get PDF bytes
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes
