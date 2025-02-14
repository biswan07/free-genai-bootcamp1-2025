from flask import Blueprint, jsonify, request
from .models import db, Word, Group, StudySession, StudyActivity, WordReviewItem
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from .utils import get_word_stats, get_study_streak_days, get_quick_stats

api = Blueprint('api', __name__)

# Error Handlers
@api.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad Request', 'message': str(error)}), 400

@api.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not Found', 'message': str(error)}), 404

@api.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal Server Error', 'message': str(error)}), 500

# Dashboard Endpoints
@api.route('/api/dashboard/last_study_session')
def get_last_study_session():
    """Get information about the most recent study session."""
    try:
        last_session = StudySession.query.order_by(desc(StudySession.created_at)).first()
        if not last_session:
            return jsonify({"message": "No study sessions found"}), 404
            
        group = Group.query.get(last_session.group_id)
        return jsonify({
            "id": last_session.id,
            "group_id": last_session.group_id,
            "created_at": last_session.created_at.isoformat(),
            "study_activity_id": last_session.study_activity_id,
            "group_name": group.name if group else None
        })
    except SQLAlchemyError as e:
        return jsonify({"error": "Database error", "message": str(e)}), 500

@api.route('/api/dashboard/study_progress')
def get_study_progress():
    """Get study progress statistics."""
    try:
        total_available = Word.query.count()
        total_studied = db.session.query(func.count(func.distinct(WordReviewItem.word_id))).scalar()
        
        return jsonify({
            "total_words_studied": total_studied,
            "total_available_words": total_available
        })
    except SQLAlchemyError as e:
        return jsonify({"error": "Database error", "message": str(e)}), 500

@api.route('/api/dashboard/quick-stats')
def get_dashboard_quick_stats():
    """Get quick overview statistics."""
    try:
        stats = get_quick_stats()
        return jsonify(stats)
    except SQLAlchemyError as e:
        return jsonify({"error": "Database error", "message": str(e)}), 500

# Words Endpoints
@api.route('/api/words', methods=['GET'])
def get_words():
    """Get all words with pagination."""
    try:
        query = Word.query
        items = query.all()
        
        # Convert SQLAlchemy objects to dictionaries and add stats
        items_dict = []
        for item in items:
            item_dict = {
                'id': item.id,
                'french': item.french,
                'english': item.english,
                'parts': item.parts_dict,
                'created_at': item.created_at.isoformat()
            }
            stats = get_word_stats(item.id)
            item_dict.update({
                'correct_count': stats['correct_count'],
                'wrong_count': stats['wrong_count']
            })
            items_dict.append(item_dict)
        
        # Manual pagination
        page = request.args.get('page', 1, type=int)
        items_per_page = 100
        start = (page - 1) * items_per_page
        end = start + items_per_page
        
        total_items = len(items_dict)
        total_pages = (total_items + items_per_page - 1) // items_per_page
        
        return jsonify({
            'items': items_dict[start:end],
            'pagination': {
                'current_page': page,
                'total_pages': total_pages,
                'total_items': total_items,
                'items_per_page': items_per_page
            }
        })
    except SQLAlchemyError as e:
        return jsonify({'error': 'Database error', 'message': str(e)}), 500

@api.route('/api/words/<int:word_id>')
def get_word(word_id):
    """Get a specific word by ID."""
    try:
        word = Word.query.get(word_id)
        if not word:
            return jsonify({"error": "Word not found"}), 404
            
        stats = get_word_stats(word_id)
        groups = Group.query.join(Group.words).filter(Word.id == word_id).all()
        
        return jsonify({
            "french": word.french,
            "english": word.english,
            "stats": stats,
            "groups": [{
                "id": group.id,
                "name": group.name
            } for group in groups]
        })
    except SQLAlchemyError as e:
        return jsonify({"error": "Database error", "message": str(e)}), 500

@api.route('/api/words', methods=['POST'])
def create_word():
    """Create a new word."""
    try:
        data = request.get_json()
        
        if not data or 'french' not in data or 'english' not in data:
            return jsonify({"error": "Missing required fields"}), 400
            
        word = Word(
            french=data['french'],
            english=data['english'],
            parts=data.get('parts', {})
        )
        
        db.session.add(word)
        db.session.commit()
        
        return jsonify({
            "id": word.id,
            "french": word.french,
            "english": word.english,
            "parts": word.parts,
            "created_at": word.created_at.isoformat()
        }), 201
        
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": "Database error", "message": str(e)}), 500

