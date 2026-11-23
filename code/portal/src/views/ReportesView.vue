<script setup>
import { ref, computed, onMounted } from 'vue'

import {
  obtenerResumenPedidos,
  obtenerResumenAutorizaciones,
  obtenerResumenEntregas,
  obtenerTiposComida
} from '@/services/resumenes'

import { obtenerTiposMenu } from '@/services/pedidos'
import { apiFetch } from '@/services/api'
import { exportarReportesCSV } from '@/services/exportarReportes'

import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
  ArcElement,
  PointElement,
  LineElement
} from 'chart.js'

import { Bar, Doughnut, Line } from 'vue-chartjs'

ChartJS.register(
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
  ArcElement,
  PointElement,
  LineElement
)

const filtros = ref({
  fecha_desde: '',
  fecha_hasta: '',
  sector_id: '',
  tipo_comida_id: '',
  tipo_menu_id: '',
  condicion: '',
  agrupar_por: ['sector']
})

const sectores = ref([])
const tiposComida = ref([])
const tiposMenu = ref([])

const pedidos = ref([])
const autorizaciones = ref([])
const entregas = ref([])

const datosGraficos = ref({
  por_sector: [],
  por_tipo_menu: [],
  evolucion: []
})

const cargando = ref(false)
const error = ref('')

const agrupamientos = [
  { valor: 'sector', texto: 'Sector' },
  { valor: 'tipo_comida', texto: 'Tipo de comida' },
  { valor: 'tipo_menu', texto: 'Tipo de menú' },
  { valor: 'dia', texto: 'Día' },
  { valor: 'semana', texto: 'Semana' },
  { valor: 'mes', texto: 'Mes' }
]

async function cargarFiltros() {
  const [resSectores, resComidas, resMenus] = await Promise.all([
    apiFetch('/sectores/?activo=true'),
    obtenerTiposComida(),
    obtenerTiposMenu()
  ])

  sectores.value = Array.isArray(resSectores)
    ? resSectores
    : resSectores?.data || []

  tiposComida.value = resComidas
  tiposMenu.value = resMenus
}

function obtenerFiltrosConsulta() {
  const filtrosComunes = { ...filtros.value }

  delete filtrosComunes.condicion

  if (!filtrosComunes.sector_id) {
    delete filtrosComunes.sector_id
  }

  if (!filtrosComunes.tipo_comida_id) {
    delete filtrosComunes.tipo_comida_id
  }

  if (!filtrosComunes.tipo_menu_id) {
    delete filtrosComunes.tipo_menu_id
  }

  filtrosComunes.agrupar_por = filtrosComunes.agrupar_por.join(',')

  const filtrosPedidos = { ...filtrosComunes }

  if (filtros.value.condicion) {
    filtrosPedidos.condicion = filtros.value.condicion
  }

  return {
    filtrosComunes,
    filtrosPedidos
  }
}

async function consultarReportes() {
  error.value = ''

  if (
    filtros.value.fecha_desde &&
    filtros.value.fecha_hasta &&
    filtros.value.fecha_desde > filtros.value.fecha_hasta
  ) {
    error.value = 'La fecha desde no puede ser posterior a la fecha hasta.'
    return
  }

  if (filtros.value.agrupar_por.length === 0) {
    error.value = 'Seleccioná al menos un criterio de agrupamiento.'
    return
  }

  const cantidadTemporales = filtros.value.agrupar_por.filter(
    valor => ['dia', 'semana', 'mes'].includes(valor)
  ).length

  if (cantidadTemporales > 1) {
    error.value = 'Solo podés seleccionar un agrupamiento temporal.'
    return
  }

  cargando.value = true

  try {
    const { filtrosComunes, filtrosPedidos } = obtenerFiltrosConsulta()

    const [resPedidos, resAutorizaciones, resEntregas] =
      await Promise.all([
        obtenerResumenPedidos(filtrosPedidos),
        obtenerResumenAutorizaciones(filtrosComunes),
        obtenerResumenEntregas(filtrosComunes)
      ])

    pedidos.value = resPedidos?.data || []
    autorizaciones.value = resAutorizaciones?.data || []
    entregas.value = resEntregas?.data || []

    datosGraficos.value = resPedidos?.graficos || {
      por_sector: [],
      por_tipo_menu: [],
      evolucion: []
    }
  } catch (err) {
    error.value = err?.message || 'No se pudieron obtener los reportes.'
  } finally {
    cargando.value = false
  }
}

function totalizar(datos, campo) {
  return datos.reduce(
    (total, registro) => total + Number(registro[campo] || 0),
    0
  )
}

