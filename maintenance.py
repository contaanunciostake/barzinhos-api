#!/usr/bin/env python3
"""
Script de manutenção para verificação e expiração de assinaturas.
Execute este script periodicamente (ex: via cron) para manter o sistema atualizado.

Uso:
    python maintenance.py [comando]

Comandos disponíveis:
    check-expired    - Verifica e expira assinaturas vencidas
    notify-expiring  - Envia notificações para assinaturas prestes a expirar
    full-maintenance - Executa manutenção completa
    stats           - Mostra estatísticas das assinaturas
"""

import sys
import os
import logging
from datetime import datetime

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from src.models.base import db
from src.services.subscription_service import SubscriptionService

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('maintenance.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def create_app():
    """Cria a aplicação Flask para o script de manutenção."""
    app = Flask(__name__)
    
    # Configurações básicas
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'maintenance-key')
    
    # Configuração do banco de dados
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'src', 'database', 'app.db')}"
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    return app

def check_expired():
    """Verifica e expira assinaturas vencidas."""
    logger.info("Iniciando verificação de assinaturas expiradas...")
    
    service = SubscriptionService()
    result = service.check_expired_subscriptions()
    
    if result['success']:
        logger.info(f"✓ {result['message']}")
    else:
        logger.error(f"✗ Erro: {result['error']}")
    
    return result['success']

def notify_expiring():
    """Envia notificações para assinaturas prestes a expirar."""
    logger.info("Iniciando envio de notificações de expiração...")
    
    service = SubscriptionService()
    result = service.notify_expiring_subscriptions()
    
    if result['success']:
        logger.info(f"✓ {result['message']}")
    else:
        logger.error(f"✗ Erro: {result['error']}")
    
    return result['success']

def full_maintenance():
    """Executa manutenção completa."""
    logger.info("Iniciando manutenção completa das assinaturas...")
    
    service = SubscriptionService()
    result = service.run_maintenance()
    
    if result['success']:
        logger.info("✓ Manutenção completa executada com sucesso")
        
        # Log dos resultados
        expired = result['results']['expired']
        notifications = result['results']['notifications']
        
        logger.info(f"  - Assinaturas expiradas: {expired.get('expired_count', 0)}")
        logger.info(f"  - Notificações enviadas: {notifications.get('notified_count', 0)}")
        
    else:
        logger.error(f"✗ Erro na manutenção: {result['error']}")
    
    return result['success']

def show_stats():
    """Mostra estatísticas das assinaturas."""
    logger.info("Obtendo estatísticas das assinaturas...")
    
    service = SubscriptionService()
    result = service.get_subscription_stats()
    
    if result['success']:
        stats = result['stats']
        
        print("\n=== ESTATÍSTICAS DAS ASSINATURAS ===")
        print(f"Data/Hora: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
        
        print("\nAssinaturas ativas por plano:")
        for plan, count in stats['active_by_plan'].items():
            print(f"  {plan}: {count}")
        
        print("\nAssinaturas expirando:")
        print(f"  Em 1 dia: {stats['expiring']['1_day']}")
        print(f"  Em 3 dias: {stats['expiring']['3_days']}")
        print(f"  Em 7 dias: {stats['expiring']['7_days']}")
        
        print("\nAssinaturas por status:")
        for status, count in stats['by_status'].items():
            print(f"  {status}: {count}")
        
        print("\n" + "="*40)
        
    else:
        logger.error(f"✗ Erro ao obter estatísticas: {result['error']}")
    
    return result['success']

def main():
    """Função principal do script."""
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    command = sys.argv[1]
    
    # Criar aplicação Flask
    app = create_app()
    
    with app.app_context():
        success = False
        
        if command == 'check-expired':
            success = check_expired()
        elif command == 'notify-expiring':
            success = notify_expiring()
        elif command == 'full-maintenance':
            success = full_maintenance()
        elif command == 'stats':
            success = show_stats()
        else:
            print(f"Comando desconhecido: {command}")
            print(__doc__)
            sys.exit(1)
        
        if success:
            logger.info("Script executado com sucesso")
            sys.exit(0)
        else:
            logger.error("Script executado com erros")
            sys.exit(1)

if __name__ == '__main__':
    main()

