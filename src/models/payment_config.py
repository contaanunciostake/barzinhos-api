from src.models.base import db, BaseModel
from werkzeug.security import generate_password_hash, check_password_hash

class PaymentConfig(BaseModel):
    __tablename__ = 'payment_configs'
    
    # Configurações gerais
    is_production = db.Column(db.Boolean, default=False, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Credenciais do MercadoPago
    public_key_sandbox = db.Column(db.Text)
    access_token_sandbox = db.Column(db.Text)
    public_key_production = db.Column(db.Text)
    access_token_production = db.Column(db.Text)
    
    # Configurações de webhook
    webhook_url = db.Column(db.String(500))
    webhook_secret = db.Column(db.String(255))
    
    # Configurações de planos e preços
    premium_price = db.Column(db.Float, default=29.90)
    vip_price = db.Column(db.Float, default=49.90)
    
    # Configurações de notificação
    notification_email = db.Column(db.String(255))
    
    def get_current_credentials(self):
        """Retorna as credenciais baseadas no ambiente atual."""
        if self.is_production:
            return {
                'public_key': self.public_key_production,
                'access_token': self.access_token_production
            }
        else:
            return {
                'public_key': self.public_key_sandbox,
                'access_token': self.access_token_sandbox
            }
    
    def set_access_token(self, token, is_production=None):
        """Define o access token com criptografia básica."""
        if is_production is None:
            is_production = self.is_production
            
        if is_production:
            self.access_token_production = generate_password_hash(token)
        else:
            self.access_token_sandbox = generate_password_hash(token)
    
    def verify_access_token(self, token, is_production=None):
        """Verifica se o access token está correto."""
        if is_production is None:
            is_production = self.is_production
            
        stored_token = self.access_token_production if is_production else self.access_token_sandbox
        if not stored_token:
            return False
        return check_password_hash(stored_token, token)
    
    def get_plan_price(self, plan_id):
        """Retorna o preço do plano especificado."""
        prices = {
            'premium': self.premium_price,
            'vip': self.vip_price,
            'free': 0.0
        }
        return prices.get(plan_id, 0.0)
    
    def to_dict(self, include_sensitive=False):
        """Converte o objeto para dicionário."""
        data = {
            'id': self.id,
            'is_production': self.is_production,
            'is_active': self.is_active,
            'webhook_url': self.webhook_url,
            'premium_price': self.premium_price,
            'vip_price': self.vip_price,
            'notification_email': self.notification_email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_sensitive:
            credentials = self.get_current_credentials()
            data.update({
                'public_key': credentials['public_key'],
                'has_access_token': bool(credentials['access_token'])
            })
        
        return data
    
    @classmethod
    def get_active_config(cls):
        """Retorna a configuração ativa atual."""
        config = cls.query.filter_by(is_active=True).first()
        if not config:
            # Criar configuração padrão se não existir
            config = cls(
                is_production=False,
                is_active=True,
                premium_price=29.90,
                vip_price=49.90
            )
            db.session.add(config)
            db.session.commit()
        return config
    
    def __repr__(self):
        env = "PROD" if self.is_production else "DEV"
        return f'<PaymentConfig {env}:{self.is_active}>'

