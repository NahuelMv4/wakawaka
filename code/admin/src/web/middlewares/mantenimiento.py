from flask import jsonify, redirect, request, session, url_for

from src.core.database import db
from src.core.enums import RolEnum
from src.core.services import config_sistema_service


def register_mantenimiento_middleware(app):
    @app.before_request
    def verificar_modo_mantenimiento():
        if request.method == "OPTIONS":
            return None

        endpoint_actual = request.endpoint or ""
        path_actual = request.path or ""

        if path_actual.startswith("/api/"):
            if request.method == "GET" and path_actual.rstrip("/") == "/api/configuration":
                return None

            try:
                configuracion = config_sistema_service.get_configuracion()
            except Exception:
                db.session.rollback()
                return None

            if configuracion and configuracion.mantenimiento:
                mensaje = (
                    configuracion.mensaje_mantenimiento
                    or "El sistema se encuentra en mantenimiento programado."
                )
                return jsonify(
                    {
                        "error": "mantenimiento",
                        "mensaje": mensaje,
                    }
                ), 503

            return None

        # Rutas HTML del panel privado
        if (
            endpoint_actual == "configuracion.vista_mantenimiento"
            or endpoint_actual.startswith("static")
            or endpoint_actual.startswith("auth.")
        ):
            return None

        try:
            configuracion = config_sistema_service.get_configuracion()
            if configuracion and configuracion.mantenimiento:
                if session.get("rol") != RolEnum.ADMINISTRADOR.value:
                    return redirect(url_for("configuracion.vista_mantenimiento"))
        except Exception:
            db.session.rollback()
            return None