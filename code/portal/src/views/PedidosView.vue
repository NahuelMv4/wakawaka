<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import {
  eliminarPedido,
  listarPedidos,
  obtenerConfiguracionSistema,
  obtenerPedido,
  obtenerTiposMenu,
} from '@/services/pedidos'
import { manejarErrorApi } from '@/utils/apiErrorHandler.js'

const router = useRouter()
const auth = useAuthStore()

const pedidos = ref([])
const tiposMenu = ref([])
const cargando = ref(false)
const error = ref('')
const mensajeExito = ref('')
const horarioCorte = ref('18:00')

const paginacion = reactive({
  page: 1,
  pages: 1,
  total: 0,
})

const filtros = reactive({
  estado: '',
  tipo_comida_id: '',
  tipo_menu_id: '',
  fecha_desde: '',
  fecha_hasta: '',
})

// Modal de detalle
const pedidoSeleccionado = ref(null)
const cargandoDetalle = ref(false)

const puedeCrear = computed(() => auth.user?.permisos?.includes('pedido_create'))
const puedeEditar = computed(() => auth.user?.permisos?.includes('pedido_update'))
const puedeEliminar = computed(() => auth.user?.permisos?.includes('pedido_destroy'))

const COMIDAS = [
  { id: 1, nombre: 'Desayuno' },
  { id: 2, nombre: 'Almuerzo' },
  { id: 3, nombre: 'Merienda' },
  { id: 4, nombre: 'Cena' },
]

function esModificable(pedido) {
  if (pedido.estado !== 'Confirmado') return false
  const [horas, minutos] = (horarioCorte.value || '18:00').split(':').map(Number)
  const [y, m, d] = pedido.fecha.split('-').map(Number)
  const limite = new Date(y, m - 1, d - 1, horas, minutos, 0, 0)
  return new Date() < limite
}

async function cargarConfiguracionYCatalogos() {
  try {
    const [config, menusRes] = await Promise.all([
      obtenerConfiguracionSistema().catch(() => null),
      obtenerTiposMenu().catch(() => []),
    ])
    if (config?.horario_corte) {
      horarioCorte.value = config.horario_corte
    }
    tiposMenu.value = Array.isArray(menusRes) ? menusRes : menusRes.data || menusRes.items || []
  } catch {
    // Mantiene los valores por defecto si falla la lectura inicial
  }
}

async function cargarPedidos(pagina = 1) {
  cargando.value = true
  error.value = ''
  try {
    const res = await listarPedidos({
      page: pagina,
      estado: filtros.estado || undefined,
      tipo_comida_id: filtros.tipo_comida_id || undefined,
      tipo_menu_id: filtros.tipo_menu_id || undefined,
      fecha_desde: filtros.fecha_desde || undefined,
      fecha_hasta: filtros.fecha_hasta || undefined,
    })
    pedidos.value = res.data || []
    paginacion.page = res.page || 1
    paginacion.pages = res.pages || 1
    paginacion.total = res.total || 0
  } catch (err) {
    error.value = await manejarErrorApi(err, router, {
      mensajePorDefecto: 'No se pudieron cargar los pedidos.',
    })
  } finally {
    cargando.value = false
  }
}

function limpiarFiltros() {
  filtros.estado = ''
  filtros.tipo_comida_id = ''
  filtros.tipo_menu_id = ''
  filtros.fecha_desde = ''
  filtros.fecha_hasta = ''
  cargarPedidos(1)
}

async function verDetalle(pedido) {
  cargandoDetalle.value = true
  error.value = ''
  try {
    pedidoSeleccionado.value = await obtenerPedido(pedido.id)
  } catch (err) {
    error.value = await manejarErrorApi(err, router, {
      mensajePorDefecto: 'No se pudo obtener el detalle del pedido.',
    })
  } finally {
    cargandoDetalle.value = false
  }
}

function cerrarModal() {
  pedidoSeleccionado.value = null
}

async function confirmarEliminacion(pedido) {
  const ok = window.confirm(
    `¿Seguro que deseas eliminar el pedido de ${pedido.tipo_comida} para el ${pedido.fecha_formateada}?`
  )
  if (!ok) return

  error.value = ''
  mensajeExito.value = ''
  try {
    await eliminarPedido(pedido.id)
    mensajeExito.value = 'Pedido eliminado correctamente.'
    if (pedidoSeleccionado.value?.id === pedido.id) {
      cerrarModal()
    }
    await cargarPedidos(paginacion.page)
  } catch (err) {
    error.value = await manejarErrorApi(err, router, {
      mensajePorDefecto: 'No se pudo eliminar el pedido.',
    })
  }
}