# Groups Endpoints
@api.route('/api/groups', methods=['GET'])
def get_groups():
    """Get all groups with pagination."""
    try:
        query = Group.query
        items = query.all()
        
        # Convert SQLAlchemy objects to dictionaries and add word count
        items_dict = []
        for item in items:
            item_dict = {
                'id': item.id,
                'name': item.name,
                'word_count': len(item.words),
                'created_at': item.created_at.isoformat()
            }
            items_dict.append(item_dict)
        
        # Manual pagination
        page = request.args.get('page', 1, type=int)
        items_per_page = 100
        start = (page - 1) * items_per_page
        end = start + items_per_page
        
        total_items = len(items_dict)
        total_pages = (total_items + items_per_page - 1) // items_per_page
        
        return jsonify({
            'items': items_dict[start:end],
            'pagination': {
                'current_page': page,
                'total_pages': total_pages,
                'total_items': total_items,
                'items_per_page': items_per_page
            }
        })
    except SQLAlchemyError as e:
        return jsonify({'error': 'Database error', 'message': str(e)}), 500

@api.route('/api/groups', methods=['POST'])
def create_group():
    """Create a new group."""
    try:
        data = request.get_json()
        if not data or 'name' not in data:
            return jsonify({'error': 'Missing required fields'}), 400
        
        group = Group(name=data['name'])
        db.session.add(group)
        db.session.commit()
        return jsonify({
            'id': group.id,
            'name': group.name,
            'created_at': group.created_at.isoformat()
        }), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': 'Database error', 'message': str(e)}), 500

@api.route('/api/groups/<int:group_id>')
def get_group(group_id):
    """Get a specific group by ID."""
    try:
        group = Group.query.get(group_id)
        if not group:
            return jsonify({"error": "Group not found"}), 404
            
        return jsonify({
            "id": group.id,
            "name": group.name,
            "stats": {
                "total_word_count": len(group.words)
            }
        })
    except SQLAlchemyError as e:
        return jsonify({"error": "Database error", "message": str(e)}), 500

@api.route('/api/groups/<int:group_id>/words')
def get_group_words(group_id):
    """Get words for a specific group."""
    try:
        group = Group.query.get(group_id)
        if not group:
            return jsonify({"error": "Group not found"}), 404
            
        query = Word.query.join(Word.groups).filter(Group.id == group_id)
        items = query.all()
        
        # Convert SQLAlchemy objects to dictionaries and add stats
        items_dict = []
        for item in items:
            item_dict = {
                'id': item.id,
                'french': item.french,
                'english': item.english,
                'parts': item.parts_dict,
                'created_at': item.created_at.isoformat()
            }
            stats = get_word_stats(item.id)
            item_dict.update({
                'correct_count': stats['correct_count'],
                'wrong_count': stats['wrong_count']
            })
            items_dict.append(item_dict)
        
        # Manual pagination
        page = request.args.get('page', 1, type=int)
        items_per_page = 100
        start = (page - 1) * items_per_page
        end = start + items_per_page
        
        total_items = len(items_dict)
        total_pages = (total_items + items_per_page - 1) // items_per_page
        
        return jsonify({
            'items': items_dict[start:end],
            'pagination': {
                'current_page': page,
                'total_pages': total_pages,
                'total_items': total_items,
                'items_per_page': items_per_page
            }
        })
    except SQLAlchemyError as e:
        return jsonify({"error": "Database error", "message": str(e)}), 500

@api.route('/api/groups/<int:group_id>/study_sessions')
def get_group_study_sessions(group_id):
    """Get study sessions for a specific group."""
    try:
        group = Group.query.get(group_id)
        if not group:
            return jsonify({"error": "Group not found"}), 404
            
        query = StudySession.query.filter_by(group_id=group_id)
        items = query.all()
        
        # Convert SQLAlchemy objects to dictionaries and add additional information
        items_dict = []
        for item in items:
            item_dict = {
                'id': item.id,
                'group_id': item.group_id,
                'study_activity_id': item.study_activity_id,
                'created_at': item.created_at.isoformat()
            }
            activity = StudyActivity.query.get(item.study_activity_id)
            review_count = WordReviewItem.query.filter_by(study_session_id=item.id).count()
            
            item_dict.update({
                "activity_name": activity.name if activity else None,
                "group_name": group.name,
                "start_time": item_dict["created_at"],
                "end_time": (item.created_at + timedelta(minutes=10)).isoformat(),  # Assuming 10min sessions
                "review_items_count": review_count
            })
            items_dict.append(item_dict)
        
        # Manual pagination
        page = request.args.get('page', 1, type=int)
        items_per_page = 100
        start = (page - 1) * items_per_page
        end = start + items_per_page
        
        total_items = len(items_dict)
        total_pages = (total_items + items_per_page - 1) // items_per_page
        
        return jsonify({
            'items': items_dict[start:end],
            'pagination': {
                'current_page': page,
                'total_pages': total_pages,
                'total_items': total_items,
                'items_per_page': items_per_page
            }
        })
    except SQLAlchemyError as e:
        return jsonify({"error": "Database error", "message": str(e)}), 500

