from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal
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


class MesaWithTipoResponse(MesaResponse):
    tipo_mesa: TipoMesaResponse

    class Config:
        from_attributes = True