function totalNoRetiradas() {
  return Math.max(
    0,
    totalizar(entregas.value, 'total_autorizado') -
    totalizar(entregas.value, 'total_entregado')
  )
}

/* PALETA DE COLORES */

const colores = [
  '#42A5F5',
  '#66BB6A',
  '#FFA726',
  '#AB47BC',
  '#EF5350',
  '#26A69A',
  '#EC407A',
  '#78909C'
]

/* GRÁFICO 1: comparación general */

const datosComparacion = computed(() => ({
  labels: ['Pedidas', 'Autorizadas', 'Entregadas'],
  datasets: [
    {
      label: 'Cantidad de comidas',
      data: [
        totalizar(pedidos.value, 'total'),
        totalizar(autorizaciones.value, 'total_autorizado'),
        totalizar(entregas.value, 'total_entregado')
      ],
      backgroundColor: [
        '#42A5F5',
        '#66BB6A',
        '#FFA726'
      ],
      borderColor: [
        '#1E88E5',
        '#43A047',
        '#FB8C00'
      ],
      borderWidth: 1
    }
  ]
}))

/* GRÁFICO 2: comidas por sector */

const datosPorSector = computed(() => ({
  labels: datosGraficos.value.por_sector.map(
    registro => registro.categoria
  ),
  datasets: [
    {
      label: 'Comidas pedidas',
      data: datosGraficos.value.por_sector.map(
        registro => registro.total
      ),
      backgroundColor: datosGraficos.value.por_sector.map(
        (_, index) => colores[index % colores.length]
      ),
      borderColor: '#FFFFFF',
      borderWidth: 2
    }
  ]
}))

/* GRÁFICO 3: comidas por tipo de menú */

const datosPorMenu = computed(() => ({
  labels: datosGraficos.value.por_tipo_menu.map(
    registro => registro.categoria
  ),
  datasets: [
    {
      label: 'Comidas pedidas',
      data: datosGraficos.value.por_tipo_menu.map(
        registro => registro.total
      ),
      backgroundColor: datosGraficos.value.por_tipo_menu.map(
        (_, index) => colores[index % colores.length]
      ),
      borderColor: '#FFFFFF',
      borderWidth: 2
    }
  ]
}))

/* GRÁFICO 4: evolución diaria */

const datosEvolucion = computed(() => ({
  labels: datosGraficos.value.evolucion.map(
    registro => registro.categoria
  ),
  datasets: [
    {
      label: 'Comidas pedidas',
      data: datosGraficos.value.evolucion.map(
        registro => registro.total
      ),
      borderColor: '#42A5F5',
      backgroundColor: 'rgba(66, 165, 245, 0.2)',
      pointBackgroundColor: '#1E88E5',
      pointBorderColor: '#FFFFFF',
      pointRadius: 4,
      pointHoverRadius: 6,
      tension: 0.3,
      fill: true
    }
  ]
}))

const opcionesGraficos = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: true
    }
  }
}

const opcionesBarras = {
  ...opcionesGraficos,
  scales: {
    y: {
      beginAtZero: true,
      ticks: {
        precision: 0
      }
    }
  }
}

/* EXPORTACIÓN CSV */

function exportarCSV() {
  exportarReportesCSV({
    filtros: filtros.value,
    sectores: sectores.value,
    tiposComida: tiposComida.value,
    tiposMenu: tiposMenu.value,
    agrupamientos,
    pedidos: pedidos.value,
    autorizaciones: autorizaciones.value,
    entregas: entregas.value
  })
}

onMounted(async () => {
  try {
    await cargarFiltros()
    await consultarReportes()
  } catch (err) {
    error.value = err?.message || 'No se pudieron cargar los filtros.'
  }
})
</script>

