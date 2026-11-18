from flask import redirect, request, url_for

from src.core.database import db
from src.core.enums import RolEnum
from src.core.services import config_sistema_service


def register_mantenimiento_middleware(app):
    @app.before_request
    def verificar_modo_mantenimiento():
        endpoint_actual = request.endpoint or ""

        # Permitir acceder a la pantalla de mantenimiento y archivos estáticos
        if endpoint_actual == "configuracion.vista_mantenimiento" or endpoint_actual.startswith("static"):
            return None

        # Permitir autenticación
        if endpoint_actual.startswith("auth."):
            return None

        try:
            configuracion = config_sistema_service.get_configuracion()

            if configuracion and configuracion.mantenimiento:

                # Si no es administrador, mostrar mantenimiento
                if session.get("rol") != RolEnum.ADMINISTRADOR.value:
                    return redirect(url_for("configuracion.vista_mantenimiento"))

        except Exception:
            db.session.rollback()
            return None