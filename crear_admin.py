from app.database import SessionLocal, engine
from app.models import Base, Usuario
from app.main import get_password_hash
import sys

# Asegurarnos de que las tablas existan
Base.metadata.create_all(bind=engine)

def crear_super_admin():
    db = SessionLocal()
    try:
        print("🔍 Buscando usuario admin...")
        existing_user = db.query(Usuario).filter(Usuario.username == "admin").first()

        if existing_user:
            print("⚠️ El usuario 'admin' ya existía. Eliminándolo para recrearlo...")
            db.delete(existing_user)
            db.commit()

        print("✨ Creando nuevo usuario admin...")
        # AQUÍ PUEDES CAMBIAR LA CONTRASEÑA SI QUIERES
        password_segura = "admin123" 

        hashed_password = get_password_hash(password_segura)

        nuevo_usuario = Usuario(
            username="admin", 
            contraseña=hashed_password
        )

        db.add(nuevo_usuario)
        db.commit()
        print("------------------------------------------------")
        print(f"✅ ¡ÉXITO! Usuario creado correctamente.")
        print(f"👤 Usuario: admin")
        print(f"🔑 Contraseña: {password_segura}")
        print("------------------------------------------------")

    except Exception as e:
        print(f"❌ ERROR: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    crear_super_admin()
