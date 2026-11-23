from datetime import datetime, timezone
from typing import List

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


class Sector(Base):
  __tablename__ = "SECTOR"

  id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
  nombre: Mapped[str] = mapped_column()
  descripcion: Mapped[str] = mapped_column()
  activo: Mapped[bool] = mapped_column(default=True)
  creado_en: Mapped[datetime] = mapped_column(
    DateTime, default=lambda: datetime.now(timezone.utc)
  )
  actualizado_en: Mapped[datetime] = mapped_column(
    DateTime, 
    default=lambda: datetime.now(timezone.utc),
    onupdate=lambda: datetime.now(timezone.utc)
  )
  pedidos: Mapped[List["Pedido"]] = relationship(back_populates="sector")

  usuarios: Mapped[List["Usuario"]] = relationship(back_populates="sector")
  lista_personal: Mapped[List["Personal"]] = relationship(back_populates="sector")
  cupos: Mapped[List["Cupo"]] = relationship(back_populates="sector")
  pedidos: Mapped[List["Pedido"]] = relationship(back_populates="sector")

  def __repr__(self):
    return f"<SECTOR(id={self.id}, nombre={self.nombre}, activo={self.activo})>"