from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Literal


class UsuarioAdminBase(BaseModel):
    nombre: str = Field(..., max_length=120, description="Nombre del usuario")
    email: EmailStr = Field(..., description="Email del usuario")
    rol: Literal["admin", "superadmin", "staff"] = Field(
        default="admin",
        description="Rol del usuario"
    )
    is_active: bool = Field(default=True, description="Si el usuario está activo")


class UsuarioAdminCreate(UsuarioAdminBase):
    password: str = Field(..., min_length=6, description="Contraseña del usuario")


class UsuarioAdminUpdate(BaseModel):
    nombre: str | None = Field(None, max_length=120)
    email: EmailStr | None = None
    password: str | None = Field(None, min_length=6)
    rol: Literal["admin", "superadmin", "staff"] | None = None
    is_active: bool | None = None


class UsuarioAdminResponse(UsuarioAdminBase):
    id_usuario: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
