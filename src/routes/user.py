from flask import Blueprint, jsonify, request
from werkzeug.security import generate_password_hash
from src.models.user import User, db

user_bp = Blueprint('user', __name__)

# Listar todos os usuários
@user_bp.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

# Criar novo usuário
@user_bp.route('/users', methods=['POST'])
def create_user():
    data = request.json

    hashed_password = generate_password_hash(data['password'])

    user = User(
        username=data['username'],
        email=data['email'],
        password_hash=hashed_password,
        role=data.get('role', 'user')  # padrão 'user'
    )

    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()), 201

# Obter usuário por ID
@user_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())

# Atualizar dados do usuário
@user_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.json
    user.username = data.get('username', user.username)
    user.email = data.get('email', user.email)
    db.session.commit()
    return jsonify(user.to_dict())

# Excluir usuário
@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return '', 204
