from datetime import datetime
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


@priv_configuracion_bp.post("/admin/ajustes/<int:config_id>")
@login_required
@check("config_index")
def actualizar_ajustes(config_id):
    paginacion_raw = request.form.get("paginacion", "").strip()
    horario_corte_raw = request.form.get("horario_corte", "").strip()

    try:
        paginacion = int(paginacion_raw)
        if paginacion < 1:
            raise ValueError()
        horario_corte = datetime.strptime(horario_corte_raw, "%H:%M").time()
    except ValueError:
        flash("Paginación debe ser un número entero mayor a 0 y el horario de corte debe tener formato HH:MM.", "danger")
        return redirect(url_for("configuracion.listar"))

    actualizada = config_sistema_service.actualizar_parametros_generales(
        config_id=config_id,
        paginacion=paginacion,
        horario_corte=horario_corte,
        usuario_id=session.get("usuario_id"),
    )
    if not actualizada:
        flash("No se encontró la configuración del sistema.", "danger")
        return redirect(url_for("configuracion.listar"))

    flash("Ajustes generales actualizados correctamente.", "success")
    return redirect(url_for("configuracion.listar"))


@priv_configuracion_bp.post("/admin/mantenimiento/toggle/<int:config_id>")
@login_required
@check("config_index")
def toggle_mantenimiento_por_id(config_id):
    accion = request.form.get("accion")
    usuario_id = session.get("usuario_id")

    if accion == "activar":
        mensaje = request.form.get("mensaje_mantenimiento", "").strip()
        if not mensaje:
            mensaje = "El sistema se encuentra en mantenimiento programado."
        config_sistema_service.activar_mantenimiento(
            mensaje=mensaje,
            usuario_id=usuario_id,
            config_id=config_id,
        )
        flash("El modo mantenimiento ha sido ACTIVADO.", "warning")

    elif accion == "desactivar":
        config_sistema_service.desactivar_mantenimiento(
            usuario_id=usuario_id,
            config_id=config_id,
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