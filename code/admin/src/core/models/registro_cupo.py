from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


class RegistroCupo(Base):
    __tablename__ = "REGISTRO_CUPO"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    estado: Mapped[str] = mapped_column(nullable=False)
    fecha: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    # Agregue un nuevo campo: cupo_historico
    # Guarda la cantidad permitida por el cupo en el momento exacto del registro
    # Esto garantiza que las modificaciones futuras al cupo no alteren este historial
    cupo_historico: Mapped[int] = mapped_column(nullable=False)

    cupo_id: Mapped[int] = mapped_column(ForeignKey("CUPO.id"), nullable=False)
    cupo: Mapped["Cupo"] = relationship(back_populates="registros_cupo")

    solicitud_comida_id: Mapped[int] = mapped_column(ForeignKey("SOLICITUD_COMIDA.id"), nullable=False, unique=True)
    solicitud_comida: Mapped["SolicitudComida"] = relationship(back_populates="registro_cupo")

    def __repr__(self):
        return f"<REGISTRO_CUPO(id={self.id}, estado={self.estado}, cupo_historico={self.cupo_historico})>"