from src.core.database import db
from src.core.models import Pedido, SolicitudComida, TipoComida, TipoMenu, Personal, Entrega
from sqlalchemy import func, or_, select
from sqlalchemy.orm import joinedload
from sqlalchemy.sql import case
from datetime import date, datetime

from src.core.database import db
from src.core.enums import TipoComidaEnum
from src.core.models import Pedido, Personal, SolicitudComida, TipoComida

def consultar_comidas(fecha, dni=None, nya=None, sector_id=None, tipo_comida=None):
    stmt = (
        select(SolicitudComida)
        .join(SolicitudComida.pedido)
        .join(SolicitudComida.personal)
        .join(Pedido.tipo_comida)
        .options(
            joinedload(SolicitudComida.personal).joinedload(Personal.sector),
            joinedload(SolicitudComida.tipo_menu),
            joinedload(SolicitudComida.pedido).joinedload(Pedido.tipo_comida),
        )
        .where(SolicitudComida.fecha_comida == fecha)
    )

    if dni:
        stmt = stmt.where(Personal.dni == dni)

    if nya:
        palabras = nya.strip().split()
        tildes = "áéíóúÁÉÍÓÚüÜñÑ"
        sin_tildes = "aeiouAEIOUuUnN"
        col_nombre = func.translate(Personal.nombre, tildes, sin_tildes)
        col_apellido = func.translate(Personal.apellido, tildes, sin_tildes)

        for palabra in palabras:
            patron = f"%{palabra}%"
            stmt = stmt.where(
                or_(
                    col_nombre.ilike(patron),
                    col_apellido.ilike(patron),
                )
            )

    if sector_id:
        stmt = stmt.where(Personal.sector_id == sector_id)

    if tipo_comida:
        enum_match = next(
            (e for e in TipoComidaEnum if e.value.lower() == tipo_comida.lower() or e.name.lower() == tipo_comida.lower()),
            None,
        )
        if enum_match:
            stmt = stmt.where(TipoComida.nombre == enum_match)
        else:
            stmt = stmt.where(func.lower(TipoComida.nombre) == tipo_comida.lower())

    solicitudes = db.session.scalars(stmt).all()

    salida = []
    for s in solicitudes:
        estado_pedido = (s.pedido.estado or "").lower()
        ya_entregado = s.entrega_id is not None
        if ya_entregado:
            estado_visual = "entregado"
        elif estado_pedido in ("autorizado", "aprobado"):
            estado_visual = "autorizado"
        else:
            estado_visual = "no_autorizado"
        nombre_comida = s.pedido.tipo_comida.nombre.value if s.pedido and s.pedido.tipo_comida else ""
        nombre_menu = getattr(s.tipo_menu.nombre, "value", s.tipo_menu.nombre) if s.tipo_menu else "General"
        salida.append({
            "id": s.personal.id,
            "solicitud_id": s.id,
            "pedido_id": s.pedido_id,
            "nombre": s.personal.nombre,
            "apellido": s.personal.apellido,
            "dni": s.personal.dni,
            "sector": s.personal.sector.nombre if s.personal.sector else "Sin sector",
            "tipo_comida": nombre_comida,
            "tipo_menu": nombre_menu,
            "estado": estado_visual,
            "estado_pedido": s.pedido.estado,
            "entregado": ya_entregado,
        })
    return salida


