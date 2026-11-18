"""Modelo de datos para la configuración global del sistema."""

from datetime import datetime, time, timezone
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


class ConfiguracionSistema(Base):
    """Parámetros globales configurables del sistema."""

    __tablename__ = "CONFIGURACION_SISTEMA"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    clave: Mapped[str] = mapped_column(unique=True, nullable=False)
    paginacion: Mapped[int] = mapped_column(nullable=False)
    # Agregue hora limite del dia anterior para cargar modificar o eliminar pedidos
    horario_corte: Mapped[time] = mapped_column(Time, default=time(18, 0), nullable=False)
    mantenimiento: Mapped[bool] = mapped_column(default=False, nullable=False)
    mensaje_mantenimiento: Mapped[str] = mapped_column(nullable=True)
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    actualizado_por_usuario_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("USUARIO.id"), nullable=True
    )
    actualizado_por_usuario: Mapped[Optional["Usuario"]] = relationship()