#!/usr/bin/env python3
"""
Script de teste para validar o sistema de pagamento do MercadoPago.
Este script testa as principais funcionalidades sem fazer pagamentos reais.
"""

import sys
import os
import json
from datetime import datetime, timedelta

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from src.models.base import db
from src.models.user import User
from src.models.establishment import Establishment, EstablishmentImage
from src.models.review import Review
from src.models.payment_config import PaymentConfig
from src.models.payment import Payment
from src.models.subscription import Subscription
from src.services.subscription_service import SubscriptionService

def create_test_app():
    """Cria a aplicação Flask para testes."""
    app = Flask(__name__)
    
    # Configurações de teste
    app.config['SECRET_KEY'] = 'test-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Banco em memória para testes
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['TESTING'] = True
    
    db.init_app(app)
    
    return app

def setup_test_data():
    """Configura dados de teste."""
    print("Configurando dados de teste...")
    
    # Criar tabelas
    db.create_all()
    
    # Criar usuário de teste
    user = User(
        username='test_user',
        email='test@example.com',
        role='establishment'
    )
    user.set_password('test123')
    db.session.add(user)
    
    # Criar usuário admin
    admin = User(
        username='admin',
        email='admin@example.com',
        role='admin'
    )
    admin.set_password('admin123')
    db.session.add(admin)
    
    # Criar configuração de pagamento
    config = PaymentConfig(
        is_production=False,
        is_active=True,
        public_key_sandbox='TEST-public-key',
        access_token_sandbox='TEST-access-token',
        premium_price=29.90,
        vip_price=49.90,
        webhook_url='https://example.com/webhook'
    )
    db.session.add(config)
    
    db.session.commit()
    
    return user, admin, config

def test_payment_config():
    """Testa o modelo PaymentConfig."""
    print("\n=== Testando PaymentConfig ===")
    
    config = PaymentConfig.get_active_config()
    
    # Testar obtenção de credenciais
    credentials = config.get_current_credentials()
    assert credentials['public_key'] == 'TEST-public-key'
    assert credentials['access_token'] == 'TEST-access-token'
    print("✓ Credenciais obtidas corretamente")
    
    # Testar preços dos planos
    assert config.get_plan_price('premium') == 29.90
    assert config.get_plan_price('vip') == 49.90
    assert config.get_plan_price('free') == 0.0
    print("✓ Preços dos planos corretos")
    
    # Testar conversão para dict
    config_dict = config.to_dict(include_sensitive=True)
    assert 'public_key' in config_dict
    assert config_dict['premium_price'] == 29.90
    print("✓ Conversão para dict funcionando")

def test_payment_model():
    """Testa o modelo Payment."""
    print("\n=== Testando Payment ===")
    
    user = User.query.filter_by(username='test_user').first()
    
    # Criar pagamento de teste
    payment = Payment(
        user_id=user.id,
        plan_id='premium',
        amount=29.90,
        currency='BRL',
        mp_payment_id='123456789',
        status='pending',
        description='Teste de pagamento'
    )
    db.session.add(payment)
    db.session.commit()
    
    # Testar status
    assert payment.is_pending()
    assert not payment.is_approved()
    print("✓ Status de pagamento correto")
    
    # Testar aprovação
    payment.status = 'approved'
    payment.approved_at = datetime.utcnow()
    subscription = payment.approve_payment()
    db.session.commit()
    
    assert payment.is_approved()
    assert subscription.plan_id == 'premium'
    assert subscription.user_id == user.id
    print("✓ Aprovação de pagamento funcionando")
    
    # Testar busca por MP ID
    found_payment = Payment.get_by_mp_payment_id('123456789')
    assert found_payment.id == payment.id
    print("✓ Busca por MP ID funcionando")

def test_subscription_model():
    """Testa o modelo Subscription."""
    print("\n=== Testando Subscription ===")
    
    user = User.query.filter_by(username='test_user').first()
    
    # Criar assinatura de teste
    subscription = Subscription(
        user_id=user.id,
        plan_id='premium',
        status='active',
        starts_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(days=30)
    )
    db.session.add(subscription)
    db.session.commit()
    
    # Testar se está ativa
    assert subscription.is_active()
    print("✓ Assinatura ativa")
    
    # Testar dias até expiração
    days_left = subscription.days_until_expiration()
    assert 29 <= days_left <= 30
    print(f"✓ Dias até expiração: {days_left}")
    
    # Testar características do plano
    features = subscription.get_plan_features()
    assert features['name'] == 'Premium'
    assert features['max_photos'] == -1
    print("✓ Características do plano corretas")
    
    # Testar extensão
    old_expiration = subscription.expires_at
    subscription.extend_subscription(7)
    assert subscription.expires_at > old_expiration
    print("✓ Extensão de assinatura funcionando")

