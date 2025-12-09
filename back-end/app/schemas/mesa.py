from pydantic import BaseModel, Field
from datetime import datetime, date, time
from typing import Literal, Optional
from app.schemas.tipo_mesa import TipoMesaResponse


class MesaBase(BaseModel):
    id_tipo_mesa: int = Field(..., description="ID del tipo de mesa")
    estado: Literal["disponible", "ocupada", "reservada"] = Field(
        default="disponible",
        description="Estado de la mesa"
    )


class MesaCreate(MesaBase):
    pass


class MesaUpdate(BaseModel):
    id_tipo_mesa: int | None = None
    estado: Literal["disponible", "ocupada", "reservada"] | None = None


class MesaResponse(MesaBase):
    id_mesa: int
    updated_at: datetime

    class Config:
        from_attributes = True


class ReservacionActiva(BaseModel):
    """Información resumida de la reservación activa para una mesa"""
    id_reserva: int
    nombre: str
    apellido: str
    telefono: Optional[str] = None
    correo: str
    cantidad_personas: int
    fecha: date
    hora: time
    estado: str

    class Config:
        from_attributes = True


class MesaWithTipoResponse(MesaResponse):
    tipo_mesa: TipoMesaResponse
    reservacion_activa: Optional[ReservacionActiva] = None

    class Config:
        from_attributes = True
