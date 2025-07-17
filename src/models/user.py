from werkzeug.security import generate_password_hash, check_password_hash
from src.models.base import db, BaseModel

class User(BaseModel):
    __tablename__ = 'users'
    
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='establishment')  # 'admin' or 'establishment'
    is_active = db.Column(db.Boolean, default=True)
    
    # Campos de perfil
    phone = db.Column(db.String(20))
    address = db.Column(db.String(255))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    bio = db.Column(db.Text)
    profile_photo = db.Column(db.String(255))
    
    # Relacionamento com estabelecimentos (um usuário pode ter um estabelecimento)
    establishment = db.relationship('Establishment', backref='owner', uselist=False)
    
    def set_password(self, password):
        """Define a senha do usuário usando hash."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verifica se a senha fornecida está correta."""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Converte o objeto User para dicionário."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'phone': self.phone,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'bio': self.bio,
            'profile_photo': self.profile_photo,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<User {self.username}>'