def obtener_resumen_dia(fecha=None):
    fecha_consulta = fecha or date.today()

    stmt = (
        select(SolicitudComida)
        .join(SolicitudComida.pedido)
        .join(Pedido.tipo_comida)
        .where(
            SolicitudComida.fecha_comida == fecha_consulta,
            func.lower(Pedido.estado).in_(["autorizado", "aprobado"]),
        )
    )
    solicitudes = db.session.scalars(stmt).all()

    orden_comidas = ["Desayuno", "Almuerzo", "Merienda", "Cena"]
    agrupado = {c: {} for c in orden_comidas}

    for s in solicitudes:
        raw_comida = s.pedido.tipo_comida.nombre
        nombre_comida = (
            raw_comida.value.capitalize()
            if hasattr(raw_comida, "value")
            else str(raw_comida).capitalize()
        )
        if nombre_comida not in agrupado:
            agrupado[nombre_comida] = {}


        tipo_menu = "General"
        if s.tipo_menu:
            raw_menu = s.tipo_menu.nombre
            tipo_menu = raw_menu.value if hasattr(raw_menu, "value") else str(raw_menu)

        if tipo_menu not in agrupado[nombre_comida]:
            agrupado[nombre_comida][tipo_menu] = {
                "tipo_menu": tipo_menu,
                "autorizados": 0,
                "entregados": 0,
                "pendientes": 0,
            }

        agrupado[nombre_comida][tipo_menu]["autorizados"] += 1
        if s.entrega_id is not None:
            agrupado[nombre_comida][tipo_menu]["entregados"] += 1
        else:
            agrupado[nombre_comida][tipo_menu]["pendientes"] += 1

    resultado = []
    for comida in orden_comidas:
        menus_lista = list(agrupado[comida].values())
        resultado.append({
            "comida": comida,
            "subtotal_autorizados": sum(m["autorizados"] for m in menus_lista),
            "subtotal_entregados": sum(m["entregados"] for m in menus_lista),
            "menus": menus_lista,
        })

    return resultado

from datetime import date, datetime, timezone
from sqlalchemy import func, select
from src.core.database import db
from src.core.enums import TipoComidaEnum
from src.core.models import Entrega, Pedido, Personal, SolicitudComida, TipoComida


def registrar_entrega(
    personas_ids,
    tipo_comida,
    fecha=None,
    usuario_id=None,
    responsable_id=None,
    tercero=None,
):
    if not personas_ids:
        raise ValueError("Debe seleccionar al menos una persona para registrar la entrega.")
    
    fecha_entrega = fecha or date.today()

    enum_match = next(
        (
            e
            for e in TipoComidaEnum
            if e.value.lower() == tipo_comida.lower() or e.name.lower() == tipo_comida.lower()
        ),
        None,
    )

    stmt = (
        select(SolicitudComida)
        .join(SolicitudComida.pedido)
        .join(Pedido.tipo_comida)
        .where(
            SolicitudComida.fecha_comida == fecha_entrega,
            SolicitudComida.personal_id.in_(personas_ids),
            func.lower(Pedido.estado).in_(["autorizado", "aprobado"]),
        )
    )

    if enum_match:
        stmt = stmt.where(TipoComida.nombre == enum_match)
    else:
        stmt = stmt.where(func.lower(TipoComida.nombre) == tipo_comida.lower())

    solicitudes = db.session.scalars(stmt).all()

    if not solicitudes:
        raise ValueError("No se encontraron solicitudes autorizadas para entregar en esta fecha y comida.")

    # Se verifica que ninguna haya sido entregada ya
    if any(s.entrega_id is not None for s in solicitudes):
        raise ValueError("Una o más viandas seleccionadas ya fueron entregadas.")

    # quién retira 
    retira_personal_id = None
    if responsable_id:
        retira_personal_id = int(responsable_id)
    elif tercero and tercero.get("dni"):
        persona_tercero = db.session.scalar(
            select(Personal).where(Personal.dni == str(tercero["dni"]).strip())
        )
        if not persona_tercero:
            raise ValueError(f"No se encontró personal registrado con DNI {tercero['dni']}.")
        retira_personal_id = persona_tercero.id
    else:
        # En retiro individual (o grupal de 1 persona), retira el mismo titular
        retira_personal_id = int(personas_ids[0])

    # Creo el registro de Entrega con los campos exactos de tu modelo
    nueva_entrega = Entrega(
        fecha=datetime.now(timezone.utc),
        personal_id=retira_personal_id,
    )
    db.session.add(nueva_entrega)
    db.session.flush()

    # Asocio cada solicitud a la entrega recién creada
    for s in solicitudes:
        s.entrega_id = nueva_entrega.id

    db.session.commit()

    return {
        "entrega_id": nueva_entrega.id,
        "cantidad_entregada": len(solicitudes),
    }