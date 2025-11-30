from sqlalchemy import Column, Integer, String, CheckConstraint
from app.database import Base


class TipoMesa(Base):
    __tablename__ = "tipo_mesa"

    id_tipo_mesa = Column(Integer, primary_key=True, index=True)
    descripcion = Column(String(50), nullable=False)
    cantidad_sillas = Column(Integer, nullable=False)

    __table_args__ = (
        CheckConstraint('cantidad_sillas > 0', name='tipo_mesa_cantidad_sillas_check'),
    )
