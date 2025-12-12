"""
Assessment Scoring Helper Module
Calculates scores and updates assessment after each response

This fixes the issue where responses are saved but scores show as 0
"""

from typing import Dict, List
from datetime import datetime


def calculate_assessment_scores(assessment: Dict, questions: List) -> None:
    """
    Calculate and update all scores in the assessment
    
    This function:
    1. Calculates overall score based on responses
    2. Calculates pillar scores
    3. Updates progress percentage (correctly!)
    4. Generates action items if needed
    
    Args:
        assessment: The assessment dictionary
        questions: List of all Question objects
    """
    responses = assessment.get('responses', {})
    
    if not responses:
        assessment['overall_score'] = 0
        assessment['progress'] = 0
        assessment['scores'] = {}
        return
    
    # ============================================================================
    # 1. CALCULATE OVERALL SCORE
    # ============================================================================
    total_points = 0
    max_points = 0
    
    for question in questions:
        if question.id in responses:
            response = responses[question.id]
            # Response has 'points' directly stored
            total_points += response.get('points', 0)
        max_points += 100  # Each question is worth 100 points max
    
    overall_score = (total_points / max_points * 100) if max_points > 0 else 0
    assessment['overall_score'] = round(overall_score, 1)
    
    # ============================================================================
    # 2. CALCULATE PILLAR SCORES
    # ============================================================================
    # Import Pillar enum
    try:
        from waf_review_module import Pillar
    except:
        # Fallback if import fails
        class Pillar:
            class Enum:
                pass
            OPERATIONAL_EXCELLENCE = "Operational Excellence"
            SECURITY = "Security"
            RELIABILITY = "Reliability"
            PERFORMANCE_EFFICIENCY = "Performance Efficiency"
            COST_OPTIMIZATION = "Cost Optimization"
            SUSTAINABILITY = "Sustainability"
    
    pillar_scores = {}
    
    for pillar in Pillar:
        pillar_questions = [q for q in questions if q.pillar == pillar]
        
        if not pillar_questions:
            pillar_scores[pillar.value] = 0
            continue
        
        pillar_points = 0
        pillar_max = 0
        
        for question in pillar_questions:
            if question.id in responses:
                response = responses[question.id]
                pillar_points += response.get('points', 0)
            pillar_max += 100
        
        pillar_score = (pillar_points / pillar_max * 100) if pillar_max > 0 else 0
        pillar_scores[pillar.value] = round(pillar_score, 1)
    
    assessment['scores'] = pillar_scores
    
    # ============================================================================
    # 3. CALCULATE CORRECT PROGRESS
    # ============================================================================
    total_questions = len(questions)
    answered_questions = len(responses)
    
    progress = (answered_questions / total_questions * 100) if total_questions > 0 else 0
    assessment['progress'] = round(progress, 1)
    
    # ============================================================================
    # 4. UPDATE METADATA
    # ============================================================================
    assessment['questions_answered'] = answered_questions
    assessment['questions_total'] = total_questions
    assessment['updated_at'] = datetime.now().isoformat()
    
    # ============================================================================
    # 5. GENERATE ACTION ITEMS (if needed)
    # ============================================================================
    # Check if we need to generate action items
    # Only generate if assessment is substantially complete and has risks
    if progress > 50 and overall_score < 80:  # If >50% done and score <80
        generate_action_items(assessment, questions)


def generate_action_items(assessment: Dict, questions: List) -> None:
    """
    Generate action items based on responses
    
    Args:
        assessment: The assessment dictionary
        questions: List of all Question objects
    """
    responses = assessment.get('responses', {})
    action_items = []
    
    for question in questions:
        if question.id in responses:
            response = responses[question.id]
            risk_level = response.get('risk_level', 'NONE')
            
            # Generate action item for HIGH and CRITICAL risks
            if risk_level in ['HIGH', 'CRITICAL']:
                action_item = {
                    'id': f"action_{question.id}",
                    'question_id': question.id,
                    'title': f"Address {question.text[:50]}...",
                    'description': question.description,
                    'risk_level': risk_level,
                    'pillar': question.pillar.value,
                    'status': 'Open',
                    'priority': 1 if risk_level == 'CRITICAL' else 2,
                    'estimated_effort': 'TBD',
                    'estimated_cost': 'TBD',
                    'created_at': datetime.now().isoformat()
                }
                action_items.append(action_item)
    
    # Only update if we have new action items
    if action_items:
        assessment['action_items'] = action_items


def get_score_color(score: float) -> str:
    """Get color for score display"""
    if score >= 80:
        return '#28a745'  # Green
    elif score >= 60:
        return '#ffc107'  # Yellow
    elif score >= 40:
        return '#fd7e14'  # Orange
    else:
        return '#dc3545'  # Red


def get_score_status(score: float) -> str:
    """Get status text for score"""
    if score >= 80:
        return 'EXCELLENT'
    elif score >= 60:
        return 'GOOD'
    elif score >= 40:
        return 'NEEDS IMPROVEMENT'
    else:
        return 'CRITICAL'


# Export all functions
__all__ = [
    'calculate_assessment_scores',
    'generate_action_items',
    'get_score_color',
    'get_score_status'
]
