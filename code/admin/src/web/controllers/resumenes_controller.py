"""Endpoints REST para los resúmenes del sistema."""

from datetime import date

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity

from src.core.services import usuario_service
from src.core.services import resumenes_service
from src.core.errores.custom_errors import BadRequestError, ForbiddenError
from src.web.helpers.api_auth import jwt_check


resumenes_api_bp = Blueprint(
    "resumenes_api",
    __name__,
    url_prefix="/api/summaries"
)


def _obtener_filtros():
    """Obtiene y valida los filtros recibidos por query string."""

    filtros = request.args.to_dict()

    campos_id = [
        "sector_id",
        "tipo_comida_id",
        "tipo_menu_id"
    ]

    campos_fecha = [
        "fecha_desde",
        "fecha_hasta"
    ]

    try:
        for campo in campos_id:
            if campo in filtros:
                if not filtros[campo].strip():
                    raise ValueError(
                        f"El parámetro {campo} no puede estar vacío."
                    )

                filtros[campo] = int(filtros[campo])

                if filtros[campo] <= 0:
                    raise ValueError(
                        f"El parámetro {campo} debe ser positivo."
                    )

        for campo in campos_fecha:
            if campo in filtros:
                if not filtros[campo].strip():
                    raise ValueError(
                        f"El parámetro {campo} no puede estar vacío."
                    )

                filtros[campo] = date.fromisoformat(filtros[campo])

        fecha_desde = filtros.get("fecha_desde")
        fecha_hasta = filtros.get("fecha_hasta")

        if (
            fecha_desde is not None
            and fecha_hasta is not None
            and fecha_desde > fecha_hasta
        ):
            raise ValueError(
                "La fecha desde no puede ser posterior a la fecha hasta."
            )

        if "condicion" in filtros:
            condiciones_permitidas = {"Regular", "Excepción"}

            if filtros["condicion"] not in condiciones_permitidas:
                raise ValueError(
                    "La condición debe ser Regular o Excepción."
                )

        if "agrupar_por" in filtros:
            filtros["agrupar_por"] = [
                valor.strip()
                for valor in filtros["agrupar_por"].split(",")
            ]

    except (ValueError, TypeError):
        raise BadRequestError({
            "error": "Los filtros tienen un formato inválido."
        })

    return filtros


@resumenes_api_bp.get("/requests")
@jwt_check("summary_requests")
def resumen_pedidos():
    """Devuelve el resumen de solicitudes y los datos de gráficos."""

    usuario_id = int(get_jwt_identity())
    usuario = usuario_service.obtener_usuario_activo(usuario_id)

    if usuario is None:
        raise ForbiddenError("Usuario inactivo o inexistente.")

    rol = usuario.rol.nombre.value

    if rol == "Jefe de Servicio":

        if not usuario.sector_id:
            raise ForbiddenError(
                "El usuario no tiene un sector asignado."
            )

        sector_id = usuario.sector_id

    elif rol == "Servicio de Alimentación":
        sector_id = None

    else:
        raise ForbiddenError(
            "No tiene permiso para consultar resúmenes."
        )

    filtros = _obtener_filtros()

    try:
        resultado = resumenes_service.obtener_resumen(
            filtros=filtros,
            sector_id=sector_id
        )

    except ValueError as error:
        raise BadRequestError({
            "error": str(error)
        })

    return jsonify(resultado), 200


@resumenes_api_bp.get("/authorizations")
@jwt_check("summary_authorizations")
def resumen_autorizaciones():
    """Devuelve el resumen de solicitudes pedidas y autorizadas."""

    usuario_id = int(get_jwt_identity())
    usuario = usuario_service.obtener_usuario_activo(usuario_id)

    if usuario is None:
        raise ForbiddenError("Usuario inactivo o inexistente.")

    rol = usuario.rol.nombre.value

    if rol != "Servicio de Alimentación":
        raise ForbiddenError(
            "No tiene permiso para consultar este resumen."
        )

    filtros = _obtener_filtros()

    try:
        resultado = resumenes_service.obtener_resumen_autorizaciones(
            filtros=filtros
        )

    except ValueError as error:
        raise BadRequestError({
            "error": str(error)
        })

    return jsonify({
        "data": resultado
    }), 200


@resumenes_api_bp.get("/deliveries")
@jwt_check("summary_deliveries")
def resumen_entregas():
    """Devuelve el resumen de solicitudes autorizadas y entregadas."""

    usuario_id = int(get_jwt_identity())
    usuario = usuario_service.obtener_usuario_activo(usuario_id)

    if usuario is None:
        raise ForbiddenError("Usuario inactivo o inexistente.")

    rol = usuario.rol.nombre.value

    if rol != "Servicio de Alimentación":
        raise ForbiddenError(
            "No tiene permiso para consultar este resumen."
        )

    filtros = _obtener_filtros()

    try:
        resultado = resumenes_service.obtener_resumen_entregas(
            filtros=filtros
        )

    except ValueError as error:
        raise BadRequestError({
            "error": str(error)
        })

    return jsonify({
        "data": resultado
    }), 200