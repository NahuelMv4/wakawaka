from enum import Enum


class TipoPersonalEnum(str, Enum):
  RESIDENTE = "Residente"
  FIJO = "Personal Fijo"

class TipoComidaEnum(str, Enum):
  DESAYUNO = "Desayuno"
  ALMUERZO = "Almuerzo"
  MERIENDA = "Merienda"
  CENA = "Cena"

class TipoMenuEnum(str, Enum):
  GENERAL = "General"
  VEGETARIANO = "Vegetariano"
  CELIACO = "Celiaco"

class RolEnum(str, Enum):
  ADMINISTRADOR = "Administrador"
  JEFE_SERVICIO = "Jefe de Servicio"
  SERVICIO_ALIMENTACION = "Servicio de Alimentación"
  SECTOR_COMEDOR = "Sector Comedor"


class PermisoEnum(str, Enum):
  USER_INDEX = "user_index"  # listar usuarios
  USER_NEW = "user_new"  # crear usuario
  USER_SHOW = "user_show"  # ver detalle de usuario
  USER_UPDATE = "user_update"  # actualizar usuario
  USER_DESTROY = "user_destroy"  # eliminar usuario
  USER_BLOCK = "user_block"  # bloquear usuario
  USER_UNLOCK = "user_unlock"  # desbloquear usuario

  CONFIG_INDEX = "config_index"
  CONFIG_NEW = "config_new"
  CONFIG_ACTIVATE = "config_activate"
  CONFIG_DEACTIVATE = "config_deactivate"

  PERSONAL_INDEX = "personal_index"
  PERSONAL_SHOW = "personal_show"
  PERSONAL_CREATE = "personal_create"
  PERSONAL_UPDATE = "personal_update"
  PERSONAL_DESTROY = "personal_destroy"
  PERSONAL_CSV = "personal_csv"
  
  CUPO_INDEX = "cupo_index"
  CUPO_SHOW = "cupo_show"
  CUPO_CREATE = "cupo_create"
  CUPO_UPDATE = "cupo_update"
  CUPO_DESTROY = "cupo_destroy"

  PEDIDO_INDEX = "pedido_index"
  PEDIDO_SHOW = "pedido_show"
  PEDIDO_CREATE = "pedido_create"
  PEDIDO_UPDATE = "pedido_update"
  PEDIDO_DESTROY = "pedido_destroy"

  SECTOR_INDEX = "sector_index"
  SECTOR_UPDATE = "sector_update"
  SECTOR_CREATE = "sector_create"
  SECTOR_ACTIVATE = "sector_activate"
  SECTOR_DEACTIVATE = "sector_deactivate"
  
  AUTORIZACION_INDEX = "autorizacion_index"

  SUMMARY_REQUESTS = "summary_requests"
  SUMMARY_AUTHORIZATIONS = "summary_authorizations"
  SUMMARY_DELIVERIES = "summary_deliveries"
  DELIVERY_SUMMARY = "delivery_summary"
