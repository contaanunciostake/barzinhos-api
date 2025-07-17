from src.models.base import db, BaseModel

class Review(BaseModel):
    __tablename__ = 'reviews'
    
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    comment = db.Column(db.Text)
    reviewer_name = db.Column(db.String(100), nullable=False)
    reviewer_email = db.Column(db.String(120))
    
    # Status
    is_approved = db.Column(db.Boolean, default=True)  # Admin pode reprovar
    
    # Relacionamento
    establishment_id = db.Column(db.Integer, db.ForeignKey('establishments.id'), nullable=False)
    
    def to_dict(self):
        """Converte o objeto Review para dicionário."""
        return {
            'id': self.id,
            'rating': self.rating,
            'comment': self.comment,
            'reviewer_name': self.reviewer_name,
            'reviewer_email': self.reviewer_email,
            'is_approved': self.is_approved,
            'establishment_id': self.establishment_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Review {self.rating} stars for {self.establishment_id}>'

