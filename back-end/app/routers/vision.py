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

    for det in data.detecciones:
        mesa = db.query(Mesa).filter(Mesa.id_mesa == det.id_mesa).first()

        # --- A: AUTO-CREAR MESA (Si es nueva) ---
        if not mesa:
            mesa = Mesa(
                id_mesa=det.id_mesa, 
                id_tipo_mesa=tipo.id_tipo_mesa, 
                estado="disponible"
            )
            db.add(mesa)
            db.commit()
            db.refresh(mesa)
            print(f"🆕 Mesa #{det.id_mesa} creada dinámicamente")
            cambios_hubo = True

        # --- B: ACTUALIZAR ESTADO ---
        estado_anterior = mesa.estado
        
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

        if mesa.estado != estado_anterior:
            db.commit()
            cambios_hubo = True

        resultados.append({"id": det.id_mesa, "estado": mesa.estado})

    # --- C: ¡AVISAR AL FRONTEND! (SSE) ---
    if cambios_hubo:
        # Preparamos los datos tal cual los espera MesasGrid.tsx
        todas_las_mesas = db.query(Mesa).all()
        mesas_data = []
        for m in todas_las_mesas:
            mesas_data.append({
                "id_mesa": m.id_mesa,
                "estado": m.estado,
                "id_tipo_mesa": m.id_tipo_mesa,
                "tipo_mesa": { # El frontend necesita estos detalles anidados
                    "descripcion": m.tipo_mesa.descripcion,
                    "cantidad_sillas": m.tipo_mesa.cantidad_sillas
                } if m.tipo_mesa else None
            })
        
        # Enviamos la señal a React
        broadcast_mesa_update(mesas_data)
        print("📡 Actualización enviada al Dashboard en tiempo real")

    return {"ok": True, "resultados": resultados}