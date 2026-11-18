import bcrypt
from sqlalchemy import select

from src.core.database import db
from src.core.models.usuario import Usuario


def _contrasenia_valida(guardada, ingresada):
    return bcrypt.checkpw(
        ingresada.encode("utf-8"),
        guardada.encode("utf-8")
    )


def autenticar(email, password):
    usuario = db.session.execute(
        select(Usuario).where(Usuario.email == email)
    ).scalars().first()

    if usuario is None:
        return None
    if not _contrasenia_valida(usuario.contrasenia, password):
        return None
    if usuario.activo is False:
        return None
    return usuario