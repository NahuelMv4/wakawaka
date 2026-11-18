import csv
import io
import logging

from flask import session
from sqlalchemy import asc, desc, or_, select

from src.core.database import db
from src.core.enums import RolEnum, TipoPersonalEnum
from src.core.errores.custom_errors import (
    BadRequestError,
    ConflictError,
    ForbiddenError,
    NotFoundError,
)
from src.core.models.personal import Personal
from src.core.models.sector import Sector
from src.core.models.tipo_personal import TipoPersonal
from src.core.services import config_sistema_service

logger = logging.getLogger(__name__)

def popular_personal(**kwargs):
    """Se agregan datos de personal desde el seeder"""
    try:
        personal = Personal(**kwargs)
        db.session.add(personal)
        db.session.commit()
        logger.info("Personal populado exitosamente con DNI: %s", kwargs.get("dni"))
        return personal
    except Exception as e:
        db.session.rollback()
        logger.error("Error al popular personal con DNI %s: %s", kwargs.get("dni"), str(e))
        raise ConflictError("Ya existe personal con este DNI.")


def list_personal(filters: dict):
    """Obtiene una lista con todos los miembros del personal registrados en la base de datos.

    Returns:
        List[Personal]: Lista de instancias del modelo Personal.
    """
    stmt = select(Personal).join(Personal.tipo_personal)

    rol_actual = session.get("rol")
    sector_id = session.get("sector_id")

    if rol_actual == RolEnum.JEFE_SERVICIO.value:
        stmt = stmt.where(
            or_(
                (Personal.sector_id == sector_id) & (TipoPersonal.nombre == TipoPersonalEnum.FIJO.value),
                TipoPersonal.nombre == TipoPersonalEnum.RESIDENTE.value
            )
        )

    if filters.get("sector"):
        stmt = stmt.join(Personal.sector).where(Sector.nombre.ilike(f"%{filters['sector']}%"))

    if filters.get("tipo_personal"):
        stmt = stmt.where(TipoPersonal.nombre.ilike(f"%{filters['tipo_personal']}%"))

    if filters.get("dni"):
        stmt = stmt.where(Personal.dni.ilike(f"%{filters['dni']}%"))

    if filters.get("nombre"):
        stmt = stmt.where(Personal.nombre.ilike(f"%{filters['nombre']}%"))

    if filters.get("apellido"):
        stmt = stmt.where(Personal.apellido.ilike(f"%{filters['apellido']}%"))

    if filters.get("tipo_personal_id"):
        stmt = stmt.where(Personal.tipo_personal_id == filters["tipo_personal_id"])

    activo = filters.get("activo", True) 
    stmt = stmt.where(Personal.activo == activo)

    stmt = _apply_sorting(stmt, filters)

    cant_elementos = config_sistema_service.get_paginacion()
    page = filters.get("page", 1)
    per_page = min(filters.get("per_page", cant_elementos), cant_elementos)
    
    stmt = stmt.offset((page - 1) * per_page).limit(per_page)
    
    resultados = db.session.execute(stmt).scalars().all()
    logger.debug("Listado de personal obtenido. Filtros aplicados: %s. Total resultados: %d", filters, len(resultados))
    return resultados

def _apply_sorting(stmt, filters: dict):
    """Aplica el criterio de ordenamiento a la sentencia SQL según los filtros."""
    sort_mapping = {
        "dni": Personal.dni,
        "nombre": Personal.nombre,
        "apellido": Personal.apellido,
        "creado_en": Personal.creado_en,
    }

    sort_by = filters.get("sort_by")
    order = filters.get("order", "asc")

    if sort_by in sort_mapping:
        column = sort_mapping[sort_by]
        if order.lower() == "desc":
            return stmt.order_by(desc(column))
        else:
            return stmt.order_by(asc(column))
    
    return stmt.order_by(asc(Personal.apellido))


def find_personal_by_id(personal_id: int):
    """Busca y retorna un miembro del personal según su ID único.

    Args:
        personal_id (int): ID del miembro del personal a buscar.

    Returns:
        Personal: La instancia del modelo Personal encontrada.

    Raises:
        NotFoundError: Si no existe ningún miembro del personal con el ID especificado[cite: 20].
    """
    personal = db.session.get(Personal, personal_id)
    if not personal:
        logger.warning("Intento de búsqueda fallido: Personal con ID %d no encontrado.", personal_id)
        raise NotFoundError("Miembro del personal no encontrado.")

    rol_actual = session.get("rol")
    sector_id = session.get("sector_id")

    if rol_actual == RolEnum.JEFE_SERVICIO.value:
        es_mismo_sector = personal.sector_id == sector_id
        es_residente = personal.tipo_personal and personal.tipo_personal.nombre == TipoPersonalEnum.RESIDENTE

        if not (es_mismo_sector or es_residente):
            logger.warning("Acceso denegado (403): Jefe de Servicio (Sector ID: %s) intentó acceder al personal ID %d de otro sector.", sector_id, personal_id)
            raise ForbiddenError("No tiene permisos para acceder a personal de otro sector.")

    logger.debug("Personal con ID %d encontrado y autorizado correctamente.", personal_id)
    return personal


