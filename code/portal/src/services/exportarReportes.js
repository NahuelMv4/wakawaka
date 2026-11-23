
function escaparCSV(valor) {
  const texto = String(valor ?? '')
  return `"${texto.replace(/"/g, '""')}"`
}

function agregarSeccionCSV(filas, titulo, registros, columnas) {
  filas.push(escaparCSV(titulo))

  filas.push(
    columnas.map(columna => escaparCSV(columna.titulo)).join(';')
  )

  for (const registro of registros) {
    filas.push(
      columnas
        .map(columna => escaparCSV(columna.obtener
          ? columna.obtener(registro)
          : registro[columna.campo]
        ))
        .join(';')
    )
  }

  filas.push('')
}

export function exportarReportesCSV({
  filtros,
  sectores,
  tiposComida,
  tiposMenu,
  agrupamientos,
  pedidos,
  autorizaciones,
  entregas
}) {
  const filas = []

  filas.push(escaparCSV('Reportes y estadísticas'))
  filas.push('')
  filas.push(escaparCSV('Filtros aplicados'))

  const sector = sectores.find(
    item => String(item.id) === String(filtros.sector_id)
  )

  const tipoComida = tiposComida.find(
    item => String(item.id) === String(filtros.tipo_comida_id)
  )

  const tipoMenu = tiposMenu.find(
    item => String(item.id) === String(filtros.tipo_menu_id)
  )

  const datosFiltros = [
    ['Fecha desde', filtros.fecha_desde || 'Todas'],
    ['Fecha hasta', filtros.fecha_hasta || 'Todas'],
    ['Sector', sector?.nombre || 'Todos'],
    ['Tipo de comida', tipoComida?.nombre || 'Todos'],
    ['Tipo de menú', tipoMenu?.nombre || 'Todos'],
    ['Condición (solo pedidos)', filtros.condicion || 'Todas']
  ]

  for (const [nombre, valor] of datosFiltros) {
    filas.push([
      escaparCSV(nombre),
      escaparCSV(valor)
    ].join(';'))
  }

  filas.push('')

  const columnasAgrupamiento = filtros.agrupar_por.map(campo => ({
    campo,
    titulo: agrupamientos.find(
      opcion => opcion.valor === campo
    )?.texto || campo
  }))

  agregarSeccionCSV(
    filas,
    'Pedidos',
    pedidos,
    [
      ...columnasAgrupamiento,
      { campo: 'total', titulo: 'Total' },
      { campo: 'total_regular', titulo: 'Regular' },
      { campo: 'total_excepcion', titulo: 'Excepción' }
    ]
  )

  agregarSeccionCSV(
    filas,
    'Autorizaciones',
    autorizaciones,
    [
      ...columnasAgrupamiento,
      { campo: 'total_pedido', titulo: 'Pedidos' },
      { campo: 'total_autorizado', titulo: 'Autorizados' },
      {
        titulo: 'No autorizadas',
        obtener: registro =>
          Number(registro.total_pedido || 0) -
          Number(registro.total_autorizado || 0)
      }
    ]
  )

  agregarSeccionCSV(
    filas,
    'Entregas',
    entregas,
    [
      ...columnasAgrupamiento,
      { campo: 'total_autorizado', titulo: 'Autorizados' },
      { campo: 'total_entregado', titulo: 'Entregados' },
      {
        titulo: 'No entregadas',
        obtener: registro =>
          Number(registro.total_autorizado || 0) -
          Number(registro.total_entregado || 0)
      }
    ]
  )

  const contenido = '\uFEFF' + filas.join('\r\n')
  const archivo = new Blob(
    [contenido],
    { type: 'text/csv;charset=utf-8;' }
  )

  const url = URL.createObjectURL(archivo)
  const enlace = document.createElement('a')

  enlace.href = url
  enlace.download = 'reportes-estadisticas.csv'
  document.body.appendChild(enlace)
  enlace.click()
  document.body.removeChild(enlace)

  URL.revokeObjectURL(url)
}
