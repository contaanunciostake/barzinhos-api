from flask import Blueprint, request, jsonify, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
import requests
import os
import json
import hmac
import hashlib
from datetime import datetime, timedelta
from src.models.base import db
from src.models.fitbit import FitbitUser, FitbitActivity, FitbitSubscription
from src.models.user import User

fitbit_bp = Blueprint('fitbit', __name__)

# Configurações do Fitbit
FITBIT_CLIENT_ID = os.environ.get('FITBIT_CLIENT_ID', '23TG6L')
FITBIT_CLIENT_SECRET = os.environ.get('FITBIT_CLIENT_SECRET', '865176f8088f0d18023a42586addbae8')
FITBIT_REDIRECT_URI = os.environ.get('FITBIT_REDIRECT_URI', 'https://betfit-frontend-thwz.onrender.com/fitbit/callback')
FITBIT_WEBHOOK_VERIFY_CODE = os.environ.get('FITBIT_WEBHOOK_VERIFY_CODE', 'betfit_secret_verification_2025')

# 1. CONECTAR FITBIT - Iniciar OAuth
@fitbit_bp.route('/connect', methods=['GET'])
@jwt_required()
def connect_fitbit():
    """Redireciona usuário para autorização Fitbit"""
    user_id = get_jwt_identity()
    
    # URL de autorização do Fitbit
    auth_url = (
        f"https://www.fitbit.com/oauth2/authorize?"
        f"response_type=code&"
        f"client_id={FITBIT_CLIENT_ID}&"
        f"redirect_uri={FITBIT_REDIRECT_URI}&"
        f"scope=activity%20heartrate%20location%20nutrition%20profile%20settings%20sleep%20social%20weight&"
        f"state={user_id}"
    )
    
    return jsonify({
        'authorization_url': auth_url
    })

# 2. CALLBACK - Receber código de autorização
@fitbit_bp.route('/callback', methods=['GET'])
def fitbit_callback():
    """Processa callback do Fitbit após autorização"""
    code = request.args.get('code')
    state = request.args.get('state')  # user_id
    
    if not code:
        return jsonify({'error': 'Código de autorização não fornecido'}), 400
    
    # Trocar código por tokens
    token_url = 'https://api.fitbit.com/oauth2/token'
    
    auth_header = requests.auth.HTTPBasicAuth(FITBIT_CLIENT_ID, FITBIT_CLIENT_SECRET)
    
    data = {
        'client_id': FITBIT_CLIENT_ID,
        'grant_type': 'authorization_code',
        'redirect_uri': FITBIT_REDIRECT_URI,
        'code': code
    }
    
    response = requests.post(token_url, auth=auth_header, data=data)
    
    if response.status_code != 200:
        return jsonify({'error': 'Falha ao obter tokens', 'details': response.text}), 400
    
    token_data = response.json()
    
    # Salvar no banco
    fitbit_user = FitbitUser.query.filter_by(user_id=state).first()
    
    if fitbit_user:
        # Atualizar tokens existentes
        fitbit_user.access_token = token_data['access_token']
        fitbit_user.refresh_token = token_data['refresh_token']
        fitbit_user.token_expires_at = datetime.utcnow() + timedelta(seconds=token_data['expires_in'])
        fitbit_user.updated_at = datetime.utcnow()
    else:
        # Criar novo usuário Fitbit
        fitbit_user = FitbitUser(
            user_id=state,
            fitbit_user_id=token_data['user_id'],
            access_token=token_data['access_token'],
            refresh_token=token_data['refresh_token'],
            token_expires_at=datetime.utcnow() + timedelta(seconds=token_data['expires_in'])
        )
        db.session.add(fitbit_user)
    
    db.session.commit()
    
    # Criar subscription após conectar
    create_subscription(fitbit_user)
    
    # Redirecionar para frontend
    return redirect('https://betfit-frontend-thwz.onrender.com/dashboard?fitbit_connected=true')

# 3. WEBHOOK VERIFICATION - Fitbit verifica endpoint
@fitbit_bp.route('/webhook', methods=['GET'])
def webhook_verify():
    """Verificação do endpoint pelo Fitbit"""
    verify = request.args.get('verify')
    
    if verify == FITBIT_WEBHOOK_VERIFY_CODE:
        return '', 204  # Resposta vazia com status 204
    
    return '', 404