def create_personal(data: dict):
    """Registra un nuevo miembro del personal aplicando las reglas de negocio.

    Args:
        data (dict): Diccionario con los datos del personal 
        -> (nombre, apellido, dni, tipo_personal_id, tipo_menu_id, sector_id).

    Returns:
        Personal: La instancia del modelo Personal creada y guardada con éxito.
    """
    existe = db.session.execute(select(Personal).where(Personal.dni == data["dni"])).scalars().first()
    if existe:
        logger.warning("Conflicto al crear personal: Ya existe una persona con el DNI %s.", data["dni"])
        raise ConflictError("Ya existe una persona registrada con el mismo DNI.")

    tipo_personal = db.session.get(TipoPersonal, data.get("tipo_personal_id"))
    if not tipo_personal:
        logger.warning("Error de validación al crear personal: El tipo de personal ID %s no existe.", data.get("tipo_personal_id"))
        raise BadRequestError("El tipo de personal indicado no existe.")

    rol_actual = session.get("rol")
    sector_usuario = session.get("sector_id")

    if rol_actual == RolEnum.JEFE_SERVICIO.value:
        if tipo_personal.nombre == TipoPersonalEnum.RESIDENTE:
            logger.warning("Acceso denegado (403): Jefe de Servicio intentó crear un personal de tipo Residente.")
            raise ForbiddenError("Un Jefe de Servicio no puede crear personal de tipo Residente.")
        
        if tipo_personal.nombre == TipoPersonalEnum.FIJO:
            data["sector_id"] = sector_usuario
        else:
            data["sector_id"] = sector_usuario

    if tipo_personal.nombre == TipoPersonalEnum.RESIDENTE:
        data["sector_id"] = None

    data["activo"] = True

    try:
        personal = Personal(**data)
        db.session.add(personal)
        db.session.commit()
        logger.info("Personal creado exitosamente con ID %d y DNI %s.", personal.id, personal.dni)
        return personal
    except Exception as e:
        db.session.rollback()
        logger.exception("Error inesperado al crear el personal con DNI %s: %s", data.get("dni"), str(e))
        raise e

def update_personal(personal_id: int, data: dict):
    """Actualiza los datos de un miembro del personal aplicando las reglas de negocio.

    Args:
        personal_id (int): ID del miembro del personal a actualizar.
        data (dict): Diccionario con los datos a modificar.

    Returns:
        Personal: La instancia del modelo Personal actualizada y guardada con éxito.
    """
    personal = db.session.get(Personal, personal_id)
    if not personal:
        logger.warning("Intento de actualización fallido: Personal con ID %d no encontrado.", personal_id)
        raise NotFoundError("Miembro del personal no encontrado.")

    rol_actual = session.get("rol")
    sector_usuario = session.get("sector_id")

    if rol_actual == RolEnum.JEFE_SERVICIO.value:
        es_residente = personal.tipo_personal and personal.tipo_personal.nombre == TipoPersonalEnum.RESIDENTE
        distinto_sector = personal.sector_id != sector_usuario
        traslado_sector = "sector_id" in data and data["sector_id"] != sector_usuario

        if es_residente or distinto_sector or traslado_sector:
            logger.warning("Acceso denegado (403): Jefe de Servicio intentó modificar un residente o personal ajeno (ID: %d).", personal_id)
            raise ForbiddenError("Un Jefe de Servicio no puede modificar personal de tipo Residente o modificar personal de otro sector.")

    if "dni" in data and data["dni"] != personal.dni:
        existe = db.session.execute(
            select(Personal).where(Personal.dni == data["dni"], Personal.id != personal_id)
        ).scalars().first()
        if existe:
            logger.warning("Conflicto al actualizar personal ID %d: El DNI %s ya pertenece a otra persona.", personal_id, data["dni"])
            raise ConflictError("Ya existe otra persona registrada con el mismo DNI.")

    nuevo_tipo_personal_id = data.get("tipo_personal_id")
    if nuevo_tipo_personal_id and nuevo_tipo_personal_id != personal.tipo_personal_id:
        nuevo_tipo = db.session.get(TipoPersonal, nuevo_tipo_personal_id)
        if not nuevo_tipo:
            logger.warning("Error de validación al actualizar personal ID %d: El tipo de personal ID %s no existe.", personal_id, nuevo_tipo_personal_id)
            raise BadRequestError("El tipo de personal indicado no existe.")
        
        tipo_actual_nombre = personal.tipo_personal.nombre if personal.tipo_personal else None
        nuevo_tipo_nombre = nuevo_tipo.nombre

        if tipo_actual_nombre == TipoPersonalEnum.FIJO and nuevo_tipo_nombre == TipoPersonalEnum.RESIDENTE:
            if rol_actual == RolEnum.JEFE_SERVICIO.value:
                logger.warning("Acceso denegado (403): Jefe de Servicio intentó cambiar tipo a Residente en personal ID %d.", personal_id)
                raise ForbiddenError("Un Jefe de Servicio no puede cambiar el tipo de personal a Residente.")
            data["sector_id"] = None

        elif tipo_actual_nombre == TipoPersonalEnum.RESIDENTE and nuevo_tipo_nombre == TipoPersonalEnum.FIJO:
            sector_destino = data.get("sector_id") or personal.sector_id
            if not sector_destino:
                logger.warning("Error de validación al actualizar personal ID %d: Falta sector al pasar de Residente a Fijo.", personal_id)
                raise BadRequestError("Debe indicar obligatoriamente el sector al pasar de Residente a Personal Fijo.")
            if rol_actual == RolEnum.JEFE_SERVICIO.value and sector_destino != sector_usuario:
                logger.warning("Acceso denegado (403): Jefe de Servicio intentó asignar sector ajeno en personal ID %d.", personal_id)
                raise ForbiddenError("El sector indicado no corresponde al del Jefe de Servicio.")
            data["sector_id"] = sector_destino

    for key, value in data.items():
        setattr(personal, key, value)

    try:
        db.session.commit()
        logger.info("Personal con ID %d actualizado exitosamente.", personal_id)
        return personal
    except Exception as e:
        db.session.rollback()
        logger.exception("Error inesperado al actualizar el personal con ID %d: %s", personal_id, str(e))
        raise e


