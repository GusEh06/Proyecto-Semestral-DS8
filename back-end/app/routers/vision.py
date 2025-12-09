from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from app.database import get_db
from app.models.mesa import Mesa
from app.models.tipo_mesa import TipoMesa
from app.models.reservacion import Reservacion
from datetime import date

# Importamos la función que avisa al frontend
from app.routers.mesas import broadcast_mesa_update 

router = APIRouter(prefix="/vision", tags=["Visión Artificial"])

class DeteccionMesa(BaseModel):
    id_mesa: int
    personas_detectadas: int

class ActualizacionEstadoMesas(BaseModel):
    detecciones: List[DeteccionMesa]

@router.get("/estado-general")
def obtener_estado_general(db: Session = Depends(get_db)):
    """
    Obtiene el estado actual de todas las mesas.
    Este endpoint es consumido por el frontend para mostrar el estado en tiempo real.
    """
    mesas = db.query(Mesa).all()
    mesas_data = []

    for m in mesas:
        mesas_data.append({
            "id_mesa": m.id_mesa,
            "estado": m.estado,
            "personas_actuales": m.personas_actuales,
            "id_tipo_mesa": m.id_tipo_mesa,
            "updated_at": m.updated_at.isoformat() if m.updated_at else None,
            "tipo_mesa": {
                "descripcion": m.tipo_mesa.descripcion,
                "cantidad_sillas": m.tipo_mesa.cantidad_sillas
            } if m.tipo_mesa else None
        })

    return mesas_data

@router.post("/actualizar-estado-mesas")
def actualizar_estado_mesas_vision(
    data: ActualizacionEstadoMesas,
    db: Session = Depends(get_db)
):
    # 1. Asegurar tipo de mesa por defecto
    tipo = db.query(TipoMesa).first()
    if not tipo:
        tipo = TipoMesa(descripcion="Estándar", cantidad_sillas=4)
        db.add(tipo)
        db.commit()
        db.refresh(tipo)

    cambios_hubo = False
    resultados = []

    # IDs de mesas detectadas por YOLO en este ciclo
    mesas_detectadas = [det.id_mesa for det in data.detecciones]

    for det in data.detecciones:
        mesa = db.query(Mesa).filter(Mesa.id_mesa == det.id_mesa).first()

        # --- A: AUTO-CREAR MESA (Si es nueva) ---
        if not mesa:
            mesa = Mesa(
                id_mesa=det.id_mesa,
                id_tipo_mesa=tipo.id_tipo_mesa,
                estado="disponible",
                personas_actuales=det.personas_detectadas
            )
            db.add(mesa)
            db.commit()
            db.refresh(mesa)
            print(f"🆕 Mesa #{det.id_mesa} creada dinámicamente")
            cambios_hubo = True

        # --- B: ACTUALIZAR ESTADO Y PERSONAS ---
        estado_anterior = mesa.estado
        personas_anterior = mesa.personas_actuales

        # Actualizar personas actuales SIEMPRE
        mesa.personas_actuales = det.personas_detectadas

        if det.personas_detectadas > 0:
            mesa.estado = "ocupada"
        else:
            # Respetar reservas
            reserva = db.query(Reservacion).filter(
                Reservacion.id_mesa == mesa.id_mesa,
                Reservacion.fecha == date.today(),
                Reservacion.estado.in_(["pendiente", "confirmada"])
            ).first()
            mesa.estado = "reservada" if reserva else "disponible"

        # Verificar si hubo cambios
        if mesa.estado != estado_anterior or mesa.personas_actuales != personas_anterior:
            db.commit()
            cambios_hubo = True

        # SIEMPRE agregar a resultados (no solo si cambió estado)
        resultados.append({
            "id_mesa": det.id_mesa,
            "estado_anterior": estado_anterior,
            "estado_nuevo": mesa.estado,
            "personas_detectadas": det.personas_detectadas
        })

    # --- C: LIMPIEZA DE MESAS FANTASMA ---
    # Eliminar mesas que ya no detecta YOLO (solo las que fueron creadas dinámicamente)
    mesas_en_bd = db.query(Mesa).all()
    for mesa in mesas_en_bd:
        if mesa.id_mesa not in mesas_detectadas:
            # Verificar que no tenga reservaciones activas antes de eliminar
            reserva_activa = db.query(Reservacion).filter(
                Reservacion.id_mesa == mesa.id_mesa,
                Reservacion.estado.in_(["pendiente", "confirmada"])
            ).first()

            if not reserva_activa:
                print(f"🗑️  Mesa #{mesa.id_mesa} eliminada (ya no detectada por YOLO)")
                db.delete(mesa)
                cambios_hubo = True

    db.commit()

    # --- D: ¡AVISAR AL FRONTEND! (SSE) ---
    if cambios_hubo:
        # Preparamos los datos con personas_actuales
        todas_las_mesas = db.query(Mesa).all()
        mesas_data = []
        for m in todas_las_mesas:
            mesas_data.append({
                "id_mesa": m.id_mesa,
                "estado": m.estado,
                "personas_actuales": m.personas_actuales,  # ← NUEVO
                "id_tipo_mesa": m.id_tipo_mesa,
                "tipo_mesa": {
                    "descripcion": m.tipo_mesa.descripcion,
                    "cantidad_sillas": m.tipo_mesa.cantidad_sillas
                } if m.tipo_mesa else None
            })

        # Enviamos la señal a React
        broadcast_mesa_update(mesas_data)
        print("📡 Actualización enviada al Dashboard en tiempo real")

    return {"success": True, "resultados": resultados}  # ← CAMBIADO "ok" por "success"