from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Mesa(Base):
    __tablename__ = "mesas"

    id_mesa = Column(Integer, primary_key=True, index=True)
    id_tipo_mesa = Column(Integer, ForeignKey("tipo_mesa.id_tipo_mesa", ondelete="RESTRICT"), nullable=False)
    estado = Column(String(20), nullable=False, default="disponible")
    personas_actuales = Column(Integer, nullable=False, default=0)
    updated_at = Column(DateTime(timezone=False), default=func.now(), onupdate=func.now())

    tipo_mesa = relationship("TipoMesa", backref="mesas")

    __table_args__ = (
        CheckConstraint(
            "estado IN ('disponible', 'ocupada', 'reservada')",
            name='mesas_estado_check'
        ),
    )
