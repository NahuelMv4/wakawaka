from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from src.core.enums import RolEnum
from src.core.services import auth_service, usuario_service

ROLES_PERMITIDOS_PORTAL = {
    RolEnum.JEFE_SERVICIO,
    RolEnum.SERVICIO_ALIMENTACION,
    RolEnum.SECTOR_COMEDOR,
}

api_auth_bp = Blueprint("api_auth", __name__, url_prefix="/api/auth")


@api_auth_bp.route("/login", methods=["POST"])
def login():
  data = request.get_json(silent=True) or {}
  email = data.get("email")
  password = data.get("password")

  if not email or not password:
    return jsonify({"error": "Debe ingresar email y contraseña"}), 400
  usuario = auth_service.autenticar(email, password)
  if usuario is None:
    return jsonify({"error": "Credenciales inválidas o usuario inactivo"}), 401
  access_token = create_access_token(identity=str(usuario.id))
  return jsonify({"access_token": access_token}), 200


@api_auth_bp.route("/logout", methods=["POST"])
def logout():
  return jsonify({"message": "Sesión cerrada"}), 200


@api_auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
  usuario_id = int(get_jwt_identity())
  usuario = usuario_service.obtener_usuario_activo(usuario_id)

  if usuario is None:
    return jsonify({"error": "Usuario no encontrado o inactivo"}), 401
  return (
      jsonify({
          "id": usuario.id,
          "nombre": usuario.nombre,
          "apellido": usuario.apellido,
          "email": usuario.email,
          "rol": usuario.rol.nombre.value,
          "sector_id": usuario.sector_id,
          "permisos": [p.codigo.value for p in usuario.rol.permisos],
      }),
      200,
  )

@api_auth_bp.route("/google", methods=["POST"])
def login_google():
  data = request.get_json(silent=True) or {}
  token_google = data.get("credential")

  if not token_google:
    return jsonify({"error": "No se recibió el token de Google"}), 400

  client_id = current_app.config.get("GOOGLE_CLIENT_ID")
  try:
    idinfo = id_token.verify_oauth2_token(token_google, google_requests.Request(), client_id)
  except ValueError:
    return jsonify({"error": "Token de Google inválido o expirado"}), 401

  if not idinfo.get("email_verified"):
    return jsonify({"error": "El correo de Google no está verificado"}), 401

  email = idinfo.get("email")
  usuario = usuario_service.obtener_usuario_por_email(email)

  if usuario is None or not usuario.activo:
    return (
        jsonify({
            "error": (
                "Tu cuenta no está registrada o activa en el sistema. "
                "Debes solicitar el alta al Administrador."
            )
        }),
        403,
    )

  if usuario.rol.nombre.value not in ROLES_PERMITIDOS_PORTAL:
    return (
        jsonify({
            "error": (
                "Tu rol no tiene acceso a este portal. "
                "Debes solicitar el alta al Administrador."
            )
        }),
        403,
    )

  access_token = create_access_token(identity=str(usuario.id))
  return jsonify({"access_token": access_token}), 200