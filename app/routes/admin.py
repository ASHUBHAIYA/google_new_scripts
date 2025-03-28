from flask import Blueprint, request
from app.models import Article
from app import db

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/articles', methods=['POST'])
def create_article():
    data = request.json
    new_article = Article(**data)
    db.session.add(new_article)
    db.session.commit()
    return {'message': 'Article created successfully'}, 201

@admin_bp.route('/admin/articles/<int:id>', methods=['PUT'])
def update_article(id):
    article = Article.query.get_or_404(id)
    for key, value in request.json.items():
        setattr(article, key, value)
    db.session.commit()
    return {'message': 'Article updated successfully'}, 200

@admin_bp.route('/admin/articles/<int:id>', methods=['DELETE'])
def delete_article(id):
    article = Article.query.get_or_404(id)
    db.session.delete(article)
    db.session.commit()
    return {'message': 'Article deleted successfully'}, 200