from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity
)

from src.models.base import db
from src.models.user import User
from src.models.establishment import Establishment

auth_bp = Blueprint("auth", __name__)
jwt = JWTManager()

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    username = data.get("username")
    role = data.get("role", "user")  # padrão "user" se não informado

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email já cadastrado"}), 409

    hashed_password = generate_password_hash(password)
    user = User(username=username, email=email, password_hash=hashed_password, role=role)
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "Usuário registrado com sucesso!"}), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Credenciais inválidas"}), 401

    access_token = create_access_token(identity=user.email)
    return jsonify({
        "access_token": access_token,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role
        }
    }), 200

@auth_bp.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

@auth_bp.route('/register-establishment', methods=['POST'])
def register_establishment():
    try:
        data = request.get_json()

        required_fields = ['name', 'type', 'email', 'password', 'address', 'neighborhood']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({"success": False, "error": f"Campo obrigatório: {field}"}), 400

        if User.query.filter_by(email=data['email']).first():
            return jsonify({"success": False, "error": "Email já cadastrado."}), 409

        hashed_password = generate_password_hash(data['password'])
        user = User(email=data['email'], password=hashed_password, role='establishment')
        db.session.add(user)
        db.session.flush()

        establishment = Establishment(
            user_id=user.id,
            name=data['name'],
            type=data['type'],
            address=data.get('address', ''),
            neighborhood=data.get('neighborhood', ''),
            description=data.get('description', ''),
            phone=data.get('phone', ''),
            whatsapp=data.get('whatsapp', ''),
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            website=data.get('website', ''),
            instagram=data.get('instagram', ''),
            plan_type=data.get('plan_type', 'bronze'),
            is_open=data.get('is_open', True),
            image_url=data.get('image_url', ''),
            menu_url=data.get('menu_url', ''),
            is_approved=False
        )

        db.session.add(establishment)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Estabelecimento registrado com sucesso. Aguardando aprovação.",
            "data": establishment.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


