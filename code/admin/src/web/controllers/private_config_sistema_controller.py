from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from src.web.helpers.auth import check, login_required
from src.core.services import config_sistema_service

priv_configuracion_bp = Blueprint("configuracion", __name__, url_prefix="/configuracion")


@priv_configuracion_bp.get("/admin/lista")
@login_required
@check("config_index")
def listar():
    configuraciones = config_sistema_service.get_all_configuraciones()
    return render_template("configuracion/listar_mantenimiento.html", configuraciones=configuraciones)


@priv_configuracion_bp.post("/admin/mantenimiento/toggle/<int:config_id>")
@login_required
@check("config_activate")
@check("config_deactivate")
def toggle_mantenimiento_por_id(config_id):
    accion = request.form.get("accion")
    usuario_id = session.get("usuario_id") 

    if accion == "activar":
        configuracion = config_sistema_service.activar_mantenimiento(mensaje= "", usuario_id=usuario_id)
        flash("El modo mantenimiento ha sido ACTIVADO.", "warning")

    elif accion == "desactivar":
        configuracion = config_sistema_service.desactivar_mantenimiento(
            usuario_id=usuario_id
        )
        flash("El modo mantenimiento ha sido DESACTIVADO.", "success")

    return redirect(url_for("configuracion.listar"))


@priv_configuracion_bp.get("/mantenimiento")
def vista_mantenimiento():
    configuracion = config_sistema_service.get_configuracion()
    mensaje = (
        configuracion.mensaje_mantenimiento 
        if configuracion and configuracion.mensaje_mantenimiento 
        else "El sistema se encuentra en mantenimiento programado."
    )
    return render_template("configuracion/mantenimiento.html", mensaje=mensaje), 503