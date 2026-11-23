from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity
from marshmallow import ValidationError

from src.core.enums import RolEnum
from src.core.errores.custom_errors import BadRequestError, ForbiddenError
from src.core.services import cupo_service, usuario_service
from src.web.helpers.api_auth import jwt_check
from src.web.schemas.cupo_schema import cupo_schema, cupos_schema

# Inicializa el blueprint para agrupar todas las rutas bajo el prefijo comun de la API
cupos_api_bp = Blueprint("cupos_api", __name__, url_prefix="/api/quotas")


def _obtener_usuario_jwt():
    """Obtiene la instancia del usuario autenticado mediante el token JWT."""
    usuario_id = int(get_jwt_identity())
    return usuario_service.obtener(usuario_id)


@cupos_api_bp.route("/", methods=["GET"])
@jwt_check("cupo_index")
def listar_cupos():
    """Listar cupos registrados con filtros y paginacion."""
    
    # Extrae los parametros de busqueda y paginacion enviados en la URL
    sector_id = request.args.get("sector_id", type=int)
    tipo_comida_id = request.args.get("tipo_comida_id", type=int)
    page = request.args.get("page", 1, type=int)

    usuario = _obtener_usuario_jwt()

    if usuario and usuario.rol and usuario.rol.nombre == RolEnum.JEFE_SERVICIO.value:
        user_sector = usuario.sector_id
        if sector_id and sector_id != user_sector:
            raise ForbiddenError("No tiene permiso para consultar cupos de otros sectores.")
        sector_id = user_sector

    # Delega la consulta a la base de datos a traves del servicio
    cupos_paginados = cupo_service.get_cupos(
        sector_id=sector_id,
        tipo_comida_id=tipo_comida_id,
        page=page,
    )

    # Retorna un diccionario serializado usando Marshmallow y datos de paginacion
    return jsonify({
        "data": cupos_schema.dump(cupos_paginados["items"]),
        "total": cupos_paginados["total"],
        "page": cupos_paginados["page"],
        "pages": cupos_paginados["pages"],
        "elementos_por_pagina": cupos_paginados.get("elementos_por_pagina")
    }), 200


@cupos_api_bp.route("/<int:quota_id>", methods=["GET"])
@jwt_check("cupo_show")
def obtener_cupo(quota_id: int):
    """Obtener el detalle de un cupo por su ID."""
    
    # Delega la busqueda al servicio (el servicio levanta el error 404 si no existe)
    cupo = cupo_service.get_cupo_by_id(quota_id)
    usuario = _obtener_usuario_jwt()

    # Comprueba que el cupo consultado pertenezca al sector del Jefe de Servicio
    if usuario and usuario.rol and usuario.rol.nombre == RolEnum.JEFE_SERVICIO.value:
        if cupo.sector_id != usuario.sector_id:
            raise ForbiddenError("No tiene permiso para consultar cupos de otros sectores.")

    # Serializa la instancia a JSON y responde con estado 200 OK
    return jsonify(cupo_schema.dump(cupo)), 200


@cupos_api_bp.route("/", methods=["POST"])
@jwt_check("cupo_create")
def crear_cupo():
    """Crear un nuevo cupo. Exclusivo para rol 'Servicio de Alimentacion'."""
    
    # Recupera el cuerpo de la peticion
    json_data = request.get_json()
    if not json_data:
        raise BadRequestError({"error": "No se proveyeron datos JSON"})

    # Utiliza Marshmallow para validar que el formato sea correcto y no falten datos
    try:
        data = cupo_schema.load(json_data)
    except ValidationError as err:
        raise BadRequestError(err.messages)

    # Pasa los datos validados al cupo_service para aplicar reglas y persistir
    nuevo_cupo = cupo_service.create_cupo(data)

    # Retorna el registro creado y el codigo HTTP 201 (Created)
    return jsonify(cupo_schema.dump(nuevo_cupo)), 201


@cupos_api_bp.route("/<int:quota_id>", methods=["PUT"])
@jwt_check("cupo_update")
def modificar_cupo(quota_id: int):
    """Modificar la cantidad de comensales de un cupo."""

    json_data = request.get_json()
    if not json_data:
        raise BadRequestError({"error": "No se proveyeron datos JSON"})

    # Valida parcialmente los datos (permite enviar solo la cantidad gracias a partial=True)
    try:
        data = cupo_schema.load(json_data, partial=True)
    except ValidationError as err:
        raise BadRequestError(err.messages)

    # Actualiza el registro a traves del servicio usando el ID de la ruta
    cupo_actualizado = cupo_service.update_cupo(quota_id, **data)

    # Responde con los datos actualizados tras la transaccion
    return jsonify(cupo_schema.dump(cupo_actualizado)), 200


@cupos_api_bp.route("/<int:quota_id>", methods=["DELETE"])
@jwt_check("cupo_destroy")
def delete_cupo(quota_id: int):
    """Eliminar un cupo de la base de datos."""
    
    # Delega la eliminacion al servicio
    cupo_service.eliminar_cupo(quota_id)
    
    return jsonify({"mensaje": "Cupo eliminado correctamente"}), 200