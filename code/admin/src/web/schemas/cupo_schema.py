from marshmallow import Schema, fields, validate

class CupoSchema(Schema):
    """Esquema para la serialización y validación de los datos de Cupo."""
    
    id = fields.Integer(dump_only=True)
    creado_en = fields.DateTime(dump_only=True)
    actualizado_en = fields.DateTime(dump_only=True)
    
    # Se agrega la validacion que sea mayor a cero
    cantidad = fields.Integer(
        required=True,
        validate=validate.Range(min=1, error="La cantidad debe ser mayor a cero.")
    )
    sector_id = fields.Integer(required=True)
    tipo_comida_id = fields.Integer(required=True)

    sector_nombre = fields.Function(
        lambda obj: obj.sector.nombre if obj.sector else None, 
        dump_only=True
    )
    tipo_comida_nombre = fields.Function(
        lambda obj: obj.tipo_comida.nombre.value if obj.tipo_comida else None, 
        dump_only=True
    )

cupo_schema = CupoSchema()
cupos_schema = CupoSchema(many=True)