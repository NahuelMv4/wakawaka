from src.core.database import db
from src.core.models.configuracion_sistema import ConfiguracionSistema


def create_configuracion(**kwargs):
    configuracion = ConfiguracionSistema(**kwargs)
    db.session.add(configuracion)
    db.session.commit()
    return configuracion


def get_configuracion():
    return db.session.query(ConfiguracionSistema).first()


def activar_mantenimiento(
    mensaje: str = "El sistema se encuentra en mantenimiento.",
    usuario_id: int = None,
):
    configuracion = get_configuracion()
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


def desactivar_mantenimiento(usuario_id: int = None):
    configuracion = get_configuracion()
    if not configuracion:
        return create_configuracion(
            clave="DEFAULT",
            paginacion=10,
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
    mensaje: str = "El sistema se encuentra en mantenimiento.",
    usuario_id: int = None,
):
    configuracion = get_configuracion()
    if configuracion and configuracion.mantenimiento:
        return desactivar_mantenimiento(usuario_id=usuario_id)
    return activar_mantenimiento(mensaje=mensaje, usuario_id=usuario_id)

def get_all_configuraciones():
    return db.session.query(ConfiguracionSistema).all()

def get_paginacion():
    configuracion = db.session.query(ConfiguracionSistema).first()
    if not configuracion:
        return 25
    return configuracion.paginacion