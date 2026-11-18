from functools import wraps

from flask import jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from src.core.services import usuario_service


def jwt_check(permission):
  def decorator(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
      verify_jwt_in_request()
      usuario_id = int(get_jwt_identity())
      permissions = usuario_service.obtener_permisos_usuario(usuario_id)
      codigos = [p.value if hasattr(p, "value") else p for p in permissions]
      if permission not in codigos:
        return jsonify({"error": "No tienes permiso para esta acción"}), 403
      return f(*args, **kwargs)

    return decorated_function

  return decorator