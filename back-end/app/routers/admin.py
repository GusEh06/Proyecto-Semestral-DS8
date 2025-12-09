from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List
from datetime import date, datetime
from app.database import get_db
from app.models.reservacion import Reservacion
from app.models.mesa import Mesa
from app.models.usuario_admin import UsuarioAdmin
from app.schemas.reservacion import ReservacionWithDetailsResponse, ReservacionUpdate
from app.schemas.usuario import UsuarioAdminCreate, UsuarioAdminResponse, UsuarioAdminUpdate
from app.utils.dependencies import get_current_user, get_current_active_superadmin
from app.utils.security import get_password_hash

router = APIRouter(prefix="/admin", tags=["Administración"])


# ===== GESTIÓN DE RESERVACIONES (Admin) =====

@router.get("/reservaciones", response_model=List[ReservacionWithDetailsResponse])
def listar_reservaciones(
    estado: str | None = Query(None, description="Filtrar por estado"),
    fecha: date | None = Query(None, description="Filtrar por fecha"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=100),
    db: Session = Depends(get_db),
    current_user: UsuarioAdmin = Depends(get_current_user)
):
    """
    Lista todas las reservaciones con filtros opcionales.
    Requiere autenticación.
    """
    query = db.query(Reservacion)

    if estado:
        query = query.filter(Reservacion.estado == estado)
    if fecha:
        query = query.filter(Reservacion.fecha == fecha)

    reservaciones = query.order_by(Reservacion.fecha.desc(), Reservacion.hora.desc()).offset(skip).limit(limit).all()
    return reservaciones


@router.get("/reservaciones/{reservacion_id}", response_model=ReservacionWithDetailsResponse)
def obtener_reservacion_admin(
    reservacion_id: int,
    db: Session = Depends(get_db),
    current_user: UsuarioAdmin = Depends(get_current_user)
):
    """
    Obtiene detalles completos de una reservación.
    Requiere autenticación.
    """
    reservacion = db.query(Reservacion).filter(Reservacion.id_reserva == reservacion_id).first()

    if not reservacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reservación no encontrada"
        )

    return reservacion


@router.put("/reservaciones/{reservacion_id}", response_model=ReservacionWithDetailsResponse)
def actualizar_reservacion(
    reservacion_id: int,
    reservacion_data: ReservacionUpdate,
    db: Session = Depends(get_db),
    current_user: UsuarioAdmin = Depends(get_current_user)
):
    """
    Actualiza una reservación existente.
    Requiere autenticación.
    """
    reservacion = db.query(Reservacion).filter(Reservacion.id_reserva == reservacion_id).first()

    if not reservacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reservación no encontrada"
        )

    # Actualizar campos si se proporcionan
    update_data = reservacion_data.model_dump(exclude_unset=True)

    # Si se está asignando una mesa, verificar que exista y esté disponible
    if "id_mesa" in update_data and update_data["id_mesa"]:
        mesa = db.query(Mesa).filter(Mesa.id_mesa == update_data["id_mesa"]).first()
        if not mesa:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mesa no encontrada"
            )

        # Liberar mesa anterior si existía
        if reservacion.id_mesa and reservacion.id_mesa != update_data["id_mesa"]:
            mesa_anterior = db.query(Mesa).filter(Mesa.id_mesa == reservacion.id_mesa).first()
            if mesa_anterior:
                mesa_anterior.estado = "disponible"

        # Asignar nueva mesa
        mesa.estado = "reservada"

    for key, value in update_data.items():
        setattr(reservacion, key, value)

    db.commit()
    db.refresh(reservacion)

    return reservacion


@router.delete("/reservaciones/{reservacion_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_reservacion(
    reservacion_id: int,
    db: Session = Depends(get_db),
    current_user: UsuarioAdmin = Depends(get_current_user)
):
    """
    Elimina una reservación permanentemente.
    Requiere autenticación.
    """
    reservacion = db.query(Reservacion).filter(Reservacion.id_reserva == reservacion_id).first()

    if not reservacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reservación no encontrada"
        )

    # Liberar la mesa si tenía una asignada
    if reservacion.id_mesa:
        mesa = db.query(Mesa).filter(Mesa.id_mesa == reservacion.id_mesa).first()
        if mesa:
            mesa.estado = "disponible"

    db.delete(reservacion)
    db.commit()
    return None


# ===== GESTIÓN DE USUARIOS ADMIN =====

