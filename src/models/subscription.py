from datetime import datetime, timedelta
from src.models.base import db

class Subscription(db.Model):
    __tablename__ = 'subscriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    plan_id = db.Column(db.String(50), nullable=False, default='free')
    status = db.Column(db.String(20), nullable=False, default='active')
    starts_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    
    # Novas colunas para pagamentos
    payment_id = db.Column(db.Integer, db.ForeignKey('payments.id'), nullable=True)
    expiration_notified = db.Column(db.Boolean, default=False, nullable=False)
    auto_renew = db.Column(db.Boolean, default=False, nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    user = db.relationship('User', backref='subscriptions')
    payment = db.relationship('Payment', backref='subscription', uselist=False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.starts_at:
            self.starts_at = datetime.utcnow()
        if self.plan_id != 'free' and not self.expires_at:
            self.expires_at = datetime.utcnow() + timedelta(days=30)
    
    def is_active(self):
        """Verifica se a assinatura está ativa."""
        if self.status != 'active':
            return False
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False
        return True
    
    @property
    def days_until_expiration(self):
        """Retorna quantos dias faltam para expirar."""
        if not self.expires_at:
            return None
        delta = self.expires_at - datetime.utcnow()
        return max(0, delta.days)
    
    @property
    def is_expiring_soon(self):
        """Verifica se a assinatura expira em 3 dias ou menos."""
        days = self.days_until_expiration
        return days is not None and days <= 3
    
    def get_plan_features(self):
        """Retorna as características do plano atual."""
        features = {
            'free': [
                'Acesso básico aos estabelecimentos',
                'Visualização de avaliações',
                'Busca simples'
            ],
            'premium': [
                'Todos os recursos gratuitos',
                'Avaliações ilimitadas',
                'Busca avançada com filtros',
                'Notificações de novos estabelecimentos',
                'Suporte prioritário'
            ],
            'vip': [
                'Todos os recursos premium',
                'Acesso antecipado a novos recursos',
                'Relatórios personalizados',
                'API de integração',
                'Suporte 24/7',
                'Badge VIP no perfil'
            ]
        }
        return features.get(self.plan_id, features['free'])
    
    def extend_subscription(self, days=30):
        """Estende a assinatura por X dias."""
        if self.expires_at:
            # Se ainda não expirou, adiciona aos dias restantes
            if datetime.utcnow() < self.expires_at:
                self.expires_at += timedelta(days=days)
            else:
                # Se já expirou, começa a contar de hoje
                self.expires_at = datetime.utcnow() + timedelta(days=days)
        else:
            # Se não tinha expiração, define para X dias a partir de hoje
            self.expires_at = datetime.utcnow() + timedelta(days=days)
        
        self.status = 'active'
        self.expiration_notified = False
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def expire_subscription(self):
        """Expira a assinatura e cria uma gratuita."""
        self.status = 'expired'
        self.updated_at = datetime.utcnow()
        
        # Criar nova assinatura gratuita
        new_subscription = Subscription(
            user_id=self.user_id,
            plan_id='free',
            status='active',
            starts_at=datetime.utcnow(),
            expires_at=None
        )
        
        db.session.add(new_subscription)
        db.session.commit()
        
        return new_subscription
    
    def activate_paid_plan(self, plan_id, payment_id=None):
        """Ativa um plano pago."""
        self.plan_id = plan_id
        self.status = 'active'
        self.starts_at = datetime.utcnow()
        self.expires_at = datetime.utcnow() + timedelta(days=30)
        self.payment_id = payment_id
        self.expiration_notified = False
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def to_dict(self):
        """Converte para dicionário."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'plan_id': self.plan_id,
            'status': self.status,
            'starts_at': self.starts_at.isoformat() if self.starts_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'payment_id': self.payment_id,
            'expiration_notified': self.expiration_notified,
            'auto_renew': self.auto_renew,
            'is_active': self.is_active,
            'days_until_expiration': self.days_until_expiration,
            'is_expiring_soon': self.is_expiring_soon,
            'features': self.get_plan_features(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

