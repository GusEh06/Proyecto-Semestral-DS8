from sqlalchemy import Column, Integer, String, Date, Time, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Reservacion(Base):
    __tablename__ = "reservaciones"

    id_reserva = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    correo = Column(String(150), nullable=False, index=True)
    telefono = Column(String(50))
    cantidad_personas = Column(Integer, nullable=False)
    fecha = Column(Date, nullable=False, index=True)
    hora = Column(Time, nullable=False)
    id_mesa = Column(Integer, ForeignKey("mesas.id_mesa", ondelete="SET NULL"))
    estado = Column(String(20), default="pendiente")
    created_at = Column(DateTime(timezone=False), default=func.now())
    updated_at = Column(DateTime(timezone=False), default=func.now(), onupdate=func.now())

    mesa = relationship("Mesa", backref="reservaciones")

    __table_args__ = (
        CheckConstraint('cantidad_personas > 0', name='reservaciones_cantidad_personas_check'),
        CheckConstraint(
            "estado IN ('pendiente', 'confirmada', 'cancelada', 'completada')",
            name='reservaciones_estado_check'
        ),
    )
