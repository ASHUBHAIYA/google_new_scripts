from flask import Blueprint, request
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User
from app import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/auth/register', methods=['POST'])
def register():
    data = request.json
    username = data['username']
    password = generate_password_hash(data['password'], method='sha256')
    
    new_user = User(username=username, password_hash=password)
    db.session.add(new_user)
    db.session.commit()
    
    return {'message': 'User created successfully'}, 201

@auth_bp.route('/auth/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data['username']).first()
    if not user or not check_password_hash(user.password_hash, data['password']):
        return {'message': 'Bad credentials'}, 401
    
    access_token = create_access_token(identity={'username': user.username})
    return {'access_token': access_token}, 200