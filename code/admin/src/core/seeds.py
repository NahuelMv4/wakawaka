from datetime import date, time, timedelta
from datetime import datetime, timezone
from src.core.database import db
from src.core.models import Pedido, SolicitudComida
from src.core.enums import (
  PermisoEnum,
  RolEnum,
  TipoComidaEnum,
  TipoMenuEnum,
  TipoPersonalEnum,
)
from src.core.services import (
  config_sistema_service,
  cupo_service,
  pedido_service,
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

  c_desayuno = tipo_comida_service.create_tipo_comida(
    nombre=TipoComidaEnum.DESAYUNO,
    hora_inicio=time(8, 0),
    hora_fin=time(12, 0),
  )
  c_almuerzo = tipo_comida_service.create_tipo_comida(
    nombre=TipoComidaEnum.ALMUERZO,
    hora_inicio=time(12, 0),
    hora_fin=time(15, 0),
  )
  c_merienda = tipo_comida_service.create_tipo_comida(
    nombre=TipoComidaEnum.MERIENDA,
    hora_inicio=time(15, 0),
    hora_fin=time(20, 0),
  )
  c_cena = tipo_comida_service.create_tipo_comida(
    nombre=TipoComidaEnum.CENA,
    hora_inicio=time(20, 0),
    hora_fin=time(23, 0),
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

  # Permisos de Sectores
  p_sector_index = rol_permiso_service.create_permiso(
    codigo=PermisoEnum.SECTOR_INDEX
  )
  p_sector_update = rol_permiso_service.create_permiso(
    codigo=PermisoEnum.SECTOR_UPDATE
  )
  p_sector_create = rol_permiso_service.create_permiso(
    codigo=PermisoEnum.SECTOR_CREATE
  )
  p_sector_activate = rol_permiso_service.create_permiso(
    codigo=PermisoEnum.SECTOR_ACTIVATE
  )
  p_sector_deactivate = rol_permiso_service.create_permiso(
    codigo=PermisoEnum.SECTOR_DEACTIVATE
  )

  p_autorizacion_index = rol_permiso_service.create_permiso(
    codigo=PermisoEnum.AUTORIZACION_INDEX
  )

  # Permisos de Resumenes
  p_summary_requests = rol_permiso_service.create_permiso(
      codigo=PermisoEnum.SUMMARY_REQUESTS
  )
  p_summary_authorizations = rol_permiso_service.create_permiso(
      codigo=PermisoEnum.SUMMARY_AUTHORIZATIONS
  )
  p_summary_deliveries = rol_permiso_service.create_permiso(
      codigo=PermisoEnum.SUMMARY_DELIVERIES
  )
  p_delivery_summary = rol_permiso_service.create_permiso(
      codigo=PermisoEnum.DELIVERY_SUMMARY
  )

  permisos_usuario = [p_u_index, p_u_new, p_u_show, p_u_update, p_u_destroy, p_u_block, p_u_unlock]
  permisos_personal = [p_p_index, p_p_create, p_p_show, p_p_update, p_p_destroy, p_p_csv]
  permisos_configuracion = [p_c_index, p_c_activate, p_c_deactivate]
  permisos_cupo_lectura = [p_cupo_index, p_cupo_show]
  permisos_cupo_total = [p_cupo_index, p_cupo_show, p_cupo_create, p_cupo_update, p_cupo_destroy]
  permisos_pedido = [p_ped_index, p_ped_show, p_ped_create, p_ped_update, p_ped_destroy]
  permisos_sector = [p_sector_index, p_sector_update, p_sector_create, p_sector_activate, p_sector_deactivate]
  permisos_summary = [p_summary_requests, p_summary_authorizations, p_summary_deliveries, p_delivery_summary]

  rol_permiso_service.asignar_permisos_a_rol(admin, permisos_usuario)
  rol_permiso_service.asignar_permisos_a_rol(admin, permisos_configuracion)
  rol_permiso_service.asignar_permisos_a_rol(admin, permisos_personal)
  rol_permiso_service.asignar_permisos_a_rol(admin, permisos_sector)

  # El jefe de servicio puede gestionar personal, consultar cupos y gestionar pedidos de su sector
  rol_permiso_service.asignar_permisos_a_rol(
    jefe_servicio,
    [p_p_index, p_p_create, p_p_show, p_p_update, p_p_destroy, p_summary_requests] + permisos_cupo_lectura + permisos_pedido,
  )

  rol_permiso_service.asignar_permisos_a_rol(sector_comedor, [p_delivery_summary] + permisos_personal)

  # El servicio de alimentación administra el CRUD completo de cupos
  rol_permiso_service.asignar_permisos_a_rol(servicio_alimentacion, permisos_personal + permisos_cupo_total + [p_autorizacion_index] + permisos_summary)

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

  u_jefe_diagnostico = usuario_service.create_usuario(
    email="user4@gmail.com",
    contrasenia=hashear_password("1234"),
    nombre="Enzo",
    apellido="Almeida",
    dni="40234768",
    rol=jefe_servicio,
    sector=s_diagnostico_imagenes
  )

  usuario_service.create_usuario(
    email="ezequielb.perez@gmail.com",
    contrasenia=hashear_password("1234"),
    nombre="Brian",
    apellido="Perez",
    dni="37234768",
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

  pers_diag_1 = personal_service.popular_personal(
    nombre="Sofía",
    apellido="Fernández",
    dni="35112233",
    tipo_personal=p_fijo,
    sector=s_diagnostico_imagenes,
    tipo_menu=general,
  )

  pers_diag_2 = personal_service.popular_personal(
    nombre="Martín",
    apellido="Gómez",
    dni="36445566",
    tipo_personal=p_fijo,
    sector=s_diagnostico_imagenes,
    tipo_menu=vegetariano,
  )

  pers_diag_3 = personal_service.popular_personal(
    nombre="Sofía",
    apellido="Acosta",
    dni="38778899",
    tipo_personal=p_fijo,
    sector=s_diagnostico_imagenes,
    tipo_menu=celiaco,
  )
  print("Se agregaron datos a tabla PERSONAL")

  cupo_service.create_cupo({"sector_id": s_diagnostico_imagenes.id, "tipo_comida_id": c_desayuno.id, "cantidad": 3})
  cupo_service.create_cupo({"sector_id": s_diagnostico_imagenes.id, "tipo_comida_id": c_almuerzo.id, "cantidad": 2})
  cupo_service.create_cupo({"sector_id": s_diagnostico_imagenes.id, "tipo_comida_id": c_merienda.id, "cantidad": 3})
  cupo_service.create_cupo({"sector_id": s_diagnostico_imagenes.id, "tipo_comida_id": c_cena.id, "cantidad": 2})
  print("Se agregaron datos a tabla CUPO")

  pedido_service.crear_pedidos(
    data={
      "periodicidad": "diaria",
      "fecha_inicio": date.today() + timedelta(days=2),
      "comidas": {
        "almuerzo": [pers_diag_1.id, pers_diag_2.id, pers_diag_3.id],
      },
    },
    usuario_id=u_jefe_diagnostico.id,
    sector_id=s_diagnostico_imagenes.id,
  )
  print("Se agregaron datos a tabla PEDIDO")


  #Prueba de la función consultar_comidas_autorizadas
  hoy = date.today()
  ahora_utc = datetime.now(timezone.utc)

  comidas_seed = [
    (c_desayuno, [pers_diag_1, pers_diag_2, pers_diag_3]),
    (c_almuerzo, [pers_diag_1, pers_diag_2]),
    (c_merienda, [pers_diag_1, pers_diag_2, pers_diag_3]),
    (c_cena, [pers_diag_1, pers_diag_3]),
  ]

  for tipo_comida_obj, lista_personas in comidas_seed:
    nuevo_pedido = Pedido(
      fecha_desde=ahora_utc,
      fecha_hasta=ahora_utc,
      estado="autorizado",
      sector_id=s_diagnostico_imagenes.id,
      tipo_comida_id=tipo_comida_obj.id,
      usuario_id=u_jefe_diagnostico.id,
    )
    db.session.add(nuevo_pedido)
    db.session.flush()  # Obtiene nuevo_pedido.id antes del commit

    for persona in lista_personas:
      solicitud = SolicitudComida(
        fecha_comida=hoy,
        condicion="autorizado",
        pedido_id=nuevo_pedido.id,
        personal_id=persona.id,
        tipo_menu_id=persona.tipo_menu_id,
      )
      db.session.add(solicitud)

  db.session.commit()
  print("Se agregaron y autorizaron pedidos para HOY")

  print("Proceso terminado.")