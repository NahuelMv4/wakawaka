from src.web.helpers.auth import check, login_required
from flask import Blueprint, flash, redirect, render_template, request, url_for
from marshmallow import ValidationError
from src.core.errores.custom_errors import ConflictError

from src.core.errores.custom_errors import AppError
from src.core.services import sector_service, usuario_service
from src.web.schemas.sector_schema import sector_schema

priv_sector_bp = Blueprint("sectores", __name__, url_prefix="/sectores")

@priv_sector_bp.get("/")
@login_required
@check("sector_index")
def listar():
  nombre = request.args.get("nombre", "").strip()
  estado = request.args.get("estado", "")
  orden = request.args.get("orden", "nombre")
  descendente = request.args.get("dir") == "desc"
  pagina = request.args.get("pagina", 1, type=int)
  jefe_servicio_id = request.args.get("jefe_servicio_id", "")

  activo = None
  if estado == "activo":
    activo = True
  elif estado == "inactivo":
    activo = False

  usuario_id = int(jefe_servicio_id) if jefe_servicio_id.isdigit() else None

  resultado = sector_service.funcionalidad_busqueda(
    nombre=nombre,
    activo=activo,
    usuario_id=usuario_id,
    orden=orden,
    descendente=descendente,
    pagina=pagina,
  )
  jefes = usuario_service.listar_jefes_de_servicio()
  filtros = {
    "nombre": nombre,
    "estado": estado,
    "orden": orden,
    "dir": "desc" if descendente else "asc",
    "jefe_servicio_id": jefe_servicio_id,
  }
  return render_template("sector/sector.html", **resultado, jefes=jefes, filtros=filtros)


@priv_sector_bp.get("/<int:sector_id>/editar")
@login_required
@check("sector_update")
def editar(sector_id):
  sector = sector_service.read_sector(sector_id)
  if sector is None:
    flash("Sector no encontrado", "error")
    return redirect(url_for("sectores.listar"))
  return render_template("sector/sector_form.html", sector=sector)

@priv_sector_bp.get("/nuevo")
@login_required
def nuevo():
    return render_template("sector/sector_nuevo.html")


@priv_sector_bp.post("/nuevo")
@login_required
@check("sector_create")
def crear():
  try:
    datos = sector_schema.load(request.form.to_dict())
    sector_service.create_sector(**datos)
  except ValidationError as err:
    flash(str(err.messages), "error")
    return render_template("sector/sector_nuevo.html"), 400
  except AppError as err:
    flash(err.message, "error")
    return render_template("sector/sector_nuevo.html"), err.status_code

  flash("Sector creado", "success")
  return redirect(url_for("sectores.listar"))


@priv_sector_bp.post("/<int:sector_id>/desactivar")
@login_required
@check("sector_deactivate")
def desactivar(sector_id):
    try:
        sector = sector_service.delete_sector(sector_id)
    except ConflictError as err:
        flash(str(err), "warning")
        return redirect(url_for("sectores.listar"))

    if sector is None:
        flash("Sector no encontrado", "error")
    else:
        flash("Sector desactivado", "success")

    return redirect(url_for("sectores.listar"))


@priv_sector_bp.post("/<int:sector_id>/reactivar")
@login_required
@check("sector_activate")
def reactivar(sector_id):
  sector = sector_service.update_sector(sector_id, activo=True)
  if sector is None:
    flash("Sector no encontrado", "error")
  else:
    flash("Sector reactivado", "success")
  return redirect(url_for("sectores.listar"))

@priv_sector_bp.post("/<int:sector_id>/editar")
@login_required
@check("sector_update")
def actualizar(sector_id):
  sector = sector_service.read_sector(sector_id)
  if sector is None:
    flash("Sector no encontrado", "error")
    return redirect(url_for("sectores.listar"))

  try:
    datos = sector_schema.load(request.form.to_dict())
    sector_service.update_sector(sector_id, **datos)
  except ValidationError as err:
    flash(str(err.messages), "error")
    return render_template("sector/sector_form.html", sector=sector), 400
  except AppError as err:
    flash(err.message, "error")
    return render_template("sector/sector_form.html", sector=sector), err.status_code

  flash("Sector actualizado", "success")
  return redirect(url_for("sectores.listar"))