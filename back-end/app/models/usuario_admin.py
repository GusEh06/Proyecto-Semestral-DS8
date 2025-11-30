from sqlalchemy import Column, Integer, String, Boolean, DateTime, CheckConstraint
from sqlalchemy.sql import func
from app.database import Base


class UsuarioAdmin(Base):
    __tablename__ = "usuarios_admin"

    id_usuario = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(120), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    rol = Column(String(30), default="admin")
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=False), default=func.now())
    updated_at = Column(DateTime(timezone=False), default=func.now(), onupdate=func.now())

    __table_args__ = (
        CheckConstraint(
            "rol IN ('admin', 'superadmin', 'staff')",
            name='usuarios_admin_rol_check'
        ),
    )
