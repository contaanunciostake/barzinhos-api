from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from src.models.user import db
from src.models.establishment import Establishment, Review, EstablishmentImage
from sqlalchemy import or_

establishment_bp = Blueprint('establishment', __name__)

@establishment_bp.route('/establishments', methods=['GET'])
@cross_origin()
def get_establishments():
    """Buscar estabelecimentos com filtros opcionais"""
    try:
        # Parâmetros de filtro
        search = request.args.get('search', '')
        neighborhood = request.args.get('neighborhood', '')
        establishment_type = request.args.get('type', '')
        is_open = request.args.get('is_open', '')
        approved_only = request.args.get('approved_only', 'true')
        
        # Query base
        query = Establishment.query
        
        # Filtrar apenas estabelecimentos aprovados por padrão
        if approved_only.lower() == 'true':
            query = query.filter(Establishment.is_approved == True)
        
        # Filtro de busca por nome ou descrição
        if search:
            query = query.filter(
                or_(
                    Establishment.name.ilike(f'%{search}%'),
                    Establishment.description.ilike(f'%{search}%')
                )
            )
        
        # Filtro por bairro
        if neighborhood and neighborhood != 'Todos':
            query = query.filter(Establishment.neighborhood == neighborhood)
        
        # Filtro por tipo
        if establishment_type and establishment_type != 'Todos':
            query = query.filter(Establishment.type == establishment_type)
        
        # Filtro por status (aberto/fechado)
        if is_open:
            query = query.filter(Establishment.is_open == (is_open.lower() == 'true'))
        
        establishments = query.all()
        
        return jsonify({
            'success': True,
            'data': [establishment.to_dict() for establishment in establishments],
            'count': len(establishments)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@establishment_bp.route('/establishments/<int:establishment_id>', methods=['GET'])
@cross_origin()
def get_establishment(establishment_id):
    """Buscar um estabelecimento específico"""
    try:
        establishment = Establishment.query.get_or_404(establishment_id)
        
        # Buscar imagens do estabelecimento
        images = EstablishmentImage.query.filter_by(establishment_id=establishment_id).all()
        
        establishment_data = establishment.to_dict()
        establishment_data['images'] = [image.to_dict() for image in images]
        establishment_data['reviews'] = [review.to_dict() for review in establishment.reviews]
        
        return jsonify({
            'success': True,
            'data': establishment_data
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@establishment_bp.route('/establishments', methods=['POST'])
@cross_origin()
def create_establishment():
    """Criar um novo estabelecimento"""
    try:
        data = request.get_json()
        
        # Validação básica
        required_fields = ['name', 'address', 'neighborhood', 'type']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Campo obrigatório: {field}'
                }), 400
        
        establishment = Establishment(
            name=data['name'],
            description=data.get('description', ''),
            address=data['address'],
            neighborhood=data['neighborhood'],
            phone=data.get('phone', ''),
            whatsapp=data.get('whatsapp', ''),
            type=data['type'],
            is_open=data.get('is_open', True),
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            image_url=data.get('image_url', ''),
            menu_url=data.get('menu_url', ''),
            website=data.get('website', ''),
            instagram=data.get('instagram', ''),
            plan_type=data.get('plan_type', 'bronze'),
            is_approved=data.get('is_approved', False)
        )
        
        db.session.add(establishment)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': establishment.to_dict(),
            'message': 'Estabelecimento criado com sucesso'
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@establishment_bp.route('/establishments/<int:establishment_id>', methods=['PUT'])
@cross_origin()
def update_establishment(establishment_id):
    """Atualizar um estabelecimento"""
    try:
        establishment = Establishment.query.get_or_404(establishment_id)
        data = request.get_json()
        
        # Atualizar campos
        for field in ['name', 'description', 'address', 'neighborhood', 'phone', 
                     'whatsapp', 'type', 'is_open', 'latitude', 'longitude', 
                     'image_url', 'menu_url', 'website', 'instagram', 'plan_type', 'is_approved']:
            if field in data:
                setattr(establishment, field, data[field])
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': establishment.to_dict(),
            'message': 'Estabelecimento atualizado com sucesso'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@establishment_bp.route('/establishments/<int:establishment_id>/reviews', methods=['POST'])
@cross_origin()
def create_review(establishment_id):
    """Criar uma avaliação para um estabelecimento"""
    try:
        establishment = Establishment.query.get_or_404(establishment_id)
        data = request.get_json()
        
        # Validação
        required_fields = ['user_name', 'rating']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Campo obrigatório: {field}'
                }), 400
        
        if not (1 <= data['rating'] <= 5):
            return jsonify({
                'success': False,
                'error': 'Rating deve ser entre 1 e 5'
            }), 400
        
        review = Review(
            establishment_id=establishment_id,
            user_name=data['user_name'],
            user_email=data.get('user_email', ''),
            rating=data['rating'],
            comment=data.get('comment', '')
        )
        
        db.session.add(review)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': review.to_dict(),
            'message': 'Avaliação criada com sucesso'
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@establishment_bp.route('/establishments/<int:establishment_id>/images', methods=['POST'])
@cross_origin()
def add_establishment_image(establishment_id):
    """Adicionar uma imagem a um estabelecimento"""
    try:
        establishment = Establishment.query.get_or_404(establishment_id)
        data = request.get_json()
        
        if 'image_url' not in data:
            return jsonify({
                'success': False,
                'error': 'Campo obrigatório: image_url'
            }), 400
        
        image = EstablishmentImage(
            establishment_id=establishment_id,
            image_url=data['image_url'],
            is_primary=data.get('is_primary', False)
        )
        
        db.session.add(image)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': image.to_dict(),
            'message': 'Imagem adicionada com sucesso'
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@establishment_bp.route('/neighborhoods', methods=['GET'])
@cross_origin()
def get_neighborhoods():
    """Buscar todos os bairros únicos"""
    try:
        neighborhoods = db.session.query(Establishment.neighborhood).distinct().all()
        neighborhood_list = [n[0] for n in neighborhoods if n[0]]
        
        return jsonify({
            'success': True,
            'data': sorted(neighborhood_list)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@establishment_bp.route('/types', methods=['GET'])
@cross_origin()
def get_types():
    """Buscar todos os tipos únicos"""
    try:
        types = db.session.query(Establishment.type).distinct().all()
        type_list = [t[0] for t in types if t[0]]
        
        return jsonify({
            'success': True,
            'data': sorted(type_list)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

