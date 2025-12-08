"""
Script para verificar reservas activas
"""
from datetime import date
from app.database import SessionLocal
from app.models.reservacion import Reservacion, EstadoReservacion
from app.models.mesa import Mesa

def verificar_reservas():
    db = SessionLocal()
    try:
        # Ver todas las reservas de hoy
        reservas_hoy = db.query(Reservacion).filter(
            Reservacion.fecha == date.today()
        ).all()

        print(f"[INFO] Reservas para hoy ({date.today()}):")
        print(f"   Total: {len(reservas_hoy)}")
        print()

        if reservas_hoy:
            for reserva in reservas_hoy:
                print(f"   [Reserva {reserva.id_reserva}]")
                print(f"      Mesa: {reserva.id_mesa}")
                print(f"      Cliente: {reserva.nombre} {reserva.apellido}")
                print(f"      Estado: {reserva.estado}")
                print(f"      Hora: {reserva.hora}")

                # Verificar estado de la mesa
                mesa = db.query(Mesa).filter(Mesa.id_mesa == reserva.id_mesa).first()
                if mesa:
                    print(f"      Estado de mesa en BD: {mesa.estado}")
                print()

        # Ver reservas activas (pendiente o confirmada)
        reservas_activas = db.query(Reservacion).filter(
            Reservacion.fecha == date.today(),
            Reservacion.estado.in_([
                EstadoReservacion.PENDIENTE,
                EstadoReservacion.CONFIRMADA
            ])
        ).all()

        print(f"[INFO] Reservas ACTIVAS (pendiente/confirmada): {len(reservas_activas)}")
        for r in reservas_activas:
            print(f"   Mesa {r.id_mesa}: {r.estado}")

    except Exception as e:
        print(f"[ERROR] Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("VERIFICAR RESERVAS")
    print("=" * 60)
    verificar_reservas()
    print("=" * 60)
