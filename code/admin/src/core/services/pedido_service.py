"""Servicios y reglas de negocio para la carga, consulta y gestión de pedidos."""

from datetime import date, datetime, time, timedelta, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import func, select
from sqlalchemy.orm import joinedload

from src.core.database import db
from src.core.enums import TipoComidaEnum, TipoPersonalEnum
from src.core.errores.custom_errors import (
    BadRequestError,
    ConflictError,
    ForbiddenError,
    NotFoundError,
)
from src.core.models.configuracion_sistema import ConfiguracionSistema
from src.core.models.cupo import Cupo
from src.core.models.pedido import Pedido
from src.core.models.personal import Personal
from src.core.models.registro_cupo import RegistroCupo
from src.core.models.solicitud_comida import SolicitudComida
from src.core.models.tipo_comida import TipoComida

MAPA_COMIDAS_ENUM = {
    "desayuno": TipoComidaEnum.DESAYUNO.value,
    "almuerzo": TipoComidaEnum.ALMUERZO.value,
    "merienda": TipoComidaEnum.MERIENDA.value,
    "cena": TipoComidaEnum.CENA.value,
}


def _nombre_enum(valor: Any) -> str:
    """Devuelve el valor string de un Enum o convierte a str si ya es texto."""
    return valor.value if hasattr(valor, "value") else str(valor)


def _obtener_configuracion() -> ConfiguracionSistema:
    """Obtiene la configuración vigente del sistema."""
    config = db.session.execute(select(ConfiguracionSistema)).scalars().first()
    if not config:
        raise BadRequestError("No se encontró configuración del sistema.")
    return config


def _validar_horario_corte(fechas: List[date]) -> None:
    """Verifica que ninguna fecha sea pasada ni haya superado el horario de corte."""
    config = _obtener_configuracion()
    ahora = datetime.now()
    hoy = ahora.date()
    fechas_invalidas = []

    for f in fechas:
        if f <= hoy:
            fechas_invalidas.append(
                f"{f.strftime('%d/%m/%Y')} (no se permiten fechas pasadas ni del día en curso)"
            )
            continue

        limite = datetime.combine(f - timedelta(days=1), config.horario_corte)
        if ahora > limite:
            fechas_invalidas.append(
                f"{f.strftime('%d/%m/%Y')} (horario de corte {config.horario_corte.strftime('%H:%M')} vencido)"
            )

    if fechas_invalidas:
        detalle = ", ".join(fechas_invalidas)
        raise BadRequestError(
            f"Existen fechas fuera de término por horario de corte: {detalle}."
        )


def _generar_lista_fechas(data: Dict[str, Any]) -> List[date]:
    """Construye la lista ordenada de fechas válidas aplicando exclusiones."""
    inicio: date = data["fecha_inicio"]
    fin: date = inicio if data["periodicidad"] == "diaria" else data["fecha_fin"]
    excluidas = set(data.get("fechas_excluidas", []))

    fechas = []
    actual = inicio
    while actual <= fin:
        if actual not in excluidas:
            fechas.append(actual)
        actual += timedelta(days=1)

    if not fechas:
        raise BadRequestError("Todas las fechas del período fueron excluidas.")
    return fechas


def _obtener_tipos_comida_por_clave() -> Dict[str, TipoComida]:
    """Mapea las claves de comida ('desayuno', etc.) a sus registros TipoComida."""
    tipos = db.session.execute(select(TipoComida)).scalars().all()
    por_nombre = {_nombre_enum(t.nombre): t for t in tipos}
    resultado = {}
    for clave, nombre_enum in MAPA_COMIDAS_ENUM.items():
        if nombre_enum not in por_nombre:
            raise BadRequestError(f"Tipo de comida '{nombre_enum}' no configurado.")
        resultado[clave] = por_nombre[nombre_enum]
    return resultado


