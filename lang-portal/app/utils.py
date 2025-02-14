from flask import request
from sqlalchemy import func
from app import db
from app.models import Word

def paginate(query, schema=None, items_per_page=100):
    """Helper function to paginate SQLAlchemy queries.
    
    Args:
        query: SQLAlchemy query object
        schema: Optional Marshmallow schema for serialization
        items_per_page: Number of items per page (default: 100)
    """
    page = request.args.get('page', 1, type=int)
    total_items = query.count()
    total_pages = (total_items + items_per_page - 1) // items_per_page
    
    items = query.limit(items_per_page).offset((page - 1) * items_per_page).all()
    
    if schema:
        items = [schema.dump(item) for item in items]
    
    return {
        "items": items,
        "pagination": {
            "current_page": page,
            "total_pages": total_pages,
            "total_items": total_items,
            "items_per_page": items_per_page
        }
    }

def get_word_stats(word_id):
    """Get statistics for a word."""
    from app.models import WordReviewItem
    
    correct = WordReviewItem.query.filter_by(word_id=word_id, is_correct=True).count()
    wrong = WordReviewItem.query.filter_by(word_id=word_id, is_correct=False).count()
    
    return {
        "correct_count": correct,
        "wrong_count": wrong
    }

def get_study_streak_days():
    """Calculate the number of consecutive days with study sessions."""
    from .models import StudySession
    from datetime import datetime, timedelta
    
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
    
    return streak

def get_study_progress():
    """Get study progress statistics."""
    total_available_words = Word.query.count()
    total_words_studied = db.session.query(WordReviewItem.word_id).distinct().count()

    return {
        'total_words_studied': total_words_studied,
        'total_available_words': total_available_words
    }

def get_quick_stats():
    """Get quick overview statistics."""
    from app.models import WordReviewItem, StudySession, Group
    
    # Calculate success rate
    total_reviews = WordReviewItem.query.count()
    correct_reviews = WordReviewItem.query.filter_by(is_correct=True).count()
    success_rate = (correct_reviews / total_reviews * 100) if total_reviews > 0 else 0
    
    # Get total study sessions
    total_study_sessions = StudySession.query.count()
    
    # Get total active groups (groups with study sessions)
    total_active_groups = Group.query.join(StudySession).distinct(Group.id).count()
    
    # Calculate study streak
    study_streak_days = get_study_streak_days()
    
    return {
        'success_rate': round(success_rate, 1),
        'total_study_sessions': total_study_sessions,
        'total_active_groups': total_active_groups,
        'study_streak_days': study_streak_days
    }