<template>
  <section class="reportes">
    <header class="encabezado">
      <h1>Reportes y estadísticas</h1>
      <p>Consultá información sobre pedidos, autorizaciones y entregas.</p>
    </header>

    <!-- FILTROS -->
    <section class="panel filtros">
      <h2>Filtros de consulta</h2>

      <div class="filtros-grid">
        <label>
          Fecha desde
          <input type="date" v-model="filtros.fecha_desde">
        </label>

        <label>
          Fecha hasta
          <input type="date" v-model="filtros.fecha_hasta">
        </label>

        <label>
          Sector
          <select v-model="filtros.sector_id">
            <option value="">Todos los sectores</option>
            <option
              v-for="sector in sectores"
              :key="sector.id"
              :value="sector.id"
            >
              {{ sector.nombre }}
            </option>
          </select>
        </label>

        <label>
          Tipo de comida
          <select v-model="filtros.tipo_comida_id">
            <option value="">Todos los tipos</option>
            <option
              v-for="tipo in tiposComida"
              :key="tipo.id"
              :value="tipo.id"
            >
              {{ tipo.nombre }}
            </option>
          </select>
        </label>

        <label>
          Tipo de menú
          <select v-model="filtros.tipo_menu_id">
            <option value="">Todos los menús</option>
            <option
              v-for="tipo in tiposMenu"
              :key="tipo.id"
              :value="tipo.id"
            >
              {{ tipo.nombre }}
            </option>
          </select>
        </label>

        <label>
          Condición (solo pedidos)
          <select v-model="filtros.condicion">
            <option value="">Todas</option>
            <option value="Excepción">Excepción</option>
            <option value="Regular">Regular</option>
          </select>
        </label>
      </div>

      <div class="agrupamientos">
        <h3>Agrupar resultados por</h3>

        <label
          v-for="opcion in agrupamientos"
          :key="opcion.valor"
          class="opcion-agrupamiento"
        >
          <input
            type="checkbox"
            :value="opcion.valor"
            v-model="filtros.agrupar_por"
          >
          {{ opcion.texto }}
        </label>
      </div>

      <button
        class="btn-consultar"
        :disabled="cargando"
        @click="consultarReportes"
      >
        {{ cargando ? 'Consultando...' : 'Consultar reportes' }}
      </button>

      <button
        class="btn-exportar"
        :disabled="cargando"
        @click="exportarCSV"
      >
        Exportar CSV
      </button>

      <p v-if="error" class="mensaje-error">
        {{ error }}
      </p>
    </section>

    <!-- INDICADORES GENERALES -->
    <section class="indicadores">
      <article class="indicador">
        <span>Total de comidas pedidas</span>
        <strong>{{ totalizar(pedidos, 'total') }}</strong>
      </article>

      <article class="indicador">
        <span>Total autorizadas</span>
        <strong>{{ totalizar(autorizaciones, 'total_autorizado') }}</strong>
      </article>

      <article class="indicador">
        <span>Total entregadas</span>
        <strong>{{ totalizar(entregas, 'total_entregado') }}</strong>
      </article>

      <article class="indicador">
        <span>Total no retiradas</span>
        <strong>{{ totalNoRetiradas() }}</strong>
      </article>
    </section>

    <!-- GRÁFICOS -->
    <section class="graficos">
      <article class="panel">
        <h2>Comparación de comidas</h2>

        <div class="grafico-contenedor">
          <Bar
            :data="datosComparacion"
            :options="opcionesBarras"
          />
        </div>
      </article>

      <div class="graficos-grid">
        <article class="panel">
          <h2>Comidas pedidas por sector</h2>

          <p v-if="datosGraficos.por_sector.length === 0">
            No hay datos para mostrar.
          </p>

          <div v-else class="grafico-contenedor">
            <Doughnut
              :data="datosPorSector"
              :options="opcionesGraficos"
            />
          </div>
        </article>

        <article class="panel">
          <h2>Comidas pedidas por tipo de menú</h2>

          <p v-if="datosGraficos.por_tipo_menu.length === 0">
            No hay datos para mostrar.
          </p>

          <div v-else class="grafico-contenedor">
            <Doughnut
              :data="datosPorMenu"
              :options="opcionesGraficos"
            />
          </div>
        </article>
      </div>

      <article class="panel">
        <h2>Evolución de comidas pedidas</h2>

        <p v-if="datosGraficos.evolucion.length === 0">
          No hay datos para mostrar.
        </p>

        <div v-else class="grafico-contenedor grafico-evolucion">
          <Line
            :data="datosEvolucion"
            :options="opcionesBarras"
          />
        </div>
      </article>
    </section>

    <!-- TABLAS -->
    <section class="resultados">

      <!-- PEDIDOS -->
      <article class="panel">
        <h2>Pedidos</h2>

        <p v-if="pedidos.length === 0">
          No hay resultados para mostrar.
        </p>

        <div v-else class="tabla-contenedor">
          <table>
            <thead>
              <tr>
                <th v-for="campo in filtros.agrupar_por" :key="campo">
                  {{ agrupamientos.find(a => a.valor === campo)?.texto }}
                </th>
                <th>Total</th>
                <th>Regular</th>
                <th>Excepción</th>
              </tr>
            </thead>

            <tbody>
              <tr v-for="(registro, index) in pedidos" :key="index">
                <td v-for="campo in filtros.agrupar_por" :key="campo">
                  {{ registro[campo] ?? '-' }}
                </td>

                <td>{{ registro.total }}</td>
                <td>{{ registro.total_regular }}</td>
                <td>{{ registro.total_excepcion }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </article>

      <!-- AUTORIZACIONES -->
      <article class="panel">
        <h2>Autorizaciones</h2>

        <p v-if="autorizaciones.length === 0">
          No hay resultados para mostrar.
        </p>

        <div v-else class="tabla-contenedor">
          <table>
            <thead>
              <tr>
                <th v-for="campo in filtros.agrupar_por" :key="campo">
                  {{ agrupamientos.find(a => a.valor === campo)?.texto }}
                </th>
                <th>Pedidos</th>
                <th>Autorizados</th>
                <th>No autorizadas</th>
              </tr>
            </thead>

            <tbody>
              <tr
                v-for="(registro, index) in autorizaciones"
                :key="index"
              >
                <td v-for="campo in filtros.agrupar_por" :key="campo">
                  {{ registro[campo] ?? '-' }}
                </td>

                <td>{{ registro.total_pedido }}</td>
                <td>{{ registro.total_autorizado }}</td>
                <td>
                  {{
                    Number(registro.total_pedido || 0) -
                    Number(registro.total_autorizado || 0)
                  }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </article>

      <!-- ENTREGAS -->
      <article class="panel">
        <h2>Entregas</h2>

        <p v-if="entregas.length === 0">
          No hay resultados para mostrar.
        </p>

        <div v-else class="tabla-contenedor">
          <table>
            <thead>
              <tr>
                <th v-for="campo in filtros.agrupar_por" :key="campo">
                  {{ agrupamientos.find(a => a.valor === campo)?.texto }}
                </th>
                <th>Autorizados</th>
                <th>Entregados</th>
                <th>No entregadas</th>
              </tr>
            </thead>

            <tbody>
              <tr v-for="(registro, index) in entregas" :key="index">
                <td v-for="campo in filtros.agrupar_por" :key="campo">
                  {{ registro[campo] ?? '-' }}
                </td>

                <td>{{ registro.total_autorizado }}</td>
                <td>{{ registro.total_entregado }}</td>
                <td>
                  {{
                    Number(registro.total_autorizado || 0) -
                    Number(registro.total_entregado || 0)
                  }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </article>
    </section>
  </section>
</template>

<style scoped>
.reportes {
  display: flex;
  flex-direction: column;
  gap: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.encabezado h1 {
  color: #2d3748;
  margin-bottom: 8px;
}

.encabezado p {
  color: #718096;
}

.panel,
.indicador {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 24px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.04);
}

.panel h2 {
  margin: 0 0 20px;
  color: #2d3748;
}

.filtros-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
  gap: 18px;
}

.filtros-grid label {
  display: flex;
  flex-direction: column;
  gap: 8px;
  font-weight: 600;
  color: #4a5568;
}

input,
select {
  padding: 10px;
  border: 1px solid #cbd5e0;
  border-radius: 6px;
  font: inherit;
  min-width: 0;
}

.agrupamientos {
  margin-top: 24px;
}

.agrupamientos h3 {
  font-size: 16px;
  margin-bottom: 12px;
}

.opcion-agrupamiento {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin: 0 18px 10px 0;
  color: #4a5568;
}

.opcion-agrupamiento input {
  accent-color: #42b883;
}

.btn-consultar,
.btn-exportar {
  margin-top: 16px;
  margin-right: 8px;
  padding: 11px 20px;
  border: none;
  border-radius: 6px;
  color: white;
  font-weight: 600;
  cursor: pointer;
}

.btn-consultar {
  background: #42b883;
}

.btn-consultar:hover {
  background: #369b70;
}

.btn-exportar {
  background: #3182ce;
}

.btn-exportar:hover {
  background: #2b6cb0;
}

.btn-consultar:disabled,
.btn-exportar:disabled {
  opacity: 0.6;
  cursor: wait;
}

.mensaje-error {
  color: #c53030;
  margin-top: 12px;
}

.indicadores {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
  gap: 18px;
}

.indicador {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.indicador span {
  color: #718096;
  font-weight: 600;
}

.indicador strong {
  font-size: 30px;
  color: #2c3e50;
}

.graficos {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.graficos-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 20px;
}

.grafico-contenedor {
  position: relative;
  width: 100%;
  height: 320px;
}

.grafico-evolucion {
  height: 350px;
}

.resultados {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.tabla-contenedor {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

th,
td {
  padding: 12px;
  border-bottom: 1px solid #e2e8f0;
  white-space: nowrap;
}

th {
  color: #2c3e50;
  background: #f7fafc;
}

@media (max-width: 750px) {
  .graficos-grid {
    grid-template-columns: 1fr;
  }

  .grafico-contenedor {
    height: 280px;
  }
}

@media (max-width: 600px) {
  .panel {
    padding: 16px;
  }
}
</style>
