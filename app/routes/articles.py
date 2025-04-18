from flask import Blueprint, request
from app.models import Article
from app import db

articles_bp = Blueprint('articles', __name__)

@articles_bp.route('/articles', methods=['GET'])
def get_articles():
def get_articles():
    category = request.args.get('category')

    if category:
        # Case-insensitive filtering using ilike()
        articles = Article.query.filter(Article.category.ilike(category)).all()
    else:
        articles = Article.query.all()  # Fetch all articles if no category is provided

    if not articles:
        return {'error': 'No articles found'}, 404

    return [{
        'id': article.id,
        'title': article.title,
        'sub_title': article.sub_title,
        'content': article.content,
        'category': article.category,
        'date': article.date.strftime('%Y-%m-%d %H:%M:%S') if article.date else None,
        'created_at': article.created_at.strftime('%Y-%m-%d %H:%M:%S') if article.created_at else None,
        'updated_at': article.updated_at.strftime('%Y-%m-%d %H:%M:%S') if article.updated_at else None,
    } for article in articles], 200

@articles_bp.route('/articles/<int:id>', methods=['GET'])
def get_article(id):
    article = Article.query.get_or_404(id)
    return {
        'id': article.id,
        'title': article.title,
        'sub_title': article.sub_title,
        'content': article.content,
        'category': article.category,
        'date': article.date.strftime('%Y-%m-%d %H:%M:%S'),
        'created_at': article.created_at.strftime('%Y-%m-%d %H:%M:%S') if article.created_at else None,
        'updated_at': article.updated_at.strftime('%Y-%m-%d %H:%M:%S') if article.updated_at else None,
    }, 200
