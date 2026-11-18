"""Esquemas Marshmallow para validación y filtrado de pedidos de comida."""

from marshmallow import Schema, ValidationError, fields, validate, validates_schema


class DetalleComidasInputSchema(Schema):
    """Valida la asignación de listas de personal_id por cada tipo de comida."""

    desayuno = fields.List(fields.Int(validate=validate.Range(min=1)), load_default=list)
    almuerzo = fields.List(fields.Int(validate=validate.Range(min=1)), load_default=list)
    merienda = fields.List(fields.Int(validate=validate.Range(min=1)), load_default=list)
    cena = fields.List(fields.Int(validate=validate.Range(min=1)), load_default=list)

    @validates_schema
    def validar_no_vacio_ni_duplicado(self, data, **kwargs):
        """Verifica que haya al menos una persona asignada y sin duplicados por comida."""
        total = 0
        for comida, ids in data.items():
            if len(ids) != len(set(ids)):
                raise ValidationError(
                    {comida: f"No se puede repetir la misma persona en {comida}."}
                )
            total += len(ids)
        if total == 0:
            raise ValidationError("Debe incluir al menos una solicitud de comida en el pedido.")


class CrearPedidoSchema(Schema):
    """Valida la carga diaria, semanal o mensual de pedidos."""

    periodicidad = fields.Str(
        required=True,
        validate=validate.OneOf(["diaria", "semanal", "mensual"]),
    )
    fecha_inicio = fields.Date(required=True)
    fecha_fin = fields.Date(required=False, allow_none=True)
    fechas_excluidas = fields.List(fields.Date(), load_default=list)
    comidas = fields.Nested(DetalleComidasInputSchema, required=True)

    @validates_schema
    def validar_rango_fechas(self, data, **kwargs):
        """Valida coherencia entre fecha_inicio y fecha_fin según periodicidad."""
        periodicidad = data.get("periodicidad")
        inicio = data.get("fecha_inicio")
        fin = data.get("fecha_fin")

        if periodicidad == "diaria":
            if fin and fin != inicio:
                raise ValidationError(
                    {"fecha_fin": "En periodicidad diaria fecha_fin debe coincidir con fecha_inicio."}
                )
        else:
            if not fin:
                raise ValidationError(
                    {"fecha_fin": "Debe indicar fecha_fin para cargas semanales o mensuales."}
                )
            if fin < inicio:
                raise ValidationError(
                    {"fecha_fin": "La fecha de fin no puede ser anterior a la fecha de inicio."}
                )


class ActualizarPedidoSchema(Schema):
    """Valida la modificación de un pedido (admite listado de personal_id o dict de comidas)."""

    personal_ids = fields.List(
        fields.Int(validate=validate.Range(min=1)),
        required=False,
    )
    comidas = fields.Nested(DetalleComidasInputSchema, required=False)

    @validates_schema
    def validar_payload_edicion(self, data, **kwargs):
        """Exige personal_ids o comidas sin duplicados para actualizar el pedido."""
        if "personal_ids" not in data and "comidas" not in data:
            raise ValidationError("Debe enviar 'personal_ids' o 'comidas' para modificar el pedido.")

        if "personal_ids" in data:
            ids = data["personal_ids"]
            if not ids:
                raise ValidationError(
                    {"personal_ids": "El pedido debe tener al menos una persona asignada."}
                )
            if len(ids) != len(set(ids)):
                raise ValidationError(
                    {"personal_ids": "No se puede repetir la misma persona en el pedido."}
                )


class FiltroPedidosSchema(Schema):
    """Valida los parámetros de consulta para listar pedidos actuales e históricos."""

    fecha_desde = fields.Date(required=False)
    fecha_hasta = fields.Date(required=False)
    tipo_comida_id = fields.Int(required=False, validate=validate.Range(min=1))
    tipo_menu_id = fields.Int(required=False, validate=validate.Range(min=1))
    estado = fields.Str(
        required=False,
        validate=validate.OneOf(["Confirmado", "Autorizado", "Rechazado"]),
    )
    page = fields.Int(load_default=1, validate=validate.Range(min=1))


crear_pedido_schema = CrearPedidoSchema()
actualizar_pedido_schema = ActualizarPedidoSchema()
filtro_pedidos_schema = FiltroPedidosSchema()