def _validar_personal_permitido(
    personal_ids: List[int],
    sector_id: int,
    ids_existentes: Optional[set[int]] = None,
) -> Dict[int, Personal]:
    """Valida que cada nueva persona exista, esté activa y sea Personal Fijo del sector o Residente."""
    todos_ids = set(personal_ids)
    existentes = ids_existentes or set()
    personas = (
        db.session.execute(
            select(Personal)
            .options(joinedload(Personal.tipo_personal), joinedload(Personal.tipo_menu))
            .where(Personal.id.in_(todos_ids))
        )
        .scalars()
        .all()
    )
    mapa_personas = {p.id: p for p in personas}

    for pid in todos_ids:
        persona = mapa_personas.get(pid)
        if not persona:
            raise BadRequestError(f"La persona con ID {pid} no existe.")
        if pid in existentes:
            continue
        if not persona.activo:
            raise BadRequestError(
                f"{persona.apellido}, {persona.nombre} se encuentra inactivo/a y no puede incorporarse."
            )
        es_residente = _nombre_enum(persona.tipo_personal.nombre) == TipoPersonalEnum.RESIDENTE.value
        if not es_residente and persona.sector_id != sector_id:
            raise BadRequestError(
                f"{persona.apellido}, {persona.nombre} pertenece a otro sector y no puede ser incluido."
            )
    return mapa_personas


def _validar_residentes_sin_duplicados(
    fechas: List[date],
    ids: List[int],
    mapa_personas: Dict[int, Personal],
    tipo_comida: TipoComida,
    sector_id: int,
    pedido_excluido_id: Optional[int] = None,
) -> None:
    """Impide asignar a un Residente una comida ya solicitada o generada en otro sector."""
    residentes_ids = [
        pid
        for pid in ids
        if _nombre_enum(mapa_personas[pid].tipo_personal.nombre) == TipoPersonalEnum.RESIDENTE.value
    ]
    if not residentes_ids:
        return

    stmt = (
        select(SolicitudComida)
        .join(Pedido)
        .options(
            joinedload(SolicitudComida.pedido).joinedload(Pedido.sector),
            joinedload(SolicitudComida.personal),
        )
        .where(
            SolicitudComida.personal_id.in_(residentes_ids),
            SolicitudComida.fecha_comida.in_(fechas),
            Pedido.tipo_comida_id == tipo_comida.id,
            Pedido.estado != "Rechazado",
            Pedido.sector_id != sector_id,
        )
    )
    if pedido_excluido_id:
        stmt = stmt.where(Pedido.id != pedido_excluido_id)

    conflicto = db.session.execute(stmt).scalars().first()
    if conflicto:
        pers = conflicto.personal
        raise ConflictError(
            f"El residente {pers.apellido}, {pers.nombre} (DNI {pers.dni}) ya tiene asignado "
            f"{_nombre_enum(tipo_comida.nombre)} el {conflicto.fecha_comida.strftime('%d/%m/%Y')} "
            f"en el sector {conflicto.pedido.sector.nombre}."
        )


def _obtener_cupos_sector(sector_id: int) -> Dict[int, Optional[Cupo]]:
    """Obtiene los cupos vigentes del sector indexados por tipo_comida_id."""
    cupos = (
        db.session.execute(select(Cupo).where(Cupo.sector_id == sector_id))
        .scalars()
        .all()
    )
    return {c.tipo_comida_id: c for c in cupos}


