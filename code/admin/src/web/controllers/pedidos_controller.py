"""Controlador REST para la gestión de pedidos de comidas del Jefe de Servicio."""

from collections import defaultdict
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity
from marshmallow import ValidationError
from src.core.errores.custom_errors import BadRequestError, ForbiddenError
from src.core.models.pedido import Pedido
from src.core.services import pedido_service, usuario_service
from src.web.helpers.api_auth import jwt_check
from src.web.schemas.pedido_schema import (
    actualizar_pedido_schema,
    crear_pedido_schema,
    filtro_pedidos_schema,
)

pedidos_api_bp = Blueprint("pedidos_api", __name__, url_prefix="/api/requests")


def _obtener_contexto_usuario() -> tuple[int, int]:
    """Obtiene el usuario_id y sector_id del usuario autenticado vía JWT."""
    usuario_id = int(get_jwt_identity())
    usuario = usuario_service.obtener(usuario_id)
    if not usuario or not usuario.sector_id:
        raise ForbiddenError("El usuario autenticado no tiene un sector asignado.")
    return usuario.id, usuario.sector_id


def _serializar_resumen_pedido(pedido: Pedido) -> dict:
    """Construye la representación resumida de un pedido con totales por menú y condición."""
    totales_por_menu = defaultdict(int)
    regulares = 0
    excepciones = 0

    for sol in pedido.solicitudes_comida:
        totales_por_menu[sol.tipo_menu.nombre] += 1
        if sol.condicion == "Regular":
            regulares += 1
        else:
            excepciones += 1

    fecha_pedido = pedido.fecha_desde.date()
    resultado = {
        "id": pedido.id,
        "fecha": fecha_pedido.strftime("%Y-%m-%d"),
        "fecha_formateada": fecha_pedido.strftime("%d/%m/%Y"),
        "estado": pedido.estado,
        "sector_id": pedido.sector_id,
        "tipo_comida_id": pedido.tipo_comida_id,
        "tipo_comida": pedido.tipo_comida.nombre,
        "creado_en": pedido.creado_en.isoformat(),
        "actualizado_en": pedido.actualizado_en.isoformat(),
        "total_personas": len(pedido.solicitudes_comida),
        "totales_pedidos": dict(totales_por_menu),
        "resumen_condicion": {"regulares": regulares, "excepciones": excepciones},
    }

    if pedido.estado == "Autorizado":
        resultado["totales_autorizados"] = {
            "total": len(pedido.solicitudes_comida),
            "por_menu": dict(totales_por_menu),
        }
    elif pedido.estado == "Rechazado":
        resultado["totales_autorizados"] = {"total": 0, "por_menu": {}}
        resultado["motivo_rechazo"] = pedido.motivo_rechazo

    return resultado


def _serializar_detalle_pedido(pedido: Pedido) -> dict:
    """Construye la representación detallada de un pedido con sus solicitudes nominadas."""
    data = _serializar_resumen_pedido(pedido)
    solicitudes_ordenadas = sorted(pedido.solicitudes_comida, key=lambda s: s.id)
    data["solicitudes"] = [
        {
            "id": sol.id,
            "personal_id": sol.personal_id,
            "dni": sol.personal.dni,
            "nombre": sol.personal.nombre,
            "apellido": sol.personal.apellido,
            "tipo_menu_id": sol.tipo_menu_id,
            "tipo_menu": sol.tipo_menu.nombre,
            "condicion": sol.condicion,
            "autorizada": True if pedido.estado == "Autorizado" else (
                False if pedido.estado == "Rechazado" else None
            ),
        }
        for sol in solicitudes_ordenadas
    ]
    return data


@pedidos_api_bp.get("/")
@jwt_check("pedido_index")
def listar_pedidos():
    """Lista los pedidos actuales e históricos del sector del Jefe de Servicio."""
    try:
        filtros = filtro_pedidos_schema.load(request.args.to_dict())
    except ValidationError as err:
        raise BadRequestError(err.messages)

    _, sector_id = _obtener_contexto_usuario()
    paginado = pedido_service.listar_pedidos_sector(sector_id=sector_id, filtros=filtros)

    return jsonify(
        {
            "data": [_serializar_resumen_pedido(p) for p in paginado["items"]],
            "total": paginado["total"],
            "page": paginado["page"],
            "pages": paginado["pages"],
            "elementos_por_pagina": paginado["elementos_por_pagina"],
        }
    ), 200


@pedidos_api_bp.post("/")
@jwt_check("pedido_create")
def crear_pedido():
    """Registra uno o múltiples pedidos para el sector del usuario autenticado."""
    json_data = request.get_json(silent=True)
    if not json_data:
        raise BadRequestError({"error": "No se proveyeron datos JSON."})

    try:
        data = crear_pedido_schema.load(json_data)
    except ValidationError as err:
        raise BadRequestError(err.messages)

    usuario_id, sector_id = _obtener_contexto_usuario()
    pedidos = pedido_service.crear_pedidos(
        data=data, usuario_id=usuario_id, sector_id=sector_id
    )

    return jsonify(
        {
            "mensaje": f"Se registraron {len(pedidos)} pedido(s) correctamente.",
            "pedidos": [_serializar_detalle_pedido(p) for p in pedidos],
        }
    ), 201


@pedidos_api_bp.get("/<int:request_id>")
@jwt_check("pedido_show")
def obtener_pedido(request_id: int):
    """Obtiene el detalle completo de un pedido del sector."""
    _, sector_id = _obtener_contexto_usuario()
    pedido = pedido_service.obtener_pedido_detalle(
        request_id=request_id, sector_id=sector_id
    )
    return jsonify(_serializar_detalle_pedido(pedido)), 200


@pedidos_api_bp.put("/<int:request_id>")
@jwt_check("pedido_update")
def modificar_pedido(request_id: int):
    """Modifica un pedido existente en estado Confirmado antes del horario de corte."""
    json_data = request.get_json(silent=True)
    if not json_data:
        raise BadRequestError({"error": "No se proveyeron datos JSON."})

    try:
        data = actualizar_pedido_schema.load(json_data)
    except ValidationError as err:
        raise BadRequestError(err.messages)

    _, sector_id = _obtener_contexto_usuario()
    pedido = pedido_service.actualizar_pedido(
        request_id=request_id, data=data, sector_id=sector_id
    )
    return jsonify(_serializar_detalle_pedido(pedido)), 200


@pedidos_api_bp.delete("/<int:request_id>")
@jwt_check("pedido_destroy")
def eliminar_pedido(request_id: int):
    """Elimina un pedido en estado Confirmado antes de su horario de corte."""
    _, sector_id = _obtener_contexto_usuario()
    pedido_service.eliminar_pedido(request_id=request_id, sector_id=sector_id)
    return jsonify({"mensaje": "Pedido eliminado correctamente."}), 200