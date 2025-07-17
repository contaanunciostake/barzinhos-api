from src.models.base import db, BaseModel

class Establishment(BaseModel):
    __tablename__ = 'establishments'
    
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    type = db.Column(db.String(50), nullable=False)  # Bar, Restaurante, Pub, etc.
    
    # Endereço
    cep = db.Column(db.String(10))
    state = db.Column(db.String(50))
    city = db.Column(db.String(100))
    neighborhood = db.Column(db.String(100))
    address = db.Column(db.String(200))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    
    # Contato
    phone = db.Column(db.String(20))
    whatsapp = db.Column(db.String(20))
    instagram = db.Column(db.String(100))
    website = db.Column(db.String(200))
    
    # Características do estabelecimento
    faixa_etaria = db.Column(db.String(50))  # "18+", "Livre", "21+", etc.
    pet_friendly = db.Column(db.Boolean, default=False)
    lgbt_friendly = db.Column(db.Boolean, default=False)
    
    # Funcionamento e delivery
    horarios_funcionamento = db.Column(db.JSON)  # {"segunda": "18:00-02:00", "terca": "18:00-02:00", ...}
    delivery = db.Column(db.Boolean, default=False)
    link_delivery = db.Column(db.String(200))
    
    # Localização e referências
    ponto_referencia = db.Column(db.Text)
    como_chegar_transporte = db.Column(db.Text)  # Informações de metro/ônibus
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    is_approved = db.Column(db.Boolean, default=False)  # Admin aprova
    
    # Relacionamentos
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    images = db.relationship('EstablishmentImage', backref='establishment', lazy=True, cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='establishment', lazy=True, cascade='all, delete-orphan')
    
    # Campos calculados
    @property
    def average_rating(self):
        """Calcula a média das avaliações."""
        if not self.reviews:
            return 0
        return sum(review.rating for review in self.reviews) / len(self.reviews)
    
    @property
    def total_reviews(self):
        """Retorna o total de avaliações."""
        return len(self.reviews)
    
    def to_dict(self, include_reviews=False):
        """Converte o objeto Establishment para dicionário."""
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'type': self.type,
            'cep': self.cep,
            'state': self.state,
            'city': self.city,
            'neighborhood': self.neighborhood,
            'address': self.address,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'phone': self.phone,
            'whatsapp': self.whatsapp,
            'instagram': self.instagram,
            'website': self.website,
            'faixa_etaria': self.faixa_etaria,
            'pet_friendly': self.pet_friendly,
            'lgbt_friendly': self.lgbt_friendly,
            'horarios_funcionamento': self.horarios_funcionamento,
            'delivery': self.delivery,
            'link_delivery': self.link_delivery,
            'ponto_referencia': self.ponto_referencia,
            'como_chegar_transporte': self.como_chegar_transporte,
            'is_active': self.is_active,
            'is_approved': self.is_approved,
            'user_id': self.user_id,
            'average_rating': self.average_rating,
            'total_reviews': self.total_reviews,
            'images': [img.to_dict() for img in self.images],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_reviews:
            data['reviews'] = [review.to_dict() for review in self.reviews]
        
        return data
    
    def __repr__(self):
        return f'<Establishment {self.name}>'


class EstablishmentImage(BaseModel):
    __tablename__ = 'establishment_images'
    
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255))
    is_primary = db.Column(db.Boolean, default=False)
    
    # Relacionamento
    establishment_id = db.Column(db.Integer, db.ForeignKey('establishments.id'), nullable=False)
    
    def to_dict(self):
        """Converte o objeto EstablishmentImage para dicionário."""
        return {
            'id': self.id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'is_primary': self.is_primary,
            'establishment_id': self.establishment_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<EstablishmentImage {self.filename}>'

