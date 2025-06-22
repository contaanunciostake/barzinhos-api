from src.models.user import User
from src.models.establishment import Establishment
from src.main import app
from werkzeug.security import generate_password_hash
from src.models.base import db # Import db from base.py

with app.app_context():
    # Drop all tables and recreate them to ensure fresh start
    db.drop_all()
    db.create_all()

    # Create admin user if not exists
    admin_email = "admin@barzinhos.com"
    admin_user = User.query.filter_by(email=admin_email).first()
    if not admin_user:
        hashed_password = generate_password_hash("admin123")
        new_admin = User(
            email=admin_email,
            password=hashed_password,
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
            email=establishment_email,
            password=hashed_password,
            role="establishment"
        )
        db.session.add(new_establishment_user)
        db.session.flush()

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

    # Create 10 example establishments
    example_establishments_data = [
        {
            "name": "Boteco do Zé",
            "address": "Rua da Cerveja, 10",
            "neighborhood": "Vila Madalena",
            "type": "Boteco",
            "is_approved": True
        },
        {
            "name": "Choperia Central",
            "address": "Av. Principal, 500",
            "neighborhood": "Centro",
            "type": "Choperia",
            "is_approved": True
        },
        {
            "name": "Petiscaria da Esquina",
            "address": "Praça da Alegria, 7",
            "neighborhood": "Jardins",
            "type": "Petiscaria",
            "is_approved": True
        },
        {
            "name": "Bar e Restaurante Sabor",
            "address": "Rua do Sabor, 22",
            "neighborhood": "Pinheiros",
            "type": "Bar e Restaurante",
            "is_approved": True
        },
        {
            "name": "Pub Irlandês",
            "address": "Rua da Irlanda, 17",
            "neighborhood": "Moema",
            "type": "Pub",
            "is_approved": True
        },
        {
            "name": "Cervejaria Artesanal",
            "address": "Av. das Indústrias, 100",
            "neighborhood": "Barra Funda",
            "type": "Cervejaria",
            "is_approved": True
        },
        {
            "name": "Bar da Praia",
            "address": "Rua da Areia, 30",
            "neighborhood": "Copacabana",
            "type": "Bar",
            "is_approved": True
        },
        {
            "name": "Restaurante Temático",
            "address": "Alameda dos Sonhos, 5",
            "neighborhood": "Vila Olímpia",
            "type": "Restaurante",
            "is_approved": True
        },
        {
            "name": "Café e Bar",
            "address": "Rua do Café, 88",
            "neighborhood": "Consolação",
            "type": "Café e Bar",
            "is_approved": True
        },
        {
            "name": "Bar Noturno",
            "address": "Av. da Noite, 1",
            "neighborhood": "Lapa",
            "type": "Bar",
            "is_approved": True
        }
    ]

    for data in example_establishments_data:
        # Check if establishment already exists to avoid duplicates
        existing_establishment = Establishment.query.filter_by(name=data["name"]).first()
        if not existing_establishment:
            # Create a dummy user for each example establishment
            dummy_user_email = f"dummy_{data['name'].replace(' ', '_').lower()}@example.com"
            dummy_user = User.query.filter_by(email=dummy_user_email).first()
            if not dummy_user:
                hashed_password = generate_password_hash("password123")
                dummy_user = User(
                    email=dummy_user_email,
                    password=hashed_password,
                    role="establishment"
                )
                db.session.add(dummy_user)
                db.session.flush()

            new_establishment = Establishment(
                user_id=dummy_user.id,
                name=data["name"],
                address=data["address"],
                neighborhood=data["neighborhood"],
                type=data["type"],
                is_approved=data["is_approved"]
            )
            db.session.add(new_establishment)
            db.session.commit()
            print(f"Establishment {data['name']} created.")
        else:
            print(f"Establishment {data['name']} already exists.")

    print("Database populated with example users and establishments.")


