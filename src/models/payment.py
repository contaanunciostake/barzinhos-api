from datetime import datetime
from src.models.base import db, BaseModel

class Payment(BaseModel):
    __tablename__ = 'payments'
    
    # Relacionamento com usuário
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Informações do plano
    plan_id = db.Column(db.String(50), nullable=False)  # 'premium', 'vip'
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='BRL')
    
    # Informações do MercadoPago
    mp_payment_id = db.Column(db.String(100), unique=True)  # ID do pagamento no MP
    mp_preference_id = db.Column(db.String(100))  # ID da preferência no MP
    mp_merchant_order_id = db.Column(db.String(100))  # ID da ordem no MP
    
    # Status do pagamento
    status = db.Column(db.String(50), default='pending')  # pending, approved, rejected, cancelled, refunded
    status_detail = db.Column(db.String(100))
    
    # Informações de processamento
    payment_method = db.Column(db.String(50))  # credit_card, debit_card, pix, etc
    payment_type = db.Column(db.String(50))
    
    # Datas importantes
    approved_at = db.Column(db.DateTime)
    expires_at = db.Column(db.DateTime)
    
    # Informações adicionais
    external_reference = db.Column(db.String(255))  # Referência externa personalizada
    description = db.Column(db.String(500))
    
    # Dados do webhook
    webhook_data = db.Column(db.Text)  # JSON com dados completos do webhook
    
    # Relacionamentos
    user = db.relationship('User', backref='payments')
    
    def is_approved(self):
        """Verifica se o pagamento foi aprovado."""
        return self.status == 'approved'
    
    def is_pending(self):
        """Verifica se o pagamento está pendente."""
        return self.status == 'pending'
    
    def is_rejected(self):
        """Verifica se o pagamento foi rejeitado."""
        return self.status in ['rejected', 'cancelled']
    
    def approve_payment(self):
        """Marca o pagamento como aprovado."""
        self.status = 'approved'
        self.approved_at = datetime.utcnow()
        
        # Ativar/renovar assinatura do usuário
        from src.models.subscription import Subscription
        from datetime import timedelta
        
        # Cancelar assinatura ativa anterior
        existing_subscription = Subscription.query.filter_by(
            user_id=self.user_id,
            status='active'
        ).first()
        
        if existing_subscription:
            existing_subscription.status = 'cancelled'
        
        # Criar nova assinatura
        expires_at = datetime.utcnow() + timedelta(days=30)
        subscription = Subscription(
            user_id=self.user_id,
            plan_id=self.plan_id,
            status='active',
            starts_at=datetime.utcnow(),
            expires_at=expires_at,
            payment_id=self.id
        )
        
        db.session.add(subscription)
        return subscription
    
    def get_status_display(self):
        """Retorna o status em português."""
        status_map = {
            'pending': 'Pendente',
            'approved': 'Aprovado',
            'rejected': 'Rejeitado',
            'cancelled': 'Cancelado',
            'refunded': 'Reembolsado',
            'in_process': 'Em processamento',
            'in_mediation': 'Em mediação',
            'charged_back': 'Estornado'
        }
        return status_map.get(self.status, self.status.title())
    
    def to_dict(self):
        """Converte o objeto para dicionário."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'plan_id': self.plan_id,
            'amount': self.amount,
            'currency': self.currency,
            'mp_payment_id': self.mp_payment_id,
            'mp_preference_id': self.mp_preference_id,
            'mp_merchant_order_id': self.mp_merchant_order_id,
            'status': self.status,
            'status_display': self.get_status_display(),
            'status_detail': self.status_detail,
            'payment_method': self.payment_method,
            'payment_type': self.payment_type,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'external_reference': self.external_reference,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def get_by_mp_payment_id(cls, mp_payment_id):
        """Busca pagamento pelo ID do MercadoPago."""
        return cls.query.filter_by(mp_payment_id=str(mp_payment_id)).first()
    
    @classmethod
    def get_user_payments(cls, user_id, limit=10):
        """Retorna os pagamentos de um usuário."""
        return cls.query.filter_by(user_id=user_id)\
                      .order_by(cls.created_at.desc())\
                      .limit(limit).all()
    
    def __repr__(self):
        return f'<Payment {self.id}:{self.plan_id}:{self.status}>'

