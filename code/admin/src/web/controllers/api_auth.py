from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from src.core.services import auth_service, usuario_service

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