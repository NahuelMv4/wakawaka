from typing import List

from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base
from src.core.enums import TipoPersonalEnum


class TipoPersonal(Base):
  __tablename__ = "TIPO_PERSONAL"

  id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
  nombre: Mapped[TipoPersonalEnum] = mapped_column(
      SQLEnum(
        TipoPersonalEnum,
        values_callable=lambda x: [e.value for e in x],
        native_enum=False
      ),
      unique=True,
      nullable=False
    )

  lista_personal: Mapped[List["Personal"]] = relationship(back_populates="tipo_personal")

  def __repr__(self):
    return f"<TIPO_PERSONAL(id={self.id}, nombre={self.nombre})>"