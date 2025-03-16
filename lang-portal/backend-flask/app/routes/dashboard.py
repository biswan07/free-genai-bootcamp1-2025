from flask import Blueprint, jsonify
from ..models import db, StudySession, Word, Group, WordReviewItem
from sqlalchemy import func
from datetime import datetime, timedelta

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/last_study_session')
def last_study_session():
    session = StudySession.query.order_by(StudySession.created_at.desc()).first()
    
    if not session:
        return jsonify({"error": "No study sessions found"}), 404
        
    return jsonify({
        "id": session.id,
        "group_id": session.group_id,
        "created_at": session.created_at.isoformat(),
        "study_activity_id": session.study_activity_id,
        "group_name": session.group.name
    })

@dashboard_bp.route('/study_progress')
def study_progress():
    total_words = Word.query.count()
    studied_words = db.session.query(func.count(func.distinct(WordReviewItem.word_id))).scalar()
    
    return jsonify({
        "total_words_studied": studied_words,
        "total_available_words": total_words
    })

@dashboard_bp.route('/quick-stats')
def quick_stats():
    # Calculate success rate
    reviews = WordReviewItem.query.all()
    correct_count = sum(1 for r in reviews if r.correct)
    total_count = len(reviews)
    success_rate = (correct_count / total_count * 100) if total_count > 0 else 0
    
    # Get total study sessions
    total_sessions = StudySession.query.count()
    
    # Get total active groups
    active_groups = Group.query.join(StudySession).distinct().count()
    
    # Calculate study streak
    today = datetime.utcnow().date()
    streak = 0
    current_date = today
    
    while True:
        session_exists = StudySession.query.filter(
            func.date(StudySession.created_at) == current_date
        ).first() is not None
        
        if not session_exists:
            break
            
        streak += 1
        current_date -= timedelta(days=1)
    
    return jsonify({
        "success_rate": round(success_rate, 1),
        "total_study_sessions": total_sessions,
        "total_active_groups": active_groups,
        "study_streak_days": streak
    })