@router.post("/usuarios", response_model=UsuarioAdminResponse, status_code=status.HTTP_201_CREATED)
def crear_usuario_admin(
    usuario_data: UsuarioAdminCreate,
    db: Session = Depends(get_db),
    current_user: UsuarioAdmin = Depends(get_current_active_superadmin)
):
    """
    Crea un nuevo usuario administrador.
    Solo accesible para superadmins.
    """
    # Verificar si el email ya existe
    existing_user = db.query(UsuarioAdmin).filter(UsuarioAdmin.email == usuario_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado"
        )

    # Crear usuario con password hasheado
    user_dict = usuario_data.model_dump(exclude={"password"})
    user_dict["password_hash"] = get_password_hash(usuario_data.password)

    nuevo_usuario = UsuarioAdmin(**user_dict)
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    return nuevo_usuario


@router.get("/usuarios", response_model=List[UsuarioAdminResponse])
def listar_usuarios_admin(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=100),
    db: Session = Depends(get_db),
    current_user: UsuarioAdmin = Depends(get_current_active_superadmin)
):
    """
    Lista todos los usuarios administradores.
    Solo accesible para superadmins.
    """
    usuarios = db.query(UsuarioAdmin).offset(skip).limit(limit).all()
    return usuarios


@router.put("/usuarios/{usuario_id}", response_model=UsuarioAdminResponse)
def actualizar_usuario_admin(
    usuario_id: int,
    usuario_data: UsuarioAdminUpdate,
    db: Session = Depends(get_db),
    current_user: UsuarioAdmin = Depends(get_current_active_superadmin)
):
    """
    Actualiza un usuario administrador.
    Solo accesible para superadmins.
    """
    usuario = db.query(UsuarioAdmin).filter(UsuarioAdmin.id_usuario == usuario_id).first()

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

    update_data = usuario_data.model_dump(exclude_unset=True, exclude={"password"})

    # Si se proporciona password, hashearlo
    if usuario_data.password:
        update_data["password_hash"] = get_password_hash(usuario_data.password)

    for key, value in update_data.items():
        setattr(usuario, key, value)

    db.commit()
    db.refresh(usuario)

    return usuario


# ===== DASHBOARD Y ESTADÍSTICAS =====

@router.get("/dashboard/estadisticas")
def obtener_estadisticas(
    db: Session = Depends(get_db),
    current_user: UsuarioAdmin = Depends(get_current_user)
):
    """
    Obtiene estadísticas generales del sistema para el dashboard.
    """
    hoy = date.today()

    # Total de reservaciones
    total_reservaciones = db.query(func.count(Reservacion.id_reserva)).scalar()

    # Reservaciones de hoy
    reservaciones_hoy = db.query(func.count(Reservacion.id_reserva)).filter(
        Reservacion.fecha == hoy
    ).scalar()

    # Reservaciones pendientes
    reservaciones_pendientes = db.query(func.count(Reservacion.id_reserva)).filter(
        Reservacion.estado == "pendiente"
    ).scalar()

    # Reservaciones confirmadas para hoy
    reservaciones_confirmadas_hoy = db.query(func.count(Reservacion.id_reserva)).filter(
        and_(Reservacion.fecha == hoy, Reservacion.estado == "confirmada")
    ).scalar()

    # Total de mesas
    total_mesas = db.query(func.count(Mesa.id_mesa)).scalar()

    # Mesas disponibles
    mesas_disponibles = db.query(func.count(Mesa.id_mesa)).filter(
        Mesa.estado == "disponible"
    ).scalar()

    # Mesas ocupadas
    mesas_ocupadas = db.query(func.count(Mesa.id_mesa)).filter(
        Mesa.estado == "ocupada"
    ).scalar()

    # Mesas reservadas
    mesas_reservadas = db.query(func.count(Mesa.id_mesa)).filter(
        Mesa.estado == "reservada"
    ).scalar()

    # Reservaciones por estado
    reservaciones_por_estado = db.query(
        Reservacion.estado,
        func.count(Reservacion.id_reserva)
    ).group_by(Reservacion.estado).all()

    return {
        "total_reservaciones": total_reservaciones,
        "reservaciones_hoy": reservaciones_hoy,
        "reservaciones_pendientes": reservaciones_pendientes,
        "reservaciones_confirmadas_hoy": reservaciones_confirmadas_hoy,
        "reservaciones_por_estado": {estado: count for estado, count in reservaciones_por_estado},
        "total_mesas": total_mesas,
        "mesas_disponibles": mesas_disponibles,
        "mesas_ocupadas": mesas_ocupadas,
        "mesas_reservadas": mesas_reservadas
    }
