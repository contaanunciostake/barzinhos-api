from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.base import db
from src.models.user import User
from src.models.payment_config import PaymentConfig
from src.models.payment import Payment
from src.models.subscription import Subscription
from src.services.mercadopago_service import MercadoPagoService
from src.services.subscription_service import SubscriptionService
from functools import wraps

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    """Decorator para verificar se o usuário é admin."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or user.role != 'admin':
            return jsonify({'error': 'Acesso negado. Apenas administradores podem acessar esta funcionalidade.'}), 403
        
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/payment-config', methods=['GET'])
@jwt_required()
@admin_required
def get_payment_config():
    """Retorna a configuração atual de pagamento."""
    try:
        config = PaymentConfig.get_active_config()
        return jsonify({
            'config': config.to_dict(include_sensitive=True)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/payment-config', methods=['POST'])
@jwt_required()
@admin_required
def update_payment_config():
    """Atualiza a configuração de pagamento."""
    try:
        data = request.get_json()
        config = PaymentConfig.get_active_config()
        
        # Atualizar campos básicos
        if 'is_production' in data:
            config.is_production = bool(data['is_production'])
        
        if 'premium_price' in data:
            config.premium_price = float(data['premium_price'])
        
        if 'vip_price' in data:
            config.vip_price = float(data['vip_price'])
        
        if 'webhook_url' in data:
            config.webhook_url = data['webhook_url']
        
        if 'notification_email' in data:
            config.notification_email = data['notification_email']
        
        # Atualizar credenciais
        if 'public_key_sandbox' in data:
            config.public_key_sandbox = data['public_key_sandbox']
        
        if 'public_key_production' in data:
            config.public_key_production = data['public_key_production']
        
        if 'access_token_sandbox' in data:
            config.access_token_sandbox = data['access_token_sandbox']
        
        if 'access_token_production' in data:
            config.access_token_production = data['access_token_production']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Configuração atualizada com sucesso',
            'config': config.to_dict(include_sensitive=True)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/validate-credentials', methods=['POST'])
@jwt_required()
@admin_required
def validate_mercadopago_credentials():
    """Valida as credenciais do MercadoPago."""
    try:
        data = request.get_json()
        access_token = data.get('access_token')
        is_production = data.get('is_production', False)
        
        if not access_token:
            return jsonify({'error': 'Access token é obrigatório'}), 400
        
        # Validar credenciais usando o serviço
        mp_service = MercadoPagoService()
        is_valid = mp_service.validate_credentials(access_token, is_production)
        
        return jsonify({
            'valid': is_valid,
            'environment': 'production' if is_production else 'sandbox'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/payments', methods=['GET'])
@jwt_required()
@admin_required
def get_all_payments():
    """Retorna todos os pagamentos (admin)."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status')
        
        query = Payment.query
        
        if status:
            query = query.filter(Payment.status == status)
        
        payments = query.order_by(Payment.created_at.desc())\
                       .paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'payments': [payment.to_dict() for payment in payments.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': payments.total,
                'pages': payments.pages,
                'has_next': payments.has_next,
                'has_prev': payments.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/subscriptions', methods=['GET'])
@jwt_required()
@admin_required
def get_all_subscriptions():
    """Retorna todas as assinaturas (admin)."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status')
        plan_id = request.args.get('plan_id')
        
        query = Subscription.query
        
        if status:
            query = query.filter(Subscription.status == status)
        
        if plan_id:
            query = query.filter(Subscription.plan_id == plan_id)
        
        subscriptions = query.order_by(Subscription.created_at.desc())\
                           .paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'subscriptions': [sub.to_dict() for sub in subscriptions.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': subscriptions.total,
                'pages': subscriptions.pages,
                'has_next': subscriptions.has_next,
                'has_prev': subscriptions.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/subscription/<int:subscription_id>/extend', methods=['POST'])
@jwt_required()
@admin_required
def extend_subscription(subscription_id):
    """Estende uma assinatura manualmente (admin)."""
    try:
        data = request.get_json()
        days = data.get('days', 30)
        
        subscription = Subscription.query.get(subscription_id)
        if not subscription:
            return jsonify({'error': 'Assinatura não encontrada'}), 404
        
        subscription.extend_subscription(days)
        db.session.commit()
        
        return jsonify({
            'message': f'Assinatura estendida por {days} dias',
            'subscription': subscription.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/subscription/<int:subscription_id>/cancel', methods=['POST'])
@jwt_required()
@admin_required
def cancel_subscription_admin(subscription_id):
    """Cancela uma assinatura manualmente (admin)."""
    try:
        subscription = Subscription.query.get(subscription_id)
        if not subscription:
            return jsonify({'error': 'Assinatura não encontrada'}), 404
        
        if subscription.status != 'active':
            return jsonify({'error': 'Assinatura não está ativa'}), 400
        
        # Cancelar assinatura atual
        subscription.status = 'cancelled'
        
        # Criar assinatura gratuita se não for gratuita
        if subscription.plan_id != 'free':
            from datetime import datetime
            free_subscription = Subscription(
                user_id=subscription.user_id,
                plan_id='free',
                status='active',
                starts_at=datetime.utcnow()
            )
            db.session.add(free_subscription)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Assinatura cancelada com sucesso'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/stats', methods=['GET'])
@jwt_required()
@admin_required
def get_payment_stats():
    """Retorna estatísticas de pagamentos e assinaturas."""
    try:
        from sqlalchemy import func
        from datetime import datetime, timedelta
        
        # Estatísticas de pagamentos
        total_payments = Payment.query.count()
        approved_payments = Payment.query.filter(Payment.status == 'approved').count()
        pending_payments = Payment.query.filter(Payment.status == 'pending').count()
        
        # Receita total
        total_revenue = db.session.query(func.sum(Payment.amount))\
                                 .filter(Payment.status == 'approved').scalar() or 0
        
        # Receita do mês atual
        current_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        monthly_revenue = db.session.query(func.sum(Payment.amount))\
                                   .filter(Payment.status == 'approved')\
                                   .filter(Payment.created_at >= current_month).scalar() or 0
        
        # Estatísticas de assinaturas
        total_subscriptions = Subscription.query.count()
        active_subscriptions = Subscription.query.filter(Subscription.status == 'active').count()
        
        # Assinaturas por plano
        plan_stats = db.session.query(Subscription.plan_id, func.count(Subscription.id))\
                              .filter(Subscription.status == 'active')\
                              .group_by(Subscription.plan_id).all()
        
        # Assinaturas expirando em 7 dias
        expiring_soon = len(Subscription.get_expiring_subscriptions(7))
        
        return jsonify({
            'payments': {
                'total': total_payments,
                'approved': approved_payments,
                'pending': pending_payments,
                'approval_rate': (approved_payments / total_payments * 100) if total_payments > 0 else 0
            },
            'revenue': {
                'total': total_revenue,
                'monthly': monthly_revenue
            },
            'subscriptions': {
                'total': total_subscriptions,
                'active': active_subscriptions,
                'expiring_soon': expiring_soon,
                'by_plan': {plan: count for plan, count in plan_stats}
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/test-webhook', methods=['POST'])
@jwt_required()
@admin_required
def test_webhook():
    """Testa o webhook do MercadoPago com dados simulados."""
    try:
        # Dados de teste do webhook
        test_data = {
            "type": "payment",
            "data": {
                "id": "123456789"
            }
        }
        
        mp_service = MercadoPagoService()
        result = mp_service.process_webhook_notification(test_data)
        
        return jsonify({
            'message': 'Teste de webhook executado',
            'result': result
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@admin_bp.route('/maintenance/check-expired', methods=['POST'])
@jwt_required()
@admin_required
def run_check_expired():
    """Executa verificação de assinaturas expiradas manualmente."""
    try:
        service = SubscriptionService()
        result = service.check_expired_subscriptions()
        
        return jsonify(result), 200 if result['success'] else 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/maintenance/notify-expiring', methods=['POST'])
@jwt_required()
@admin_required
def run_notify_expiring():
    """Executa envio de notificações de expiração manualmente."""
    try:
        data = request.get_json() or {}
        days_ahead = data.get('days_ahead', 7)
        
        service = SubscriptionService()
        result = service.notify_expiring_subscriptions(days_ahead)
        
        return jsonify(result), 200 if result['success'] else 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/maintenance/full', methods=['POST'])
@jwt_required()
@admin_required
def run_full_maintenance():
    """Executa manutenção completa das assinaturas."""
    try:
        service = SubscriptionService()
        result = service.run_maintenance()
        
        return jsonify(result), 200 if result['success'] else 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/maintenance/subscription-stats', methods=['GET'])
@jwt_required()
@admin_required
def get_subscription_stats():
    """Retorna estatísticas detalhadas das assinaturas."""
    try:
        service = SubscriptionService()
        result = service.get_subscription_stats()
        
        return jsonify(result), 200 if result['success'] else 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/maintenance/extend-subscription', methods=['POST'])
@jwt_required()
@admin_required
def extend_subscription_admin():
    """Estende uma assinatura manualmente."""
    try:
        data = request.get_json()
        subscription_id = data.get('subscription_id')
        days = data.get('days', 30)
        
        if not subscription_id:
            return jsonify({'error': 'ID da assinatura é obrigatório'}), 400
        
        service = SubscriptionService()
        result = service.extend_subscription(subscription_id, days)
        
        return jsonify(result), 200 if result['success'] else 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/maintenance/reactivate-subscription', methods=['POST'])
@jwt_required()
@admin_required
def reactivate_subscription_admin():
    """Reativa uma assinatura após pagamento."""
    try:
        data = request.get_json()
        payment_id = data.get('payment_id')
        
        if not payment_id:
            return jsonify({'error': 'ID do pagamento é obrigatório'}), 400
        
        service = SubscriptionService()
        result = service.reactivate_subscription_after_payment(payment_id)
        
        return jsonify(result), 200 if result['success'] else 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

