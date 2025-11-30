"""
Script para crear un usuario administrador inicial.
Ejecutar con: python create_admin.py
"""
from app.database import SessionLocal
from app.models.usuario_admin import UsuarioAdmin
from app.utils.security import get_password_hash

def create_admin():
    db = SessionLocal()

    try:
        # Verificar si ya existe un admin
        existing_admin = db.query(UsuarioAdmin).filter(
            UsuarioAdmin.email == "admin@example.com"
        ).first()

        if existing_admin:
            print("El usuario admin@example.com ya existe.")
            return

        # Crear nuevo admin
        admin = UsuarioAdmin(
            nombre="Administrador",
            email="admin@example.com",
            password_hash=get_password_hash("admin123"),
            rol="superadmin",
            is_active=True
        )

        db.add(admin)
        db.commit()

        print("✓ Usuario administrador creado exitosamente")
        print("  Email: admin@example.com")
        print("  Password: admin123")
        print("  Rol: superadmin")
        print("\n¡IMPORTANTE! Cambia la contraseña después del primer login.")

    except Exception as e:
        print(f"Error al crear usuario administrador: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_admin()