def crear_pedidos(data: Dict[str, Any], usuario_id: int, sector_id: int) -> List[Pedido]:
    """Crea pedidos diarios por fecha y tipo de comida validando cupos, corte y residentes."""
    if not sector_id:
        raise ForbiddenError("El usuario no tiene un sector asignado para cargar pedidos.")

    fechas = _generar_lista_fechas(data)
    _validar_horario_corte(fechas)

    comidas_data = data["comidas"]
    tipos_comida = _obtener_tipos_comida_por_clave()
    comidas_activas = {
        clave: ids for clave, ids in comidas_data.items() if ids
    }
    tipos_ids_solicitados = [tipos_comida[c].id for c in comidas_activas]
    rango_dt = [datetime.combine(f, time.min) for f in fechas]

    existentes = (
        db.session.execute(
            select(Pedido)
            .options(joinedload(Pedido.tipo_comida))
            .where(
                Pedido.sector_id == sector_id,
                Pedido.fecha_desde.in_(rango_dt),
                Pedido.tipo_comida_id.in_(tipos_ids_solicitados),
            )
        )
        .scalars()
        .all()
    )
    if existentes:
        # MODIFICADO: Extraer .value del enum para mostrar 'Almuerzo' en lugar de 'TipoComidaEnum.ALMUERZO'
        detalle_conflictos = ", ".join(
            f"{_nombre_enum(p.tipo_comida.nombre)} ({p.fecha_desde.strftime('%d/%m/%Y')})"
            for p in existentes
        )
        raise ConflictError(
            f"Ya existen pedidos registrados para algunas fechas y comidas seleccionadas: {detalle_conflictos}."
        )

    todos_ids = [pid for ids in comidas_activas.values() for pid in ids]
    mapa_personas = _validar_personal_permitido(todos_ids, sector_id)

    for clave, ids in comidas_activas.items():
        _validar_residentes_sin_duplicados(
            fechas, ids, mapa_personas, tipos_comida[clave], sector_id
        )

    cupos_sector = _obtener_cupos_sector(sector_id)
    pedidos_creados: List[Pedido] = []

    for f in fechas:
        fecha_dt = datetime.combine(f, time.min)
        for clave, ids in comidas_activas.items():
            tipo_comida = tipos_comida[clave]
            cupo = cupos_sector.get(tipo_comida.id)
            limite_cupo = cupo.cantidad if cupo else 0

            pedido = Pedido(
                fecha_desde=fecha_dt,
                fecha_hasta=fecha_dt,
                estado="Confirmado",
                sector_id=sector_id,
                tipo_comida_id=tipo_comida.id,
                usuario_id=usuario_id,
            )
            db.session.add(pedido)
            db.session.flush()

            for idx, pid in enumerate(ids, start=1):
                persona = mapa_personas[pid]
                condicion = "Regular" if idx <= limite_cupo else "Excepción"

                solicitud = SolicitudComida(
                    fecha_comida=f,
                    condicion=condicion,
                    pedido_id=pedido.id,
                    personal_id=persona.id,
                    tipo_menu_id=persona.tipo_menu_id,
                )
                db.session.add(solicitud)
                db.session.flush()

                if cupo:
                    db.session.add(
                        RegistroCupo(
                            estado=condicion,
                            cupo_id=cupo.id,
                            solicitud_comida_id=solicitud.id,
                            cupo_historico=cupo.cantidad,
                        )
                    )

            pedidos_creados.append(pedido)

    db.session.commit()
    return [obtener_pedido_detalle(p.id, sector_id) for p in pedidos_creados]


