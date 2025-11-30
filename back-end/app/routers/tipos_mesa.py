from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.tipo_mesa import TipoMesa
from app.models.usuario_admin import UsuarioAdmin
from app.schemas.tipo_mesa import TipoMesaCreate, TipoMesaUpdate, TipoMesaResponse
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/tipos-mesa", tags=["Gestión de Tipos de Mesa"])


@router.get("/", response_model=List[TipoMesaResponse])
def listar_tipos_mesa(db: Session = Depends(get_db)):
    """
    Lista todos los tipos de mesa.
    Endpoint público.
    """
    tipos = db.query(TipoMesa).all()
    return tipos


@router.get("/{tipo_id}", response_model=TipoMesaResponse)
def obtener_tipo_mesa(
    tipo_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene un tipo de mesa específico.
    """
    tipo = db.query(TipoMesa).filter(TipoMesa.id_tipo_mesa == tipo_id).first()

    if not tipo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tipo de mesa no encontrado"
        )

    return tipo


@router.post("/", response_model=TipoMesaResponse, status_code=status.HTTP_201_CREATED)
def crear_tipo_mesa(
    tipo_data: TipoMesaCreate,
    db: Session = Depends(get_db),
    current_user: UsuarioAdmin = Depends(get_current_user)
):
    """
    Crea un nuevo tipo de mesa.
    Requiere autenticación de administrador.
    """
    nuevo_tipo = TipoMesa(**tipo_data.model_dump())
    db.add(nuevo_tipo)
    db.commit()
    db.refresh(nuevo_tipo)

    return nuevo_tipo


@router.put("/{tipo_id}", response_model=TipoMesaResponse)
def actualizar_tipo_mesa(
    tipo_id: int,
    tipo_data: TipoMesaUpdate,
    db: Session = Depends(get_db),
    current_user: UsuarioAdmin = Depends(get_current_user)
):
    """
    Actualiza un tipo de mesa existente.
    Requiere autenticación de administrador.
    """
    tipo = db.query(TipoMesa).filter(TipoMesa.id_tipo_mesa == tipo_id).first()

    if not tipo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tipo de mesa no encontrado"
        )

    update_data = tipo_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(tipo, key, value)

    db.commit()
    db.refresh(tipo)

    return tipo


@router.delete("/{tipo_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_tipo_mesa(
    tipo_id: int,
    db: Session = Depends(get_db),
    current_user: UsuarioAdmin = Depends(get_current_user)
):
    """
    Elimina un tipo de mesa.
    Requiere autenticación de administrador.
    """
    tipo = db.query(TipoMesa).filter(TipoMesa.id_tipo_mesa == tipo_id).first()

    if not tipo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tipo de mesa no encontrado"
        )

    # Verificar que no tenga mesas asociadas
    from app.models.mesa import Mesa
    mesas_asociadas = db.query(Mesa).filter(Mesa.id_tipo_mesa == tipo_id).first()

    if mesas_asociadas:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede eliminar un tipo de mesa que tiene mesas asociadas"
        )

    db.delete(tipo)
    db.commit()
    return None
