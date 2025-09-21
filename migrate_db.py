from app.main import create_app 
from app.models import db

app = create_app()
with app.app_context():
    db.create_all()
    print("✅ Base de datos creada/migrada correctamente")
