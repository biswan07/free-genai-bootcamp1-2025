from flask import Blueprint, jsonify, request
from .models import db, Word, Group, StudySession, StudyActivity, WordReviewItem
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from .utils import get_word_stats, get_study_streak_days, get_quick_stats
from app.writing_practice import generate_writing_prompts, evaluate_writing

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
        
        pagination = Word.query.paginate(
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

# Quiz Endpoints
@api.route('/api/quiz/generate', methods=['POST'])
def generate_quiz():
    """Generate a quiz with multiple choice questions."""
    try:
        data = request.get_json()
        
        if not data or 'question_count' not in data or 'study_activity_id' not in data:
            return jsonify({"error": "Missing required fields"}), 400
            
        question_count = min(int(data['question_count']), 20)  # Limit to 20 questions max
        study_activity_id = int(data['study_activity_id'])
        
        # Check if study activity exists
        activity = StudyActivity.query.get(study_activity_id)
        if not activity:
            return jsonify({"error": "Study activity not found"}), 404
        
        # Get words based on group_id if provided, otherwise use all words
        if 'group_id' in data and data['group_id']:
            group_id = int(data['group_id'])
            group = Group.query.get(group_id)
            if not group:
                return jsonify({"error": "Group not found"}), 404
                
            words = Word.query.join(Word.groups).filter(Group.id == group_id).all()
        else:
            words = Word.query.all()
        
        if not words:
            return jsonify({"error": "No words available for quiz"}), 400
            
        # Shuffle words and select up to question_count
        import random
        selected_words = random.sample(words, min(len(words), question_count))
        
        # Create a new study session
        session = StudySession(
            study_activity_id=study_activity_id,
            group_id=data.get('group_id', 1)  # Default to group_id 1 if not provided
        )
        db.session.add(session)
        db.session.commit()
        
        # Generate multiple choice questions
        questions = []
        for word in selected_words:
            # Get 3 random incorrect options
            incorrect_options = [w.english for w in words if w.id != word.id]
            if len(incorrect_options) < 3:
                # If not enough words, duplicate some
                while len(incorrect_options) < 3:
                    incorrect_options.append(random.choice([w.english for w in words if w.id != word.id]))
            
            # Select 3 random incorrect options
            random.shuffle(incorrect_options)
            options = incorrect_options[:3] + [word.english]
            random.shuffle(options)
            
            questions.append({
                "word_id": word.id,
                "question": f"What is the English translation of '{word.french}'?",
                "options": options,
                "correct_answer": word.english
            })
        
        # Store questions in session for later reference
        # In a real app, this would be stored in a database
        import json
        session.questions = json.dumps(questions)
        db.session.commit()
        
        return jsonify({
            "session_id": session.id,
            "question_count": len(questions),
            "message": "Quiz generated successfully"
        }), 201
        
    except Exception as e:
        import traceback
        print(f"Error generating quiz: {str(e)}")
        print(traceback.format_exc())
        db.session.rollback()
        return jsonify({"error": "Failed to generate quiz", "message": str(e)}), 500

@api.route('/api/quiz/answer', methods=['POST'])
def submit_quiz_answer():
    """Submit an answer for a quiz question."""
    try:
        data = request.get_json()
        
        if not data or 'session_id' not in data or 'question_index' not in data or 'selected_answer' not in data:
            return jsonify({"error": "Missing required fields"}), 400
            
        session_id = int(data['session_id'])
        question_index = int(data['question_index'])
        selected_answer = data['selected_answer']
        
        # Get the session
        session = StudySession.query.get(session_id)
        if not session:
            return jsonify({"error": "Session not found"}), 404
            
        # Get questions from session
        import json
        if not hasattr(session, 'questions') or not session.questions:
            return jsonify({"error": "No questions found for this session"}), 400
            
        questions = json.loads(session.questions)
        
        if question_index < 0 or question_index >= len(questions):
            return jsonify({"error": "Invalid question index"}), 400
            
        # Get the question
        question = questions[question_index]
        correct_answer = question['correct_answer']
        is_correct = selected_answer == correct_answer
        
        # Update the question with user's answer
        question['user_answer'] = selected_answer
        question['is_correct'] = is_correct
        
        # Record the word review
        word = Word.query.get(question['word_id'])
        if word:
            review = WordReviewItem(
                study_session_id=session_id,
                word_id=word.id,
                is_correct=is_correct
            )
            db.session.add(review)
        
        # Update questions in session
        questions[question_index] = question
        session.questions = json.dumps(questions)
        db.session.commit()
        
        # Provide feedback
        explanation = f"The correct translation of '{word.french}' is '{correct_answer}'."
        
        return jsonify({
            "is_correct": is_correct,
            "correct_answer": correct_answer,
            "explanation": explanation
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to submit answer", "message": str(e)}), 500

@api.route('/api/quiz/summary/<int:session_id>')
def get_quiz_summary(session_id):
    """Get a summary of a quiz session."""
    try:
        session = StudySession.query.get(session_id)
        if not session:
            return jsonify({"error": "Session not found"}), 404
            
        # Get questions from session
        import json
        if not hasattr(session, 'questions') or not session.questions:
            return jsonify({"error": "No questions found for this session"}), 400
            
        questions = json.loads(session.questions)
        
        # Calculate stats
        answered_questions = [q for q in questions if 'user_answer' in q]
        correct_answers = sum(1 for q in answered_questions if q.get('is_correct', False))
        total_questions = len(questions)
        accuracy = round((correct_answers / total_questions * 100) if total_questions > 0 else 0)
        
        return jsonify({
            "session_id": session_id,
            "total_questions": total_questions,
            "answered_questions": len(answered_questions),
            "correct_answers": correct_answers,
            "accuracy": accuracy,
            "questions": questions
        })
        
    except Exception as e:
        return jsonify({"error": "Failed to get quiz summary", "message": str(e)}), 500

# Writing Practice Endpoints
@api.route('/api/writing/prompts', methods=['GET'])
def get_writing_prompts():
    """Get a list of writing prompts."""
    try:
        count = request.args.get('count', 10, type=int)
        level = request.args.get('level', 'intermediate')
        
        prompts = generate_writing_prompts(count=count, language_level=level)
        
        return jsonify({
            "prompts": prompts,
            "count": len(prompts)
        }), 200
        
    except Exception as e:
        return jsonify({"error": "Failed to generate writing prompts", "message": str(e)}), 500

@api.route('/api/writing/submit', methods=['POST'])
def submit_writing():
    """Submit a writing assignment for evaluation."""
    try:
        data = request.get_json()
        
        if not data or 'prompt' not in data or 'text' not in data:
            return jsonify({"error": "Missing required fields"}), 400
            
        prompt = data['prompt']
        text = data['text']
        level = data.get('level', 'intermediate')
        study_activity_id = data.get('study_activity_id')
        
        # Validate text length
        word_count = len(text.split())
        if word_count < 50:
            return jsonify({"error": "Writing is too short", "message": "Please write at least 50 words"}), 400
        if word_count > 200:
            return jsonify({"error": "Writing is too long", "message": "Please write no more than 200 words"}), 400
        
        # Evaluate the writing
        evaluation = evaluate_writing(prompt, text, language_level=level)
        
        # Create a new study session if study_activity_id is provided
        if study_activity_id:
            try:
                study_activity_id = int(study_activity_id)
                
                # Check if study activity exists
                activity = StudyActivity.query.get(study_activity_id)
                if not activity:
                    return jsonify({"error": "Study activity not found"}), 404
                
                # Create a new study session
                session = StudySession(
                    study_activity_id=study_activity_id,
                    group_id=data.get('group_id', 1)  # Default to group_id 1 if not provided
                )
                
                # Store the writing submission and evaluation
                session_data = {
                    "prompt": prompt,
                    "text": text,
                    "evaluation": evaluation
                }
                
                session.questions = json.dumps(session_data)
                db.session.add(session)
                db.session.commit()
                
                # Add session_id to the response
                evaluation["session_id"] = session.id
                
            except Exception as e:
                print(f"Error creating study session: {e}")
                # Continue with the evaluation even if session creation fails
        
        return jsonify(evaluation), 200
        
    except Exception as e:
        return jsonify({"error": "Failed to evaluate writing", "message": str(e)}), 500

@api.route('/api/writing/summary/<int:session_id>', methods=['GET'])
def get_writing_summary(session_id):
    """Get a summary of a writing session."""
    try:
        session = StudySession.query.get(session_id)
        if not session:
            return jsonify({"error": "Session not found"}), 404
            
        if not session.questions:
            return jsonify({"error": "No writing data found for this session"}), 404
            
        session_data = json.loads(session.questions)
        
        return jsonify({
            "session_id": session.id,
            "prompt": session_data.get("prompt", ""),
            "text": session_data.get("text", ""),
            "evaluation": session_data.get("evaluation", {}),
            "created_at": session.created_at.isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({"error": "Failed to get writing summary", "message": str(e)}), 500
