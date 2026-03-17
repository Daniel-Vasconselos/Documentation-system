from app import create_app, db
from app.models import Usuario
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():

    senha = generate_password_hash("admin_Luma")

    admin = Usuario(
        empresa_id=None,
        email="admin@email.com",
        senha_hash=senha,
        tipo_usuario="admin"
    )

    db.session.add(admin)
    db.session.commit()

    print("Admin criado com sucesso!")
