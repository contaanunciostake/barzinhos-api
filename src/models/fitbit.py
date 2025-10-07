from src.models.base import db
from datetime import datetime

class FitbitUser(db.Model):
    __tablename__ = 'fitbit_users'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    fitbit_user_id = db.Column(db.String(50), unique=True, nullable=False)
    access_token = db.Column(db.String(500), nullable=False)
    refresh_token = db.Column(db.String(500), nullable=False)
    token_expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamento
    user = db.relationship('User', backref='fitbit_connection')

class FitbitActivity(db.Model):
    __tablename__ = 'fitbit_activities'
    
    id = db.Column(db.Integer, primary_key=True)
    fitbit_user_id = db.Column(db.Integer, db.ForeignKey('fitbit_users.id'), nullable=False)
    activity_id = db.Column(db.String(50), unique=True, nullable=False)
    activity_type = db.Column(db.String(50))  # run, walk, bike, etc
    start_time = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.Integer)  # em milissegundos
    distance = db.Column(db.Float)  # em km
    calories = db.Column(db.Integer)
    steps = db.Column(db.Integer)
    received_at = db.Column(db.DateTime, default=datetime.utcnow)
    raw_data = db.Column(db.Text)  # JSON completo da atividade
    
    # Relacionamento
    fitbit_user = db.relationship('FitbitUser', backref='activities')

class FitbitSubscription(db.Model):
    __tablename__ = 'fitbit_subscriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    fitbit_user_id = db.Column(db.Integer, db.ForeignKey('fitbit_users.id'), nullable=False)
    subscription_id = db.Column(db.String(100), unique=True, nullable=False)
    collection_type = db.Column(db.String(50))  # activities, sleep, body, etc
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamento
    fitbit_user = db.relationship('FitbitUser', backref='subscriptions')