from datetime import date, datetime, timezone
import csv
import io
from datetime import date
from collections import defaultdict
from flask import Response
from sqlalchemy import func, select
from src.core.database import db
from src.core.errores.custom_errors import BadRequestError, ConflictError, NotFoundError
from src.core.models.pedido import Pedido
from src.core.models.solicitud_comida import SolicitudComida


def _a_date(valor):
    if valor is None:
        return None
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor
    return date.fromisoformat(str(valor)[:10])


def obtener_fechas_con_pedidos(fecha_desde=None, fecha_hasta=None):
    """Devuelve fechas que tienen solicitudes de comida en el rango."""
    stmt = (
        select(SolicitudComida.fecha_comida)
        .distinct()
        .order_by(SolicitudComida.fecha_comida.asc())
    )
    if fecha_desde:
        stmt = stmt.where(SolicitudComida.fecha_comida >= fecha_desde)
    if fecha_hasta:
        stmt = stmt.where(SolicitudComida.fecha_comida <= fecha_hasta)

    fechas = db.session.scalars(stmt).all()
    hoy = date.today()
    return [
        {
            "fecha": _a_date(f).isoformat(),
            "es_pasada": _a_date(f) < hoy,
            "solo_lectura": _a_date(f) < hoy,
        }
        for f in fechas
        if _a_date(f) is not None
    ]


def listar_pedidos_autorizacion(
    fecha=None,
    sector_id=None,
    tipo_comida_id=None,
    tipo_menu_id=None,
    condicion=None,
    estado=None,
):
    """Lista pedidos para el panel de autorización con cantidades pedidas y autorizadas."""
    stmt = select(Pedido).order_by(Pedido.creado_en.desc())

    if sector_id:
        stmt = stmt.where(Pedido.sector_id == int(sector_id))
    if tipo_comida_id:
        stmt = stmt.where(Pedido.tipo_comida_id == int(tipo_comida_id))
    if estado:
        stmt = stmt.where(func.lower(Pedido.estado) == str(estado).strip().lower())

    pedidos = db.session.scalars(stmt).all()
    hoy = date.today()
    resultado = []

    for p in pedidos:
        solicitudes = list(p.solicitudes_comida or [])

        if fecha:
            solicitudes = [
                s for s in solicitudes if _a_date(s.fecha_comida).isoformat() == fecha
            ]
        if tipo_menu_id:
            solicitudes = [
                s for s in solicitudes if s.tipo_menu_id == int(tipo_menu_id)
            ]
        if condicion:
            cond_norm = str(condicion).strip().lower()
            solicitudes = [
                s for s in solicitudes if str(s.condicion or "").strip().lower() == cond_norm
            ]

        if (fecha or tipo_menu_id or condicion) and not solicitudes:
            continue

        cantidad_pedida = len(solicitudes)
        cantidad_autorizada = sum(1 for s in solicitudes if bool(getattr(s, "autorizada", False)))

        fecha_ref = (
            _a_date(solicitudes[0].fecha_comida)
            if solicitudes
            else _a_date(getattr(p, "fecha_desde", None)) or hoy
        )
        es_pasada = fecha_ref < hoy

        resultado.append({
            "id": p.id,
            "fecha": fecha_ref.isoformat(),
            "sector_id": p.sector_id,
            "sector_nombre": p.sector.nombre if getattr(p, "sector", None) else "",
            "tipo_comida_id": p.tipo_comida_id,
            "tipo_comida_nombre": (
                p.tipo_comida.nombre if getattr(p, "tipo_comida", None) else ""
            ),
            "estado": p.estado,
            "es_confirmado": str(p.estado).strip().lower() == "confirmado",
            "motivo_rechazo": getattr(p, "motivo_rechazo", None),
            "cantidad_pedida": cantidad_pedida,
            "cantidad_autorizada": cantidad_autorizada,
            "solo_lectura": es_pasada,
            "actualizado_en": (
                p.actualizado_en.isoformat() if getattr(p, "actualizado_en", None) else None
            ),
        })

    return resultado


def marcar_pedido_autorizado(pedido_id: int):
    pedido = db.session.get(Pedido, pedido_id)
    if not pedido:
        return None

    pedido.estado = "Autorizado"
    db.session.commit()
    return pedido


def marcar_pedido_rechazado(pedido_id: int, motivo_rechazo: str | None, usuario_id: int | None = None):
    motivo_limpio = (motivo_rechazo or "").strip()
    if not motivo_limpio:
        raise BadRequestError("El motivo de rechazo es obligatorio.")

    pedido = db.session.get(Pedido, pedido_id)
    if not pedido:
        raise NotFoundError("Pedido no encontrado.")

    if str(getattr(pedido, "estado", "")).strip().lower() == "rechazado":
        raise ConflictError("El pedido ya fue rechazado.")

    pedido.estado = "Rechazado"
    if hasattr(pedido, "motivo_rechazo"):
        pedido.motivo_rechazo = motivo_limpio
    if hasattr(pedido, "actualizado_en"):
        pedido.actualizado_en = datetime.now(timezone.utc)
    if usuario_id is not None and hasattr(pedido, "autorizado_por_id"):
        pedido.autorizado_por_id = usuario_id

    db.session.commit()
    return pedido




