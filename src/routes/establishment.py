import os
import uuid
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from PIL import Image
import requests
from src.models.base import db
from src.models.user import User
from src.models.establishment import Establishment, EstablishmentImage

establishment_bp = Blueprint('establishment', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    """Verifica se o arquivo tem uma extensão permitida."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_address_from_cep(cep):
    """Busca endereço usando a API ViaCEP."""
    try:
        # Remover caracteres não numéricos do CEP
        clean_cep = ''.join(filter(str.isdigit, cep))
        
        if len(clean_cep) != 8:
            return None
        
        response = requests.get(f'https://viacep.com.br/ws/{clean_cep}/json/')
        
        if response.status_code == 200:
            data = response.json()
            if 'erro' not in data:
                return {
                    'state': data.get('uf', ''),
                    'city': data.get('localidade', ''),
                    'neighborhood': data.get('bairro', ''),
                    'address': data.get('logradouro', '')
                }
        return None
    except Exception:
        return None

@establishment_bp.route('/', methods=['POST'])
@jwt_required()
def create_establishment():
    """Cria um novo estabelecimento."""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        # Verificar se usuário já tem um estabelecimento
        if user.establishment:
            return jsonify({'error': 'Usuário já possui um estabelecimento'}), 400
        
        data = request.get_json()
        
        # Validar se dados foram enviados
        if not data:
            return jsonify({
                'error': 'Dados não fornecidos',
                'details': 'O corpo da requisição deve conter dados JSON válidos'
            }), 422
        
        # Lista de erros de validação
        validation_errors = []
        
        # Validar campos obrigatórios
        required_fields = {
            'name': 'Nome do estabelecimento',
            'type': 'Tipo do estabelecimento'
        }
        
        for field, description in required_fields.items():
            if not data.get(field) or not str(data.get(field)).strip():
                validation_errors.append(f'{description} é obrigatório')
        
        # Validar tipo de estabelecimento
        valid_types = ['Bar', 'Restaurante', 'Lanchonete', 'Cafeteria', 'Pizzaria', 'Sorveteria', 'Padaria', 'Outro']
        if data.get('type') and data['type'] not in valid_types:
            validation_errors.append(f'Tipo deve ser um dos seguintes: {", ".join(valid_types)}')
        
        # Validar nome (mínimo 2 caracteres)
        if data.get('name') and len(str(data['name']).strip()) < 2:
            validation_errors.append('Nome deve ter pelo menos 2 caracteres')
        
        # Validar CEP se fornecido
        if data.get('cep'):
            clean_cep = ''.join(filter(str.isdigit, data['cep']))
            if len(clean_cep) != 8:
                validation_errors.append('CEP deve conter exatamente 8 dígitos')
        
        # Validar telefone se fornecido
        if data.get('phone'):
            clean_phone = ''.join(filter(str.isdigit, data['phone']))
            if len(clean_phone) < 10 or len(clean_phone) > 11:
                validation_errors.append('Telefone deve ter entre 10 e 11 dígitos')
        
        # Validar WhatsApp se fornecido
        if data.get('whatsapp'):
            clean_whatsapp = ''.join(filter(str.isdigit, data['whatsapp']))
            if len(clean_whatsapp) < 10 or len(clean_whatsapp) > 11:
                validation_errors.append('WhatsApp deve ter entre 10 e 11 dígitos')
        
        # Validar Instagram se fornecido
        if data.get('instagram'):
            instagram = str(data['instagram']).strip()
            if instagram and not instagram.startswith('@'):
                validation_errors.append('Instagram deve começar com @')
        
        # Validar website se fornecido
        if data.get('website'):
            website = str(data['website']).strip()
            if website and not (website.startswith('http://') or website.startswith('https://')):
                validation_errors.append('Website deve começar com http:// ou https://')
        
        # Validar coordenadas se fornecidas
        if data.get('latitude') is not None:
            try:
                lat = float(data['latitude'])
                if lat < -90 or lat > 90:
                    validation_errors.append('Latitude deve estar entre -90 e 90')
            except (ValueError, TypeError):
                validation_errors.append('Latitude deve ser um número válido')
        
        if data.get('longitude') is not None:
            try:
                lng = float(data['longitude'])
                if lng < -180 or lng > 180:
                    validation_errors.append('Longitude deve estar entre -180 e 180')
            except (ValueError, TypeError):
                validation_errors.append('Longitude deve ser um número válido')
        
        # Validar faixa etária se fornecida
        if data.get('faixa_etaria'):
            valid_ages = ['Livre', '12+', '16+', '18+']
            if data['faixa_etaria'] not in valid_ages:
                validation_errors.append(f'Faixa etária deve ser uma das seguintes: {", ".join(valid_ages)}')
        
        # Se há erros de validação, retornar erro 422
        if validation_errors:
            return jsonify({
                'error': 'Dados inválidos',
                'validation_errors': validation_errors,
                'details': 'Corrija os erros listados e tente novamente'
            }), 422
        
        # Buscar endereço pelo CEP se fornecido
        address_data = {}
        if data.get('cep'):
            cep_data = get_address_from_cep(data['cep'])
            if cep_data:
                address_data = cep_data
        
        # Criar estabelecimento
        establishment = Establishment(
            name=str(data['name']).strip(),
            description=str(data.get('description', '')).strip(),
            type=data['type'],
            cep=data.get('cep', ''),
            state=address_data.get('state', data.get('state', '')),
            city=address_data.get('city', data.get('city', '')),
            neighborhood=address_data.get('neighborhood', data.get('neighborhood', '')),
            address=address_data.get('address', data.get('address', '')),
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            phone=data.get('phone', ''),
            whatsapp=data.get('whatsapp', ''),
            instagram=data.get('instagram', ''),
            website=data.get('website', ''),
            # Novos campos
            faixa_etaria=data.get('faixa_etaria', 'Livre'),
            pet_friendly=bool(data.get('pet_friendly', False)),
            lgbt_friendly=bool(data.get('lgbt_friendly', False)),
            horarios_funcionamento=data.get('horarios_funcionamento', {}),
            delivery=bool(data.get('delivery', False)),
            link_delivery=data.get('link_delivery', ''),
            ponto_referencia=data.get('ponto_referencia', ''),
            como_chegar_transporte=data.get('como_chegar_transporte', ''),
            user_id=user_id
        )
        
        db.session.add(establishment)
        db.session.commit()
        
        return jsonify({
            'message': 'Estabelecimento criado com sucesso',
            'establishment': establishment.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        # Log do erro para debug
        print(f"Erro ao criar estabelecimento: {str(e)}")
        return jsonify({
            'error': 'Erro interno do servidor',
            'details': 'Ocorreu um erro inesperado. Tente novamente mais tarde.',
            'debug_info': str(e) if current_app.debug else None
        }), 500

@establishment_bp.route('/', methods=['GET'])
def get_establishments():
    """Lista estabelecimentos com filtros e paginação."""
    try:
        # Parâmetros de consulta
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        type_filter = request.args.get('type')
        city_filter = request.args.get('city')
        neighborhood_filter = request.args.get('neighborhood')
        approved_only = request.args.get('approved_only', 'true').lower() == 'true'
        search = request.args.get('search', '').strip()
        
        # Construir query
        query = Establishment.query
        
        if approved_only:
            query = query.filter(Establishment.is_approved == True)
        
        query = query.filter(Establishment.is_active == True)
        
        if type_filter:
            query = query.filter(Establishment.type == type_filter)
        
        if city_filter:
            query = query.filter(Establishment.city.ilike(f'%{city_filter}%'))
        
        if neighborhood_filter:
            query = query.filter(Establishment.neighborhood.ilike(f'%{neighborhood_filter}%'))
        
        if search:
            query = query.filter(
                db.or_(
                    Establishment.name.ilike(f'%{search}%'),
                    Establishment.description.ilike(f'%{search}%')
                )
            )
        
        # Ordenação
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')
        
        if sort_by == 'name':
            order_column = Establishment.name
        elif sort_by == 'rating':
            # Para ordenar por rating, precisaríamos de uma query mais complexa
            order_column = Establishment.created_at
        else:
            order_column = Establishment.created_at
        
        if sort_order == 'asc':
            query = query.order_by(order_column.asc())
        else:
            query = query.order_by(order_column.desc())
        
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
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@establishment_bp.route('/<int:establishment_id>', methods=['GET'])
def get_establishment(establishment_id):
    """Retorna detalhes de um estabelecimento."""
    try:
        establishment = Establishment.query.get(establishment_id)
        
        if not establishment:
            return jsonify({'error': 'Estabelecimento não encontrado'}), 404
        
        return jsonify({
            'establishment': establishment.to_dict(include_reviews=True)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@establishment_bp.route('/<int:establishment_id>', methods=['PUT'])
@jwt_required()
def update_establishment(establishment_id):
    """Atualiza um estabelecimento."""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        establishment = Establishment.query.get(establishment_id)
        
        if not establishment:
            return jsonify({'error': 'Estabelecimento não encontrado'}), 404
        
        # Verificar permissões
        if user.role != 'admin' and establishment.user_id != user_id:
            return jsonify({'error': 'Acesso negado'}), 403
        
        data = request.get_json()
        
        # Atualizar campos
        if 'name' in data:
            establishment.name = data['name']
        if 'description' in data:
            establishment.description = data['description']
        if 'type' in data:
            establishment.type = data['type']
        
        # Atualizar endereço
        if 'cep' in data:
            establishment.cep = data['cep']
            # Buscar endereço pelo CEP se fornecido
            if data['cep']:
                cep_data = get_address_from_cep(data['cep'])
                if cep_data:
                    establishment.state = cep_data['state']
                    establishment.city = cep_data['city']
                    establishment.neighborhood = cep_data['neighborhood']
                    establishment.address = cep_data['address']
        
        if 'state' in data:
            establishment.state = data['state']
        if 'city' in data:
            establishment.city = data['city']
        if 'neighborhood' in data:
            establishment.neighborhood = data['neighborhood']
        if 'address' in data:
            establishment.address = data['address']
        if 'latitude' in data:
            establishment.latitude = data['latitude']
        if 'longitude' in data:
            establishment.longitude = data['longitude']
        
        # Atualizar contato
        if 'phone' in data:
            establishment.phone = data['phone']
        if 'whatsapp' in data:
            establishment.whatsapp = data['whatsapp']
        if 'instagram' in data:
            establishment.instagram = data['instagram']
        if 'website' in data:
            establishment.website = data['website']
        
        # Atualizar novos campos
        if 'faixa_etaria' in data:
            establishment.faixa_etaria = data['faixa_etaria']
        if 'pet_friendly' in data:
            establishment.pet_friendly = data['pet_friendly']
        if 'lgbt_friendly' in data:
            establishment.lgbt_friendly = data['lgbt_friendly']
        if 'horarios_funcionamento' in data:
            establishment.horarios_funcionamento = data['horarios_funcionamento']
        if 'delivery' in data:
            establishment.delivery = data['delivery']
        if 'link_delivery' in data:
            establishment.link_delivery = data['link_delivery']
        if 'ponto_referencia' in data:
            establishment.ponto_referencia = data['ponto_referencia']
        if 'como_chegar_transporte' in data:
            establishment.como_chegar_transporte = data['como_chegar_transporte']
        
        # Apenas admin pode alterar status
        if user.role == 'admin':
            if 'is_active' in data:
                establishment.is_active = data['is_active']
            if 'is_approved' in data:
                establishment.is_approved = data['is_approved']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Estabelecimento atualizado com sucesso',
            'establishment': establishment.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@establishment_bp.route('/<int:establishment_id>/images', methods=['POST'])
@jwt_required()
def upload_image(establishment_id):
    """Faz upload de uma imagem para o estabelecimento."""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        establishment = Establishment.query.get(establishment_id)
        
        if not establishment:
            return jsonify({'error': 'Estabelecimento não encontrado'}), 404
        
        # Verificar permissões
        if user.role != 'admin' and establishment.user_id != user_id:
            return jsonify({'error': 'Acesso negado'}), 403
        
        if 'image' not in request.files:
            return jsonify({'error': 'Nenhuma imagem fornecida'}), 400
        
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({'error': 'Nenhuma imagem selecionada'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Tipo de arquivo não permitido'}), 400
        
        # Gerar nome único para o arquivo
        filename = str(uuid.uuid4()) + '.' + file.filename.rsplit('.', 1)[1].lower()
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        
        # Salvar arquivo
        file.save(filepath)
        
        # Redimensionar imagem se necessário
        try:
            with Image.open(filepath) as img:
                # Redimensionar para máximo 1200x1200 mantendo proporção
                img.thumbnail((1200, 1200), Image.Resampling.LANCZOS)
                img.save(filepath, optimize=True, quality=85)
        except Exception:
            pass  # Se falhar, manter imagem original
        
        # Verificar se é a primeira imagem (será a principal)
        is_primary = len(establishment.images) == 0
        
        # Criar registro no banco
        image = EstablishmentImage(
            filename=filename,
            original_filename=secure_filename(file.filename),
            is_primary=is_primary,
            establishment_id=establishment_id
        )
        
        db.session.add(image)
        db.session.commit()
        
        return jsonify({
            'message': 'Imagem enviada com sucesso',
            'image': image.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        # Tentar remover arquivo se foi criado
        try:
            if 'filepath' in locals():
                os.remove(filepath)
        except:
            pass
        return jsonify({'error': str(e)}), 500

@establishment_bp.route('/<int:establishment_id>/images/<int:image_id>', methods=['DELETE'])
@jwt_required()
def delete_image(establishment_id, image_id):
    """Remove uma imagem do estabelecimento."""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        establishment = Establishment.query.get(establishment_id)
        
        if not establishment:
            return jsonify({'error': 'Estabelecimento não encontrado'}), 404
        
        # Verificar permissões
        if user.role != 'admin' and establishment.user_id != user_id:
            return jsonify({'error': 'Acesso negado'}), 403
        
        image = EstablishmentImage.query.filter_by(
            id=image_id, 
            establishment_id=establishment_id
        ).first()
        
        if not image:
            return jsonify({'error': 'Imagem não encontrada'}), 404
        
        # Remover arquivo físico
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], image.filename)
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
        except:
            pass  # Continuar mesmo se não conseguir remover o arquivo
        
        # Remover do banco
        db.session.delete(image)
        db.session.commit()
        
        return jsonify({'message': 'Imagem removida com sucesso'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@establishment_bp.route('/my', methods=['GET'])
@jwt_required()
def get_my_establishment():
    """Retorna o estabelecimento do usuário logado."""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        establishment = Establishment.query.filter_by(user_id=user_id).first()
        
        if not establishment:
            return jsonify({'error': 'Estabelecimento não encontrado'}), 404
        
        return jsonify(establishment.to_dict(include_reviews=True)), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@establishment_bp.route('/stats', methods=['GET'])
def get_establishments_stats():
    """Retorna estatísticas dos estabelecimentos."""
    try:
        total = Establishment.query.count()
        approved = Establishment.query.filter_by(is_approved=True).count()
        pending = Establishment.query.filter_by(is_approved=False).count()
        active = Establishment.query.filter_by(is_active=True).count()
        
        return jsonify({
            'total': total,
            'approved': approved,
            'pending': pending,
            'active': active
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@establishment_bp.route('/cep/<cep>', methods=['GET'])
def get_cep_info(cep):
    """Busca informações de endereço pelo CEP."""
    try:
        address_data = get_address_from_cep(cep)
        
        if not address_data:
            return jsonify({'error': 'CEP não encontrado'}), 404
        
        return jsonify(address_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

