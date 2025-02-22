from flask import Blueprint, jsonify, request
from ..models import Group

groups_bp = Blueprint('groups', __name__)

@groups_bp.route('')
def get_groups():
    page = request.args.get('page', 1, type=int)
    per_page = 100
    
    pagination = Group.query.paginate(page=page, per_page=per_page)
    
    items = [{
        "id": group.id,
        "name": group.name,
        "word_count": group.word_count
    } for group in pagination.items]
    
    return jsonify({
        "items": items,
        "pagination": {
            "current_page": pagination.page,
            "total_pages": pagination.pages,
            "total_items": pagination.total,
            "items_per_page": per_page
        }
    })
