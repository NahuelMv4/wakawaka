from flask import Blueprint, jsonify
from src.core.services.tipo_comida_service import list_tipos_comida
from src.web.helpers.api_auth import jwt_check

tipo_comida_bp = Blueprint(
    "api_tipos_comida",
    __name__,
    url_prefix="/api/tipos-comida"
)


@tipo_comida_bp.get("/")
@jwt_check("summary_requests")
def obtener_tipos_comida():
    tipos_comida = list_tipos_comida()

    return jsonify({
        "data": [
            {
                "id": tipo.id,
                "nombre": tipo.nombre.value,
                "hora_inicio": tipo.hora_inicio.isoformat(),
                "hora_fin": tipo.hora_fin.isoformat()
            }
            for tipo in tipos_comida
        ]
    }), 200