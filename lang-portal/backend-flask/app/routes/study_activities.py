from flask import Blueprint, jsonify, request
from ..models import db, StudyActivity, StudySession
from datetime import datetime

study_activities_bp = Blueprint('study_activities', __name__)

@study_activities_bp.route('/<int:id>')
def get_study_activity(id):
    activity = StudyActivity.query.get_or_404(id)
    return jsonify({
        "id": activity.id,
        "name": activity.name,
        "thumbnail_url": activity.thumbnail_url,
        "description": activity.description
    })

@study_activities_bp.route('/<int:id>/study_sessions')
def get_study_sessions(id):
    page = request.args.get('page', 1, type=int)
    per_page = 100
    
    query = StudySession.query.filter_by(study_activity_id=id)\
        .order_by(StudySession.created_at.desc())
    
    pagination = query.paginate(page=page, per_page=per_page)
    
    items = [{
        "id": session.id,
        "activity_name": session.study_activity.name,
        "group_name": session.group.name,
        "start_time": session.created_at.isoformat(),
        "end_time": (session.created_at + session.duration).isoformat() if hasattr(session, 'duration') else None,
        "review_items_count": len(session.review_items)
    } for session in pagination.items]
    
    return jsonify({
        "items": items,
        "pagination": {
            "current_page": pagination.page,
            "total_pages": pagination.pages,
            "total_items": pagination.total,
            "items_per_page": per_page
        }
    })

@study_activities_bp.route('', methods=['POST'])
def create_study_activity():
    data = request.get_json()
    
    if not data or 'group_id' not in data or 'study_activity_id' not in data:
        return jsonify({"error": "Missing required fields"}), 400
    
    session = StudySession(
        group_id=data['group_id'],
        study_activity_id=data['study_activity_id'],
        created_at=datetime.utcnow()
    )
    
    db.session.add(session)
    db.session.commit()
    
    return jsonify({
        "id": session.id,
        "group_id": session.group_id
    }), 201
