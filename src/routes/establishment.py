from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from src.models.user import db
from src.models.establishment import Establishment, Review, EstablishmentImage
from sqlalchemy import or_

establishment_bp = Blueprint('establishment', __name__)

@establishment_bp.route('/establishments', methods=['GET'])
@cross_origin()
def get_establishments():
    try:
        search = request.args.get('search', '')
        neighborhood = request.args.get('neighborhood', '')
        establishment_type = request.args.get('type', '')
        is_open = request.args.get('is_open', '')
        approved_only = request.args.get('approved_only', 'true')

        query = Establishment.query

        if approved_only.lower() == 'true':
            query = query.filter(Establishment.is_approved == True)

        if search:
            query = query.filter(
                or_(
                    Establishment.name.ilike(f'%{search}%'),
                    Establishment.description.ilike(f'%{search}%')
                )
            )

        if neighborhood and neighborhood != 'Todos':
            query = query.filter(Establishment.neighborhood == neighborhood)

        if establishment_type and establishment_type != 'Todos':
            query = query.filter(Establishment.type == establishment_type)

        if is_open:
            query = query.filter(Establishment.is_open == (is_open.lower() == 'true'))

        establishments = query.all()

        return jsonify({
            'success': True,
            'data': [establishment.to_dict() for establishment in establishments],
            'count': len(establishments)
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@establishment_bp.route('/establishments/<int:establishment_id>', methods=['GET'])
@cross_origin()
def get_establishment(establishment_id):
    try:
        establishment = Establishment.query.get_or_404(establishment_id)
        images = EstablishmentImage.query.filter_by(establishment_id=establishment_id).all()

        establishment_data = establishment.to_dict()
        establishment_data['images'] = [img.to_dict() for img in images]
        establishment_data['reviews'] = [rev.to_dict() for rev in establishment.reviews]

        return jsonify({'success': True, 'data': establishment_data})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@establishment_bp.route('/register-establishment', methods=['POST'])
@cross_origin()
def register_establishment():
    try:
        data = request.get_json()

        required_user_fields = ['email', 'password']
        for field in required_user_fields:
            if field not in data:
                return jsonify({"error": f"Campo obrigatório: {field}", "success": False}), 400

        if User.query.filter_by(email=data['email']).first():
            return jsonify({"error": "Email já cadastrado", "success": False}), 409

        hashed_password = generate_password_hash(data['password'])
        user = User(
            email=data['email'],
            password_hash=hashed_password,
            role='establishment'
        )
        db.session.add(user)
        db.session.flush()  # Obtemos o user.id antes do commit

        required_estab_fields = ['name', 'address', 'neighborhood', 'type']
        for field in required_estab_fields:
            if field not in data:
                return jsonify({"success": False, "error": f"Campo obrigatório: {field}"}), 400

        establishment = Establishment(
            user_id=user.id,
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
        return jsonify({'success': False, 'error': str(e)}), 500
        
@establishment_bp.route('/establishments/<int:establishment_id>', methods=['PUT'])
@cross_origin()
def update_establishment(establishment_id):
    try:
        establishment = Establishment.query.get_or_404(establishment_id)
        data = request.get_json()

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
        return jsonify({'success': False, 'error': str(e)}), 500

@establishment_bp.route('/establishments/<int:establishment_id>/reviews', methods=['POST'])
@cross_origin()
def create_review(establishment_id):
    try:
        establishment = Establishment.query.get_or_404(establishment_id)
        data = request.get_json()

        required_fields = ['user_name', 'rating']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Campo obrigatório: {field}'}), 400

        if not (1 <= data['rating'] <= 5):
            return jsonify({'success': False, 'error': 'Rating deve ser entre 1 e 5'}), 400

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
        return jsonify({'success': False, 'error': str(e)}), 500

@establishment_bp.route('/establishments/<int:establishment_id>/images', methods=['POST'])
@cross_origin()
def add_establishment_image(establishment_id):
    try:
        establishment = Establishment.query.get_or_404(establishment_id)
        data = request.get_json()

        if 'image_url' not in data:
            return jsonify({'success': False, 'error': 'Campo obrigatório: image_url'}), 400

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
        return jsonify({'success': False, 'error': str(e)}), 500

@establishment_bp.route('/neighborhoods', methods=['GET'])
@cross_origin()
def get_neighborhoods():
    try:
        neighborhoods = db.session.query(Establishment.neighborhood).distinct().all()
        neighborhood_list = [n[0] for n in neighborhoods if n[0]]

        return jsonify({'success': True, 'data': sorted(neighborhood_list)})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@establishment_bp.route('/types', methods=['GET'])
@cross_origin()
def get_types():
    try:
        types = db.session.query(Establishment.type).distinct().all()
        type_list = [t[0] for t in types if t[0]]

        return jsonify({'success': True, 'data': sorted(type_list)})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# 🔥 ROTA ADICIONADA: /establishments/stats
@establishment_bp.route('/establishments/stats', methods=['GET'])
@cross_origin()
def get_establishment_stats():
    """Retorna estatísticas de estabelecimentos"""
    try:
        total = Establishment.query.count()
        approved = Establishment.query.filter_by(is_approved=True).count()
        open_count = Establishment.query.filter_by(is_open=True).count()

        return jsonify({
            'success': True,
            'data': {
                'total': total,
                'approved': approved,
                'open': open_count
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
