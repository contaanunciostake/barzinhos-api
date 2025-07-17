from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.base import db
from src.models.user import User
from src.models.payment import Payment
from src.models.subscription import Subscription
from src.services.mercadopago_service import MercadoPagoService

payment_bp = Blueprint('payment', __name__)

@payment_bp.route('/create-preference', methods=['POST'])
@jwt_required()
def create_payment_preference():
    """Cria uma preferência de pagamento no MercadoPago."""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        data = request.get_json()
        plan_id = data.get('plan_id')
        success_url = data.get('success_url')
        failure_url = data.get('failure_url')
        pending_url = data.get('pending_url')
        
        if plan_id not in ['premium', 'vip']:
            return jsonify({'error': 'Plano inválido para pagamento'}), 400
        
        # Verificar se já tem uma assinatura ativa do mesmo plano
        existing_subscription = Subscription.get_active_subscription(user_id)
        if existing_subscription and existing_subscription.plan_id == plan_id:
            return jsonify({'error': 'Você já possui este plano ativo'}), 400
        
        # Criar preferência usando o serviço
        mp_service = MercadoPagoService()
        result = mp_service.create_preference(
            user_id=user_id,
            plan_id=plan_id,
            success_url=success_url,
            failure_url=failure_url,
            pending_url=pending_url
        )
        
        if result['success']:
            return jsonify({
                'message': 'Preferência criada com sucesso',
                'preference_id': result['preference_id'],
                'init_point': result['init_point'],
                'sandbox_init_point': result.get('sandbox_init_point'),
                'payment_id': result['payment_id'],
                'external_reference': result['external_reference']
            }), 200
        else:
            return jsonify({
                'error': 'Erro ao criar preferência de pagamento',
                'details': result.get('error')
            }), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@payment_bp.route('/webhook', methods=['POST'])
def mercadopago_webhook():
    """Webhook para receber notificações do MercadoPago."""
    try:
        # Verificar se é uma notificação válida
        notification_data = request.get_json()
        
        if not notification_data:
            return jsonify({'error': 'Dados de notificação inválidos'}), 400
        
        # Processar notificação usando o serviço
        mp_service = MercadoPagoService()
        result = mp_service.process_webhook_notification(notification_data)
        
        if result['success']:
            return jsonify({'message': 'Notificação processada com sucesso'}), 200
        else:
            return jsonify({
                'error': 'Erro ao processar notificação',
                'details': result.get('error')
            }), 500
            
    except Exception as e:
        # Log do erro (implementar logging adequado em produção)
        print(f"Erro no webhook: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@payment_bp.route('/status/<int:payment_id>', methods=['GET'])
@jwt_required()
def get_payment_status(payment_id):
    """Verifica o status de um pagamento."""
    try:
        user_id = get_jwt_identity()
        
        # Buscar pagamento do usuário
        payment = Payment.query.filter_by(id=payment_id, user_id=user_id).first()
        
        if not payment:
            return jsonify({'error': 'Pagamento não encontrado'}), 404
        
        # Se tem ID do MercadoPago, buscar status atualizado
        if payment.mp_payment_id:
            mp_service = MercadoPagoService()
            mp_result = mp_service.get_payment_info(payment.mp_payment_id)
            
            if mp_result['success']:
                mp_payment = mp_result['payment']
                
                # Atualizar status local se necessário
                if payment.status != mp_payment['status']:
                    payment.status = mp_payment['status']
                    payment.status_detail = mp_payment.get('status_detail')
                    
                    # Se foi aprovado, ativar assinatura
                    if mp_payment['status'] == 'approved' and not payment.is_approved():
                        payment.approve_payment()
                    
                    db.session.commit()
        
        return jsonify({
            'payment': payment.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@payment_bp.route('/my-payments', methods=['GET'])
@jwt_required()
def get_my_payments():
    """Retorna os pagamentos do usuário."""
    try:
        user_id = get_jwt_identity()
        limit = request.args.get('limit', 10, type=int)
        
        payments = Payment.get_user_payments(user_id, limit)
        
        return jsonify({
            'payments': [payment.to_dict() for payment in payments]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@payment_bp.route('/plans-pricing', methods=['GET'])
def get_plans_pricing():
    """Retorna os preços dos planos disponíveis."""
    try:
        from src.models.payment_config import PaymentConfig
        
        config = PaymentConfig.get_active_config()
        
        plans = {
            'free': {
                'name': 'Gratuito',
                'price': 0.0,
                'features': [
                    'Até 3 fotos por estabelecimento',
                    'Suporte por email',
                    'Perfil básico'
                ]
            },
            'premium': {
                'name': 'Premium',
                'price': config.premium_price,
                'features': [
                    'Fotos ilimitadas',
                    'Prioridade nas buscas',
                    'Analytics básico',
                    'Suporte por chat',
                    'Badge Premium'
                ]
            },
            'vip': {
                'name': 'VIP',
                'price': config.vip_price,
                'features': [
                    'Fotos ilimitadas',
                    'Máxima prioridade nas buscas',
                    'Analytics avançado',
                    'Suporte 24/7',
                    'Badge VIP',
                    'Destaque especial'
                ]
            }
        }
        
        return jsonify({
            'plans': plans,
            'currency': 'BRL'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@payment_bp.route('/cancel-subscription', methods=['POST'])
@jwt_required()
def cancel_subscription():
    """Cancela a assinatura atual do usuário."""
    try:
        user_id = get_jwt_identity()
        
        # Buscar assinatura ativa
        subscription = Subscription.get_active_subscription(user_id)
        
        if not subscription:
            return jsonify({'error': 'Nenhuma assinatura ativa encontrada'}), 404
        
        if subscription.plan_id == 'free':
            return jsonify({'error': 'Não é possível cancelar o plano gratuito'}), 400
        
        # Cancelar assinatura atual
        subscription.status = 'cancelled'
        
        # Criar assinatura gratuita
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

@payment_bp.route('/reactivate-plan', methods=['POST'])
@jwt_required()
def reactivate_plan():
    """Reativa um plano após pagamento bem-sucedido."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        payment_id = data.get('payment_id')
        
        if not payment_id:
            return jsonify({'error': 'ID do pagamento é obrigatório'}), 400
        
        # Buscar pagamento
        payment = Payment.query.filter_by(id=payment_id, user_id=user_id).first()
        
        if not payment:
            return jsonify({'error': 'Pagamento não encontrado'}), 404
        
        if not payment.is_approved():
            return jsonify({'error': 'Pagamento não foi aprovado'}), 400
        
        # Verificar se já tem assinatura ativa para este pagamento
        existing_subscription = Subscription.query.filter_by(payment_id=payment_id, status='active').first()
        if existing_subscription:
            return jsonify({
                'message': 'Plano já está ativo',
                'subscription': existing_subscription.to_dict()
            }), 200
        
        # Cancelar assinatura atual
        current_subscription = Subscription.get_active_subscription(user_id)
        if current_subscription:
            current_subscription.status = 'cancelled'
        
        # Criar nova assinatura
        from datetime import datetime, timedelta
        subscription = Subscription(
            user_id=user_id,
            plan_id=payment.plan_id,
            status='active',
            starts_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=30),
            payment_id=payment.id
        )
        
        db.session.add(subscription)
        db.session.commit()
        
        return jsonify({
            'message': 'Plano reativado com sucesso',
            'subscription': subscription.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

