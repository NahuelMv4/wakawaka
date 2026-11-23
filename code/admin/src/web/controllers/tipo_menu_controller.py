from flask import Blueprint, jsonify

from src.core.services.tipo_menu_service import list_tipo_menu
from src.web.helpers.api_auth import jwt_check


tipo_menu_bp = Blueprint(
    "api_tipos_menu",
    __name__,
    url_prefix="/api/menu-types"
)


@tipo_menu_bp.get("/")
@jwt_check("summary_requests")
def obtener_tipos_menu():
    tipos_menu = list_tipo_menu()

    return jsonify({
        "data": [
            {
                "id": tipo.id,
                "nombre": tipo.nombre.value
            }
            for tipo in tipos_menu
        ]
    }), 200