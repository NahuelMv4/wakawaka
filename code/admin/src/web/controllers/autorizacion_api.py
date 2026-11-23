from datetime import date
from flask import Blueprint, jsonify, request
from src.core.errores.custom_errors import BadRequestError, ConflictError, NotFoundError
from src.core.services import autorizacion_service
from src.web.helpers.auth import check, login_required
from src.web.helpers.api_auth import jwt_check
from flask_jwt_extended import get_jwt_identity
from src.core.database import db
from src.core.models.pedido import Pedido

autorizacion_api_bp = Blueprint("autorizacion_api", __name__, url_prefix="/api")


def _parse_date(valor: str | None, campo: str) -> date | None:
    if not valor:
        return None
    try:
        return date.fromisoformat(valor)
    except ValueError:
        raise BadRequestError(f"El parámetro '{campo}' debe tener formato YYYY-MM-DD.")


def _parse_optional_int(valor: str | None, campo: str) -> int | None:
    if valor is None or valor == "":
        return None
    try:
        return int(valor)
    except ValueError:
        raise BadRequestError(f"El parámetro '{campo}' debe ser un número entero válido.")


@autorizacion_api_bp.get("/authorization-dates")
@jwt_check("autorizacion_index") 
def authorization_dates():
    """Devuelve las fechas con pedidos en el rango solicitado."""
    fecha_desde = _parse_date(request.args.get("fecha_desde"), "fecha_desde")
    fecha_hasta = _parse_date(request.args.get("fecha_hasta"), "fecha_hasta")

    fechas = autorizacion_service.obtener_fechas_con_pedidos(
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
    )
    return jsonify({"dates": fechas}), 200


@autorizacion_api_bp.get("/authorizations")
@jwt_check("autorizacion_index")
def authorizations():
    """Lista los pedidos filtrados para el módulo de autorización."""
    fecha_str = request.args.get("fecha")
    fecha = _parse_date(fecha_str, "fecha")

    pedidos = autorizacion_service.listar_pedidos_autorizacion(
        fecha=fecha.isoformat() if fecha else None,
        sector_id=_parse_optional_int(request.args.get("sector_id"), "sector_id"),
        tipo_comida_id=_parse_optional_int(request.args.get("tipo_comida_id"), "tipo_comida_id"),
        tipo_menu_id=_parse_optional_int(request.args.get("tipo_menu_id"), "tipo_menu_id"),
        condicion=request.args.get("condicion"),
        estado=request.args.get("estado"),
    )
    return jsonify({"pedidos": pedidos}), 200



@autorizacion_api_bp.put("/authorizations/<int:pedido_id>")
@jwt_check("autorizacion_index")
def autorizar_pedido(pedido_id: int):
    pedido = autorizacion_service.marcar_pedido_autorizado(pedido_id)
    if not pedido:
        return jsonify({"error": "Pedido no encontrado."}), 404

    return jsonify({
        "mensaje": f"Pedido #{pedido.id} autorizado.",
        "pedido_id": pedido.id,
        "estado": pedido.estado,
    }), 200

@autorizacion_api_bp.put("/authorizations/<int:pedido_id>/reject")
@jwt_check("autorizacion_index")
def rechazar_pedido(pedido_id: int):
    data = request.get_json(silent=True) or {}
    motivo = (data.get("motivo_rechazo") or data.get("motivo") or "").strip()
    if not motivo:
        return jsonify({"error": "El motivo de rechazo es obligatorio."}), 400

    identidad = get_jwt_identity()
    usuario_id = int(identidad) if identidad is not None else None

    try:
        pedido = autorizacion_service.marcar_pedido_rechazado(
            pedido_id=pedido_id,
            motivo_rechazo=motivo,
            usuario_id=usuario_id,
        )
    except BadRequestError as err:
        return jsonify({"error": str(err)}), 400
    except NotFoundError as err:
        return jsonify({"error": str(err)}), 404
    except ConflictError as err:
        return jsonify({"error": str(err)}), 409

    return jsonify({
        "mensaje": f"Pedido #{pedido.id} rechazado.",
        "pedido_id": pedido.id,
        "estado": pedido.estado,
        "motivo_rechazo": getattr(pedido, "motivo_rechazo", motivo),
    }), 200


@autorizacion_api_bp.get("/authorizations/<int:pedido_id>")
@jwt_check("autorizacion_index")
def obtener_solicitudes_pedido(pedido_id: int):
    """Devuelve el pedido y su lista de solicitudes de comida por ID de pedido."""
    pedido = db.session.get(Pedido, pedido_id)
    if pedido is None:
        raise NotFoundError("Pedido no encontrado.")

    solicitudes = sorted(pedido.solicitudes_comida, key=lambda s: s.id)

    lista_solicitudes = [
        {
            "id": s.id,
            "pedido_id": s.pedido_id,
            "fecha_comida": s.fecha_comida.isoformat() if s.fecha_comida else None,
            "condicion": s.condicion,
            "personal_id": s.personal_id,
            "persona_nombre": (
                f"{s.personal.apellido}, {s.personal.nombre}"
                if getattr(s, "personal", None)
                else f"Personal #{s.personal_id}"
            ),
            "dni": getattr(s.personal, "dni", None) if getattr(s, "personal", None) else None,
            "tipo_menu_id": s.tipo_menu_id,
            "tipo_menu_nombre": (
                s.tipo_menu.nombre if getattr(s, "tipo_menu", None) else None
            ),
            "autorizada": bool(getattr(s, "autorizada", False)),
            "entregada": bool(s.entrega_id),
        }
        for s in solicitudes
    ]

    return jsonify({
        "pedido_id": pedido.id,
        "estado": pedido.estado,
        "fecha": pedido.fecha_desde.date().isoformat() if pedido.fecha_desde else None,
        "actualizado_en": pedido.actualizado_en.isoformat() if pedido.actualizado_en else None,
        "solicitudes_comida": lista_solicitudes,
    }), 200


def _filtros_csv_desde_request() -> dict:
    args = request.args
    return {
        "fecha": args.get("fecha") or None,
        "fecha_desde": args.get("fecha_desde") or None,
        "fecha_hasta": args.get("fecha_hasta") or None,
        "sector_id": args.get("sector_id") or None,
        "tipo_comida_id": args.get("tipo_comida_id") or None,
        "tipo_menu_id": args.get("tipo_menu_id") or None,
        "condicion": args.get("condicion") or None,
        "estado": args.get("estado") or None,
    }


@autorizacion_api_bp.get("/authorized-meals")
@jwt_check("autorizacion_index")
def listar_comidas_autorizadas():
    if request.args.get("formato") == "csv":
        return autorizacion_service.generar_csv_personas_autorizadas(
            _filtros_csv_desde_request()
        )
    return jsonify({"meals": []}), 200


@autorizacion_api_bp.get("/summaries/authorizations")
@jwt_check("autorizacion_index")
def resumen_autorizaciones():
    if request.args.get("formato") == "csv":
        return autorizacion_service.generar_csv_totales_por_sector(
            _filtros_csv_desde_request()
        )
    return jsonify({"summaries": []}), 200