"""Modelo de datos para los pedidos de comidas."""

from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


class Pedido(Base):
    """Representa un pedido de comidas de un sector para una comida y fecha."""

    __tablename__ = "PEDIDO"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    fecha_desde: Mapped[datetime] = mapped_column(nullable=False)
    fecha_hasta: Mapped[datetime] = mapped_column(nullable=False)
    estado: Mapped[str] = mapped_column(nullable=False)
    # Agregue un motivo obligatorio cuando el servicio de alimentacion rechaza el pedido
    motivo_rechazo: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    creado_en: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Agregue que vincula el pedido al sector para permitir la gestion compartida entre jefes del mismo sector
    sector_id: Mapped[int] = mapped_column(ForeignKey("SECTOR.id"), nullable=False)
    sector: Mapped["Sector"] = relationship(back_populates="pedidos")

    tipo_comida_id: Mapped[int] = mapped_column(ForeignKey("TIPO_COMIDA.id"), nullable=False)
    tipo_comida: Mapped["TipoComida"] = relationship(back_populates="pedidos")

    usuario_id: Mapped[int] = mapped_column(ForeignKey("USUARIO.id"), nullable=False)
    usuario: Mapped["Usuario"] = relationship(back_populates="pedidos")

    # Modifique cascade para permitir eliminar o editar pedidos confirmados sin dejar registros huerfanos
    revisiones: Mapped[List["Revision"]] = relationship(
        back_populates="pedido", cascade="all, delete-orphan"
    )
    solicitudes_comida: Mapped[List["SolicitudComida"]] = relationship(
        back_populates="pedido", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<PEDIDO(id={self.id}, estado={self.estado})>"