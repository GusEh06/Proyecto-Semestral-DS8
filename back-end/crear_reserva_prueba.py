"""
Script para crear reservas de prueba
"""
from datetime import date, time
from app.database import SessionLocal
from app.models.reservacion import Reservacion, EstadoReservacion
from app.models.mesa import Mesa

def crear_reserva_prueba(id_mesa: int):
    db = SessionLocal()
    try:
        # Verificar que la mesa existe
        mesa = db.query(Mesa).filter(Mesa.id_mesa == id_mesa).first()
        if not mesa:
            print(f"[ERROR] Mesa {id_mesa} no existe")
            return

        # Crear reserva para hoy
        nueva_reserva = Reservacion(
            nombre="Cliente",
            apellido="Prueba",
            correo="prueba@test.com",
            telefono="555-0123",
            fecha=date.today(),
            hora=time(19, 0),  # 7:00 PM
            cantidad_personas=4,
            id_mesa=id_mesa,
            estado=EstadoReservacion.CONFIRMADA
        )

        db.add(nueva_reserva)

        # Cambiar estado de mesa a reservada
        mesa.estado = "reservada"

        db.commit()

        print(f"[OK] Reserva creada para Mesa {id_mesa}")
        print(f"   Cliente: {nueva_reserva.nombre} {nueva_reserva.apellido}")
        print(f"   Fecha: {nueva_reserva.fecha}")
        print(f"   Hora: {nueva_reserva.hora}")
        print(f"   Estado: {nueva_reserva.estado}")
        print(f"   Estado de mesa: {mesa.estado}")

    except Exception as e:
        print(f"[ERROR] Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("CREAR RESERVAS DE PRUEBA")
    print("=" * 60)

    # Crear reservas para las mesas 1, 3 y 5
    for mesa_id in [1, 3, 5]:
        crear_reserva_prueba(mesa_id)
        print()

    print("=" * 60)
    print("[INFO] Ahora estas mesas NO deberian ser modificadas por MQTT")
    print("=" * 60)
