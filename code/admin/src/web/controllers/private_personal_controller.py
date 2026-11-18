import logging

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from marshmallow import ValidationError

from src.core.errores.custom_errors import (
    BadRequestError,
    ConflictError,
    ForbiddenError,
    NotFoundError,
)
from src.core.services import (
    personal_service,
    sector_service,
    tipo_menu_service,
    tipo_personal_service,
)
from src.web.helpers.auth import check, login_required
from src.web.schemas.personal_schema import personal_filter_schema

logger = logging.getLogger(__name__)

priv_personal_bp = Blueprint(
    "priv_personal", __name__, url_prefix="/private/personnel"
)


@priv_personal_bp.get("/")
@login_required
@check("personal_index")
def listar():
    """Muestra el listado de personal aplicando los filtros de búsqueda y paginación.

    Valida los parámetros de consulta recibidos mediante el esquema de filtrado.
    En caso de error de validación, lanza un BadRequestError.

    Returns:
        Response: Renderiza la plantilla del listado de personal con los registros obtenidos.
    """    
    try:
        filters = personal_filter_schema.load(request.args.to_dict())
    except ValidationError as err:
        logger.warning("Error de validación en filtros de personal: %s", err.messages)
        raise BadRequestError(err.messages)

    personal_list = personal_service.list_personal(filters)
    logger.debug("Listado de personal consultado correctamente. Total registros: %d", len(personal_list))
    return render_template("personal/personal.html", personal=personal_list)


@priv_personal_bp.route("/crear", methods=["GET", "POST"])
@login_required
@check("personal_create")
def crear():
    """Gestiona la creación de un nuevo miembro del personal.

    - GET: Renderiza el formulario con los tipos de personal, sectores y menús disponibles.
    - POST: Procesa los datos del formulario, ejecuta el servicio de creación y redirige al listado.
    """
    if request.method == "POST":
        tipo_personal_id = request.form.get("tipo_personal_id")
        sector_id = request.form.get("sector_id")
        tipo_menu_id = request.form.get("tipo_menu_id")

        data = {
            "dni": request.form.get("dni"),
            "nombre": request.form.get("nombre"),
            "apellido": request.form.get("apellido"),
            "tipo_personal_id": int(tipo_personal_id) if tipo_personal_id else None,
            "sector_id": int(sector_id) if sector_id else None,
            "tipo_menu_id": int(tipo_menu_id) if tipo_menu_id else None,
        }

        try:
            personal_service.create_personal(data)
            logger.info("Miembro del personal creado exitosamente con DNI: %s", data.get("dni"))
            flash("Miembro del personal creado exitosamente.", "success")
            return redirect(url_for("priv_personal.listar"))
        except ConflictError as e:
            logger.warning("Conflicto al crear personal (DNI: %s): %s", data.get("dni"), e)
            flash(str(e), "error")
        except (ForbiddenError, BadRequestError) as e:
            logger.warning("Error de permisos o validación al crear personal: %s", e)
            flash(str(e), "error")
        except Exception as e:
            logger.exception("Error inesperado al crear el registro de personal: %s", e)
            flash("Ocurrió un error inesperado al crear el registro.", "error")

    tipos_personal = tipo_personal_service.list_tipo_personal() 
    sectores = sector_service.list_sectores() 
    tipos_menu = tipo_menu_service.list_tipo_menu() 

    return render_template(
        "personal/personal_crear.html",
        tipos_personal=tipos_personal,
        sectores=sectores,
        tipos_menu=tipos_menu,
    )