def _parsear_fecha(valor):
    if not valor:
        return None
    if isinstance(valor, date):
        return valor
    return date.fromisoformat(str(valor)[:10])


def _filtrar_solicitudes_autorizadas(filtros: dict):
    query = (
        db.session.query(SolicitudComida)
        .join(Pedido, SolicitudComida.pedido_id == Pedido.id)
        .filter(SolicitudComida.autorizada.is_(True))
    )

    fecha = _parsear_fecha(filtros.get("fecha"))
    fecha_desde = _parsear_fecha(filtros.get("fecha_desde"))
    fecha_hasta = _parsear_fecha(filtros.get("fecha_hasta"))

    if fecha:
        query = query.filter(SolicitudComida.fecha_comida == fecha)
    if fecha_desde:
        query = query.filter(SolicitudComida.fecha_comida >= fecha_desde)
    if fecha_hasta:
        query = query.filter(SolicitudComida.fecha_comida <= fecha_hasta)
    if filtros.get("sector_id"):
        query = query.filter(Pedido.sector_id == int(filtros["sector_id"]))
    if filtros.get("tipo_comida_id"):
        query = query.filter(Pedido.tipo_comida_id == int(filtros["tipo_comida_id"]))
    if filtros.get("tipo_menu_id"):
        query = query.filter(SolicitudComida.tipo_menu_id == int(filtros["tipo_menu_id"]))
    if filtros.get("condicion"):
        query = query.filter(SolicitudComida.condicion == filtros["condicion"])
    if filtros.get("estado"):
        query = query.filter(Pedido.estado == filtros["estado"])

    return query.all()


def generar_csv_personas_autorizadas(filtros: dict) -> Response:
    solicitudes = _filtrar_solicitudes_autorizadas(filtros)
    agrupado = defaultdict(lambda: {
        "apellido_nombre": "",
        "dni": "",
        "sector": "",
        "menu": "",
        "comidas": set(),
    })

    for sol in solicitudes:
        persona = sol.personal
        pedido = sol.pedido
        menu_nombre = sol.tipo_menu.nombre if sol.tipo_menu else ""
        comida_nombre = (
            pedido.tipo_comida.nombre if pedido and pedido.tipo_comida else ""
        ).strip().lower()
        sector_nombre = (
            getattr(pedido.sector, "nombre", None) or f"Sector #{pedido.sector_id}"
        ) if pedido else ""

        clave = (sol.personal_id, menu_nombre)
        entry = agrupado[clave]
        entry["apellido_nombre"] = f"{persona.apellido}, {persona.nombre}".strip(", ")
        entry["dni"] = persona.dni
        entry["sector"] = sector_nombre
        entry["menu"] = menu_nombre
        if comida_nombre:
            entry["comidas"].add(comida_nombre)

    output = io.StringIO()
    output.write("\ufeff")
    writer = csv.writer(output, delimiter=";")
    writer.writerow([
        "Apellido y nombre",
        "DNI",
        "Sector",
        "Desayuno",
        "Almuerzo",
        "Merienda",
        "Cena",
        "Tipo de menú",
    ])

    for fila in sorted(
        agrupado.values(),
        key=lambda r: (r["sector"], r["apellido_nombre"], r["menu"]),
    ):
        comidas = fila["comidas"]
        writer.writerow([
            fila["apellido_nombre"],
            fila["dni"],
            fila["sector"],
            "Sí" if "desayuno" in comidas else "No",
            "Sí" if "almuerzo" in comidas else "No",
            "Sí" if "merienda" in comidas else "No",
            "Sí" if "cena" in comidas else "No",
            fila["menu"],
        ])

    return Response(
        output.getvalue(),
        mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="personas_autorizadas.csv"'},
    )


def generar_csv_totales_por_sector(filtros: dict) -> Response:
    solicitudes = _filtrar_solicitudes_autorizadas(filtros)
    conteos = defaultdict(int)

    for sol in solicitudes:
        pedido = sol.pedido
        sector_nombre = (
            getattr(pedido.sector, "nombre", None) or f"Sector #{pedido.sector_id}"
        ) if pedido else "Sin sector"
        comida_nombre = (
            pedido.tipo_comida.nombre if pedido and pedido.tipo_comida else "Sin comida"
        )
        menu_nombre = sol.tipo_menu.nombre if sol.tipo_menu else "Sin menú"
        conteos[(sector_nombre, comida_nombre, menu_nombre)] += 1

    output = io.StringIO()
    output.write("\ufeff")
    writer = csv.writer(output, delimiter=";")
    writer.writerow([
        "Sector",
        "Comida",
        "Tipo de menú",
        "Cantidad de viandas autorizadas",
    ])

    for (sector, comida, menu), cantidad in sorted(conteos.items()):
        writer.writerow([sector, comida, menu, cantidad])

    return Response(
        output.getvalue(),
        mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="totales_por_sector.csv"'},
    )