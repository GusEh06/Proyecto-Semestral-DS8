from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.mesa import Mesa
from app.models.usuario_admin import UsuarioAdmin
from app.schemas.mesa import MesaCreate, MesaUpdate, MesaWithTipoResponse
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/mesas", tags=["Gestión de Mesas"])


@router.get("/", response_model=List[MesaWithTipoResponse])
def listar_mesas(
    estado: str | None = Query(None, description="Filtrar por estado"),
    id_tipo_mesa: int | None = Query(None, description="Filtrar por tipo de mesa"),
    db: Session = Depends(get_db)
):
    """
    Lista todas las mesas con sus tipos.
    Endpoint público para consulta.
    """
    query = db.query(Mesa)

    if estado:
        query = query.filter(Mesa.estado == estado)
    if id_tipo_mesa:
        query = query.filter(Mesa.id_tipo_mesa == id_tipo_mesa)

    mesas = query.all()
    return mesas


@router.get("/{mesa_id}", response_model=MesaWithTipoResponse)
def obtener_mesa(
    mesa_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene los detalles de una mesa específica.
    """
    mesa = db.query(Mesa).filter(Mesa.id_mesa == mesa_id).first()

    if not mesa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mesa no encontrada"
        )

    return mesa


@router.post("/", response_model=MesaWithTipoResponse, status_code=status.HTTP_201_CREATED)
def crear_mesa(
    mesa_data: MesaCreate,
    db: Session = Depends(get_db),
    current_user: UsuarioAdmin = Depends(get_current_user)
):
    """
    Crea una nueva mesa.
    Requiere autenticación de administrador.
    """
    from app.models.tipo_mesa import TipoMesa

    # Verificar que el tipo de mesa existe
    tipo_mesa = db.query(TipoMesa).filter(TipoMesa.id_tipo_mesa == mesa_data.id_tipo_mesa).first()
    if not tipo_mesa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tipo de mesa no encontrado"
        )

    nueva_mesa = Mesa(**mesa_data.model_dump())
    db.add(nueva_mesa)
    db.commit()
    db.refresh(nueva_mesa)

    return nueva_mesa


@router.put("/{mesa_id}", response_model=MesaWithTipoResponse)
def actualizar_mesa(
    mesa_id: int,
    mesa_data: MesaUpdate,
    db: Session = Depends(get_db),
    current_user: UsuarioAdmin = Depends(get_current_user)
):
    """
    Actualiza una mesa existente.
    Requiere autenticación de administrador.
    """
    mesa = db.query(Mesa).filter(Mesa.id_mesa == mesa_id).first()

    if not mesa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mesa no encontrada"
        )

    update_data = mesa_data.model_dump(exclude_unset=True)

    # Si se actualiza el tipo de mesa, verificar que existe
    if "id_tipo_mesa" in update_data:
        from app.models.tipo_mesa import TipoMesa
        tipo_mesa = db.query(TipoMesa).filter(TipoMesa.id_tipo_mesa == update_data["id_tipo_mesa"]).first()
        if not tipo_mesa:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tipo de mesa no encontrado"
            )

    for key, value in update_data.items():
        setattr(mesa, key, value)

    db.commit()
    db.refresh(mesa)

    return mesa


@router.delete("/{mesa_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_mesa(
    mesa_id: int,
    db: Session = Depends(get_db),
    current_user: UsuarioAdmin = Depends(get_current_user)
):
    """
    Elimina una mesa.
    Requiere autenticación de administrador.
    """
    mesa = db.query(Mesa).filter(Mesa.id_mesa == mesa_id).first()

    if not mesa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mesa no encontrada"
        )

    # Verificar que no tenga reservaciones activas
    from app.models.reservacion import Reservacion
    reservaciones_activas = db.query(Reservacion).filter(
        Reservacion.id_mesa == mesa_id,
        Reservacion.estado.in_(["pendiente", "confirmada"])
    ).first()

    if reservaciones_activas:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede eliminar una mesa con reservaciones activas"
        )

    db.delete(mesa)
    db.commit()
    return None