@api.route('/api/study_sessions', methods=['GET', 'POST'])
def study_sessions():
    """Get all study sessions or create a new one."""
    if request.method == 'POST':
        try:
            data = request.get_json()
            
            if not data or 'group_id' not in data or 'study_activity_id' not in data:
                return jsonify({"error": "Missing required fields"}), 400
                
            group = Group.query.get(data['group_id'])
            activity = StudyActivity.query.get(data['study_activity_id'])
            
            if not group:
                return jsonify({"error": "Group not found"}), 404
            if not activity:
                return jsonify({"error": "Study activity not found"}), 404
            
            session = StudySession(
                group_id=data['group_id'],
                study_activity_id=data['study_activity_id']
            )
            db.session.add(session)
            db.session.commit()
            
            return jsonify({
                "id": session.id,
                "group_id": session.group_id,
                "study_activity_id": session.study_activity_id,
                "created_at": session.created_at.isoformat()
            }), 201
            
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({"error": "Database error", "message": str(e)}), 500
    else:
        try:
            query = StudySession.query.order_by(desc(StudySession.created_at))
            items = query.all()
            
            # Convert SQLAlchemy objects to dictionaries and add additional information
            items_dict = []
            for item in items:
                item_dict = {
                    'id': item.id,
                    'group_id': item.group_id,
                    'study_activity_id': item.study_activity_id,
                    'created_at': item.created_at.isoformat()
                }
                activity = StudyActivity.query.get(item.study_activity_id)
                group = Group.query.get(item.group_id)
                review_count = WordReviewItem.query.filter_by(study_session_id=item.id).count()
                
                item_dict.update({
                    "activity_name": activity.name if activity else None,
                    "group_name": group.name if group else None,
                    "start_time": item_dict["created_at"],
                    "end_time": (item.created_at + timedelta(minutes=10)).isoformat(),  # Assuming 10min sessions
                    "review_items_count": review_count
                })
                items_dict.append(item_dict)
            
            # Manual pagination
            page = request.args.get('page', 1, type=int)
            items_per_page = 100
            start = (page - 1) * items_per_page
            end = start + items_per_page
            
            total_items = len(items_dict)
            total_pages = (total_items + items_per_page - 1) // items_per_page
            
            return jsonify({
                'items': items_dict[start:end],
                'pagination': {
                    'current_page': page,
                    'total_pages': total_pages,
                    'total_items': total_items,
                    'items_per_page': items_per_page
                }
            })
        except SQLAlchemyError as e:
            return jsonify({"error": "Database error", "message": str(e)}), 500

@api.route('/api/study_sessions/<int:session_id>')
def get_study_session(session_id):
    """Get a specific study session."""
    try:
        session = StudySession.query.get(session_id)
        if not session:
            return jsonify({"error": "Study session not found"}), 404
            
        activity = StudyActivity.query.get(session.study_activity_id)
        group = Group.query.get(session.group_id)
        review_count = WordReviewItem.query.filter_by(study_session_id=session.id).count()
        
        return jsonify({
            "id": session.id,
            "activity_name": activity.name if activity else None,
            "group_name": group.name if group else None,
            "start_time": session.created_at.isoformat(),
            "end_time": (session.created_at + timedelta(minutes=10)).isoformat(),  # Assuming 10min sessions
            "review_items_count": review_count
        })
    except SQLAlchemyError as e:
        return jsonify({"error": "Database error", "message": str(e)}), 500

@api.route('/api/study_sessions/<int:session_id>/words')
def get_session_words(session_id):
    """Get words reviewed in a specific study session."""
    try:
        session = StudySession.query.get(session_id)
        if not session:
            return jsonify({"error": "Study session not found"}), 404
            
        # Get words that have been reviewed in this session
        query = Word.query.join(WordReviewItem).filter(WordReviewItem.study_session_id == session_id)
        items = query.all()
        
        # Convert SQLAlchemy objects to dictionaries and add stats
        items_dict = []
        for item in items:
            item_dict = {
                'id': item.id,
                'french': item.french,
                'english': item.english,
                'parts': item.parts_dict,
                'created_at': item.created_at.isoformat()
            }
            stats = get_word_stats(item.id)
            item_dict.update({
                'correct_count': stats['correct_count'],
                'wrong_count': stats['wrong_count']
            })
            items_dict.append(item_dict)
        
        # Manual pagination
        page = request.args.get('page', 1, type=int)
        items_per_page = 100
        start = (page - 1) * items_per_page
        end = start + items_per_page
        
        total_items = len(items_dict)
        total_pages = (total_items + items_per_page - 1) // items_per_page
        
        return jsonify({
            'items': items_dict[start:end],
            'pagination': {
                'current_page': page,
                'total_pages': total_pages,
                'total_items': total_items,
                'items_per_page': items_per_page
            }
        })
    except SQLAlchemyError as e:
        return jsonify({"error": "Database error", "message": str(e)}), 500

