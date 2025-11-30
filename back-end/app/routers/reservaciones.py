from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import date, time
from app.database import get_db
from app.models.reservacion import Reservacion
from app.schemas.reservacion import (
    ReservacionCreate,
    ReservacionResponse,
    ReservacionWithDetailsResponse
)
from app.schemas.mesa import MesaWithTipoResponse
from app.services.reservacion_service import get_available_tables, asignar_mesa_automatica

router = APIRouter(prefix="/reservaciones", tags=["Reservaciones Públicas"])


@router.post("/", response_model=ReservacionResponse, status_code=status.HTTP_201_CREATED)
def crear_reservacion(
    reservacion_data: ReservacionCreate,
    db: Session = Depends(get_db)
):
    """
    Crea una nueva reservación.
    Verifica disponibilidad y asigna automáticamente una mesa si hay disponible.
    """
    # Verificar si hay mesas disponibles
    mesas_disponibles = get_available_tables(
        db,
        reservacion_data.fecha,
        reservacion_data.hora,
        reservacion_data.cantidad_personas
    )

    if not mesas_disponibles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No hay mesas disponibles para la fecha, hora y cantidad de personas solicitadas"
        )

    # Crear la reservación
    nueva_reservacion = Reservacion(**reservacion_data.model_dump())
    db.add(nueva_reservacion)
    db.commit()
    db.refresh(nueva_reservacion)

    # Asignar mesa automáticamente
    asignar_mesa_automatica(db, nueva_reservacion)
    db.refresh(nueva_reservacion)

    return nueva_reservacion


@router.get("/disponibilidad", response_model=List[MesaWithTipoResponse])
def consultar_disponibilidad(
    fecha: date = Query(..., description="Fecha de la reservación"),
    hora: time = Query(..., description="Hora de la reservación"),
    cantidad_personas: int = Query(..., gt=0, description="Cantidad de personas"),
    db: Session = Depends(get_db)
):
    """
    Consulta las mesas disponibles para una fecha, hora y cantidad de personas específicas.
    """
    mesas = get_available_tables(db, fecha, hora, cantidad_personas)
    return mesas


@router.get("/{reservacion_id}", response_model=ReservacionWithDetailsResponse)
def obtener_reservacion(
    reservacion_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene los detalles de una reservación específica por su ID.
    """
    reservacion = db.query(Reservacion).filter(Reservacion.id_reserva == reservacion_id).first()

    if not reservacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reservación no encontrada"
        )

    return reservacion


@router.delete("/{reservacion_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancelar_reservacion(
    reservacion_id: int,
    db: Session = Depends(get_db)
):
    """
    Cancela una reservación cambiando su estado a 'cancelada'.
    """
    reservacion = db.query(Reservacion).filter(Reservacion.id_reserva == reservacion_id).first()

    if not reservacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reservación no encontrada"
        )

    if reservacion.estado == "completada":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede cancelar una reservación completada"
        )

    reservacion.estado = "cancelada"

    # Liberar la mesa si tenía una asignada
    if reservacion.id_mesa:
        from app.models.mesa import Mesa
        mesa = db.query(Mesa).filter(Mesa.id_mesa == reservacion.id_mesa).first()
        if mesa:
            mesa.estado = "disponible"

    db.commit()
    return None
