"""Consultas y agrupamientos para el resumen de pedidos."""

from sqlalchemy import select, func, cast, DateTime, case

from src.core.database import db
from src.core.models.pedido import Pedido
from src.core.models.solicitud_comida import SolicitudComida
from src.core.models.registro_cupo import RegistroCupo
from src.core.models.sector import Sector
from src.core.models.tipo_comida import TipoComida
from src.core.models.tipo_menu import TipoMenu


AGRUPAMIENTOS_TEMPORALES = {"dia", "semana", "mes"}

UNIDADES_TEMPORALES = {
    "dia": "day",
    "semana": "week",
    "mes": "month",
}

AGRUPAMIENTOS = {
    "sector": Sector.nombre,
    "tipo_comida": TipoComida.nombre,
    "tipo_menu": TipoMenu.nombre,
}


def validar_agrupamientos(agrupamientos):
    """Valida los agrupamientos solicitados."""

    if agrupamientos is None:
        return ["sector", "tipo_comida", "tipo_menu"]

    if not agrupamientos:
        raise ValueError("Debe indicar al menos un agrupamiento.")

    permitidos = set(AGRUPAMIENTOS) | AGRUPAMIENTOS_TEMPORALES

    if len(agrupamientos) != len(set(agrupamientos)):
        raise ValueError("No se permiten agrupamientos repetidos.")

    invalidos = set(agrupamientos) - permitidos

    if invalidos:
        raise ValueError(
            f"Agrupamientos no válidos: {', '.join(sorted(invalidos))}."
        )

    temporales = set(agrupamientos) & AGRUPAMIENTOS_TEMPORALES

    if len(temporales) > 1:
        raise ValueError(
            "Solo se permite un agrupamiento temporal: día, semana o mes."
        )

    return agrupamientos


def _obtener_columnas_agrupamiento(agrupamientos):
    """Construye las expresiones SQL de los agrupamientos."""

    columnas = []

    for agrupamiento in agrupamientos:
        if agrupamiento in AGRUPAMIENTOS_TEMPORALES:
            periodo = UNIDADES_TEMPORALES[agrupamiento]

            columna = func.date_trunc(
                periodo,
                cast(SolicitudComida.fecha_comida, DateTime)
            ).label(agrupamiento)

        else:
            columna = AGRUPAMIENTOS[agrupamiento].label(agrupamiento)

        columnas.append(columna)

    return columnas


def _serializar_valor(valor, agrupamiento):
    """Convierte los valores a tipos compatibles con JSON."""

    if valor is None:
        return None

    if agrupamiento in AGRUPAMIENTOS_TEMPORALES:
        if agrupamiento == "dia":
            return valor.date().isoformat()

        return valor.isoformat()

    if hasattr(valor, "value"):
        return valor.value

    return valor


def _aplicar_filtros_generales(stmt, filtros, sector_id=None):
    """Aplica los filtros comunes a las consultas."""

    if filtros.get("fecha_desde"):
        stmt = stmt.where(
            SolicitudComida.fecha_comida >= filtros["fecha_desde"]
        )

    if filtros.get("fecha_hasta"):
        stmt = stmt.where(
            SolicitudComida.fecha_comida <= filtros["fecha_hasta"]
        )

    if filtros.get("sector_id"):
        stmt = stmt.where(
            Pedido.sector_id == filtros["sector_id"]
        )

    if filtros.get("tipo_comida_id"):
        stmt = stmt.where(
            Pedido.tipo_comida_id == filtros["tipo_comida_id"]
        )

    if filtros.get("tipo_menu_id"):
        stmt = stmt.where(
            SolicitudComida.tipo_menu_id == filtros["tipo_menu_id"]
        )

    if sector_id is not None:
        stmt = stmt.where(
            Pedido.sector_id == sector_id
        )

    return stmt


