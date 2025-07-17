import requests
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.base import db
from src.models.user import User
from src.models.establishment import Establishment
from src.models.review import Review

review_bp = Blueprint('review', __name__)

def get_user_location_by_ip(ip_address):
    """Obtém localização do usuário pelo IP usando ipinfo.io."""
    try:
        # Para desenvolvimento local, usar um IP público de exemplo
        if ip_address in ['127.0.0.1', 'localhost', '::1']:
            ip_address = '8.8.8.8'  # IP público para teste
        
        response = requests.get(f'https://ipinfo.io/{ip_address}/json')
        
        if response.status_code == 200:
            data = response.json()
            return {
                'city': data.get('city', ''),
                'region': data.get('region', ''),
                'country': data.get('country', ''),
                'location': data.get('loc', '').split(',') if data.get('loc') else []
            }
        return None
    except Exception:
        return None

@review_bp.route('/', methods=['POST'])
def create_review():
    """Cria uma nova avaliação."""
    try:
        data = request.get_json()
        
        # Validar dados obrigatórios
        if not data or not data.get('establishment_id') or not data.get('rating') or not data.get('reviewer_name'):
            return jsonify({'error': 'establishment_id, rating e reviewer_name são obrigatórios'}), 400
        
        # Validar rating
        rating = data.get('rating')
        if not isinstance(rating, int) or rating < 1 or rating > 5:
            return jsonify({'error': 'Rating deve ser um número entre 1 e 5'}), 400
        
        # Verificar se estabelecimento existe
        establishment = Establishment.query.get(data['establishment_id'])
        if not establishment:
            return jsonify({'error': 'Estabelecimento não encontrado'}), 404
        
        # Criar avaliação
        review = Review(
            rating=rating,
            comment=data.get('comment', ''),
            reviewer_name=data['reviewer_name'],
            reviewer_email=data.get('reviewer_email', ''),
            establishment_id=data['establishment_id']
        )
        
        db.session.add(review)
        db.session.commit()
        
        return jsonify({
            'message': 'Avaliação criada com sucesso',
            'review': review.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@review_bp.route('/<int:review_id>', methods=['PUT'])
@jwt_required()
def update_review(review_id):
    """Atualiza uma avaliação (apenas admin pode aprovar/reprovar)."""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or user.role != 'admin':
            return jsonify({'error': 'Acesso negado'}), 403
        
        review = Review.query.get(review_id)
        if not review:
            return jsonify({'error': 'Avaliação não encontrada'}), 404
        
        data = request.get_json()
        
        # Atualizar campos permitidos
        if 'is_approved' in data:
            review.is_approved = data['is_approved']
        
        if 'comment' in data:
            review.comment = data['comment']
        
        if 'rating' in data:
            rating = data['rating']
            if isinstance(rating, int) and 1 <= rating <= 5:
                review.rating = rating
        
        db.session.commit()
        
        return jsonify({
            'message': 'Avaliação atualizada com sucesso',
            'review': review.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@review_bp.route('/<int:review_id>', methods=['DELETE'])
@jwt_required()
def delete_review(review_id):
    """Remove uma avaliação (apenas admin)."""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or user.role != 'admin':
            return jsonify({'error': 'Acesso negado'}), 403
        
        review = Review.query.get(review_id)
        if not review:
            return jsonify({'error': 'Avaliação não encontrada'}), 404
        
        db.session.delete(review)
        db.session.commit()
        
        return jsonify({'message': 'Avaliação removida com sucesso'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@review_bp.route('/establishment/<int:establishment_id>', methods=['GET'])
def get_establishment_reviews(establishment_id):
    """Lista avaliações de um estabelecimento."""
    try:
        # Parâmetros de consulta
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        approved_only = request.args.get('approved_only', 'true').lower() == 'true'
        
        # Verificar se estabelecimento existe
        establishment = Establishment.query.get(establishment_id)
        if not establishment:
            return jsonify({'error': 'Estabelecimento não encontrado'}), 404
        
        # Construir query
        query = Review.query.filter_by(establishment_id=establishment_id)
        
        if approved_only:
            query = query.filter(Review.is_approved == True)
        
        # Ordenar por mais recentes
        query = query.order_by(Review.created_at.desc())
        
        # Paginação
        reviews = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'reviews': [review.to_dict() for review in reviews.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': reviews.total,
                'pages': reviews.pages,
                'has_next': reviews.has_next,
                'has_prev': reviews.has_prev
            },
            'establishment': {
                'id': establishment.id,
                'name': establishment.name,
                'average_rating': establishment.average_rating,
                'total_reviews': establishment.total_reviews
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@review_bp.route('/pending', methods=['GET'])
@jwt_required()
def get_pending_reviews():
    """Lista avaliações pendentes de aprovação (apenas admin)."""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or user.role != 'admin':
            return jsonify({'error': 'Acesso negado'}), 403
        
        # Parâmetros de consulta
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        
        # Buscar avaliações não aprovadas
        reviews = Review.query.filter_by(is_approved=False).order_by(Review.created_at.desc()).paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'reviews': [review.to_dict() for review in reviews.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': reviews.total,
                'pages': reviews.pages,
                'has_next': reviews.has_next,
                'has_prev': reviews.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Rotas de geolocalização
geo_bp = Blueprint('geo', __name__)

@geo_bp.route('/location', methods=['GET'])
def get_user_location():
    """Obtém localização do usuário pelo IP."""
    try:
        # Obter IP do usuário
        user_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', ''))
        
        # Se há múltiplos IPs (proxy), pegar o primeiro
        if ',' in user_ip:
            user_ip = user_ip.split(',')[0].strip()
        
        location_data = get_user_location_by_ip(user_ip)
        
        if not location_data:
            return jsonify({'error': 'Não foi possível obter localização'}), 404
        
        return jsonify({
            'ip': user_ip,
            'location': location_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@geo_bp.route('/establishments/nearby', methods=['GET'])
def get_nearby_establishments():
    """Lista estabelecimentos próximos baseado na localização do usuário."""
    try:
        # Obter localização do usuário
        user_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', ''))
        if ',' in user_ip:
            user_ip = user_ip.split(',')[0].strip()
        
        location_data = get_user_location_by_ip(user_ip)
        
        # Parâmetros de consulta
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        
        # Construir query base
        query = Establishment.query.filter(
            Establishment.is_approved == True,
            Establishment.is_active == True
        )
        
        # Se conseguiu obter localização, filtrar por cidade
        if location_data and location_data.get('city'):
            user_city = location_data['city']
            query = query.filter(Establishment.city.ilike(f'%{user_city}%'))
        
        # Ordenar por mais recentes
        query = query.order_by(Establishment.created_at.desc())
        
        # Paginação
        establishments = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'establishments': [est.to_dict() for est in establishments.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': establishments.total,
                'pages': establishments.pages,
                'has_next': establishments.has_next,
                'has_prev': establishments.has_prev
            },
            'user_location': location_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

