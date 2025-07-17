import uuid
import os
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from PIL import Image
from src.models.user import User, db
from src.models.establishment import Establishment
from src.models.review import Review

user_bp = Blueprint('user', __name__)

@user_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_general_stats():
    """Retorna estatísticas gerais do sistema."""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user or current_user.role != 'admin':
            return jsonify({'error': 'Acesso negado'}), 403
        
        # Estatísticas de usuários
        total_users = User.query.count()
        admin_users = User.query.filter_by(role='admin').count()
        establishment_users = User.query.filter_by(role='establishment').count()
        regular_users = User.query.filter_by(role='user').count()
        active_users = User.query.filter_by(is_active=True).count()
        
        # Estatísticas de estabelecimentos
        total_establishments = Establishment.query.count()
        approved_establishments = Establishment.query.filter_by(is_approved=True).count()
        pending_establishments = Establishment.query.filter_by(is_approved=False).count()
        active_establishments = Establishment.query.filter_by(is_active=True).count()
        
        # Estatísticas de avaliações
        total_reviews = Review.query.count()
        approved_reviews = Review.query.filter_by(is_approved=True).count()
        pending_reviews = Review.query.filter_by(is_approved=False).count()
        
        # Média geral de avaliações
        avg_rating = db.session.query(db.func.avg(Review.rating)).filter_by(is_approved=True).scalar()
        avg_rating = float(avg_rating) if avg_rating else 0.0
        
        return jsonify({
            'users': {
                'total': total_users,
                'admin': admin_users,
                'establishment': establishment_users,
                'regular': regular_users,
                'active': active_users
            },
            'establishments': {
                'total': total_establishments,
                'approved': approved_establishments,
                'pending': pending_establishments,
                'active': active_establishments
            },
            'reviews': {
                'total': total_reviews,
                'approved': approved_reviews,
                'pending': pending_reviews,
                'average_rating': round(avg_rating, 1)
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@user_bp.route('/users', methods=['POST'])
def create_user():
    
    data = request.json
    user = User(username=data['username'], email=data['email'])
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()), 201

@user_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())

@user_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.json
    user.username = data.get('username', user.username)
    user.email = data.get('email', user.email)
    db.session.commit()
    return jsonify(user.to_dict())

@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return '', 204


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    """Verifica se o arquivo tem uma extensão permitida."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@user_bp.route('/users/<int:user_id>/profile', methods=['PUT'])
@jwt_required()
def update_user_profile(user_id):
    """Atualiza o perfil do usuário."""
    try:
        current_user_id = get_jwt_identity()
        
        # Verificar se o usuário está tentando atualizar seu próprio perfil ou se é admin
        current_user = User.query.get(current_user_id)
        if not current_user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        if current_user_id != user_id and current_user.role != 'admin':
            return jsonify({'error': 'Acesso negado'}), 403
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        data = request.get_json()
        
        # Atualizar campos permitidos
        if 'username' in data:
            user.username = data['username']
        if 'phone' in data:
            user.phone = data['phone']
        if 'address' in data:
            user.address = data['address']
        if 'city' in data:
            user.city = data['city']
        if 'state' in data:
            user.state = data['state']
        if 'bio' in data:
            user.bio = data['bio']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Perfil atualizado com sucesso',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@user_bp.route('/users/<int:user_id>/photo', methods=['POST'])
@jwt_required()
def upload_profile_photo(user_id):
    """Faz upload da foto de perfil do usuário."""
    try:
        current_user_id = get_jwt_identity()
        
        # Verificar se o usuário está tentando atualizar sua própria foto ou se é admin
        current_user = User.query.get(current_user_id)
        if not current_user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        if current_user_id != user_id and current_user.role != 'admin':
            return jsonify({'error': 'Acesso negado'}), 403
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        if 'photo' not in request.files:
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400
        
        file = request.files['photo']
        if file.filename == '':
            return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Tipo de arquivo não permitido'}), 400
        
        # Criar diretório se não existir
        upload_dir = os.path.join(os.path.dirname(current_app.root_path), 'static', 'images', 'profiles')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Gerar nome único para o arquivo
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{file_extension}"
        filepath = os.path.join(upload_dir, filename)
        
        # Salvar e redimensionar imagem
        image = Image.open(file.stream)
        
        # Redimensionar para 300x300 mantendo proporção
        image.thumbnail((300, 300), Image.Resampling.LANCZOS)
        
        # Converter para RGB se necessário (para JPEG)
        if image.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
            image = background
        
        image.save(filepath, 'JPEG', quality=85)
        
        # Remover foto anterior se existir
        if user.profile_photo:
            old_filepath = os.path.join(upload_dir, user.profile_photo)
            if os.path.exists(old_filepath):
                os.remove(old_filepath)
        
        # Atualizar usuário
        user.profile_photo = filename
        db.session.commit()
        
        return jsonify({
            'message': 'Foto de perfil atualizada com sucesso',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

