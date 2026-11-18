from src.core.enums import (
  PermisoEnum,
  RolEnum,
  TipoComidaEnum,
  TipoMenuEnum,
  TipoPersonalEnum,
)
from src.core.services import (
  config_sistema_service,
  personal_service,
  rol_permiso_service,
  sector_service,
  tipo_comida_service,
  tipo_menu_service,
  tipo_personal_service,
  usuario_service,
)
from src.core.services.security import hashear_password


def run():
  print("Llenando base de datos...")

  s_quirofanos = sector_service.create_sector(
    nombre="Quirófanos",
    descripcion="Salas de cirugía general, cirugías programadas y de urgencia.",
  )
  s_guardia = sector_service.create_sector(
    nombre="Guardia",
    descripcion=" Sector destinado a la atención de urgencias, emergencias médicas y traumatológicas con unidades de shockroom y camas de observación.",
  )
  s_internacion = sector_service.create_sector(
    nombre="Internación",
    descripcion="Habitaciones generales para pacientes que requieren cuidado continuo, dividido en clínica médica, cirugía, maternidad o áreas críticas.",
  )
  s_consult_externo = sector_service.create_sector(  # noqa: F841
    nombre="Consultorios Externos",
    descripcion="Área dedicada a la atención programada de diversas especialidades médicas mediante turnos previos.",
  )
  s_terapia_intensiva = sector_service.create_sector(
    nombre="Terapia Intensiva y Unidad Coronaria",
    descripcion="Sectores de alta complejidad equipados con soporte vital para pacientes en estado crítico.",
  )
  s_diagnostico_imagenes = sector_service.create_sector(
    nombre="Diagnóstico por Imágenes",
    descripcion="Servicios de radiología, ecografía, tomografía computada y mamografías.",
  )
  print("Se agregaron datos a tabla SECTOR")

  tipo_comida_service.create_tipo_comida(
    nombre=TipoComidaEnum.DESAYUNO,
  )
  tipo_comida_service.create_tipo_comida(
    nombre=TipoComidaEnum.ALMUERZO,
  )
  tipo_comida_service.create_tipo_comida(
    nombre=TipoComidaEnum.MERIENDA,
  )
  tipo_comida_service.create_tipo_comida(
    nombre=TipoComidaEnum.CENA,
  )
  print("Se agregaron datos a tabla TIPO_COMIDA")

  general = tipo_menu_service.create_tipo_menu(
    nombre=TipoMenuEnum.GENERAL
  )
  vegetariano = tipo_menu_service.create_tipo_menu(
    nombre=TipoMenuEnum.VEGETARIANO
  )
  celiaco = tipo_menu_service.create_tipo_menu(
    nombre=TipoMenuEnum.CELIACO
  )
  print("Se agregaron datos a tabla TIPO_MENU")

  p_fijo = tipo_personal_service.create_tipo_personal(
    nombre=TipoPersonalEnum.FIJO
  )
  p_residente = tipo_personal_service.create_tipo_personal(
    nombre=TipoPersonalEnum.RESIDENTE
  )
  print("Se agregaron datos a tabla TIPO_PERSONAL")

  admin = rol_permiso_service.create_rol(
    nombre=RolEnum.ADMINISTRADOR
  )
  jefe_servicio = rol_permiso_service.create_rol(
    nombre=RolEnum.JEFE_SERVICIO
  )
  sector_comedor = rol_permiso_service.create_rol(
    nombre=RolEnum.SECTOR_COMEDOR
  )
  servicio_alimentacion = rol_permiso_service.create_rol(
    nombre=RolEnum.SERVICIO_ALIMENTACION
  )

  # Permisos de Usuarios
  p_u_index = rol_permiso_service.create_permiso(
    codigo=PermisoEnum.USER_INDEX
  )
  p_u_new = rol_permiso_service.create_permiso(
    codigo=PermisoEnum.USER_NEW
  )
  p_u_show = rol_permiso_service.create_permiso(
    codigo=PermisoEnum.USER_SHOW
  )
  p_u_update = rol_permiso_service.create_permiso(
    codigo=PermisoEnum.USER_UPDATE
  )
  p_u_destroy = rol_permiso_service.create_permiso(
    codigo=PermisoEnum.USER_DESTROY
  )
  p_u_block = rol_permiso_service.create_permiso(
    codigo=PermisoEnum.USER_BLOCK
  )
  p_u_unlock = rol_permiso_service.create_permiso(
    codigo=PermisoEnum.USER_UNLOCK
  )

  # Permisos de Configuración
  p_c_index = rol_permiso_service.create_permiso(
    codigo=PermisoEnum.CONFIG_INDEX
  )
  p_c_activate = rol_permiso_service.create_permiso(
    codigo=PermisoEnum.CONFIG_ACTIVATE
  )
  p_c_deactivate = rol_permiso_service.create_permiso(
    codigo=PermisoEnum.CONFIG_DEACTIVATE
  )

  # Permisos de Personal
  p_p_index = rol_permiso_service.create_permiso(
    codigo=PermisoEnum.PERSONAL_INDEX
  )
  p_p_create = rol_permiso_service.create_permiso(
    codigo=PermisoEnum.PERSONAL_CREATE
  )
  p_p_show = rol_permiso_service.create_permiso(
    codigo=PermisoEnum.PERSONAL_SHOW
  )
  p_p_update = rol_permiso_service.create_permiso(
    codigo=PermisoEnum.PERSONAL_UPDATE
  )
  p_p_destroy = rol_permiso_service.create_permiso(
    codigo=PermisoEnum.PERSONAL_DESTROY
  )
  p_p_csv = rol_permiso_service.create_permiso(
    codigo=PermisoEnum.PERSONAL_CSV
  )

  # Permisos de Cupos
  p_cupo_index = rol_permiso_service.create_permiso(
    codigo=PermisoEnum.CUPO_INDEX
  )
  p_cupo_show = rol_permiso_service.create_permiso(
    codigo=PermisoEnum.CUPO_SHOW
  )
  p_cupo_create = rol_permiso_service.create_permiso(
    codigo=PermisoEnum.CUPO_CREATE
  )
  p_cupo_update = rol_permiso_service.create_permiso(
    codigo=PermisoEnum.CUPO_UPDATE
  )
  p_cupo_destroy = rol_permiso_service.create_permiso(
    codigo=PermisoEnum.CUPO_DESTROY
  )

  # Permisos de Pedidos
  p_ped_index = rol_permiso_service.create_permiso(
    codigo=PermisoEnum.PEDIDO_INDEX
  )
  p_ped_show = rol_permiso_service.create_permiso(
    codigo=PermisoEnum.PEDIDO_SHOW
  )
  p_ped_create = rol_permiso_service.create_permiso(
    codigo=PermisoEnum.PEDIDO_CREATE
  )
  p_ped_update = rol_permiso_service.create_permiso(
    codigo=PermisoEnum.PEDIDO_UPDATE
  )
  p_ped_destroy = rol_permiso_service.create_permiso(
    codigo=PermisoEnum.PEDIDO_DESTROY
  )

  permisos_usuario = [p_u_index, p_u_new, p_u_show, p_u_update, p_u_destroy, p_u_block, p_u_unlock]
  permisos_personal = [p_p_index, p_p_create, p_p_show, p_p_update, p_p_destroy, p_p_csv]
  permisos_configuracion = [p_c_index, p_c_activate, p_c_deactivate]
  permisos_cupo_lectura = [p_cupo_index, p_cupo_show]
  permisos_cupo_total = [p_cupo_index, p_cupo_show, p_cupo_create, p_cupo_update, p_cupo_destroy]
  permisos_pedido = [p_ped_index, p_ped_show, p_ped_create, p_ped_update, p_ped_destroy]

  rol_permiso_service.asignar_permisos_a_rol(admin, permisos_usuario)
  rol_permiso_service.asignar_permisos_a_rol(admin, permisos_configuracion)
  rol_permiso_service.asignar_permisos_a_rol(admin, permisos_personal)

  # El jefe de servicio puede gestionar personal, consultar cupos y gestionar pedidos de su sector
  rol_permiso_service.asignar_permisos_a_rol(
    jefe_servicio,
    [p_p_index, p_p_create, p_p_show, p_p_update, p_p_destroy] + permisos_cupo_lectura + permisos_pedido,
  )

  rol_permiso_service.asignar_permisos_a_rol(sector_comedor, permisos_personal)

  # El servicio de alimentación administra el CRUD completo de cupos
  rol_permiso_service.asignar_permisos_a_rol(servicio_alimentacion, permisos_personal + permisos_cupo_total)

  print("Se agregaron datos a tabla ROL y a tabla PERMISO, se asignaron los permisos a cada Rol")

  usuario_service.create_usuario(
    email="user1@gmail.com",
    contrasenia=hashear_password("1234"),
    nombre="Brian",
    apellido="Perez",
    dni="37825229",
    rol=admin,
    sector=s_guardia
  )

  usuario_service.create_usuario(
    email="user2@gmail.com",
    contrasenia=hashear_password("1234"),
    nombre="Julian",
    apellido="Alvarez",
    dni="40875269",
    rol=servicio_alimentacion,
    sector=s_internacion
  )

  usuario_service.create_usuario(
    email="user3@gmail.com",
    contrasenia=hashear_password("1234"),
    nombre="Lisandro",
    apellido="Quiroga",
    dni="34811322",
    rol=sector_comedor,
    sector=s_diagnostico_imagenes
  )

  usuario_service.create_usuario(
    email="user4@gmail.com",
    contrasenia=hashear_password("1234"),
    nombre="Enzo",
    apellido="Almeida",
    dni="40234768",
    rol=jefe_servicio,
    sector=s_diagnostico_imagenes
  )
  print("Se agregaron datos a tabla USUARIO")

  config_sistema_service.create_configuracion(
    clave="sys_config",
    paginacion=25,
    mensaje_mantenimiento="Sistema actualmente en mantenimiento, disculpe las molestias."
  )
  print("Se agregaron datos a tabla CONFIGURACION_SISTEMA")

  personal_service.popular_personal(
    nombre="Brian",
    apellido="Perez",
    dni="37825229",
    tipo_personal=p_fijo,
    sector=s_quirofanos,
    tipo_menu=general,
  )

  personal_service.popular_personal(
    nombre="Sergui",
    apellido="Alvarez",
    dni="39015029",
    tipo_personal=p_residente,
    tipo_menu=vegetariano,
  )

  personal_service.popular_personal(
    nombre="Max",
    apellido="Holtz",
    dni="38385738",
    tipo_personal=p_fijo,
    sector=s_terapia_intensiva,
    tipo_menu=celiaco,
  )
  print("Se agregaron datos a tabla PERSONAL")

  print("Proceso terminado.")