def delete_personal(personal_id: int):
    """Elimina físicamente o marca como inactivo a un miembro del personal
    según la existencia de registros históricos asociados y reglas de rol.

    Args:
        personal_id (int): ID del miembro del personal a eliminar/desactivar.

    Returns:
        dict: Mensaje de confirmación de la operación realizada.

    Raises:
        NotFoundError: Si no se encuentra un miembro del personal con el ID provisto.
        ForbiddenError: Si un Jefe de Servicio intenta operar sobre un residente o personal de otro sector.
    """
    personal = db.session.get(Personal, personal_id)
    if not personal:
        logger.warning("Intento de eliminación fallido: Personal con ID %d no encontrado.", personal_id)
        raise NotFoundError("Miembro del personal no encontrado.")

    rol_actual = session.get("rol")
    sector_usuario = session.get("sector_id")

    if rol_actual == RolEnum.JEFE_SERVICIO.value:
        if personal.tipo_personal and personal.tipo_personal.nombre == TipoPersonalEnum.RESIDENTE:
            logger.warning("Acceso denegado (403): Jefe de Servicio intentó eliminar/desactivar residente (ID: %d).", personal_id)
            raise ForbiddenError("Un Jefe de Servicio no puede eliminar o desactivar personal de tipo Residente.")
        
        if personal.sector_id != sector_usuario:
            logger.warning("Acceso denegado (403): Jefe de Servicio intentó eliminar/desactivar personal ajeno (ID: %d).", personal_id)
            raise ForbiddenError("No tiene permisos para operar sobre personal de otro sector.")

    try:
        tiene_historial = False
        
        if (len(personal.solicitudes_comida) > 0):
            tiene_historial = True

        if tiene_historial:
            personal.activo = False
            db.session.commit()
            logger.info("Personal con ID %d posee historial; marcado como inactivo (baja lógica).", personal_id)
            mensaje = "El personal posee registros históricos asociados; ha sido marcado como inactivo."
        else:
            db.session.delete(personal)
            db.session.commit()
            logger.info("Personal con ID %d sin historial; eliminado físicamente de la base de datos.", personal_id)
            mensaje = "El miembro del personal ha sido eliminado exitosamente."

        return {"mensaje": mensaje}

    except Exception as e:
        db.session.rollback()
        logger.exception("Error inesperado al eliminar/desactivar el personal con ID %d: %s", personal_id, str(e))
        raise e

