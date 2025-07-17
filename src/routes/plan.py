from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.base import db
from src.models.user import User
from src.models.subscription import Subscription

plan_bp = Blueprint('plan', __name__)

@plan_bp.route('/subscribe', methods=['POST'])
@jwt_required()
def subscribe_to_plan():
    """Assina um plano."""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        data = request.get_json()
        plan_id = data.get('plan_id')
        
        if plan_id not in ['free', 'premium', 'vip']:
            return jsonify({'error': 'Plano inválido'}), 400
        
        # Verificar se já tem uma assinatura ativa
        existing_subscription = Subscription.query.filter_by(
            user_id=user_id,
            status='active'
        ).first()
        
        if existing_subscription:
            # Cancelar assinatura anterior
            existing_subscription.status = 'cancelled'
        
        # Calcular data de expiração
        expires_at = None
        if plan_id != 'free':
            expires_at = datetime.utcnow() + timedelta(days=30)  # 30 dias
        
        # Criar nova assinatura
        subscription = Subscription(
            user_id=user_id,
            plan_id=plan_id,
            status='active',
            starts_at=datetime.utcnow(),
            expires_at=expires_at
        )
        
        db.session.add(subscription)
        db.session.commit()
        
        return jsonify({
            'message': 'Plano assinado com sucesso',
            'subscription': subscription.to_dict(),
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@plan_bp.route('/my-subscription', methods=['GET'])
@jwt_required()
def get_my_subscription():
    """Retorna a assinatura atual do usuário."""
    try:
        user_id = get_jwt_identity()
        
        subscription = Subscription.query.filter_by(
            user_id=user_id,
            status='active'
        ).first()
        
        if not subscription:
            # Criar assinatura gratuita se não existir
            subscription = Subscription(
                user_id=user_id,
                plan_id='free',
                status='active',
                starts_at=datetime.utcnow()
            )
            db.session.add(subscription)
            db.session.commit()
        
        return jsonify({
            'subscription': subscription.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@plan_bp.route('/my-subscription', methods=['DELETE'])
@jwt_required()
def cancel_subscription():
    """Cancela a assinatura atual."""
    try:
        user_id = get_jwt_identity()
        
        subscription = Subscription.query.filter_by(
            user_id=user_id,
            status='active'
        ).first()
        
        if not subscription:
            return jsonify({'error': 'Nenhuma assinatura ativa encontrada'}), 404
        
        if subscription.plan_id == 'free':
            return jsonify({'error': 'Não é possível cancelar o plano gratuito'}), 400
        
        # Cancelar assinatura e criar uma gratuita
        subscription.status = 'cancelled'
        
        free_subscription = Subscription(
            user_id=user_id,
            plan_id='free',
            status='active',
            starts_at=datetime.utcnow()
        )
        
        db.session.add(free_subscription)
        db.session.commit()
        
        return jsonify({
            'message': 'Assinatura cancelada com sucesso',
            'subscription': free_subscription.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@plan_bp.route('/check-permissions', methods=['POST'])
@jwt_required()
def check_permissions():
    """Verifica se o usuário tem permissão para uma ação específica."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        action = data.get('action')
        
        subscription = Subscription.query.filter_by(
            user_id=user_id,
            status='active'
        ).first()
        
        if not subscription:
            # Criar assinatura gratuita se não existir
            subscription = Subscription(
                user_id=user_id,
                plan_id='free',
                status='active',
                starts_at=datetime.utcnow()
            )
            db.session.add(subscription)
            db.session.commit()
        
        features = subscription.get_plan_features()
        permissions = {
            'can_create_establishment': True,  # Todos podem criar
            'can_upload_photos': True,
            'max_photos': features['max_photos'],
            'has_priority_boost': features['priority_boost'] > 0,
            'has_analytics': features['analytics'],
            'support_level': features['support_level'],
            'badge': features['badge']
        }
        
        return jsonify({
            'permissions': permissions,
            'subscription': subscription.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

