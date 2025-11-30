from pydantic import BaseModel, Field


class TipoMesaBase(BaseModel):
    descripcion: str = Field(..., max_length=50, description="Descripción del tipo de mesa")
    cantidad_sillas: int = Field(..., gt=0, description="Cantidad de sillas de la mesa")


class TipoMesaCreate(TipoMesaBase):
    pass


class TipoMesaUpdate(BaseModel):
    descripcion: str | None = Field(None, max_length=50)
    cantidad_sillas: int | None = Field(None, gt=0)


class TipoMesaResponse(TipoMesaBase):
    id_tipo_mesa: int

    class Config:
        from_attributes = True