@priv_personal_bp.route("/editar/<int:id>", methods=["GET", "POST"])
@login_required
@check("personal_update")
def editar(id: int):
    """Gestiona la modificación de los datos de un miembro del personal existente.

    Args:
        id (int): ID único del miembro del personal a editar.

    Returns:
        Response: Renderiza el formulario de edición cargado con los datos o redirige tras guardar.
    """
    try:
        persona = personal_service.find_personal_by_id(id)
    except NotFoundError as e:
        logger.warning("Intento de editar un miembro del personal inexistente (ID: %d): %s", id, e)
        flash(str(e), "error")
        return redirect(url_for("priv_personal.listar"))

    if request.method == "POST":
        tipo_personal_id = request.form.get("tipo_personal_id")
        sector_id = request.form.get("sector_id")
        tipo_menu_id = request.form.get("tipo_menu_id")

        kwargs = {
            "nombre": request.form.get("nombre"),
            "apellido": request.form.get("apellido"),
            "dni": request.form.get("dni"),
            "tipo_personal_id": int(tipo_personal_id) if tipo_personal_id else None,
            "sector_id": int(sector_id) if sector_id else None,
            "tipo_menu_id": int(tipo_menu_id) if tipo_menu_id else None,
        }

        try:
            personal_service.update_personal(id, kwargs)
            logger.info("Personal con ID %d actualizado correctamente.", id)
            flash("Personal actualizado correctamente.", "success")
            return redirect(url_for("priv_personal.listar"))
        except (ConflictError, ForbiddenError, BadRequestError) as e:
            logger.warning("Error de validación/permisos al actualizar personal con ID %d: %s", id, e)
            flash(str(e), "error")
        except Exception as e:
            logger.exception("Error inesperado al actualizar el personal con ID %d: %s", id, e)
            flash("Ocurrió un error al actualizar los datos.", "error")

    tipos_personal = tipo_personal_service.list_tipo_personal()
    sectores = sector_service.list_sectores()
    tipos_menu = tipo_menu_service.list_tipo_menu()

    return render_template(
        "personal/personal_editar.html",
        persona=persona,
        tipos_personal=tipos_personal,
        sectores=sectores,
        tipos_menu=tipos_menu,
    )


@priv_personal_bp.post("/eliminar/<int:id>")
@login_required
@check("personal_destroy")
def eliminar(id: int):
    """Elimina físicamente o marca como inactivo a un miembro del personal según su historial.

    Args:
        id (int): ID único del miembro del personal a eliminar o desactivar.

    Returns:
        Response: Redirige al listado de personal con un mensaje flash informando el resultado.
    """
    try:
        personal_service.delete_personal(id)
        logger.info("Miembro del personal con ID %d eliminado/desactivado con éxito.", id)
        flash("La operación se realizó con éxito.", "success")
    except NotFoundError as e:
        logger.warning("Intento de eliminar un personal inexistente (ID: %d): %s", id, e)
        flash(str(e), "error")
    except ForbiddenError as e:
        logger.warning("Intento no autorizado de eliminar personal (ID: %d): %s", id, e)
        flash(str(e), "error")
    except Exception as e:
        logger.exception("Error inesperado al eliminar el personal con ID %d: %s", id, e)
        flash("No se pudo completar la operación.", "error")

    return redirect(url_for("priv_personal.listar"))

@priv_personal_bp.route("/importar", methods=["GET", "POST"])
@login_required
@check("personal_csv")
def importar_csv():
    """Gestiona la importación masiva de personal a través de un archivo CSV."""
    if request.method == "POST":
        if "archivo_csv" not in request.files:
            flash("No se ha seleccionado ningún archivo.", "error")
            return redirect(request.url)
        
        file = request.files["archivo_csv"]
        
        if file.filename == "":
            flash("El archivo seleccionado no tiene un nombre válido.", "error")
            return redirect(request.url)
        
        if not file.filename.lower().endswith(".csv"):
            flash("El archivo debe tener formato CSV (.csv).", "error")
            return redirect(request.url)

        try:
            resultado = personal_service.import_personal_csv(file.stream)
            flash(f"Importación completada. Procesados: {resultado['procesados']}, Importados: {resultado['importados']}, Rechazados: {resultado['rechazados']}.", "success" if resultado['rechazados'] == 0 else "warning")
            
            return render_template("personal/personal_importar_resultado.html", resultado=resultado)
        
        except Exception as e:
            logger.exception("Error crítico al procesar la importación CSV: %s", e)
            flash("Ocurrió un error inesperado al procesar el archivo CSV.", "error")
            return redirect(url_for("priv_personal.listar"))

    return render_template("personal/personal_importar.html")