def test_subscription_service():
    """Testa o SubscriptionService."""
    print("\n=== Testando SubscriptionService ===")
    
    service = SubscriptionService()
    user = User.query.filter_by(username='test_user').first()
    
    # Criar assinatura expirada
    expired_subscription = Subscription(
        user_id=user.id,
        plan_id='vip',
        status='active',
        starts_at=datetime.utcnow() - timedelta(days=35),
        expires_at=datetime.utcnow() - timedelta(days=5)
    )
    db.session.add(expired_subscription)
    db.session.commit()
    
    # Testar verificação de expiradas
    result = service.check_expired_subscriptions()
    assert result['success']
    assert result['expired_count'] >= 1
    print("✓ Verificação de assinaturas expiradas funcionando")
    
    # Verificar se foi criada assinatura gratuita
    free_subscription = Subscription.query.filter_by(
        user_id=user.id,
        plan_id='free',
        status='active'
    ).first()
    assert free_subscription is not None
    print("✓ Assinatura gratuita criada após expiração")
    
    # Testar estatísticas
    stats_result = service.get_subscription_stats()
    assert stats_result['success']
    assert 'active_by_plan' in stats_result['stats']
    print("✓ Estatísticas funcionando")

def test_expiring_notifications():
    """Testa notificações de expiração."""
    print("\n=== Testando Notificações de Expiração ===")
    
    service = SubscriptionService()
    user = User.query.filter_by(username='test_user').first()
    
    # Criar assinatura que expira em 3 dias
    expiring_subscription = Subscription(
        user_id=user.id,
        plan_id='premium',
        status='active',
        starts_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(days=3),
        expiration_notified=False
    )
    db.session.add(expiring_subscription)
    db.session.commit()
    
    # Testar notificações
    result = service.notify_expiring_subscriptions(7)
    assert result['success']
    print("✓ Notificações de expiração funcionando")
    
    # Verificar se foi marcada como notificada
    db.session.refresh(expiring_subscription)
    assert expiring_subscription.expiration_notified
    print("✓ Flag de notificação atualizada")

def test_webhook_simulation():
    """Simula processamento de webhook."""
    print("\n=== Testando Simulação de Webhook ===")
    
    # Dados simulados de webhook
    webhook_data = {
        "type": "payment",
        "data": {
            "id": "987654321"
        }
    }
    
    # Criar pagamento para simular
    user = User.query.filter_by(username='test_user').first()
    payment = Payment(
        user_id=user.id,
        plan_id='vip',
        amount=49.90,
        currency='BRL',
        mp_payment_id='987654321',
        status='pending',
        external_reference=f'user_{user.id}_plan_vip_{int(datetime.utcnow().timestamp())}'
    )
    db.session.add(payment)
    db.session.commit()
    
    print("✓ Simulação de webhook preparada")

def run_all_tests():
    """Executa todos os testes."""
    print("Iniciando testes do sistema de pagamento...")
    print("=" * 50)
    
    try:
        # Configurar dados de teste
        user, admin, config = setup_test_data()
        
        # Executar testes
        test_payment_config()
        test_payment_model()
        test_subscription_model()
        test_subscription_service()
        test_expiring_notifications()
        test_webhook_simulation()
        
        print("\n" + "=" * 50)
        print("✅ TODOS OS TESTES PASSARAM!")
        print("Sistema de pagamento validado com sucesso.")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO NO TESTE: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Função principal."""
    app = create_test_app()
    
    with app.app_context():
        success = run_all_tests()
        
        if success:
            print("\n🎉 Sistema pronto para uso!")
            sys.exit(0)
        else:
            print("\n⚠️  Corrija os erros antes de usar o sistema.")
            sys.exit(1)

if __name__ == '__main__':
    main()