# 4. WEBHOOK RECEIVER - Recebe notificações em tempo real
@fitbit_bp.route('/webhook', methods=['POST'])
def webhook_receive():
    """Recebe notificações de atividades do Fitbit"""
    
    # Verificar assinatura
    signature = request.headers.get('X-Fitbit-Signature')
    body = request.get_data()
    
    expected_signature = hmac.new(
        FITBIT_CLIENT_SECRET.encode('utf-8'),
        body,
        hashlib.sha1
    ).hexdigest()
    
    if signature != expected_signature:
        return jsonify({'error': 'Invalid signature'}), 401
    
    # Processar notificações
    notifications = request.json
    
    for notification in notifications:
        owner_id = notification['ownerId']
        collection_type = notification['collectionType']
        date = notification['date']
        
        # Buscar usuário Fitbit
        fitbit_user = FitbitUser.query.filter_by(fitbit_user_id=owner_id).first()
        
        if not fitbit_user:
            continue
        
        # Se for atividade, buscar dados completos
        if collection_type == 'activities':
            fetch_and_save_activities(fitbit_user, date)
    
    return '', 204

# Função auxiliar: Criar subscription
def create_subscription(fitbit_user):
    """Cria subscription para receber webhooks"""
    
    subscription_url = f'https://api.fitbit.com/1/user/-/activities/apiSubscriptions/{fitbit_user.fitbit_user_id}.json'
    
    headers = {
        'Authorization': f'Bearer {fitbit_user.access_token}'
    }
    
    response = requests.post(subscription_url, headers=headers)
    
    if response.status_code in [200, 201, 409]:  # 409 = já existe
        # Salvar subscription no banco
        existing = FitbitSubscription.query.filter_by(
            fitbit_user_id=fitbit_user.id,
            collection_type='activities'
        ).first()
        
        if not existing:
            subscription = FitbitSubscription(
                fitbit_user_id=fitbit_user.id,
                subscription_id=fitbit_user.fitbit_user_id,
                collection_type='activities'
            )
            db.session.add(subscription)
            db.session.commit()

# Função auxiliar: Buscar atividades
def fetch_and_save_activities(fitbit_user, date):
    """Busca atividades do dia e salva no banco"""
    
    url = f'https://api.fitbit.com/1/user/-/activities/date/{date}.json'
    
    headers = {
        'Authorization': f'Bearer {fitbit_user.access_token}'
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        return
    
    data = response.json()
    
    # Salvar atividades
    for activity in data.get('activities', []):
        existing = FitbitActivity.query.filter_by(
            activity_id=str(activity['logId'])
        ).first()
        
        if not existing:
            new_activity = FitbitActivity(
                fitbit_user_id=fitbit_user.id,
                activity_id=str(activity['logId']),
                activity_type=activity.get('activityName'),
                start_time=datetime.strptime(activity['startTime'], '%H:%M:%S'),
                duration=activity.get('duration'),
                distance=activity.get('distance', 0),
                calories=activity.get('calories', 0),
                steps=activity.get('steps', 0),
                raw_data=json.dumps(activity)
            )
            db.session.add(new_activity)
    
    db.session.commit()

# 5. LISTAR ATIVIDADES DO USUÁRIO
@fitbit_bp.route('/activities', methods=['GET'])
@jwt_required()
def get_activities():
    """Retorna atividades do usuário"""
    user_id = get_jwt_identity()
    
    fitbit_user = FitbitUser.query.filter_by(user_id=user_id).first()
    
    if not fitbit_user:
        return jsonify({'error': 'Fitbit não conectado'}), 404
    
    activities = FitbitActivity.query.filter_by(
        fitbit_user_id=fitbit_user.id
    ).order_by(FitbitActivity.received_at.desc()).limit(50).all()
    
    return jsonify({
        'activities': [{
            'id': a.id,
            'type': a.activity_type,
            'start_time': a.start_time.isoformat(),
            'duration': a.duration,
            'distance': a.distance,
            'calories': a.calories,
            'steps': a.steps,
            'received_at': a.received_at.isoformat()
        } for a in activities]
    })