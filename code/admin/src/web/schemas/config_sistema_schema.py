from marshmallow import Schema, fields, validate


class ConfiguracionSistemaSchema(Schema):
    id = fields.Integer(dump_only=True)
    clave = fields.String(required=True, validate=validate.Length(min=1, max=255))
    paginacion = fields.Integer(required=True, validate=validate.Range(min=1), error_messages={"min": "La paginación debe ser al menos 1."})
    mantenimiento = fields.Boolean(load_default=False)
    mensaje_mantenimiento = fields.String(allow_none=True, validate=validate.Length(max=500))
    actualizado_en = fields.DateTime(dump_only=True)
    actualizado_por_usuario_id = fields.Integer(allow_none=True)


configuracion_sistema_schema = ConfiguracionSistemaSchema()
lista_configuraciones_sistema_schema = ConfiguracionSistemaSchema(many=True)