def listar_pedidos_sector(sector_id: int, filtros: Dict[str, Any]) -> Dict[str, Any]:
    """Lista los pedidos actuales e históricos del sector con filtros y paginación dinámica."""
    if not sector_id:
        raise ForbiddenError("El usuario no tiene un sector asignado.")

    config = _obtener_configuracion()
    per_page = config.paginacion or 25
    page = filtros.get("page", 1)

    stmt = (
        select(Pedido)
        .options(
            joinedload(Pedido.tipo_comida),
            joinedload(Pedido.solicitudes_comida).joinedload(SolicitudComida.tipo_menu),
            joinedload(Pedido.revisiones),
        )
        .where(Pedido.sector_id == sector_id)
    )

    if filtros.get("fecha_desde"):
        stmt = stmt.where(
            Pedido.fecha_desde >= datetime.combine(filtros["fecha_desde"], time.min)
        )
    if filtros.get("fecha_hasta"):
        stmt = stmt.where(
            Pedido.fecha_hasta <= datetime.combine(filtros["fecha_hasta"], time.max)
        )
    if filtros.get("estado"):
        stmt = stmt.where(Pedido.estado == filtros["estado"])
    if filtros.get("tipo_comida_id"):
        stmt = stmt.where(Pedido.tipo_comida_id == filtros["tipo_comida_id"])
    if filtros.get("tipo_menu_id"):
        stmt = stmt.where(
            Pedido.solicitudes_comida.any(
                SolicitudComida.tipo_menu_id == filtros["tipo_menu_id"]
            )
        )

    stmt = stmt.order_by(Pedido.fecha_desde.desc(), Pedido.tipo_comida_id.asc())
    total_stmt = select(func.count()).select_from(stmt.order_by(None).subquery())
    total = db.session.scalar(total_stmt) or 0

    items = (
        db.session.execute(stmt.offset((page - 1) * per_page).limit(per_page))
        .unique()
        .scalars()
        .all()
    )

    return {
        "items": items,
        "total": total,
        "page": page,
        "pages": max(1, (total + per_page - 1) // per_page),
        "elementos_por_pagina": per_page,
    }


def obtener_pedido_detalle(request_id: int, sector_id: int) -> Pedido:
    """Obtiene el detalle completo de un pedido validando pertenencia al sector."""
    stmt = (
        select(Pedido)
        .options(
            joinedload(Pedido.sector),
            joinedload(Pedido.usuario),
            joinedload(Pedido.tipo_comida),
            joinedload(Pedido.revisiones),
            joinedload(Pedido.solicitudes_comida).joinedload(SolicitudComida.personal),
            joinedload(Pedido.solicitudes_comida).joinedload(SolicitudComida.tipo_menu),
        )
        .where(Pedido.id == request_id)
    )
    pedido = db.session.execute(stmt).unique().scalars().first()
    if not pedido:
        raise NotFoundError("El pedido solicitado no existe.")
    if pedido.sector_id != sector_id:
        raise ForbiddenError("No tiene permiso para acceder a pedidos de otro sector.")
    return pedido


def actualizar_pedido(
    request_id: int, data: Dict[str, Any], sector_id: int
) -> Pedido:
    """Modifica un pedido en estado Confirmado antes del corte, conservando orden de cupo."""
    pedido = obtener_pedido_detalle(request_id, sector_id)

    if pedido.estado != "Confirmado":
        raise ConflictError(
            "Solo pueden modificarse pedidos en estado Confirmado que aún no fueron revisados."
        )

    fecha_pedido = pedido.fecha_desde.date()
    _validar_horario_corte([fecha_pedido])

    if "personal_ids" in data:
        ids = data["personal_ids"]
    else:
        nombre_comida = _nombre_enum(pedido.tipo_comida.nombre)
        clave_comida = next(
            (k for k, v in MAPA_COMIDAS_ENUM.items() if v == nombre_comida),
            None,
        )
        ids = data["comidas"].get(clave_comida, [])
        if not ids:
            raise BadRequestError(
                f"Debe incluir al menos una persona para {nombre_comida}."
            )

    # MODIFICADO: Eximir de validación de inactividad/sector a quienes ya pertenecían al pedido
    solicitudes_previas = sorted(pedido.solicitudes_comida, key=lambda s: s.id)
    ids_previos = {s.personal_id for s in solicitudes_previas}
    mapa_personas = _validar_personal_permitido(ids, sector_id, ids_existentes=ids_previos)

    _validar_residentes_sin_duplicados(
        [fecha_pedido],
        ids,
        mapa_personas,
        pedido.tipo_comida,
        sector_id,
        pedido_excluido_id=pedido.id,
    )
    cupos_sector = _obtener_cupos_sector(sector_id)
    cupo = cupos_sector.get(pedido.tipo_comida_id)
    limite_cupo = cupo.cantidad if cupo else 0

    orden_previo = {s.personal_id: idx for idx, s in enumerate(solicitudes_previas)}

    ids_ordenados = sorted(
        ids,
        key=lambda pid: (0 if pid in orden_previo else 1, orden_previo.get(pid, 999999)),
    )

    for s in list(pedido.solicitudes_comida):
        db.session.delete(s)
    db.session.flush()

    for idx, pid in enumerate(ids_ordenados, start=1):
        persona = mapa_personas[pid]
        condicion = "Regular" if idx <= limite_cupo else "Excepción"

        solicitud = SolicitudComida(
            fecha_comida=fecha_pedido,
            condicion=condicion,
            pedido_id=pedido.id,
            personal_id=persona.id,
            tipo_menu_id=persona.tipo_menu_id,
        )
        db.session.add(solicitud)
        db.session.flush()

        if cupo:
            db.session.add(
                RegistroCupo(
                    estado=condicion,
                    cupo_id=cupo.id,
                    solicitud_comida_id=solicitud.id,
                    cupo_historico=cupo.cantidad,
                )
            )

    pedido.actualizado_en = datetime.now(timezone.utc)
    db.session.commit()
    return obtener_pedido_detalle(request_id, sector_id)


def eliminar_pedido(request_id: int, sector_id: int) -> None:
    """Elimina un pedido en estado Confirmado antes de su horario de corte."""
    pedido = obtener_pedido_detalle(request_id, sector_id)

    if pedido.estado != "Confirmado":
        raise ConflictError(
            "No es posible eliminar un pedido que ya fue autorizado o rechazado."
        )

    _validar_horario_corte([pedido.fecha_desde.date()])

    db.session.delete(pedido)
    db.session.commit()