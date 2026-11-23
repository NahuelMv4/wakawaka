from datetime import date, datetime
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.core.services import comedor_service
from src.web.controllers.api_authorized_meals import api_comedor_bp

@api_comedor_bp.get("/daily-summary")
#@jwt_required()
def get_daily_summary():
    resumen = comedor_service.obtener_resumen_dia(fecha=date.today())
    return jsonify(resumen), 200

@api_comedor_bp.post("/deliveries")
@jwt_required()
def create_delivery():
    data = request.get_json(silent=True) or {}

    personas_ids = data.get("personas") or []
    tipo_comida = data.get("tipo_comida")
    responsable_id = data.get("responsable_id")
    tercero = data.get("responsable_tercero")

    if not personas_ids or not tipo_comida:
        return jsonify({"message": "Faltan datos obligatorios (personas o tipo_comida)."}), 400

    usuario_id = get_jwt_identity()

    try:
        resultado = comedor_service.registrar_entrega(
            personas_ids=personas_ids,
            tipo_comida=tipo_comida,
            fecha=date.today(),
            usuario_id=usuario_id,
            responsable_id=responsable_id,
            tercero=tercero,
        )
        return jsonify(resultado), 201
    except ValueError as err:
        return jsonify({"message": str(err)}), 409
    except Exception as err:
        return jsonify({"message": f"Error interno: {str(err)}"}), 500