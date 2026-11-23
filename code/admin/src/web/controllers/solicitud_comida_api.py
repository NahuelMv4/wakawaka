from flask import Blueprint, jsonify
from src.core.database import db
from src.core.services import solicitud_comida_service
from src.core.errores.custom_errors import NotFoundError
from src.core.models.solicitud_comida import SolicitudComida
from src.web.helpers.api_auth import jwt_check

solicitud_comida_bp = Blueprint(
    "solicitud_comida_api", __name__, url_prefix="/api/solicitudes-comida"
)


@solicitud_comida_bp.patch("/<int:solicitud_id>/autorizar")
@jwt_check("autorizacion_index")
def autorizar_solicitud_comida(solicitud_id: int):
    solicitud = solicitud_comida_service.autorizar_solicitud(
        solicitud_id=solicitud_id
    )
    return jsonify({
        "id": solicitud.id,
        "pedido_id": solicitud.pedido_id,
        "autorizada": solicitud.autorizada,
    }), 200