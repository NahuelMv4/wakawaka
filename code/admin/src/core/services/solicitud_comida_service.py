from datetime import datetime, timezone
from src.core.database import db
from src.core.errores.custom_errors import ConflictError, NotFoundError
from src.core.models.pedido import Pedido
from src.core.models.solicitud_comida import SolicitudComida


def autorizar_solicitud(solicitud_id: int, usuario_id: int | None = None) -> SolicitudComida:
    solicitud = db.session.get(SolicitudComida, solicitud_id)
    if solicitud is None:
        raise NotFoundError("Solicitud de comida no encontrada.")

    if solicitud.entrega_id is not None:
        raise ConflictError("No se puede modificar una solicitud ya entregada.")

    solicitud.autorizada = True

    pedido = solicitud.pedido or db.session.get(Pedido, solicitud.pedido_id)
    if pedido is not None:
        solicitudes_pedido = list(pedido.solicitudes_comida or [])
        if solicitudes_pedido and all(bool(s.autorizada) for s in solicitudes_pedido):
            pedido.estado = "Autorizado"
            if hasattr(pedido, "actualizado_en"):
                pedido.actualizado_en = datetime.now(timezone.utc)

    db.session.commit()
    return solicitud