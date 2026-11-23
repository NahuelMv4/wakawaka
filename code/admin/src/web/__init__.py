from typing import Any

from flask import Flask, jsonify, render_template, request
from flask_jwt_extended import JWTManager
from flask_session import Session
from src.core import database, seeds
from src.core.database import db
from src.core.errores.custom_errors import AppError
from src.web.config import config
from src.web.controllers.api_auth import api_auth_bp
from src.web.controllers.auth import auth_bp
from src.web.controllers.config_sistema_controller import configuracion_bp
from src.web.controllers.cupos_api import cupos_api_bp
from src.web.controllers.pedidos_controller import pedidos_api_bp
from src.web.controllers.personal_controller import personal_bp
from src.web.controllers.private_config_sistema_controller import priv_configuracion_bp
from src.web.controllers.private_personal_controller import priv_personal_bp
from src.web.controllers.autorizacion_api import autorizacion_api_bp
from src.web.controllers.resumenes_controller import resumenes_api_bp
from src.web.controllers.private_sector_controller import priv_sector_bp
from src.web.controllers.sector_controller import bp_sector
from src.web.controllers.tipo_comida_controller import tipo_comida_bp
from src.web.controllers.tipo_menu_controller import tipo_menu_bp
from src.web.controllers.usuario_controller import bp as usuarios_bp
from src.web.controllers.api_authorized_meals import api_comedor_bp
from src.web.controllers.solicitud_comida_api import solicitud_comida_bp
from src.web.handlers import errores
from src.web.helpers.auth import check_permission, is_authenticated
from src.web.middlewares.mantenimiento import register_mantenimiento_middleware

def create_app(env: str = "development", static_folder: str = "../../static") -> Flask:
    app = Flask(__name__, static_folder=static_folder)
    app.config.from_object(config[env])

    JWTManager(app)

    @app.after_request
    def add_cors_headers(response):
        if request.path.startswith("/api/"):
            allowed_origins = {
                "http://localhost:5173",
                "https://grupo32.proyecto2026.linti.unlp.edu.ar",
            }
            origin = request.headers.get("Origin")
            if origin in allowed_origins:
                response.headers["Access-Control-Allow-Origin"] = origin
                response.headers["Access-Control-Allow-Credentials"] = "true"
                response.headers["Vary"] = "Origin"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
        return response

    database.init_app(app)
    app.jinja_env.globals.update(is_authenticated=is_authenticated)
    app.jinja_env.globals.update(check_permission=check_permission)

    app.config['SESSION_TYPE'] = 'filesystem'
    Session(app)

    register_mantenimiento_middleware(app)

    @app.route("/")
    def home() -> str:
        return render_template('home.html')
    
    # --         Blueprints         --
    app.register_blueprint(personal_bp)  
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(priv_personal_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(bp_sector)
    app.register_blueprint(cupos_api_bp)
    app.register_blueprint(pedidos_api_bp)
    app.register_blueprint(priv_sector_bp)
    app.register_blueprint(configuracion_bp)
    app.register_blueprint(priv_configuracion_bp)
    app.register_blueprint(api_auth_bp)
    app.register_blueprint(autorizacion_api_bp)
    app.register_blueprint(solicitud_comida_bp)
    app.register_blueprint(resumenes_api_bp)
    app.register_blueprint(tipo_comida_bp)
    app.register_blueprint(tipo_menu_bp)
    app.register_blueprint(api_comedor_bp)

    #--   Manejador de errores REST   --
    @app.errorhandler(AppError)
    def handle_app_error(error: AppError) -> tuple[Any, int]:
        return jsonify({"error": error.message}), error.status_code
    
    #--         Errores HTML        --
    app.register_error_handler(401, errores.unauthorized)  
    app.register_error_handler(403, errores.forbidden)
    app.register_error_handler(404, errores.not_found)  
    app.register_error_handler(500, errores.internal_server_error)

    #--         Comandos        --
    @app.cli.command("reset-db")
    def reset_db() -> None:
        database.reset_db()

    @app.cli.command("seed-db")
    def seed_db() -> None:
        seeds.run()

    @app.teardown_appcontext
    def shutdown_session(exception: Exception | None = None) -> None:
        if exception:
            db.session.rollback()
        db.session.close()
    return app