from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import mercadopago
import os
from datetime import datetime, timedelta
from src.models.subscription import Subscription
from src.models.user import User
from src.models.payment_config import PaymentConfig
from src.models.payment import Payment
from src.services.mercadopago_service import MercadoPagoService
from src.models.base import db

plan_bp = Blueprint('plan', __name__)

@plan_bp.route('/', methods=['GET'])
def get_plans():
    """Retorna os planos disponíveis"""
    try:
        # Buscar configuração de preços
        config = PaymentConfig.query.first()
        
        # Valores padrão caso não haja configuração
        premium_price = config.premium_price if config else 29.90
        vip_price = config.vip_price if config else 49.90
        
        plans = [
            {
                "id": "free",
                "name": "Gratuito",
                "price": 0.00,
                "currency": "BRL",
                "features": [
                    "Acesso básico aos estabelecimentos",
                    "Visualização de avaliações",
                    "Busca simples",
                    "Suporte por email"
                ],
                "popular": False,
                "button_text": "Plano Atual"
            },
            {
                "id": "premium",
                "name": "Premium",
                "price": premium_price,
                "currency": "BRL",
                "features": [
                    "Todos os recursos do plano gratuito",
                    "Busca avançada com filtros",
                    "Avaliações detalhadas",
                    "Notificações de novos estabelecimentos",
                    "Suporte prioritário"
                ],
                "popular": True,
                "button_text": "Assinar Agora"
            },
            {
                "id": "vip",
                "name": "VIP",
                "price": vip_price,
                "currency": "BRL",
                "features": [
                    "Todos os recursos do Premium",
                    "Acesso antecipado a novos recursos",
                    "Análises personalizadas",
                    "Recomendações exclusivas",
                    "Suporte 24/7",
                    "Sem anúncios"
                ],
                "popular": False,
                "button_text": "Assinar Agora"
            }
        ]
        
        return jsonify({
            "success": True,
            "plans": plans
        }), 200
        
    except Exception as e:
        print(f"Erro ao buscar planos: {e}")
        return jsonify({
            "success": False,
            "message": "Erro interno do servidor"
        }), 500

@plan_bp.route('/subscribe', methods=['POST'])
@jwt_required()
def subscribe_plan():
    """Criar assinatura de plano"""
    try:
        data = request.get_json()
        plan_id = data.get('plan_id')
        user_id = get_jwt_identity()
        
        if not plan_id:
            return jsonify({
                "success": False,
                "message": "ID do plano é obrigatório"
            }), 400
        
        # Verificar se o plano existe
        valid_plans = ['free', 'premium', 'vip']
        if plan_id not in valid_plans:
            return jsonify({
                "success": False,
                "message": "Plano inválido"
            }), 400
        
        # Buscar usuário
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                "success": False,
                "message": "Usuário não encontrado"
            }), 404
        
        # Se for plano gratuito, criar assinatura diretamente
        if plan_id == 'free':
            # Verificar se já tem assinatura
            existing_subscription = Subscription.query.filter_by(user_id=user_id).first()
            
            if existing_subscription:
                existing_subscription.plan_type = 'free'
                existing_subscription.status = 'active'
                existing_subscription.updated_at = datetime.utcnow()
            else:
                subscription = Subscription(
                    user_id=user_id,
                    plan_type='free',
                    status='active',
                    starts_at=datetime.utcnow(),
                    expires_at=None  # Plano gratuito não expira
                )
                db.session.add(subscription)
            
            db.session.commit()
            
            return jsonify({
                "success": True,
                "message": "Assinatura gratuita ativada com sucesso",
                "subscription": {
                    "plan_type": "free",
                    "status": "active"
                }
            }), 200
        
        # Para planos pagos, criar preferência no MercadoPago
        config = PaymentConfig.query.first()
        if not config:
            return jsonify({
                "success": False,
                "message": "Configuração de pagamento não encontrada"
            }), 500
        
        # Configurar SDK do MercadoPago
        sdk = mercadopago.SDK(config.access_token)
        
        # Definir preços
        prices = {
            'premium': config.premium_price if config else 29.90,
            'vip': config.vip_price if config else 49.90
        }
        
        price = prices.get(plan_id, 0)
        
        # Criar preferência de pagamento
        preference_data = {
            "items": [
                {
                    "title": f"Plano {plan_id.title()} - Barzinhos",
                    "quantity": 1,
                    "unit_price": float(price),
                    "currency_id": "BRL"
                }
            ],
            "payer": {
                "name": user.name,
                "email": user.email
            },
            "external_reference": f"{user_id}_{plan_id}_{int(datetime.utcnow().timestamp())}",
            "notification_url": f"{request.host_url}api/payments/webhook",
            "back_urls": {
                "success": f"{request.host_url}payment/success",
                "failure": f"{request.host_url}payment/failure",
                "pending": f"{request.host_url}payment/pending"
            },
            "auto_return": "approved",
            "payment_methods": {
                "excluded_payment_methods": [],
                "excluded_payment_types": [],
                "installments": 12
            }
        }
        
        # Criar preferência
        preference_response = sdk.preference().create(preference_data)
        
        if preference_response["status"] == 201:
            preference = preference_response["response"]
            
            # Salvar informações do pagamento
            payment = Payment(
                user_id=user_id,
                plan_type=plan_id,
                amount=price,
                currency='BRL',
                payment_method='mercadopago',
                external_id=preference['id'],
                status='pending'
            )
            db.session.add(payment)
            db.session.commit()
            
            return jsonify({
                "success": True,
                "preference_id": preference['id'],
                "init_point": preference['init_point'],
                "sandbox_init_point": preference.get('sandbox_init_point'),
                "payment_id": payment.id
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "Erro ao criar preferência de pagamento",
                "error": preference_response.get("response", {})
            }), 500
            
    except Exception as e:
        print(f"Erro ao criar assinatura: {e}")
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": "Erro interno do servidor"
        }), 500

@plan_bp.route('/current', methods=['GET'])
@jwt_required()
def get_current_plan():
    """Retorna o plano atual do usuário"""
    try:
        user_id = get_jwt_identity()
        
        subscription = Subscription.query.filter_by(user_id=user_id).first()
        
        if not subscription:
            return jsonify({
                "success": True,
                "current_plan": {
                    "plan_type": "free",
                    "status": "active",
                    "expires_at": None
                }
            }), 200
        
        return jsonify({
            "success": True,
            "current_plan": {
                "plan_type": subscription.plan_type,
                "status": subscription.status,
                "starts_at": subscription.starts_at.isoformat() if subscription.starts_at else None,
                "expires_at": subscription.expires_at.isoformat() if subscription.expires_at else None
            }
        }), 200
        
    except Exception as e:
        print(f"Erro ao buscar plano atual: {e}")
        return jsonify({
            "success": False,
            "message": "Erro interno do servidor"
        }), 500

