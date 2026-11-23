from datetime import date
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from src.core.services import comedor_service

api_comedor_bp = Blueprint("api_comedor", __name__, url_prefix="/api")

@api_comedor_bp.get("/health")
def health_check():
    return jsonify({"status": "ok"}), 200

@api_comedor_bp.get("/authorized-meals")
#@jwt_required("access")
def get_authorized_meals():
    dni = request.args.get("dni", "").strip()
    nya = request.args.get("nya", "").strip()
    sector_id = request.args.get("sector", type=int)
    tipo_comida = request.args.get("tipo_comida", "").strip().lower()

    if not any([dni, nya, sector_id, tipo_comida]):
        return jsonify({
            "message": "Debe enviar al menos un filtro (dni, nya, sector o tipo_comida)."
        }), 400
    
    resultados = comedor_service.consultar_comidas(
        fecha= date.today(),
        dni=dni or None,
        nya=nya or None,
        sector_id=sector_id,
        tipo_comida=tipo_comida or None,
    )
    return jsonify(resultados), 200
from . import api_deliveries