def _obtener_datos_grafico(filtros, agrupamiento, sector_id=None):
    """
    Obtiene las solicitudes agrupadas para los gráficos de pedidos.

    Los gráficos no dependen del agrupamiento seleccionado para las tablas.
    """

    if agrupamiento == "sector":
        columna = Sector.nombre

    elif agrupamiento == "tipo_menu":
        columna = TipoMenu.nombre

    elif agrupamiento == "dia":
        columna = func.date_trunc(
            "day",
            cast(SolicitudComida.fecha_comida, DateTime)
        )

    else:
        raise ValueError("Agrupamiento de gráfico no válido.")

    stmt = (
        select(
            func.count(
                func.distinct(SolicitudComida.id)
            ).label("total"),
            columna.label("categoria")
        )
        .select_from(SolicitudComida)
        .join(
            Pedido,
            SolicitudComida.pedido_id == Pedido.id
        )
        .join(
            Sector,
            Pedido.sector_id == Sector.id
        )
        .join(
            TipoMenu,
            SolicitudComida.tipo_menu_id == TipoMenu.id
        )
    )

    stmt = _aplicar_filtros_generales(
        stmt,
        filtros,
        sector_id
    )

    # La condición se aplica solamente a los gráficos de pedidos.
    condicion = filtros.get("condicion")

    if condicion:
        stmt = stmt.where(
            SolicitudComida.condicion == condicion
        )

    stmt = stmt.group_by(columna).order_by(columna)

    resultados = db.session.execute(stmt).all()

    respuesta = []

    for fila in resultados:
        valor = fila.categoria

        if agrupamiento == "dia":
            valor = valor.date().isoformat()

        elif hasattr(valor, "value"):
            valor = valor.value

        respuesta.append({
            "categoria": valor,
            "total": fila.total
        })

    return respuesta


""" ----- RESUMEN DE SOLICITUDES ----- """


def obtener_resumen(filtros, sector_id=None):
    """
    Cuenta las solicitudes de comida y las desglosa por condición.

    Devuelve los datos de la tabla y los datos adicionales
    necesarios para los gráficos.
    """

    agrupamientos = validar_agrupamientos(
        filtros.get("agrupar_por")
    )

    columnas_agrupamiento = _obtener_columnas_agrupamiento(
        agrupamientos
    )

    total_regular = func.sum(
        case(
            (SolicitudComida.condicion == "Regular", 1),
            else_=0
        )
    ).label("total_regular")

    total_excepcion = func.sum(
        case(
            (SolicitudComida.condicion == "Excepción", 1),
            else_=0
        )
    ).label("total_excepcion")

    stmt = (
        select(
            func.count(SolicitudComida.id).label("total"),
            total_regular,
            total_excepcion,
            *columnas_agrupamiento
        )
        .join(
            Pedido,
            SolicitudComida.pedido_id == Pedido.id
        )
        .join(
            Sector,
            Pedido.sector_id == Sector.id
        )
        .join(
            TipoComida,
            Pedido.tipo_comida_id == TipoComida.id
        )
        .join(
            TipoMenu,
            SolicitudComida.tipo_menu_id == TipoMenu.id
        )
    )

    stmt = _aplicar_filtros_generales(
        stmt,
        filtros,
        sector_id
    )

    # La condición se aplica únicamente al resumen de pedidos.
    condicion = filtros.get("condicion")

    if condicion:
        stmt = stmt.where(
            SolicitudComida.condicion == condicion
        )

    stmt = stmt.group_by(*columnas_agrupamiento)
    stmt = stmt.order_by(*columnas_agrupamiento)

    resultados = db.session.execute(stmt).all()

    respuesta = []

    for fila in resultados:
        registro = {
            "total": fila.total,
            "total_regular": fila.total_regular or 0,
            "total_excepcion": fila.total_excepcion or 0
        }

        for agrupamiento in agrupamientos:
            registro[agrupamiento] = _serializar_valor(
                getattr(fila, agrupamiento),
                agrupamiento
            )

        respuesta.append(registro)

    graficos = {
        "por_sector": _obtener_datos_grafico(
            filtros,
            "sector",
            sector_id
        ),
        "por_tipo_menu": _obtener_datos_grafico(
            filtros,
            "tipo_menu",
            sector_id
        ),
        "evolucion": _obtener_datos_grafico(
            filtros,
            "dia",
            sector_id
        )
    }

    return {
        "data": respuesta,
        "graficos": graficos
    }


""" ----- RESUMEN DE AUTORIZACIONES ----- """