onMounted(async () => {
  await cargarConfiguracionYCatalogos()
  await cargarPedidos(1)
})
</script>

<template>
  <div class="pedidos-page">
    <header class="page-header">
      <div>
        <h1>Gestión de Pedidos de Comidas</h1>
        <p class="subtitle">
          Consultá el histórico de solicitudes de tu sector y gestioná pedidos confirmados antes de las
          <strong>{{ horarioCorte }} hs</strong> del día previo al servicio.
        </p>
      </div>
      <button
        v-if="puedeCrear"
        class="btn-primary"
        @click="router.push({ name: 'pedidos-nuevo' })"
      >
        + Nuevo Pedido / Personal
      </button>
    </header>

    <!-- Filtros -->
    <section class="card filtros-card">
      <div class="filtros-grid">
        <div class="field">
          <label>Estado</label>
          <select v-model="filtros.estado">
            <option value="">Todos</option>
            <option value="Confirmado">Confirmado</option>
            <option value="Autorizado">Autorizado</option>
            <option value="Rechazado">Rechazado</option>
          </select>
        </div>

        <div class="field">
          <label>Comida</label>
          <select v-model="filtros.tipo_comida_id">
            <option value="">Todas</option>
            <option v-for="c in COMIDAS" :key="c.id" :value="c.id">
              {{ c.nombre }}
            </option>
          </select>
        </div>

        <div class="field">
          <label>Tipo de Menú</label>
          <select v-model="filtros.tipo_menu_id">
            <option value="">Todos</option>
            <option v-for="m in tiposMenu" :key="m.id" :value="m.id">
              {{ m.nombre }}
            </option>
          </select>
        </div>

        <div class="field">
          <label>Fecha desde</label>
          <input v-model="filtros.fecha_desde" type="date" />
        </div>

        <div class="field">
          <label>Fecha hasta</label>
          <input v-model="filtros.fecha_hasta" type="date" />
        </div>
      </div>

      <div class="filtros-actions">
        <button class="btn-secondary" @click="limpiarFiltros">Limpiar</button>
        <button class="btn-primary" @click="cargarPedidos(1)">Filtrar</button>
      </div>
    </section>

    <div v-if="error" class="alert alert-error">{{ error }}</div>
    <div v-if="mensajeExito" class="alert alert-success">{{ mensajeExito }}</div>

    <!-- Tabla de Pedidos -->
    <section class="card">
      <div v-if="cargando" class="empty-state">Cargando pedidos...</div>

      <div v-else-if="pedidos.length === 0" class="empty-state">
        No se encontraron pedidos con los filtros seleccionados.
      </div>

      <div v-else class="table-wrapper">
        <table class="data-table">
          <thead>
            <tr>
              <th>Fecha</th>
              <th>Comida</th>
              <th>Estado</th>
              <th>Comensales</th>
              <th>Desglose por Menú</th>
              <th>Cupo (Reg / Exc)</th>
              <th class="text-right">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="pedido in pedidos" :key="pedido.id">
              <td>
                <strong>{{ pedido.fecha_formateada }}</strong>
              </td>
              <td>{{ pedido.tipo_comida }}</td>
              <td>
                <span :class="['badge', `badge-${pedido.estado.toLowerCase()}`]">
                  {{ pedido.estado }}
                </span>
                <div v-if="pedido.estado === 'Rechazado' && pedido.motivo_rechazo" class="motivo-rechazo">
                  Motivo: {{ pedido.motivo_rechazo }}
                </div>
              </td>
              <td>{{ pedido.total_personas }}</td>
              <td>
                <div class="tags-list">
                  <span
                    v-for="(cant, menu) in pedido.totales_pedidos"
                    :key="menu"
                    class="tag-menu"
                  >
                    {{ menu }}: <strong>{{ cant }}</strong>
                  </span>
                </div>
              </td>
              <td>
                <span class="cond-reg">{{ pedido.resumen_condicion?.regulares ?? 0 }} Reg</span>
                /
                <span class="cond-exc">{{ pedido.resumen_condicion?.excepciones ?? 0 }} Exc</span>
              </td>
              <td class="actions-cell">
                <button class="btn-sm btn-info" @click="verDetalle(pedido)">Ver</button>
                <button
                  v-if="puedeEditar && esModificable(pedido)"
                  class="btn-sm btn-edit"
                  @click="router.push({ name: 'pedidos-editar', params: { id: pedido.id } })"
                >
                  Editar
                </button>
                <button
                  v-if="puedeEliminar && esModificable(pedido)"
                  class="btn-sm btn-danger"
                  @click="confirmarEliminacion(pedido)"
                >
                  Eliminar
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Paginación -->
      <div v-if="paginacion.pages > 1" class="pagination">
        <button
          class="btn-secondary"
          :disabled="paginacion.page <= 1"
          @click="cargarPedidos(paginacion.page - 1)"
        >
          Anterior
        </button>
        <span>Página {{ paginacion.page }} de {{ paginacion.pages }} ({{ paginacion.total }} registros)</span>
        <button
          class="btn-secondary"
          :disabled="paginacion.page >= paginacion.pages"
          @click="cargarPedidos(paginacion.page + 1)"
        >
          Siguiente
        </button>
      </div>
    </section>

    <!-- Modal de Detalle Nominado -->
    <div v-if="pedidoSeleccionado || cargandoDetalle" class="modal-backdrop" @click.self="cerrarModal">
      <div class="modal-card">
        <div v-if="cargandoDetalle" class="empty-state">Cargando detalle...</div>
        <template v-else-if="pedidoSeleccionado">
          <div class="modal-header">
            <div>
              <h2>
                {{ pedidoSeleccionado.tipo_comida }} — {{ pedidoSeleccionado.fecha_formateada }}
              </h2>
              <span :class="['badge', `badge-${pedidoSeleccionado.estado.toLowerCase()}`]">
                {{ pedidoSeleccionado.estado }}
              </span>
            </div>
            <button class="btn-close" @click="cerrarModal">✕</button>
          </div>

          <div
            v-if="pedidoSeleccionado.estado === 'Rechazado' && pedidoSeleccionado.motivo_rechazo"
            class="alert alert-error"
          >
            <strong>Motivo de rechazo:</strong> {{ pedidoSeleccionado.motivo_rechazo }}
          </div>

          <!-- Resumen de Lo Pedido -->
          <div class="resumen-box">
            <div>
              <strong>Lo pedido:</strong> {{ pedidoSeleccionado.total_personas }} vianda(s)
              (Regulares: {{ pedidoSeleccionado.resumen_condicion?.regulares ?? 0 }} |
              Excepciones: {{ pedidoSeleccionado.resumen_condicion?.excepciones ?? 0 }})
            </div>
            <div class="tags-list">
              <span
                v-for="(cant, menu) in pedidoSeleccionado.totales_pedidos"
                :key="menu"
                class="tag-menu"
              >
                {{ menu }}: <strong>{{ cant }}</strong>
              </span>
            </div>
          </div>

          <!-- AGREGADO: Bloque separado de solo lectura con lo Autorizado cuando el pedido ya fue revisado -->
          <div
            v-if="pedidoSeleccionado.estado !== 'Confirmado' && pedidoSeleccionado.totales_autorizados"
            class="resumen-box autorizado-box"
          >
            <div>
              <strong>Lo autorizado (solo lectura):</strong>
              {{ pedidoSeleccionado.totales_autorizados.total }} vianda(s)
            </div>
            <div class="tags-list">
              <span
                v-for="(cant, menu) in pedidoSeleccionado.totales_autorizados.por_menu"
                :key="menu"
                class="tag-menu"
              >
                {{ menu }}: <strong>{{ cant }}</strong>
              </span>
              <span
                v-if="Object.keys(pedidoSeleccionado.totales_autorizados.por_menu || {}).length === 0"
                class="meta-text"
              >
                Sin viandas autorizadas
              </span>
            </div>
          </div>

          <div class="table-wrapper">
            <table class="data-table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>DNI</th>
                  <th>Apellido y Nombre</th>
                  <th>Menú</th>
                  <th>Condición</th>
                  <th v-if="pedidoSeleccionado.estado !== 'Confirmado'">Resolución</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(sol, idx) in pedidoSeleccionado.solicitudes" :key="sol.id">
                  <td>{{ idx + 1 }}</td>
                  <td>{{ sol.dni }}</td>
                  <td>{{ sol.apellido }}, {{ sol.nombre }}</td>
                  <td>{{ sol.tipo_menu }}</td>
                  <td>
                    <span
                      :class="[
                        'badge',
                        sol.condicion === 'Regular' ? 'badge-autorizado' : 'badge-excepcion',
                      ]"
                    >
                      {{ sol.condicion }}
                    </span>
                  </td>
                  <td v-if="pedidoSeleccionado.estado !== 'Confirmado'">
                    <span
                      :class="[
                        'badge',
                        sol.autorizada ? 'badge-autorizado' : 'badge-rechazado',
                      ]"
                    >
                      {{ sol.autorizada ? 'Autorizada' : 'No autorizada' }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="modal-footer">
            <button class="btn-secondary" @click="cerrarModal">Cerrar</button>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<style scoped>
.pedidos-page {
  max-width: 1150px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 24px;
}

.page-header h1 {
  font-size: 24px;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 4px;
}

.subtitle {
  color: #4a5568;
  font-size: 14px;
}

.card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.filtros-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
  gap: 14px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.field label {
  font-size: 13px;
  font-weight: 600;
  color: #4a5568;
}

.field input,
.field select {
  padding: 8px 10px;
  border: 1px solid #cbd5e0;
  border-radius: 6px;
  font-size: 14px;
}

.filtros-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 14px;
}

