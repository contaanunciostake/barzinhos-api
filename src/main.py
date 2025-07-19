import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, request, make_response
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from src.models.base import db
from src.routes.user import user_bp

app = Flask(__name__)

# Configurações
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', '1657victOr@')
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', '1657victOr@')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False  # Token não expira para desenvolvimento

# Configuração do banco de dados
database_url = os.environ.get('DATABASE_URL')
if database_url:
    # Produção - PostgreSQL
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # Desenvolvimento - SQLite
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), '..', 'static', 'images', 'establishments')

# Configuração de CORS
cors_origins = os.environ.get('CORS_ORIGINS', 'http://localhost:5173,http://localhost:5174,http://localhost:5175,https://barzinhos-front-tgjm.vercel.app')
cors_origins_list = [origin.strip() for origin in cors_origins.split(',')]

# Inicializar extensões
cors = CORS(app, 
     origins=cors_origins_list, 
     supports_credentials=True,
     allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
     expose_headers=['Content-Type', 'Authorization'])

# Handler manual para OPTIONS
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = make_response()
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "Content-Type,Authorization,X-Requested-With")
        response.headers.add('Access-Control-Allow-Methods', "GET,PUT,POST,DELETE,OPTIONS")
        response.headers.add('Access-Control-Allow-Credentials', "true")
        return response
jwt = JWTManager(app)
db.init_app(app)

# Importar todos os modelos para garantir que as tabelas sejam criadas
from src.models.user import User
from src.models.establishment import Establishment, EstablishmentImage
from src.models.review import Review
from src.models.subscription import Subscription
from src.models.payment_config import PaymentConfig
from src.models.payment import Payment

# Registrar blueprints
from src.routes.auth import auth_bp
from src.routes.establishment import establishment_bp
from src.routes.review import review_bp, geo_bp
from src.routes.plan import plan_bp
from src.routes.payment import payment_bp
from src.routes.admin import admin_bp
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(establishment_bp, url_prefix='/api/establishments')
app.register_blueprint(plan_bp, url_prefix='/api/plans')
app.register_blueprint(payment_bp, url_prefix='/api/payments')
app.register_blueprint(admin_bp, url_prefix='/api/admin')
app.register_blueprint(review_bp, url_prefix='/api/reviews')
app.register_blueprint(geo_bp, url_prefix='/api/geo')

# Rota para servir imagens estáticas
@app.route('/static/<path:filename>')
def serve_static(filename):
    static_dir = os.path.join(os.path.dirname(__file__), '..', 'static')
    return send_from_directory(static_dir, filename)

# Criar tabelas
with app.app_context():
    # Criar diretório de uploads se não existir
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    # Criar diretório de imagens de perfil se não existir
    profiles_dir = os.path.join(os.path.dirname(__file__), '..', 'static', 'images', 'profiles')
    os.makedirs(profiles_dir, exist_ok=True)
    # Criar diretório do banco de dados se não existir
    db_dir = os.path.join(os.path.dirname(__file__), 'database')
    os.makedirs(db_dir, exist_ok=True)
    db.create_all()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
