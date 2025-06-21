from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src.models.user import db, User  # Importando User para usar no relacionamento

class Establishment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    # Novo campo obrigatório para associação ao usuário (dono do estabelecimento)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship("User", backref="establishments")

    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    address = db.Column(db.String(200), nullable=False)
    neighborhood = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    whatsapp = db.Column(db.String(20))
    type = db.Column(db.String(50), nullable=False)  # Boteco, Choperia, Petiscaria, etc.
    is_open = db.Column(db.Boolean, default=True)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    image_url = db.Column(db.String(200))
    menu_url = db.Column(db.String(200))
    website = db.Column(db.String(200))
    instagram = db.Column(db.String(100))
    plan_type = db.Column(db.String(20), default='bronze')  # bronze, prata, ouro
    is_approved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamento com avaliações
    reviews = db.relationship('Review', backref='establishment', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Establishment {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'description': self.description,
            'address': self.address,
            'neighborhood': self.neighborhood,
            'phone': self.phone,
            'whatsapp': self.whatsapp,
            'type': self.type,
            'is_open': self.is_open,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'image_url': self.image_url,
            'menu_url': self.menu_url,
            'website': self.website,
            'instagram': self.instagram,
            'plan_type': self.plan_type,
            'is_approved': self.is_approved,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'rating': self.get_average_rating(),
            'review_count': len(self.reviews)
        }

    def get_average_rating(self):
        if not self.reviews:
            return 0
        return sum(review.rating for review in self.reviews) / len(self.reviews)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    establishment_id = db.Column(db.Integer, db.ForeignKey('establishment.id'), nullable=False)
    user_name = db.Column(db.String(100), nullable=False)
    user_email = db.Column(db.String(120))
    rating = db.Column(db.Integer, nullable=False)  # 1-5 estrelas
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Review {self.rating} stars for {self.establishment_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'establishment_id': self.establishment_id,
            'user_name': self.user_name,
            'user_email': self.user_email,
            'rating': self.rating,
            'comment': self.comment,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class EstablishmentImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    establishment_id = db.Column(db.Integer, db.ForeignKey('establishment.id'), nullable=False)
    image_url = db.Column(db.String(200), nullable=False)
    is_primary = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<EstablishmentImage {self.image_url}>'

    def to_dict(self):
        return {
            'id': self.id,
            'establishment_id': self.establishment_id,
            'image_url': self.image_url,
            'is_primary': self.is_primary,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
