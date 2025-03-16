from flask import Blueprint, jsonify, request
from .models import db, Word, Group, StudySession, StudyActivity, WordReviewItem
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from .utils import get_word_stats, get_study_streak_days, get_quick_stats
from .multiple_choice import generate_quiz, check_answer, get_quiz_summary
import json

api = Blueprint('api', __name__)

# Global dictionary to store quiz states
quiz_states = {}

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
        last_session = StudySession.query.order_by(StudySession.created_at.desc()).first()
        
        if not last_session:
            return jsonify({
                "message": "No study sessions yet",
                "has_sessions": False
            })
        
        # Get associated activity and group
        activity = StudyActivity.query.get(last_session.study_activity_id)
        group = Group.query.get(last_session.group_id) if last_session.group_id else None
        
        # Calculate session stats
        word_reviews = WordReviewItem.query.filter_by(study_session_id=last_session.id).all()
        total_words = len(word_reviews)
        correct_words = len([r for r in word_reviews if r.is_correct])
        
        return jsonify({
            "has_sessions": True,
            "id": last_session.id,
            "created_at": last_session.created_at.isoformat(),
            "activity_name": activity.name if activity else None,
            "group_name": group.name if group else None,
            "stats": {
                "total_words": total_words,
                "correct_words": correct_words,
                "accuracy": round((correct_words / total_words * 100) if total_words > 0 else 0, 1)
            }
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

@api.route('/api/dashboard/quick_stats')
def get_dashboard_quick_stats():
    """Get quick overview statistics."""
    try:
        # Get total words
        total_words = Word.query.count()
        
        # Get total groups
        total_groups = Group.query.count()
        
        # Get total study sessions
        total_sessions = StudySession.query.count()
        
        # Calculate study streak (simplified version)
        last_session = StudySession.query.order_by(StudySession.created_at.desc()).first()
        study_streak = 0
        if last_session:
            today = datetime.utcnow().date()
            last_study_date = last_session.created_at.date()
            if last_study_date == today:
                study_streak = 1
        
        # Get words studied (unique words that have been reviewed)
        words_studied = WordReviewItem.query.with_entities(WordReviewItem.word_id).distinct().count()
        
        return jsonify({
            "total_words": total_words,
            "total_groups": total_groups,
            "study_sessions": total_sessions,
            "study_streak": study_streak,
            "words_studied": words_studied
        })
    except SQLAlchemyError as e:
        return jsonify({"error": "Database error", "message": str(e)}), 500

# Words Endpoints
@api.route('/api/words', methods=['GET'])
def get_words():
    """Get all words with pagination."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        group_id = request.args.get('group_id', type=int)
        
        # Base query
        query = Word.query
        
        # Filter by group if group_id is provided
        if group_id:
            group = Group.query.get(group_id)
            if not group:
                return jsonify({"error": "Group not found"}), 404
                
            query = query.join(Word.groups).filter(Group.id == group_id)
        
        # Apply pagination
        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return jsonify({
            'words': [{
                'id': word.id,
                'english': word.english,
                'french': word.french,
                'stats': word.stats
            } for word in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': pagination.page
        })
    except SQLAlchemyError as e:
        return jsonify({"error": "Database error", "message": str(e)}), 500

@api.route('/api/words/<int:word_id>', methods=['GET', 'PUT'])
def word_operations(word_id):
    """Get or update a specific word by ID."""
    if request.method == 'GET':
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
    elif request.method == 'PUT':
        try:
            data = request.get_json()
            word = Word.query.get(word_id)
            
            if not word:
                return jsonify({"error": "Word not found"}), 404
                
            # Update basic word properties if provided
            if 'french' in data:
                word.french = data['french']
            if 'english' in data:
                word.english = data['english']
            if 'parts' in data:
                word.parts = data['parts']
                
            # Update group associations if group_ids is provided
            if 'group_ids' in data and isinstance(data['group_ids'], list):
                # Clear existing group associations
                word.groups = []
                
                # Add the word to specified groups
                for group_id in data['group_ids']:
                    group = Group.query.get(group_id)
                    if group:
                        word.groups.append(group)
            
            db.session.commit()
            
            # Get the updated groups the word belongs to
            groups = Group.query.join(Group.words).filter(Word.id == word.id).all()
            
            return jsonify({
                "id": word.id,
                "french": word.french,
                "english": word.english,
                "parts": word.parts,
                "updated_at": word.created_at.isoformat(),
                "groups": [{
                    "id": group.id,
                    "name": group.name
                } for group in groups]
            })
        except SQLAlchemyError as e:
            db.session.rollback()
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
        
        # Add the word to specified groups if group_ids is provided
        if 'group_ids' in data and isinstance(data['group_ids'], list):
            for group_id in data['group_ids']:
                group = Group.query.get(group_id)
                if group:
                    word.groups.append(group)
        
        db.session.add(word)
        db.session.commit()
        
        # Get the groups the word was added to
        groups = Group.query.join(Group.words).filter(Word.id == word.id).all()
        
        return jsonify({
            "id": word.id,
            "french": word.french,
            "english": word.english,
            "parts": word.parts,
            "created_at": word.created_at.isoformat(),
            "groups": [{
                "id": group.id,
                "name": group.name
            } for group in groups]
        }), 201
        
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": "Database error", "message": str(e)}), 500

# Groups Endpoints
@api.route('/api/groups', methods=['GET'])
def get_groups():
    """Get all groups with pagination."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        pagination = Group.query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return jsonify({
            'groups': [{
                'id': group.id,
                'name': group.name,
                'word_count': len(group.words)
            } for group in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': pagination.page
        })
    except SQLAlchemyError as e:
        return jsonify({"error": "Database error", "message": str(e)}), 500

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
            },
            "words": [{
                "id": word.id,
                "english": word.english,
                "french": word.french,
                "stats": word.stats
            } for word in group.words]
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
            
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Use Word query with join instead of group.words
        pagination = Word.query.join(Word.groups).filter(Group.id == group_id).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return jsonify({
            'words': [{
                'id': word.id,
                'english': word.english,
                'french': word.french
            } for word in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': pagination.page
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
            
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        pagination = StudySession.query.filter_by(group_id=group_id).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        sessions = []
        for session in pagination.items:
            activity = StudyActivity.query.get(session.study_activity_id)
            reviews = WordReviewItem.query.filter_by(study_session_id=session.id).all()
            total_words = len(reviews)
            correct_words = len([r for r in reviews if r.is_correct])
            
            sessions.append({
                'id': session.id,
                'created_at': session.created_at.isoformat(),
                'activity_name': activity.name if activity else None,
                'stats': {
                    'total_words': total_words,
                    'correct_words': correct_words,
                    'accuracy': round((correct_words / total_words * 100) if total_words > 0 else 0, 1)
                }
            })
        
        return jsonify({
            'sessions': sessions,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': pagination.page
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
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            
            pagination = StudySession.query.paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )
            
            sessions = []
            for session in pagination.items:
                activity = StudyActivity.query.get(session.study_activity_id)
                group = Group.query.get(session.group_id)
                reviews = WordReviewItem.query.filter_by(study_session_id=session.id).all()
                total_words = len(reviews)
                correct_words = len([r for r in reviews if r.is_correct])
                
                sessions.append({
                    'id': session.id,
                    'created_at': session.created_at.isoformat(),
                    'activity_name': activity.name if activity else None,
                    'group_name': group.name if group else None,
                    'stats': {
                        'total_words': total_words,
                        'correct_words': correct_words,
                        'accuracy': round((correct_words / total_words * 100) if total_words > 0 else 0, 1)
                    }
                })
            
            return jsonify({
                'sessions': sessions,
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': pagination.page
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
        reviews = WordReviewItem.query.filter_by(study_session_id=session.id).all()
        total_words = len(reviews)
        correct_words = len([r for r in reviews if r.is_correct])
        
        return jsonify({
            "id": session.id,
            "created_at": session.created_at.isoformat(),
            "activity_name": activity.name if activity else None,
            "group_name": group.name if group else None,
            "stats": {
                "total_words": total_words,
                "correct_words": correct_words,
                "accuracy": round((correct_words / total_words * 100) if total_words > 0 else 0, 1)
            }
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
            
        reviews = WordReviewItem.query.filter_by(study_session_id=session_id).all()
        words = []
        
        for review in reviews:
            word = Word.query.get(review.word_id)
            if word:
                words.append({
                    'id': word.id,
                    'english': word.english,
                    'french': word.french,
                    'is_correct': review.is_correct
                })
        
        return jsonify({
            'words': words,
            'total': len(words)
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

# Word Review Items Endpoint
@api.route('/api/word_review_items', methods=['POST'])
def create_word_review():
    """Create a new word review item."""
    try:
        data = request.get_json()
        
        if not data or 'word_id' not in data or 'study_session_id' not in data or 'correct' not in data:
            return jsonify({"error": "Missing required fields"}), 400
            
        session = StudySession.query.get(data['study_session_id'])
        word = Word.query.get(data['word_id'])
        
        if not session:
            return jsonify({"error": "Study session not found"}), 404
        if not word:
            return jsonify({"error": "Word not found"}), 404
            
        review = WordReviewItem(
            study_session_id=data['study_session_id'],
            word_id=data['word_id'],
            is_correct=data['correct']
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
@api.route('/api/study_activities', methods=['GET'])
def get_study_activities():
    """Get all study activities."""
    try:
        activities = StudyActivity.query.all()
        descriptions = {
            'Flashcards': 'Practice vocabulary with interactive flashcards. Perfect for memorizing new words and their meanings.',
            'Multiple Choice': 'Test your knowledge with multiple choice questions. Great for reviewing vocabulary and grammar.',
            'Writing Practice': 'Improve your writing skills by practicing sentence construction and vocabulary usage.'
        }
        return jsonify([{
            'id': activity.id,
            'name': activity.name,
            'description': descriptions.get(activity.name, activity.description)
        } for activity in activities])
    except SQLAlchemyError as e:
        return jsonify({"error": "Database error", "message": str(e)}), 500

@api.route('/api/study_activities/<int:activity_id>')
def get_study_activity(activity_id):
    """Get a specific study activity."""
    try:
        activity = StudyActivity.query.get(activity_id)
        if not activity:
            return jsonify({"error": "Study activity not found"}), 404
            
        descriptions = {
            'Flashcards': 'Practice vocabulary with interactive flashcards. Perfect for memorizing new words and their meanings.',
            'Multiple Choice': 'Test your knowledge with multiple choice questions. Great for reviewing vocabulary and grammar.',
            'Writing Practice': 'Improve your writing skills by practicing sentence construction and vocabulary usage.'
        }
        
        return jsonify({
            "id": activity.id,
            "name": activity.name,
            "description": descriptions.get(activity.name, activity.description)
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
            
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        pagination = StudySession.query.filter_by(study_activity_id=activity_id).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        sessions = []
        for session in pagination.items:
            group = Group.query.get(session.group_id)
            reviews = WordReviewItem.query.filter_by(study_session_id=session.id).all()
            total_words = len(reviews)
            correct_words = len([r for r in reviews if r.is_correct])
            
            sessions.append({
                'id': session.id,
                'created_at': session.created_at.isoformat(),
                'activity_name': activity.name,
                'group_name': group.name if group else None,
                'stats': {
                    'total_words': total_words,
                    'correct_words': correct_words,
                    'accuracy': round((correct_words / total_words * 100) if total_words > 0 else 0, 1)
                }
            })
        
        return jsonify({
            'sessions': sessions,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': pagination.page
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

# Multiple Choice Quiz Endpoints
@api.route('/api/quiz/generate', methods=['POST'])
def generate_quiz_endpoint():
    """Generate a multiple-choice quiz based on words."""
    try:
        data = request.get_json()
        
        # Get words to use for the quiz
        words = []
        if 'group_id' in data:
            # Get words from a specific group
            group = Group.query.get(data['group_id'])
            if not group:
                return jsonify({"error": "Group not found"}), 404
            
            words = [
                {
                    "id": word.id,
                    "french": word.french,
                    "english": word.english,
                    "parts": word.parts
                } for word in group.words
            ]
        elif 'word_ids' in data and isinstance(data['word_ids'], list):
            # Get specific words by IDs
            word_objects = Word.query.filter(Word.id.in_(data['word_ids'])).all()
            words = [
                {
                    "id": word.id,
                    "french": word.french,
                    "english": word.english,
                    "parts": word.parts
                } for word in word_objects
            ]
        else:
            # Get all words
            word_objects = Word.query.all()
            words = [
                {
                    "id": word.id,
                    "french": word.french,
                    "english": word.english,
                    "parts": word.parts
                } for word in word_objects
            ]
        
        if not words:
            return jsonify({"error": "No words available for quiz generation"}), 400
        
        # Generate the quiz
        question_count = data.get('question_count', 10)
        quiz_state = generate_quiz(words, question_count)
        
        # Create a new study session for the quiz
        study_session = StudySession(
            study_activity_id=data.get('study_activity_id', 1),
            group_id=data.get('group_id', 1)
        )
        db.session.add(study_session)
        db.session.commit()
        
        # Store the quiz state in the global dictionary
        quiz_id = str(study_session.id)
        quiz_states[quiz_id] = quiz_state
        
        return jsonify({
            "session_id": study_session.id,
            "questions": quiz_state["questions"],
            "total_questions": len(quiz_state["questions"])
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error generating quiz: {str(e)}")
        return jsonify({"error": "Failed to generate quiz", "message": str(e)}), 500

@api.route('/api/quiz/answer', methods=['POST'])
def submit_quiz_answer():
    """Submit an answer for a quiz question."""
    try:
        data = request.get_json()
        
        session_id = data.get('session_id')
        question_index = data.get('question_index')
        selected_answer = data.get('selected_answer')
        
        if not all([session_id, question_index is not None, selected_answer]):
            return jsonify({"error": "Missing required fields"}), 400
        
        # Get the study session
        study_session = StudySession.query.get(session_id)
        if not study_session:
            return jsonify({"error": "Study session not found"}), 404
        
        # Get the quiz state from the global dictionary
        quiz_id = str(session_id)
        quiz_state = quiz_states.get(quiz_id)
        
        if not quiz_state:
            return jsonify({"error": "Quiz state not found"}), 404
        
        # Check the answer
        updated_quiz_state = check_answer(quiz_state, question_index, selected_answer)
        
        # Update the quiz state in the global dictionary
        quiz_states[quiz_id] = updated_quiz_state
        
        # Get the current question
        question = updated_quiz_state["questions"][question_index]
        
        return jsonify({
            "is_correct": question.get("user_answer") == question.get("correct_answer"),
            "correct_answer": question.get("correct_answer"),
            "explanation": question.get("explanation", ""),
            "correct_count": updated_quiz_state.get("correct_count", 0),
            "incorrect_count": updated_quiz_state.get("incorrect_count", 0)
        })
        
    except Exception as e:
        print(f"Error submitting answer: {str(e)}")
        return jsonify({"error": "Failed to submit answer", "message": str(e)}), 500

@api.route('/api/quiz/summary/<int:session_id>', methods=['GET'])
def get_quiz_summary_endpoint(session_id):
    """Get a summary of the quiz results."""
    try:
        # Get the study session
        study_session = StudySession.query.get(session_id)
        if not study_session:
            return jsonify({"error": "Study session not found"}), 404
        
        # Get the quiz state from the global dictionary
        quiz_id = str(session_id)
        quiz_state = quiz_states.get(quiz_id)
        
        if not quiz_state:
            return jsonify({"error": "Quiz state not found"}), 404
        
        # Get the quiz summary
        summary = get_quiz_summary(quiz_state)
        
        return jsonify(summary)
        
    except Exception as e:
        print(f"Error getting quiz summary: {str(e)}")
        return jsonify({"error": "Failed to get quiz summary", "message": str(e)}), 500