def obtener_resumen_autorizaciones(filtros):
    """
    Obtiene el resumen de solicitudes pedidas y autorizadas.

    Las solicitudes sin RegistroCupo se consideran pendientes.
    No aplica el filtro de condición.
    """

    agrupamientos = validar_agrupamientos(
        filtros.get("agrupar_por")
    )

    columnas_agrupamiento = _obtener_columnas_agrupamiento(
        agrupamientos
    )

    total_pedido = func.count(
        func.distinct(SolicitudComida.id)
    ).label("total_pedido")

    total_autorizado = func.count(
        func.distinct(
            case(
                (RegistroCupo.estado == "ACEPTADO", SolicitudComida.id),
                else_=None
            )
        )
    ).label("total_autorizado")

    stmt = (
        select(
            total_pedido,
            total_autorizado,
            *columnas_agrupamiento
        )
        .select_from(SolicitudComida)
        .join(
            Pedido,
            SolicitudComida.pedido_id == Pedido.id
        )
        .join(
            Sector,
            Pedido.sector_id == Sector.id
        )
        .join(
            TipoComida,
            Pedido.tipo_comida_id == TipoComida.id
        )
        .join(
            TipoMenu,
            SolicitudComida.tipo_menu_id == TipoMenu.id
        )
        .outerjoin(
            RegistroCupo,
            RegistroCupo.solicitud_comida_id == SolicitudComida.id
        )
    )

    stmt = _aplicar_filtros_generales(stmt, filtros)

    stmt = stmt.group_by(*columnas_agrupamiento)
    stmt = stmt.order_by(*columnas_agrupamiento)

    resultados = db.session.execute(stmt).all()

    respuesta = []

    for fila in resultados:
        registro = {
            "total_pedido": fila.total_pedido,
            "total_autorizado": fila.total_autorizado or 0
        }

        for agrupamiento in agrupamientos:
            registro[agrupamiento] = _serializar_valor(
                getattr(fila, agrupamiento),
                agrupamiento
            )

        respuesta.append(registro)

    return respuesta


""" ----- RESUMEN DE ENTREGAS ----- """


def obtener_resumen_entregas(filtros):
    """
    Obtiene el resumen de solicitudes autorizadas y entregadas.

    Una solicitud se considera autorizada cuando su RegistroCupo
    tiene estado ACEPTADO.

    Una solicitud se considera entregada cuando está autorizada
    y tiene entrega_id distinto de NULL.

    No aplica el filtro de condición.
    """

    agrupamientos = validar_agrupamientos(
        filtros.get("agrupar_por")
    )

    columnas_agrupamiento = _obtener_columnas_agrupamiento(
        agrupamientos
    )

    total_autorizado = func.count(
        func.distinct(
            case(
                (RegistroCupo.estado == "ACEPTADO", SolicitudComida.id),
                else_=None
            )
        )
    ).label("total_autorizado")

    total_entregado = func.count(
        func.distinct(
            case(
                (
                    (RegistroCupo.estado == "ACEPTADO")
                    & (SolicitudComida.entrega_id.is_not(None)),
                    SolicitudComida.id
                ),
                else_=None
            )
        )
    ).label("total_entregado")

    stmt = (
        select(
            total_autorizado,
            total_entregado,
            *columnas_agrupamiento
        )
        .select_from(SolicitudComida)
        .join(
            Pedido,
            SolicitudComida.pedido_id == Pedido.id
        )
        .join(
            Sector,
            Pedido.sector_id == Sector.id
        )
        .join(
            TipoComida,
            Pedido.tipo_comida_id == TipoComida.id
        )
        .join(
            TipoMenu,
            SolicitudComida.tipo_menu_id == TipoMenu.id
        )
        .outerjoin(
            RegistroCupo,
            RegistroCupo.solicitud_comida_id == SolicitudComida.id
        )
    )

    stmt = _aplicar_filtros_generales(stmt, filtros)

    stmt = stmt.group_by(*columnas_agrupamiento)
    stmt = stmt.order_by(*columnas_agrupamiento)

    resultados = db.session.execute(stmt).all()

    respuesta = []

    for fila in resultados:
        registro = {
            "total_autorizado": fila.total_autorizado or 0,
            "total_entregado": fila.total_entregado or 0
        }

        for agrupamiento in agrupamientos:
            registro[agrupamiento] = _serializar_valor(
                getattr(fila, agrupamiento),
                agrupamiento
            )

        respuesta.append(registro)

    return respuesta