@api.route('/api/study_sessions/<int:session_id>/words/<int:word_id>/review', methods=['POST'])
def record_word_review(session_id, word_id):
    """Record a word review for a study session."""
    try:
        data = request.get_json()
        
        if not data or 'is_correct' not in data:
            return jsonify({"error": "Missing required fields"}), 400
            
        session = StudySession.query.get(session_id)
        word = Word.query.get(word_id)
        
        if not session:
            return jsonify({"error": "Study session not found"}), 404
        if not word:
            return jsonify({"error": "Word not found"}), 404
            
        review = WordReviewItem(
            study_session_id=session_id,
            word_id=word_id,
            is_correct=data['is_correct']
        )
        
        db.session.add(review)
        db.session.commit()
        
        return jsonify({
            "id": review.id,
            "study_session_id": review.study_session_id,
            "word_id": review.word_id,
            "is_correct": review.is_correct,
            "created_at": review.created_at.isoformat()
        }), 201
        
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": "Database error", "message": str(e)}), 500

# System Reset Endpoints
@api.route('/api/reset_history', methods=['POST'])
def reset_history():
    """Reset study history by removing all study sessions and reviews."""
    try:
        WordReviewItem.query.delete()
        StudySession.query.delete()
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Study history has been reset"
        })
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": "Database error", "message": str(e)}), 500

@api.route('/api/full_reset', methods=['POST'])
def full_reset():
    """Reset entire system by removing all data."""
    try:
        WordReviewItem.query.delete()
        StudySession.query.delete()
        StudyActivity.query.delete()
        Group.query.delete()
        Word.query.delete()
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "System has been fully reset"
        })
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": "Database error", "message": str(e)}), 500

# Study Activities Endpoints
@api.route('/api/study_activities/<int:activity_id>')
def get_study_activity(activity_id):
    """Get a specific study activity."""
    try:
        activity = StudyActivity.query.get(activity_id)
        if not activity:
            return jsonify({"error": "Study activity not found"}), 404
            
        return jsonify({
            "id": activity.id,
            "name": activity.name,
            "thumbnail_url": "https://example.com/thumbnail.jpg",  # Placeholder
            "description": "Practice your vocabulary with flashcards"  # Placeholder
        })
    except SQLAlchemyError as e:
        return jsonify({"error": "Database error", "message": str(e)}), 500

@api.route('/api/study_activities/<int:activity_id>/study_sessions')
def get_activity_study_sessions(activity_id):
    """Get study sessions for a specific activity."""
    try:
        activity = StudyActivity.query.get(activity_id)
        if not activity:
            return jsonify({"error": "Study activity not found"}), 404
            
        query = StudySession.query.filter_by(study_activity_id=activity_id)
        items = query.all()
        
        # Convert SQLAlchemy objects to dictionaries and add additional information
        items_dict = []
        for item in items:
            item_dict = {
                'id': item.id,
                'group_id': item.group_id,
                'study_activity_id': item.study_activity_id,
                'created_at': item.created_at.isoformat()
            }
            group = Group.query.get(item.group_id)
            review_count = WordReviewItem.query.filter_by(study_session_id=item.id).count()
            
            item_dict.update({
                "activity_name": activity.name,
                "group_name": group.name if group else None,
                "start_time": item_dict["created_at"],
                "end_time": (item.created_at + timedelta(minutes=10)).isoformat(),  # Assuming 10min sessions
                "review_items_count": review_count
            })
            items_dict.append(item_dict)
        
        # Manual pagination
        page = request.args.get('page', 1, type=int)
        items_per_page = 100
        start = (page - 1) * items_per_page
        end = start + items_per_page
        
        total_items = len(items_dict)
        total_pages = (total_items + items_per_page - 1) // items_per_page
        
        return jsonify({
            'items': items_dict[start:end],
            'pagination': {
                'current_page': page,
                'total_pages': total_pages,
                'total_items': total_items,
                'items_per_page': items_per_page
            }
        })
    except SQLAlchemyError as e:
        return jsonify({"error": "Database error", "message": str(e)}), 500

@api.route('/api/study_activities', methods=['POST'])
def create_study_activity():
    """Create a new study activity."""
    try:
        data = request.get_json()
        
        if not data or 'name' not in data:
            return jsonify({"error": "Missing required fields"}), 400
            
        activity = StudyActivity(name=data['name'])
        db.session.add(activity)
        db.session.commit()
        
        return jsonify({
            "id": activity.id,
            "name": activity.name,
            "created_at": activity.created_at.isoformat()
        }), 201
        
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": "Database error", "message": str(e)}), 500
