import datetime
from typing import List

from sqlalchemy import Enum as SQLEnum
from sqlalchemy import Time
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.database import Base
from src.core.enums import TipoComidaEnum


class TipoComida(Base):
  __tablename__ = "TIPO_COMIDA"

  id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
  nombre: Mapped[TipoComidaEnum] = mapped_column(
    SQLEnum(
      TipoComidaEnum,
      values_callable=lambda x: [e.value for e in x],
      native_enum=False
    ),
    unique=True,
    nullable=False
  )
  hora_inicio: Mapped[datetime] = mapped_column(Time, nullable=False)
  hora_fin: Mapped[datetime] = mapped_column(Time, nullable=False)

  cupos: Mapped[List["Cupo"]] = relationship(back_populates="tipo_comida")
  pedidos: Mapped[List["Pedido"]] = relationship(back_populates="tipo_comida")

  def __repr__(self):
    return f"<TIPO_COMIDA(id={self.id}, nombre={self.nombre})>"