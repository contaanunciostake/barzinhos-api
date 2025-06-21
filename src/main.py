import os
import sys
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS

# Inserir caminho base do projeto
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Imports internos
from src.models.user import db
from src.routes.user import user_bp
from src.routes.establishment import establishment_bp
from src.routes.automation import automation_bp
from src.routes.auth import auth_bp, jwt

# Instância do app Flask
app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

# Configurações do app
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "asdf#FGSgvasgf$5$WGT")
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "super-secret-jwt-key")

# Suporte a PostgreSQL no Render, senão fallback para SQLite local
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL",
    f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
).replace("postgres://", "postgresql://")

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# JWT e Banco
jwt.init_app(app)
db.init_app(app)

# CORS: permitir apenas o domínio do front
CORS(app, resources={r"/api/*": {"origins": ["https://barzinhos-front.onrender.com"]}})

# Blueprints
app.register_blueprint(user_bp, url_prefix="/api")
app.register_blueprint(establishment_bp, url_prefix="/api")
app.register_blueprint(automation_bp, url_prefix="/api/automation")
app.register_blueprint(auth_bp, url_prefix="/api/auth")

# Inicializar banco na primeira vez
with app.app_context():
    db.create_all()

# Rotas básicas
@app.route("/")
def index():
    return "API Barzinhos está online!", 200

@app.route("/health")
def health_check():
    return jsonify({"status": "ok", "message": "API Barzinhos está saudável!"}), 200

# Rodar localmente
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
