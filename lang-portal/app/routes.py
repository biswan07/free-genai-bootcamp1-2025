from flask import Blueprint, jsonify, request
from .models import db, Word, Group, StudySession, StudyActivity, WordReviewItem

api = Blueprint('api', __name__)

@api.route('/api/words', methods=['GET'])
def get_words():
    """Get all words."""
    words = Word.query.all()
    return jsonify([{
        'id': word.id,
        'french': word.french,
        'english': word.english,
        'parts': word.parts_dict,
        'created_at': word.created_at.isoformat()
    } for word in words])

@api.route('/api/words', methods=['POST'])
def create_word():
    """Create a new word."""
    data = request.get_json()
    word = Word(
        french=data['french'],
        english=data['english'],
        parts_dict=data.get('parts')
    )
    db.session.add(word)
    db.session.commit()
    return jsonify({
        'id': word.id,
        'french': word.french,
        'english': word.english,
        'parts': word.parts_dict,
        'created_at': word.created_at.isoformat()
    }), 201

@api.route('/api/groups', methods=['GET'])
def get_groups():
    """Get all groups."""
    groups = Group.query.all()
    return jsonify([{
        'id': group.id,
        'name': group.name,
        'word_count': group.word_count,
        'created_at': group.created_at.isoformat()
    } for group in groups])

@api.route('/api/groups', methods=['POST'])
def create_group():
    """Create a new group."""
    data = request.get_json()
    group = Group(name=data['name'])
    db.session.add(group)
    db.session.commit()
    return jsonify({
        'id': group.id,
        'name': group.name,
        'created_at': group.created_at.isoformat()
    }), 201

@api.route('/api/study-sessions', methods=['POST'])
def create_study_session():
    """Create a new study session."""
    data = request.get_json()
    session = StudySession(
        group_id=data['group_id'],
        study_activity_id=data['study_activity_id']
    )
    db.session.add(session)
    db.session.commit()
    return jsonify({
        'id': session.id,
        'group_id': session.group_id,
        'study_activity_id': session.study_activity_id,
        'created_at': session.created_at.isoformat()
    }), 201

@api.route('/api/word-reviews', methods=['POST'])
def add_word_review():
    """Add a word review."""
    data = request.get_json()
    review = WordReviewItem(
        word_id=data['word_id'],
        study_session_id=data['study_session_id'],
        correct=data['correct']
    )
    db.session.add(review)
    db.session.commit()
    return jsonify({
        'id': review.id,
        'word_id': review.word_id,
        'study_session_id': review.study_session_id,
        'correct': review.correct,
        'created_at': review.created_at.isoformat()
    }), 201
