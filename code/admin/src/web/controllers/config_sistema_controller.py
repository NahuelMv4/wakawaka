from flask import Blueprint, jsonify
from src.core.services import config_sistema_service
from src.web.schemas.config_sistema_schema import configuracion_publica_schema

configuracion_bp = Blueprint("configuracion_api", __name__, url_prefix="/api/configuration")


@configuracion_bp.get("")
def get_configuration():
    datos = config_sistema_service.get_configuracion_publica()
    return jsonify(configuracion_publica_schema.dump(datos)), 200