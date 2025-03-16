from flask import Blueprint, jsonify, request
from ..models import Group
import logging

groups_bp = Blueprint('groups', __name__)

@groups_bp.route('')
def get_groups():
    page = request.args.get('page', 1, type=int)
    per_page = 100
    
    # Debug: Check all groups in the database
    all_groups = Group.query.all()
    print(f"DEBUG: Found {len(all_groups)} groups in database:")
    for group in all_groups:
        print(f"DEBUG: Group ID: {group.id}, Name: {group.name}")
    
    # Use the paginate method
    pagination = Group.query.paginate(page=page, per_page=per_page)
    print(f"DEBUG: Pagination items: {len(pagination.items)}")
    
    groups = [{
        "id": group.id,
        "name": group.name
    } for group in pagination.items]
    
    response = {
        "groups": groups,
        "current_page": pagination.page,
        "pages": pagination.pages,
        "total": pagination.total
    }
    
    print(f"DEBUG: Response: {response}")
    return jsonify(response)
