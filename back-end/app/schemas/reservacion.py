from pydantic import BaseModel, Field, EmailStr
from datetime import date, time, datetime
from typing import Literal, Optional
from app.schemas.mesa import MesaWithTipoResponse


class ReservacionBase(BaseModel):
    nombre: str = Field(..., max_length=100, description="Nombre del cliente")
    apellido: str = Field(..., max_length=100, description="Apellido del cliente")
    correo: EmailStr = Field(..., description="Correo electrónico del cliente")
    telefono: str | None = Field(None, max_length=50, description="Teléfono del cliente")
    cantidad_personas: int = Field(..., gt=0, description="Cantidad de personas")
    fecha: date = Field(..., description="Fecha de la reservación")
    hora: time = Field(..., description="Hora de la reservación")


class ReservacionCreate(ReservacionBase):
    pass


class ReservacionUpdate(BaseModel):
    nombre: str | None = Field(None, max_length=100)
    apellido: str | None = Field(None, max_length=100)
    correo: EmailStr | None = None
    telefono: str | None = Field(None, max_length=50)
    cantidad_personas: int | None = Field(None, gt=0)
    fecha: date | None = None
    hora: time | None = None
    id_mesa: int | None = None
    estado: Literal["pendiente", "confirmada", "cancelada", "completada"] | None = None


class ReservacionResponse(ReservacionBase):
    id_reserva: int
    id_mesa: int | None
    estado: Literal["pendiente", "confirmada", "cancelada", "completada"]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReservacionWithDetailsResponse(ReservacionResponse):
    mesa: Optional[MesaWithTipoResponse] = None

    class Config:
        from_attributes = True
