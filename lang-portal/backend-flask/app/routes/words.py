from flask import Blueprint, jsonify, request
from ..models import Word

words_bp = Blueprint('words', __name__)

@words_bp.route('')
def get_words():
    page = request.args.get('page', 1, type=int)
    per_page = 100
    
    pagination = Word.query.paginate(page=page, per_page=per_page)
    
    items = [{
        "french": word.french,
        "english": word.english,
        "correct_count": word.stats["correct_count"],
        "wrong_count": word.stats["wrong_count"]
    } for word in pagination.items]
    
    return jsonify({
        "items": items,
        "pagination": {
            "current_page": pagination.page,
            "total_pages": pagination.pages,
            "total_items": pagination.total,
            "items_per_page": per_page
        }
    })

@words_bp.route('/<int:id>')
def get_word(id):
    word = Word.query.get_or_404(id)
    
    return jsonify({
        "french": word.french,
        "english": word.english,
        "stats": word.stats,
        "groups": [{
            "id": group.id,
            "name": group.name
        } for group in word.groups]
    })
