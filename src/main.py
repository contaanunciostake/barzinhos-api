import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.user import db
from src.routes.user import user_bp
from src.routes.establishment import establishment_bp
from src.routes.automation import automation_bp
from src.routes.auth import auth_bp, jwt

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "super-secret-jwt-key") # Use variável de ambiente ou fallback
jwt.init_app(app)

# Habilitar CORS para todas as rotas
CORS(app, resources={r"/*": {"origins": "*"}}) # Permitir todas as origens para desenvolvimento

app.register_blueprint(user_bp, url_prefix="/api")
app.register_blueprint(establishment_bp, url_prefix="/api")
app.register_blueprint(automation_bp, url_prefix="/api/automation")
app.register_blueprint(auth_bp, url_prefix="/api/auth")

# uncomment if you need to use database
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(os.path.dirname(__file__), "database", "app.db")}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)
with app.app_context():
    db.create_all()

@app.route("/")
def index():
    return "API Barzinhos está online!", 200

@app.route("/health")
def health_check():
    return jsonify({"status": "ok", "message": "API Barzinhos está saudável!"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)