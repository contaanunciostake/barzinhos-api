from src.models.user import User
from src import db, app
from werkzeug.security import generate_password_hash

with app.app_context():
    admin = User(
        email='admin@barzinhos.com',
        username='admin',
        password=generate_password_hash('123456'),
        role='admin'
    )
    db.session.add(admin)
    db.session.commit()
    print("✅ Usuário admin criado com sucesso.")
