from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import date, time, timedelta
from fastapi import HTTPException, status
from app.models.reservacion import Reservacion
from app.models.mesa import Mesa
from app.models.tipo_mesa import TipoMesa


def get_available_tables(
    db: Session,
    fecha: date,
    hora: time,
    cantidad_personas: int
):
    """
    Obtiene las mesas disponibles para una fecha, hora y cantidad de personas específica.
    Una mesa está disponible si tiene capacidad suficiente y no tiene reservas confirmadas
    en un rango de 2 horas alrededor de la hora solicitada.
    """
    # Calcular rango de tiempo (2 horas antes y después)
    hora_inicio = (timedelta(hours=hora.hour, minutes=hora.minute) - timedelta(hours=1)).total_seconds()
    hora_fin = (timedelta(hours=hora.hour, minutes=hora.minute) + timedelta(hours=1)).total_seconds()

    # Convertir a time objects
    hora_inicio_time = time(hour=int(hora_inicio // 3600), minute=int((hora_inicio % 3600) // 60))
    hora_fin_time = time(hour=int(hora_fin // 3600), minute=int((hora_fin % 3600) // 60))

    # Buscar tipos de mesa con capacidad suficiente
    tipos_mesa_validos = db.query(TipoMesa).filter(
        TipoMesa.cantidad_sillas >= cantidad_personas
    ).all()

    if not tipos_mesa_validos:
        return []

    tipo_ids = [t.id_tipo_mesa for t in tipos_mesa_validos]

    # Buscar mesas del tipo adecuado
    mesas_candidatas = db.query(Mesa).filter(
        Mesa.id_tipo_mesa.in_(tipo_ids),
        Mesa.estado.in_(["disponible", "reservada"])
    ).all()

    # Filtrar mesas que no tienen reservas en conflicto
    mesas_disponibles = []
    for mesa in mesas_candidatas:
        conflicto = db.query(Reservacion).filter(
            and_(
                Reservacion.id_mesa == mesa.id_mesa,
                Reservacion.fecha == fecha,
                Reservacion.estado.in_(["pendiente", "confirmada"]),
                or_(
                    and_(Reservacion.hora >= hora_inicio_time, Reservacion.hora <= hora_fin_time),
                    and_(Reservacion.hora <= hora, hora <= hora_fin_time)
                )
            )
        ).first()

        if not conflicto:
            mesas_disponibles.append(mesa)

    return mesas_disponibles


def asignar_mesa_automatica(
    db: Session,
    reservacion: Reservacion
):
    """
    Asigna automáticamente una mesa disponible a una reservación.
    """
    mesas_disponibles = get_available_tables(
        db,
        reservacion.fecha,
        reservacion.hora,
        reservacion.cantidad_personas
    )

    if mesas_disponibles:
        # Asignar la primera mesa disponible
        mesa = mesas_disponibles[0]
        reservacion.id_mesa = mesa.id_mesa
        mesa.estado = "reservada"
        db.commit()
        return mesa

    return None
