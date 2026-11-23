from datetime import date, datetime, timezone
from typing import Optional
from sqlalchemy import Date, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.database import Base
from src.core.models.pedido import Pedido
from src.core.models.personal import Personal
from src.core.models.tipo_menu import TipoMenu
from src.core.models.entrega import Entrega


class SolicitudComida(Base):
    """Representa la solicitud nominada de comida para una persona."""

    __tablename__ = "SOLICITUD_COMIDA"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    fecha_comida: Mapped[date] = mapped_column(Date, nullable=False)
    condicion: Mapped[str] = mapped_column(String, nullable=False)
    solicitado_en: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    autorizada: Mapped[bool] = mapped_column(default=False, nullable=False)

    pedido_id: Mapped[int] = mapped_column(ForeignKey("PEDIDO.id"), nullable=False)
    pedido: Mapped["Pedido"] = relationship(back_populates="solicitudes_comida")

    personal_id: Mapped[int] = mapped_column(ForeignKey("PERSONAL.id"), nullable=False)
    personal: Mapped["Personal"] = relationship(back_populates="solicitudes_comida")

    tipo_menu_id: Mapped[int] = mapped_column(ForeignKey("TIPO_MENU.id"), nullable=False)
    tipo_menu: Mapped["TipoMenu"] = relationship(back_populates="solicitudes_comida")

    entrega_id: Mapped[Optional[int]] = mapped_column(ForeignKey("ENTREGA.id"), nullable=True)
    entrega: Mapped[Optional["Entrega"]] = relationship(back_populates="solicitudes")

    # Modifique cascade para limpiar registro_cupo al modificar/borrar un pedido confirmado
    registro_cupo: Mapped[Optional["RegistroCupo"]] = relationship(
        back_populates="solicitud_comida", uselist=False, cascade="all, delete-orphan"
    )