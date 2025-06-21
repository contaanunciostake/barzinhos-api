from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from src.models.user import User, db
from src.models.establishment import Establishment  # ✅ Import necessário

auth_bp = Blueprint('auth', __name__)
jwt = JWTManager()

# Rota de registro de usuário
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email já cadastrado"}), 409

    hashed_password = generate_password_hash(password)
    user = User(email=email, password=hashed_password)
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "Usuário registrado com sucesso!"}), 201

# Rota de login
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({"error": "Credenciais inválidas"}), 401

    access_token = create_access_token(identity=user.email)
    return jsonify({"access_token": access_token}), 200

# Rota protegida para teste
@auth_bp.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

# ✅ Rota para cadastro rápido de estabelecimento
@auth_bp.route('/register-establishment', methods=['POST'])
@jwt_required()
def register_establishment():
    """Registra um novo estabelecimento com dados mínimos"""
    try:
        data = request.get_json()

        required_fields = ['name', 'type']
        for field in required_fields:
            if field not in data:
                return jsonify({"success": False, "error": f"Campo obrigatório: {field}"}), 400

        establishment = Establishment(
            name=data['name'],
            type=data['type'],
            is_approved=True  # Assume aprovado no registro rápido
        )

        db.session.add(establishment)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Estabelecimento registrado com sucesso",
            "data": establishment.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
