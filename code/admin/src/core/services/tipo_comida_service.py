from src.core.database import db
from src.core.models.tipo_comida import TipoComida
from sqlalchemy import select


def create_tipo_comida(**kwargs):
  tipo_comida = TipoComida(**kwargs)
  db.session.add(tipo_comida)
  db.session.commit()
  return tipo_comida

def list_tipos_comida():
    stmt = select(TipoComida).order_by(TipoComida.id)
    return db.session.scalars(stmt).all()