def import_personal_csv(file_stream):
    """Procesa un archivo CSV para la importación masiva de personal de forma robusta.

    Args:
        file_stream: Stream o archivo subido (ej. request.files['archivo'].stream)

    Returns:
        dict: Resumen con registros procesados, importados, rechazados y detalles de error.
    """
    contenido_bytes = file_stream.read()
    
    # Intentamos detectar la codificación correcta compatible con Excel en español y UTF-8
    stream = None
    for encoding in ["utf-8-sig", "cp1252", "latin-1", "utf-8"]:
        try:
            stream = io.TextIOWrapper(io.BytesIO(contenido_bytes), encoding=encoding)
            muestra = stream.read(2048)
            stream.seek(0)
            break
        except UnicodeDecodeError:
            continue
            
    if not stream:
        return {
            "procesados": 0,
            "importados": 0,
            "rechazados": 1,
            "errores": [{"fila": 0, "dni": "-", "motivo": "No se pudo detectar la codificación del archivo. Guarde el CSV como UTF-8."}]
        }

    # Detectar delimitador automáticamente entre punto y coma (;) y coma (,)
    delimitador = ";" if ";" in muestra else ","
    reader = csv.DictReader(stream, delimiter=delimitador)

    procesados = 0
    importados = 0
    rechazados = 0
    errores = []

    for index, row in enumerate(reader, start=1):
        # Limpiar claves eliminando espacios, BOM y pasando a minúsculas
        clean_row = {}
        for k, v in row.items():
            if k is not None:
                clave_limpia = str(k).strip().lstrip('\ufeff').lower()
                valor_limpio = v.strip() if isinstance(v, str) else v
                if clave_limpia:
                    clean_row[clave_limpia] = valor_limpio

        # Ignorar filas completamente vacías
        if not any(clean_row.values()):
            continue

        procesados += 1
        dni = clean_row.get("dni", "")
        nombre = clean_row.get("nombre", "")
        apellido = clean_row.get("apellido", "")
        
        try:
            # Soportamos ambos formatos (con guión bajo o sin guión bajo en los encabezados)
            tipo_personal_str = clean_row.get("tipo_personal_id") or clean_row.get("tipopersonalid")
            sector_str = clean_row.get("sector_id") or clean_row.get("sectorid")
            tipo_menu_str = clean_row.get("tipo_menu_id") or clean_row.get("tipomenuid")

            tipo_personal_id = int(tipo_personal_str) if tipo_personal_str else None
            sector_id = int(sector_str) if sector_str else None
            tipo_menu_id = int(tipo_menu_str) if tipo_menu_str else None
        except ValueError:
            rechazados += 1
            errores.append({"fila": index, "dni": dni, "motivo": "IDs de tipo, sector o menú inválidos (deben ser numéricos)."})
            continue

        # Validación de campos obligatorios
        if not dni or not nombre or not apellido or not tipo_personal_id or not tipo_menu_id:
            rechazados += 1
            errores.append({"fila": index, "dni": dni, "motivo": "Faltan campos obligatorios (dni, nombre, apellido, tipo_personal_id, tipo_menu_id)."})
            continue

        # Validar si ya existe el DNI en la base de datos
        existe = db.session.execute(select(Personal).where(Personal.dni == dni)).scalars().first()
        if existe:
            rechazados += 1
            errores.append({"fila": index, "dni": dni, "motivo": f"Ya existe una persona registrada con el DNI {dni}."})
            continue

        # Validar existencia de la entidad TipoPersonal
        tipo_personal = db.session.get(TipoPersonal, tipo_personal_id)
        if not tipo_personal:
            rechazados += 1
            errores.append({"fila": index, "dni": dni, "motivo": f"El tipo_personal_id {tipo_personal_id} no existe."})
            continue

        # Validar existencia de la entidad Sector (si fue proporcionado)
        if sector_id:
            sector = db.session.get(Sector, sector_id)
            if not sector:
                rechazados += 1
                errores.append({"fila": index, "dni": dni, "motivo": f"El sector_id {sector_id} no existe."})
                continue


        # Crear e insertar el registro de forma individual para no abortar el lote completo si una fila falla
        try:
            nuevo_personal = Personal(
                dni=dni,
                nombre=nombre,
                apellido=apellido,
                tipo_personal_id=tipo_personal_id,
                sector_id=sector_id,
                tipo_menu_id=tipo_menu_id,
                activo=True
            )
            db.session.add(nuevo_personal)
            db.session.commit()
            importados += 1
        except Exception as e:
            db.session.rollback()
            rechazados += 1
            errores.append({"fila": index, "dni": dni, "motivo": f"Error de base de datos: {str(e)}"})
            logger.exception("Error al importar fila %d (DNI: %s): %s", index, dni, e)

    logger.info("Importación CSV finalizada. Procesados: %d, Importados: %d, Rechazados: %d", procesados, importados, rechazados)
    return {
        "procesados": procesados,
        "importados": importados,
        "rechazados": rechazados,
        "errores": errores
    }