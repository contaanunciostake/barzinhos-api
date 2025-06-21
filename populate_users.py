from src.models.user import User, db
from src.models.establishment import Establishment
from src.main import app
from werkzeug.security import generate_password_hash

with app.app_context():
    # Create admin user if not exists
    admin_email = "admin@barzinhos.com"
    admin_user = User.query.filter_by(email=admin_email).first()
    if not admin_user:
        hashed_password = generate_password_hash("admin123")
        new_admin = User(
            username="admin",  # <-- adicionado
            email=admin_email,
            password_hash=hashed_password,  # <-- corrigido
            role="admin"
        )
        db.session.add(new_admin)
        db.session.commit()
        print(f"Admin user {admin_email} created.")
    else:
        print(f"Admin user {admin_email} already exists.")

    # Create establishment user if not exists
    establishment_email = "bar@exemplo.com"
    establishment_user = User.query.filter_by(email=establishment_email).first()
    if not establishment_user:
        hashed_password = generate_password_hash("123456")
        new_establishment_user = User(
            username="bardexemplo",  # <-- adicionado
            email=establishment_email,
            password_hash=hashed_password,  # <-- corrigido
            role="establishment"
        )
        db.session.add(new_establishment_user)
        db.session.flush()  # Para obter o ID antes do commit

        new_establishment = Establishment(
            user_id=new_establishment_user.id,
            name="Bar do Exemplo",
            address="Rua Exemplo, 123",
            neighborhood="Centro",
            type="Bar",
            is_approved=True
        )
        db.session.add(new_establishment)
        db.session.commit()
        print(f"Establishment user {establishment_email} created and approved.")
    else:
        print(f"Establishment user {establishment_email} already exists.")
