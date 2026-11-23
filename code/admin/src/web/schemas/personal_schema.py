from marshmallow import Schema, fields, validate


class PersonalFilterSchema(Schema):
    dni = fields.String(required=False)
    nombre = fields.String(required=False)
    apellido = fields.String(required=False)
    sector = fields.String(required=False)
    tipo_personal = fields.String(required=False)
    tipo_personal_id = fields.Integer(required=False)
    activo = fields.Boolean(required=False)
    page = fields.Integer(required=False, load_default=1)
    per_page = fields.Integer(required=False)
    sort_by = fields.Str(
        load_default="creado_en",
        validate=validate.OneOf(["dni", "nombre", "apellido", "creado_en"])
    )
    order = fields.Str(
        load_default="asc",
        validate=validate.OneOf(["asc", "desc"])
    )


class PersonalSchema(Schema):
    id = fields.Integer(dump_only=True)
    activo = fields.Boolean(dump_only=True)
    creado_en = fields.DateTime(dump_only=True)
    actualizado_en = fields.DateTime(dump_only=True)

    nombre = fields.String(required=True)
    apellido = fields.String(required=True)
    dni = fields.String(required=True)

    tipo_personal_id = fields.Integer(required=True)
    sector_id = fields.Integer(required=False, allow_none=True)
    tipo_menu_id = fields.Integer(required=True)

    tipo_personal = fields.String(attribute="tipo_personal.nombre", dump_only=True)
    sector = fields.String(attribute="sector.nombre", dump_only=True)


personal_schema = PersonalSchema()
lista_personal_schema = PersonalSchema(many=True)
personal_filter_schema = PersonalFilterSchema()