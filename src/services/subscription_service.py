from datetime import datetime, timedelta
from src.models.base import db
from src.models.subscription import Subscription
from src.models.user import User
from src.models.payment_config import PaymentConfig
import logging

class SubscriptionService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def check_expired_subscriptions(self):
        """Verifica e expira assinaturas vencidas."""
        try:
            expired_subscriptions = Subscription.get_expired_subscriptions()
            expired_count = 0
            
            for subscription in expired_subscriptions:
                self.logger.info(f"Expirando assinatura {subscription.id} do usuário {subscription.user_id}")
                subscription.expire()
                expired_count += 1
            
            if expired_count > 0:
                db.session.commit()
                self.logger.info(f"Total de {expired_count} assinaturas expiradas")
            
            return {
                'success': True,
                'expired_count': expired_count,
                'message': f'{expired_count} assinaturas expiradas'
            }
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Erro ao verificar assinaturas expiradas: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def notify_expiring_subscriptions(self, days_ahead=7):
        """Notifica usuários sobre assinaturas que estão prestes a expirar."""
        try:
            expiring_subscriptions = Subscription.get_expiring_subscriptions(days_ahead)
            notified_count = 0
            
            for subscription in expiring_subscriptions:
                # Enviar notificação (implementar conforme necessário)
                self._send_expiration_notification(subscription)
                
                # Marcar como notificado
                subscription.expiration_notified = True
                notified_count += 1
                
                self.logger.info(f"Notificação de expiração enviada para usuário {subscription.user_id}")
            
            if notified_count > 0:
                db.session.commit()
                self.logger.info(f"Total de {notified_count} notificações enviadas")
            
            return {
                'success': True,
                'notified_count': notified_count,
                'message': f'{notified_count} notificações enviadas'
            }
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Erro ao enviar notificações: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _send_expiration_notification(self, subscription):
        """Envia notificação de expiração para o usuário."""
        # Implementar envio de email/notificação
        # Por enquanto, apenas log
        user = subscription.user
        days_left = subscription.days_until_expiration()
        
        self.logger.info(f"NOTIFICAÇÃO: Usuário {user.email} - Plano {subscription.plan_id} expira em {days_left} dias")
        
        # Aqui você pode implementar:
        # - Envio de email
        # - Notificação push
        # - Notificação no sistema
        # - etc.
    
    def reactivate_subscription_after_payment(self, payment_id):
        """Reativa assinatura após pagamento aprovado."""
        try:
            from src.models.payment import Payment
            
            payment = Payment.query.get(payment_id)
            if not payment:
                return {
                    'success': False,
                    'error': 'Pagamento não encontrado'
                }
            
            if not payment.is_approved():
                return {
                    'success': False,
                    'error': 'Pagamento não foi aprovado'
                }
            
            # Verificar se já existe assinatura ativa para este pagamento
            existing_subscription = Subscription.query.filter_by(
                payment_id=payment_id,
                status='active'
            ).first()
            
            if existing_subscription:
                return {
                    'success': True,
                    'message': 'Assinatura já está ativa',
                    'subscription_id': existing_subscription.id
                }
            
            # Cancelar assinatura atual do usuário
            current_subscription = Subscription.get_active_subscription(payment.user_id)
            if current_subscription:
                current_subscription.status = 'cancelled'
            
            # Criar nova assinatura
            new_subscription = Subscription(
                user_id=payment.user_id,
                plan_id=payment.plan_id,
                status='active',
                starts_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(days=30),
                payment_id=payment.id
            )
            
            db.session.add(new_subscription)
            db.session.commit()
            
            self.logger.info(f"Assinatura reativada para usuário {payment.user_id} - Plano {payment.plan_id}")
            
            return {
                'success': True,
                'message': 'Assinatura reativada com sucesso',
                'subscription_id': new_subscription.id
            }
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Erro ao reativar assinatura: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_subscription_stats(self):
        """Retorna estatísticas das assinaturas."""
        try:
            from sqlalchemy import func
            
            # Assinaturas ativas por plano
            active_by_plan = db.session.query(
                Subscription.plan_id,
                func.count(Subscription.id)
            ).filter(Subscription.status == 'active')\
             .group_by(Subscription.plan_id).all()
            
            # Assinaturas expirando em diferentes períodos
            expiring_1_day = len(Subscription.get_expiring_subscriptions(1))
            expiring_3_days = len(Subscription.get_expiring_subscriptions(3))
            expiring_7_days = len(Subscription.get_expiring_subscriptions(7))
            
            # Total de assinaturas por status
            status_counts = db.session.query(
                Subscription.status,
                func.count(Subscription.id)
            ).group_by(Subscription.status).all()
            
            return {
                'success': True,
                'stats': {
                    'active_by_plan': {plan: count for plan, count in active_by_plan},
                    'expiring': {
                        '1_day': expiring_1_day,
                        '3_days': expiring_3_days,
                        '7_days': expiring_7_days
                    },
                    'by_status': {status: count for status, count in status_counts}
                }
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao obter estatísticas: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def extend_subscription(self, subscription_id, days=30):
        """Estende uma assinatura por X dias."""
        try:
            subscription = Subscription.query.get(subscription_id)
            if not subscription:
                return {
                    'success': False,
                    'error': 'Assinatura não encontrada'
                }
            
            subscription.extend_subscription(days)
            db.session.commit()
            
            self.logger.info(f"Assinatura {subscription_id} estendida por {days} dias")
            
            return {
                'success': True,
                'message': f'Assinatura estendida por {days} dias',
                'new_expiration': subscription.expires_at.isoformat() if subscription.expires_at else None
            }
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Erro ao estender assinatura: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def run_maintenance(self):
        """Executa manutenção completa das assinaturas."""
        try:
            results = {
                'expired': self.check_expired_subscriptions(),
                'notifications': self.notify_expiring_subscriptions(),
                'stats': self.get_subscription_stats()
            }
            
            self.logger.info("Manutenção de assinaturas executada com sucesso")
            
            return {
                'success': True,
                'results': results,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Erro na manutenção de assinaturas: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

