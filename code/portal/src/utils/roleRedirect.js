export function obtenerRutaInicialPorRol(rol) {
  switch (rol) {
    case 'Jefe de Servicio': 
      return { name: 'pedidos' }
    case 'Servicio de Alimentación': 
      return { name: 'autorizacion' }
    case 'Sector Comedor': 
      return { name: 'kiosco-busqueda' }
    default:
      return { name: 'dashboard' }
  }
}