"""
Script para vaciar la tabla de reservaciones
"""
from app.database import SessionLocal
from app.models.reservacion import Reservacion

def vaciar_reservas():
    db = SessionLocal()
    try:
        # Contar reservaciones antes
        count_before = db.query(Reservacion).count()
        print(f"[INFO] Reservaciones antes: {count_before}")

        # Eliminar todas las reservaciones
        db.query(Reservacion).delete()
        db.commit()

        # Contar después
        count_after = db.query(Reservacion).count()
        print(f"[OK] Reservaciones despues: {count_after}")
        print(f"[OK] {count_before} reservacion(es) eliminada(s)")

    except Exception as e:
        print(f"[ERROR] Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("VACIAR TABLA DE RESERVACIONES")
    print("=" * 60)
    vaciar_reservas()
    print("=" * 60)
