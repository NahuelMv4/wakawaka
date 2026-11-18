from src.web.helpers.auth import check, login_required
from flask import Blueprint, jsonify, request
from src.core.services import config_sistema_service
from src.web.schemas import config_sistema_schema

configuracion_bp = Blueprint("configuracion_api", __name__, url_prefix="/api/configuracion")


@configuracion_bp.get("/")
@login_required
def get_configuracion():
    configuracion = config_sistema_service.get_configuracion()
    if not configuracion:
        return jsonify({"error": "No se encontró configuración registrada."}), 404

    return jsonify(config_sistema_schema.dump(configuracion)), 200


@configuracion_bp.post("/mantenimiento/activar")
def activar_mantenimiento():
    data = request.get_json(silent=True) or {} 
    mensaje = data.get("mensaje", "El sistema se encuentra en mantenimiento programado.")
    usuario_id = data.get("usuario_id")

    configuracion = config_sistema_service.activar_mantenimiento(mensaje=mensaje, usuario_id=usuario_id)

    return jsonify({
        "mensaje": "Modo mantenimiento activado exitosamente.",
        "configuracion": config_sistema_schema.dump(configuracion)
    }), 200


@configuracion_bp.post("/mantenimiento/desactivar")
@login_required
def desactivar_mantenimiento():
    data = request.get_json(silent=True) or {}
    usuario_id = data.get("usuario_id")

    configuracion = config_sistema_service.desactivar_mantenimiento(usuario_id=usuario_id)
    if not configuracion:
        return jsonify({"error": "No existe una configuración para actualizar."}), 404

    return jsonify({
        "mensaje": "Modo mantenimiento desactivado exitosamente.",
        "configuracion": config_sistema_schema.dump(configuracion)
    }), 200


@configuracion_bp.patch("/mantenimiento/toggle")
@login_required
def toggle_mantenimiento():
    data = request.get_json(silent=True) or {}
    mensaje = data.get("mensaje", "El sistema se encuentra en mantenimiento.")
    usuario_id = data.get("usuario_id")

    configuracion = config_sistema_service.toggle_mantenimiento(mensaje=mensaje, usuario_id=usuario_id)

    return jsonify({
        "mensaje": f"Mantenimiento {'activado' if configuracion.mantenimiento else 'desactivado'}.",
        "configuracion": config_sistema_schema.dump(configuracion)
    }), 200