.btn-primary {
  background-color: #42b883;
  color: white;
  border: none;
  padding: 10px 18px;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
}

.btn-primary:hover {
  background-color: #369a6e;
}

.btn-secondary {
  background-color: #edf2f7;
  color: #2d3748;
  border: 1px solid #cbd5e0;
  padding: 8px 14px;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
}

.btn-secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.table-wrapper {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.data-table th,
.data-table td {
  padding: 12px 10px;
  border-bottom: 1px solid #edf2f7;
  text-align: left;
  vertical-align: middle;
}

.data-table th {
  background-color: #f7fafc;
  font-weight: 700;
  color: #2c3e50;
}

.badge {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
}

.badge-confirmado {
  background-color: #ebf8ff;
  color: #2b6cb0;
}

.badge-autorizado {
  background-color: #f0fff4;
  color: #2f855a;
}

.badge-rechazado {
  background-color: #fff5f5;
  color: #c53030;
}

.badge-excepcion {
  background-color: #fefcbf;
  color: #975a16;
}

.motivo-rechazo {
  font-size: 12px;
  color: #c53030;
  margin-top: 4px;
}

.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.tag-menu {
  background-color: #f7fafc;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  padding: 2px 6px;
  font-size: 12px;
}

.cond-reg {
  color: #2f855a;
  font-weight: 600;
}

.cond-exc {
  color: #b7791f;
  font-weight: 600;
}

.actions-cell {
  display: flex;
  gap: 6px;
  justify-content: flex-end;
}

.btn-sm {
  padding: 5px 10px;
  border: none;
  border-radius: 5px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
}

.btn-info {
  background-color: #edf2f7;
  color: #2c3e50;
}

.btn-edit {
  background-color: #3182ce;
  color: white;
}

.btn-danger {
  background-color: #e53e3e;
  color: white;
}

.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 16px;
  font-size: 14px;
}

.alert {
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 16px;
  font-size: 14px;
}

.alert-error {
  background-color: #fff5f5;
  border: 1px solid #feb2b2;
  color: #c53030;
}

.alert-success {
  background-color: #f0fff4;
  border: 1px solid #9ae6b4;
  color: #2f855a;
}

.empty-state {
  text-align: center;
  padding: 32px;
  color: #718096;
}

.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 50;
  padding: 20px;
}

.modal-card {
  background: white;
  border-radius: 10px;
  width: 100%;
  max-width: 760px;
  max-height: 85vh;
  overflow-y: auto;
  padding: 24px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.btn-close {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #718096;
}

.resumen-box {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  background: #f7fafc;
  border: 1px solid #e2e8f0;
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 12px;
  font-size: 14px;
}

.autorizado-box {
  background: #f0fff4;
  border-color: #9ae6b4;
}

.meta-text {
  font-size: 12px;
  color: #718096;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  margin-top: 18px;
}
</style>