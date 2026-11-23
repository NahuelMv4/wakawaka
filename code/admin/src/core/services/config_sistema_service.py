from datetime import time
from typing import Optional

from sqlalchemy import select

from src.core.database import db
from src.core.models.configuracion_sistema import ConfiguracionSistema
from src.core.models.tipo_comida import TipoComida


def create_configuracion(**kwargs) -> ConfiguracionSistema:
    configuracion = ConfiguracionSistema(**kwargs)
    db.session.add(configuracion)
    db.session.commit()
    return configuracion


def get_configuracion() -> Optional[ConfiguracionSistema]:
    return db.session.query(ConfiguracionSistema).first()


def get_configuracion_by_id(config_id: int) -> Optional[ConfiguracionSistema]:
    return db.session.get(ConfiguracionSistema, config_id)


def get_all_configuraciones() -> list[ConfiguracionSistema]:
    return db.session.query(ConfiguracionSistema).order_by(ConfiguracionSistema.id).all()


def get_paginacion() -> int:
    configuracion = get_configuracion()
    return configuracion.paginacion if configuracion else 25


def actualizar_parametros_generales(
    config_id: int,
    paginacion: int,
    horario_corte: time,
    usuario_id: Optional[int] = None,
) -> Optional[ConfiguracionSistema]:
    configuracion = get_configuracion_by_id(config_id) or get_configuracion()
    if not configuracion:
        return None

    configuracion.paginacion = paginacion
    configuracion.horario_corte = horario_corte
    if usuario_id is not None:
        configuracion.actualizado_por_usuario_id = usuario_id

    db.session.commit()
    return configuracion


def activar_mantenimiento(
    mensaje: str = "El sistema se encuentra en mantenimiento programado.",
    usuario_id: Optional[int] = None,
    config_id: Optional[int] = None,
) -> ConfiguracionSistema:
    configuracion = (
        get_configuracion_by_id(config_id) if config_id else None
    ) or get_configuracion()

    if not configuracion:
        return create_configuracion(
            clave="DEFAULT",
            paginacion=25,
            mantenimiento=True,
            mensaje_mantenimiento=mensaje,
            actualizado_por_usuario_id=usuario_id,
        )

    configuracion.mantenimiento = True
    configuracion.mensaje_mantenimiento = mensaje
    if usuario_id is not None:
        configuracion.actualizado_por_usuario_id = usuario_id

    db.session.commit()
    return configuracion


def desactivar_mantenimiento(
    usuario_id: Optional[int] = None,
    config_id: Optional[int] = None,
) -> ConfiguracionSistema:
    configuracion = (
        get_configuracion_by_id(config_id) if config_id else None
    ) or get_configuracion()

    if not configuracion:
        return create_configuracion(
            clave="DEFAULT",
            paginacion=25,
            mantenimiento=False,
            mensaje_mantenimiento=None,
            actualizado_por_usuario_id=usuario_id,
        )

    configuracion.mantenimiento = False
    configuracion.mensaje_mantenimiento = None
    if usuario_id is not None:
        configuracion.actualizado_por_usuario_id = usuario_id

    db.session.commit()
    return configuracion


def toggle_mantenimiento(
    mensaje: str = "El sistema se encuentra en mantenimiento programado.",
    usuario_id: Optional[int] = None,
    config_id: Optional[int] = None,
) -> ConfiguracionSistema:
    configuracion = (
        get_configuracion_by_id(config_id) if config_id else None
    ) or get_configuracion()

    if configuracion and configuracion.mantenimiento:
        return desactivar_mantenimiento(usuario_id=usuario_id, config_id=configuracion.id)
    return activar_mantenimiento(
        mensaje=mensaje,
        usuario_id=usuario_id,
        config_id=configuracion.id if configuracion else None,
    )


def get_configuracion_publica() -> dict:
    config = get_configuracion()
    comidas = db.session.execute(select(TipoComida).order_by(TipoComida.id)).scalars().all()

    horarios_comidas = [
        {
            "comida": c.nombre.value if hasattr(c.nombre, "value") else str(c.nombre),
            "hora_inicio": c.hora_inicio.strftime("%H:%M"),
            "hora_fin": c.hora_fin.strftime("%H:%M"),
        }
        for c in comidas
    ]

    if not config:
        return {
            "paginacion": 25,
            "horario_corte": time(18, 0).strftime("%H:%M"),
            "mantenimiento": False,
            "mensaje_mantenimiento": None,
            "horarios_comidas": horarios_comidas,
        }

    return {
        "paginacion": config.paginacion,
        "horario_corte": config.horario_corte.strftime("%H:%M"),
        "mantenimiento": config.mantenimiento,
        "mensaje_mantenimiento": config.mensaje_mantenimiento if config.mantenimiento else None,
        "horarios_comidas": horarios_comidas,
    }