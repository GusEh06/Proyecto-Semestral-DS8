from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from app.database import get_db
from app.models.mesa import Mesa
from app.models.usuario_admin import UsuarioAdmin
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/vision", tags=["Visión Artificial"])


class DeteccionMesa(BaseModel):
    id_mesa: int
    personas_detectadas: int


class ActualizacionEstadoMesas(BaseModel):
    detecciones: List[DeteccionMesa]


@router.post("/actualizar-estado-mesas")
def actualizar_estado_mesas_vision(
    data: ActualizacionEstadoMesas,
    db: Session = Depends(get_db),
    current_user: UsuarioAdmin = Depends(get_current_user)
):
    """
    Actualiza el estado de las mesas basándose en las detecciones del modelo de visión artificial.

    Lógica:
    - Si se detectan personas en una mesa (personas_detectadas > 0), se marca como 'ocupada'
    - Si no se detectan personas y no tiene reserva activa, se marca como 'disponible'
    - Si tiene reserva activa pero no hay personas, mantiene el estado 'reservada'

    Requiere autenticación de administrador.
    """
    from app.models.reservacion import Reservacion
    from datetime import date, datetime

    resultados = []

    for deteccion in data.detecciones:
        mesa = db.query(Mesa).filter(Mesa.id_mesa == deteccion.id_mesa).first()

        if not mesa:
            resultados.append({
                "id_mesa": deteccion.id_mesa,
                "success": False,
                "message": "Mesa no encontrada"
            })
            continue

        estado_anterior = mesa.estado

        if deteccion.personas_detectadas > 0:
            # Hay personas en la mesa, marcarla como ocupada
            mesa.estado = "ocupada"

        else:
            # No hay personas detectadas
            # Verificar si tiene reserva activa para hoy
            hoy = date.today()
            reserva_activa = db.query(Reservacion).filter(
                Reservacion.id_mesa == mesa.id_mesa,
                Reservacion.fecha == hoy,
                Reservacion.estado.in_(["pendiente", "confirmada"])
            ).first()

            if reserva_activa:
                # Tiene reserva activa, mantener como reservada
                mesa.estado = "reservada"
            else:
                # No tiene reserva activa, marcar como disponible
                mesa.estado = "disponible"

        db.commit()

        resultados.append({
            "id_mesa": deteccion.id_mesa,
            "success": True,
            "estado_anterior": estado_anterior,
            "estado_nuevo": mesa.estado,
            "personas_detectadas": deteccion.personas_detectadas
        })

    return {
        "message": "Estados actualizados",
        "resultados": resultados
    }


@router.get("/estado-general")
def obtener_estado_general_mesas(db: Session = Depends(get_db)):
    """
    Obtiene el estado general de todas las mesas para mostrar en el sistema de visión.
    Endpoint público.
    """
    from app.models.tipo_mesa import TipoMesa

    mesas = db.query(Mesa).all()

    resultado = []
    for mesa in mesas:
        resultado.append({
            "id_mesa": mesa.id_mesa,
            "id_tipo_mesa": mesa.id_tipo_mesa,
            "estado": mesa.estado,
            "capacidad": mesa.tipo_mesa.cantidad_sillas if mesa.tipo_mesa else None,
            "descripcion": mesa.tipo_mesa.descripcion if mesa.tipo_mesa else None
        })

    return resultado
