<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import {
  actualizarPedido,
  actualizarPersonalSector,
  crearPedidos,
  crearPersonalSector,
  eliminarPersonalSector,
  obtenerConfiguracionSistema,
  obtenerCuposSector,
  obtenerPedido,
  obtenerPersonalDisponible,
  obtenerTiposMenu,
} from '@/services/pedidos'
import { manejarErrorApi } from '@/utils/apiErrorHandler.js'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const esEdicion = computed(() => Boolean(route.params.id))
const pedidoId = computed(() => Number(route.params.id))
const sectorUsuarioId = computed(() => auth.user?.sector_id ?? null)

const cargando = ref(false)
const guardando = ref(false)
const error = ref('')
const mensajeExito = ref('')
const conflictosExistentes = ref([])
const horarioCorte = ref('18:00')

const personalDisponible = ref([])
const tiposMenu = ref([])
const cuposPorComida = ref({})
const busquedaPersonal = ref('')
const comidaActiva = ref('almuerzo')
const fechaExcluirInput = ref('')

// Estado para gestión de fichas de Personal Fijo del sector
const modalPersonalAbierto = ref(false)
const guardandoPersonal = ref(false)
const personalEditandoId = ref(null)
const formPersonal = reactive({
  dni: '',
  nombre: '',
  apellido: '',
  tipo_menu_id: '',
})

const COMIDAS_META = [
  { key: 'desayuno', id: 1, label: 'Desayuno' },
  { key: 'almuerzo', id: 2, label: 'Almuerzo' },
  { key: 'merienda', id: 3, label: 'Merienda' },
  { key: 'cena', id: 4, label: 'Cena' },
]

function formatearFechaLocalISO(dt) {
  const y = dt.getFullYear()
  const m = String(dt.getMonth() + 1).padStart(2, '0')
  const d = String(dt.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

function formatearFechaLatina(iso) {
  if (!iso) return ''
  const [y, m, d] = iso.split('-')
  return `${d}/${m}/${y}`
}

function sumarDiasISO(baseISO, dias) {
  const [y, m, d] = baseISO.split('-').map(Number)
  const dt = new Date(y, m - 1, d + dias)
  return formatearFechaLocalISO(dt)
}

const hoyISO = formatearFechaLocalISO(new Date())
const mananaISO = sumarDiasISO(hoyISO, 1)

// Fecha mínima habilitada según el horario de corte vigente
const fechaMinimaISO = computed(() => {
  const ahora = new Date()
  const [horas, minutos] = (horarioCorte.value || '18:00').split(':').map(Number)
  const corteHoy = new Date(
    ahora.getFullYear(),
    ahora.getMonth(),
    ahora.getDate(),
    horas,
    minutos,
    0,
    0
  )
  return ahora > corteHoy ? sumarDiasISO(hoyISO, 2) : mananaISO
})

const form = reactive({
  periodicidad: 'diaria',
  fecha_inicio: mananaISO,
  fecha_fin: mananaISO,
  fechas_excluidas: [],
  comidas: {
    desayuno: [],
    almuerzo: [],
    merienda: [],
    cena: [],
  },
})

watch(fechaMinimaISO, (nuevaMin) => {
  if (!esEdicion.value && form.fecha_inicio < nuevaMin) {
    form.fecha_inicio = nuevaMin
  }
})

watch(
  () => [form.periodicidad, form.fecha_inicio],
  ([per, inicio]) => {
    if (!inicio) return
    if (per === 'diaria') {
      form.fecha_fin = inicio
    } else if (per === 'semanal') {
      form.fecha_fin = sumarDiasISO(inicio, 6)
    } else if (per === 'mensual') {
      form.fecha_fin = sumarDiasISO(inicio, 29)
    }
  }
)

const infoPedidoEdicion = ref(null)

function esResidente(persona) {
  return (
    !persona.sector_id ||
    String(persona.tipo_personal || '').toLowerCase().includes('residente')
  )
}

function etiquetaOrigenPersona(persona) {
  if (esResidente(persona)) return 'Residente (Rotativo)'
  const nombreSector =
    typeof persona.sector === 'object'
      ? persona.sector?.nombre
      : persona.sector || auth.user?.sector?.nombre || auth.user?.sector
  return nombreSector ? `Sector: ${nombreSector}` : 'Personal Fijo del Sector'
}

const personalFijoDelSector = computed(() =>
  personalDisponible.value.filter(
    (p) =>
      p.activo !== false &&
      !esResidente(p) &&
      (!sectorUsuarioId.value || p.sector_id === sectorUsuarioId.value)
  )
)

const personalFiltrado = computed(() => {
  const q = busquedaPersonal.value.trim().toLowerCase()
  const habilitados = personalDisponible.value.filter((p) => {
    if (p.activo === false) return false
    if (esResidente(p)) return true
    if (sectorUsuarioId.value) return p.sector_id === sectorUsuarioId.value
    return true
  })

  if (!q) return habilitados
  return habilitados.filter(
    (p) =>
      p.nombre.toLowerCase().includes(q) ||
      p.apellido.toLowerCase().includes(q) ||
      String(p.dni).includes(q)
  )
})

const fechasPrevistas = computed(() => {
  if (esEdicion.value) return [form.fecha_inicio]
  if (!form.fecha_inicio) return []
  const fin = form.periodicidad === 'diaria' ? form.fecha_inicio : form.fecha_fin || form.fecha_inicio
  if (fin < form.fecha_inicio) return []

  const excluidas = new Set(form.fechas_excluidas)
  const lista = []
  let cursor = form.fecha_inicio
  let guard = 0
  while (cursor <= fin && guard < 366) {
    if (!excluidas.has(cursor)) {
      lista.push(cursor)
    }
    cursor = sumarDiasISO(cursor, 1)
    guard += 1
  }
  return lista
})

function obtenerInfoPersona(personalId) {
  const enLista = personalDisponible.value.find((p) => p.id === personalId)
  if (enLista) return enLista
  const sol = infoPedidoEdicion.value?.solicitudes?.find((s) => s.personal_id === personalId)
  if (sol) {
    return {
      id: sol.personal_id,
      dni: sol.dni,
      nombre: sol.nombre,
      apellido: sol.apellido,
      tipo_menu: sol.tipo_menu,
    }
  }
  return null
}

function estaSeleccionado(comidaKey, personalId) {
  return form.comidas[comidaKey].includes(personalId)
}

function togglePersona(comidaKey, persona) {
  const lista = form.comidas[comidaKey]
  const idx = lista.indexOf(persona.id)
  if (idx >= 0) {
    lista.splice(idx, 1)
  } else {
    lista.push(persona.id)
  }
}

function seleccionarTodoElSectorEnComida() {
  const lista = form.comidas[comidaActiva.value]
  for (const p of personalFijoDelSector.value) {
    if (!lista.includes(p.id)) {
      lista.push(p.id)
    }
  }
}

function vaciarComidaActiva() {
  form.comidas[comidaActiva.value] = []
}

function asignarTodasLasComidasAPersona(persona) {
  for (const meta of COMIDAS_META) {
    const lista = form.comidas[meta.key]
    if (!lista.includes(persona.id)) {
      lista.push(persona.id)
    }
  }
}

function tieneTodasLasComidas(personalId) {
  return COMIDAS_META.every((meta) => form.comidas[meta.key].includes(personalId))
}

function agregarFechaExcluida() {
  if (!fechaExcluirInput.value) return
  if (!form.fechas_excluidas.includes(fechaExcluirInput.value)) {
    form.fechas_excluidas.push(fechaExcluirInput.value)
    form.fechas_excluidas.sort()
  }
  fechaExcluirInput.value = ''
}

function quitarFechaExcluida(fecha) {
  form.fechas_excluidas = form.fechas_excluidas.filter((f) => f !== fecha)
}

function resumenCupoComida(comidaMeta) {
  const ids = form.comidas[comidaMeta.key]
  const seleccionados = ids.length
  const limite = cuposPorComida.value[comidaMeta.id] ?? 0
  const regulares = Math.min(seleccionados, limite)
  const excepciones = Math.max(0, seleccionados - limite)

  const porMenu = {}
  for (const pid of ids) {
    const info = obtenerInfoPersona(pid)
    const menu = info?.tipo_menu || 'General'
    porMenu[menu] = (porMenu[menu] || 0) + 1
  }

  return { seleccionados, limite, regulares, excepciones, porMenu }
}

const totalSolicitudes = computed(() =>
  Object.values(form.comidas).reduce((acc, lista) => acc + lista.length, 0)
)

const opcionesTiposMenu = computed(() => {
  const mapa = new Map()
  for (const p of personalDisponible.value) {
    if (p.tipo_menu_id && p.tipo_menu) {
      mapa.set(Number(p.tipo_menu_id), { id: Number(p.tipo_menu_id), nombre: p.tipo_menu })
    }
  }
  if (mapa.size > 0) return Array.from(mapa.values())
  return tiposMenu.value
})

function abrirModalNuevoPersonal() {
  personalEditandoId.value = null
  formPersonal.dni = ''
  formPersonal.nombre = ''
  formPersonal.apellido = ''
  formPersonal.tipo_menu_id = opcionesTiposMenu.value[0]?.id || 1
  modalPersonalAbierto.value = true
}

function abrirModalEditarPersonal(persona) {
  if (esResidente(persona)) return
  personalEditandoId.value = persona.id
  formPersonal.dni = persona.dni
  formPersonal.nombre = persona.nombre
  formPersonal.apellido = persona.apellido
  const menuEncontrado = opcionesTiposMenu.value.find(
    (m) => m.id === persona.tipo_menu_id || m.nombre === persona.tipo_menu
  )
  formPersonal.tipo_menu_id = menuEncontrado?.id || opcionesTiposMenu.value[0]?.id || 1
  modalPersonalAbierto.value = true
}

function cerrarModalPersonal() {
  modalPersonalAbierto.value = false
  personalEditandoId.value = null
}

async function guardarFichaPersonal() {
  error.value = ''
  mensajeExito.value = ''
  guardandoPersonal.value = true
  try {
    if (personalEditandoId.value) {
      await actualizarPersonalSector(personalEditandoId.value, {
        tipo_menu_id: Number(formPersonal.tipo_menu_id),
      })
      mensajeExito.value = 'Tipo de menú actualizado correctamente.'
    } else {
      await crearPersonalSector({
        dni: String(formPersonal.dni).trim(),
        nombre: formPersonal.nombre.trim(),
        apellido: formPersonal.apellido.trim(),
        tipo_menu_id: Number(formPersonal.tipo_menu_id),
        sector_id: sectorUsuarioId.value,
        tipo_personal_id: 1,
      })
      mensajeExito.value = 'Personal fijo agregado al sector correctamente.'
    }

    cerrarModalPersonal()
    const personalRes = await obtenerPersonalDisponible()
    personalDisponible.value = Array.isArray(personalRes)
      ? personalRes
      : personalRes.items || personalRes.data || []
  } catch (err) {
    error.value = await manejarErrorApi(err, router, {
      mensajePorDefecto: 'No se pudo guardar la ficha del personal.',
    })
  } finally {
    guardandoPersonal.value = false
  }
}

async function eliminarFichaPersonal(persona) {
  if (esResidente(persona)) return
  const ok = window.confirm(
    `¿Seguro que deseas dar de baja/eliminar a ${persona.apellido}, ${persona.nombre} del sector?`
  )
  if (!ok) return

  error.value = ''
  mensajeExito.value = ''
  try {
    await eliminarPersonalSector(persona.id)
    for (const meta of COMIDAS_META) {
      form.comidas[meta.key] = form.comidas[meta.key].filter((id) => id !== persona.id)
    }
    mensajeExito.value = 'Personal eliminado del sector.'
    const personalRes = await obtenerPersonalDisponible()
    personalDisponible.value = Array.isArray(personalRes)
      ? personalRes
      : personalRes.items || personalRes.data || []
  } catch (err) {
    error.value = await manejarErrorApi(err, router, {
      mensajePorDefecto: 'No se pudo eliminar la ficha del personal.',
    })
  }
}

async function cargarDatosIniciales() {
  cargando.value = true
  error.value = ''
  try {
    const [config, personalRes, cuposRes, menusRes] = await Promise.all([
      obtenerConfiguracionSistema().catch(() => null),
      obtenerPersonalDisponible(),
      obtenerCuposSector().catch(() => ({ data: [] })),
      obtenerTiposMenu().catch(() => []),
    ])

    if (config?.horario_corte) {
      horarioCorte.value = config.horario_corte
    }

    if (!esEdicion.value && form.fecha_inicio < fechaMinimaISO.value) {
      form.fecha_inicio = fechaMinimaISO.value
    }

    personalDisponible.value = Array.isArray(personalRes)
      ? personalRes
      : personalRes.items || personalRes.data || []

    tiposMenu.value = Array.isArray(menusRes) ? menusRes : []

    const mapaCupos = {}
    for (const c of cuposRes.data || cuposRes.items || []) {
      mapaCupos[c.tipo_comida_id] = c.cantidad
    }
    cuposPorComida.value = mapaCupos

    if (esEdicion.value) {
      const pedido = await obtenerPedido(pedidoId.value)
      infoPedidoEdicion.value = pedido
      form.fecha_inicio = pedido.fecha
      form.fecha_fin = pedido.fecha
      const meta = COMIDAS_META.find((c) => c.id === pedido.tipo_comida_id)
      if (meta) {
        comidaActiva.value = meta.key
        form.comidas[meta.key] = (pedido.solicitudes || []).map((sol) => sol.personal_id)
      }
    }
  } catch (err) {
    error.value = await manejarErrorApi(err, router, {
      mensajePorDefecto: 'No se pudieron cargar los datos iniciales.',
    })
  } finally {
    cargando.value = false
  }
}

async function guardar() {
  error.value = ''
  conflictosExistentes.value = []

  if (totalSolicitudes.value === 0) {
    error.value = 'Debes seleccionar al menos una persona en alguna comida.'
    return
  }

  guardando.value = true
  try {
    if (esEdicion.value) {
      await actualizarPedido(pedidoId.value, {
        personal_ids: form.comidas[comidaActiva.value],
      })
    } else {
      const comidasPayload = {}
      for (const meta of COMIDAS_META) {
        if (form.comidas[meta.key].length > 0) {
          comidasPayload[meta.key] = form.comidas[meta.key]
        }
      }

      const payload = {
        periodicidad: form.periodicidad,
        fecha_inicio: form.fecha_inicio,
        comidas: comidasPayload,
      }

      if (form.periodicidad !== 'diaria') {
        payload.fecha_fin = form.fecha_fin
        payload.fechas_excluidas = form.fechas_excluidas
      }

      await crearPedidos(payload)
    }

    router.push({ name: 'pedidos' })
  } catch (err) {
    error.value = await manejarErrorApi(err, router, {
      mensajePorDefecto: 'No se pudo guardar el pedido.',
    })
    const raw = err.data?.error ?? err.data
    if (raw && typeof raw === 'object' && Array.isArray(raw.conflictos)) {
      conflictosExistentes.value = raw.conflictos
    }
  } finally {
    guardando.value = false
  }
}

watch(
  () => route.params.id,
  () => {
    conflictosExistentes.value = []
    cargarDatosIniciales()
  }
)

onMounted(cargarDatosIniciales)
</script>

<template>
  <div class="pedido-form-page">
    <header class="page-header">
      <div>
        <h1>{{ esEdicion ? 'Modificar Pedido' : 'Nuevo Pedido de Comidas' }}</h1>
        <p class="subtitle">
          Horario de corte vigente: <strong>{{ horarioCorte }} hs</strong> del día previo al consumo
          (primera fecha disponible: <strong>{{ formatearFechaLatina(fechaMinimaISO) }}</strong>).
        </p>
      </div>
      <div class="header-actions">
        <button
          v-if="!esEdicion"
          type="button"
          class="btn-secondary"
          @click="abrirModalNuevoPersonal"
        >
          + Agregar Personal Fijo
        </button>
        <button type="button" class="btn-secondary" @click="router.push({ name: 'pedidos' })">
          ← Volver al listado
        </button>
      </div>
    </header>

    <div v-if="mensajeExito" class="alert alert-success">{{ mensajeExito }}</div>

    <div v-if="error" class="alert alert-error">
      <div>{{ error }}</div>
      <div v-if="conflictosExistentes.length" class="conflictos-actions">
        <button
          v-for="c in conflictosExistentes"
          :key="c.request_id"
          type="button"
          class="btn-sm btn-edit"
          @click="router.push({ name: 'pedidos-editar', params: { id: c.request_id } })"
        >
          Editar pedido existente de {{ c.comida }} ({{ c.fecha }})
        </button>
      </div>
    </div>

    <div v-if="cargando" class="card empty-state">Cargando información del sector...</div>

    <template v-else>
      <section class="card">
        <div v-if="esEdicion && infoPedidoEdicion" class="edicion-banner">
          Editando pedido de <strong>{{ infoPedidoEdicion.tipo_comida }}</strong> para el día
          <strong>{{ infoPedidoEdicion.fecha_formateada }}</strong> (para cambiar la fecha, eliminá este pedido y creá uno nuevo).
        </div>

        <template v-else>
          <div class="config-grid">
            <div class="field">
              <label>Periodicidad</label>
              <select v-model="form.periodicidad">
                <option value="diaria">Diaria (1 día)</option>
                <option value="semanal">Semanal (7 días corridos)</option>
                <option value="mensual">Mensual (30 días corridos)</option>
              </select>
            </div>

            <div class="field">
              <label>{{ form.periodicidad === 'diaria' ? 'Fecha del pedido' : 'Fecha de inicio' }}</label>
              <input v-model="form.fecha_inicio" type="date" :min="fechaMinimaISO" />
            </div>

            <div v-if="form.periodicidad !== 'diaria'" class="field">
              <label>Fecha de fin</label>
              <input v-model="form.fecha_fin" type="date" :min="form.fecha_inicio" />
            </div>

            <div v-if="form.periodicidad !== 'diaria'" class="field">
              <label>Excluir días específicos (opcional)</label>
              <div class="exclude-input">
                <input
                  v-model="fechaExcluirInput"
                  type="date"
                  :min="form.fecha_inicio"
                  :max="form.fecha_fin"
                />
                <button type="button" class="btn-secondary" @click="agregarFechaExcluida">
                  Agregar
                </button>
              </div>
              <div v-if="form.fechas_excluidas.length" class="chips-list">
                <span v-for="f in form.fechas_excluidas" :key="f" class="chip">
                  {{ formatearFechaLatina(f) }}
                  <button type="button" @click="quitarFechaExcluida(f)">×</button>
                </span>
              </div>
            </div>
          </div>

          <div class="preview-dias">
            <strong>Detalle por día antes de confirmar:</strong>
            Se generarán solicitudes para <strong>{{ fechasPrevistas.length }}</strong> día(s):
            <span class="fechas-inline">
              {{ fechasPrevistas.slice(0, 10).map(formatearFechaLatina).join(', ') }}
              <template v-if="fechasPrevistas.length > 10">
                ... (+{{ fechasPrevistas.length - 10 }} días más)
              </template>
            </span>
          </div>
        </template>
      </section>

      <div v-if="!esEdicion" class="tabs">
        <button
          v-for="meta in COMIDAS_META"
          :key="meta.key"
          type="button"
          :class="['tab-btn', { active: comidaActiva === meta.key }]"
          @click="comidaActiva = meta.key"
        >
          {{ meta.label }}
          <span class="tab-count">{{ form.comidas[meta.key].length }}</span>
        </button>
      </div>

      <section class="card cupo-bar">
        <template v-for="meta in COMIDAS_META" :key="meta.key">
          <div v-if="comidaActiva === meta.key" class="cupo-info">
            <div>
              <strong>{{ meta.label }}:</strong>
              Cupo regular del sector = <strong>{{ resumenCupoComida(meta).limite }}</strong>
              <div class="tags-list" style="margin-top: 6px">
                <span
                  v-for="(cant, menu) in resumenCupoComida(meta).porMenu"
                  :key="menu"
                  class="tag-menu"
                >
                  Menú {{ menu }}: <strong>{{ cant }}</strong>
                </span>
              </div>
            </div>
            <div class="cupo-badges">
              <span class="badge badge-autorizado">
                Regulares: {{ resumenCupoComida(meta).regulares }}
              </span>
              <span class="badge badge-excepcion">
                Excepciones: {{ resumenCupoComida(meta).excepciones }}
              </span>
            </div>
          </div>
        </template>
      </section>

      <div class="builder-grid">
        <section class="card">
          <div class="panel-top">
            <h3>Personal habilitado (Sector y Residentes)</h3>
            <div class="masivas-actions">
              <button
                type="button"
                class="btn-sm btn-mass"
                @click="seleccionarTodoElSectorEnComida"
              >
                Seleccionar todo el sector ({{ personalFijoDelSector.length }})
              </button>
              <button
                type="button"
                class="btn-sm btn-info"
                @click="vaciarComidaActiva"
              >
                Vaciar
              </button>
            </div>
          </div>

          <input
            v-model="busquedaPersonal"
            type="text"
            class="search-input"
            placeholder="Buscar por apellido, nombre o DNI..."
          />

          <div class="lista-personal">
            <div
              v-for="persona in personalFiltrado"
              :key="persona.id"
              :class="['persona-row', { selected: estaSeleccionado(comidaActiva, persona.id) }]"
              @click="togglePersona(comidaActiva, persona)"
            >
              <div>
                <strong>{{ persona.apellido }}, {{ persona.nombre }}</strong>
                <div class="meta-text">
                  DNI {{ persona.dni }} ·
                  {{ etiquetaOrigenPersona(persona) }} ·
                  Menú: {{ persona.tipo_menu || 'General' }}
                </div>
              </div>
              <div class="persona-row-actions" @click.stop>
                <button
                  v-if="!esEdicion"
                  type="button"
                  :class="['btn-xs', tieneTodasLasComidas(persona.id) ? 'btn-mass-active' : 'btn-info']"
                  title="Asignar Desayuno, Almuerzo, Merienda y Cena"
                  @click="asignarTodasLasComidasAPersona(persona)"
                >
                  4 comidas
                </button>
                <button
                  v-if="!esResidente(persona)"
                  type="button"
                  class="btn-xs btn-info"
                  title="Editar tipo de menú"
                  @click="abrirModalEditarPersonal(persona)"
                >
                  ✎
                </button>
                <button
                  v-if="!esResidente(persona)"
                  type="button"
                  class="btn-xs btn-danger"
                  title="Eliminar ficha de Personal Fijo"
                  @click="eliminarFichaPersonal(persona)"
                >
                  🗑
                </button>
                <input
                  type="checkbox"
                  :checked="estaSeleccionado(comidaActiva, persona.id)"
                  @change="togglePersona(comidaActiva, persona)"
                />
              </div>
            </div>

            <div v-if="personalFiltrado.length === 0" class="empty-state">
              No hay personal coincidente.
            </div>
          </div>
        </section>

        <section class="card">
          <h3>
            Solicitudes para
            {{ COMIDAS_META.find((c) => c.key === comidaActiva)?.label }}
            ({{ form.comidas[comidaActiva].length }})
          </h3>

          <div v-if="form.comidas[comidaActiva].length === 0" class="empty-state">
            Seleccioná personas desde la lista de la izquierda.
          </div>

          <div v-else class="seleccionados-list">
            <div
              v-for="(pid, index) in form.comidas[comidaActiva]"
              :key="pid"
              class="seleccionado-row"
            >
              <div class="sel-info">
                <span class="orden-num">#{{ index + 1 }}</span>
                <div>
                  <strong>
                    {{ obtenerInfoPersona(pid)?.apellido }},
                    {{ obtenerInfoPersona(pid)?.nombre }}
                  </strong>
                  <div class="meta-text">
                    Menú asignado: {{ obtenerInfoPersona(pid)?.tipo_menu || 'General' }}
                  </div>
                </div>
              </div>

              <div class="sel-controls">
                <span
                  :class="[
                    'badge',
                    index <
                    (cuposPorComida[COMIDAS_META.find((c) => c.key === comidaActiva)?.id] ?? 0)
                      ? 'badge-autorizado'
                      : 'badge-excepcion',
                  ]"
                >
                  {{
                    index <
                    (cuposPorComida[COMIDAS_META.find((c) => c.key === comidaActiva)?.id] ?? 0)
                      ? 'Regular'
                      : 'Excepción'
                  }}
                </span>
                <button
                  type="button"
                  class="btn-remove"
                  @click="togglePersona(comidaActiva, { id: pid })"
                >
                  ✕
                </button>
              </div>
            </div>
          </div>
        </section>
      </div>

      <footer class="form-footer">
        <button type="button" class="btn-secondary" @click="router.push({ name: 'pedidos' })">
          Cancelar
        </button>
        <button type="button" class="btn-primary" :disabled="guardando" @click="guardar">
          {{
            guardando
              ? 'Guardando...'
              : esEdicion
                ? 'Guardar Cambios'
                : `Confirmar Pedido (${totalSolicitudes * fechasPrevistas.length} viandas en ${fechasPrevistas.length} día/s)`
          }}
        </button>
      </footer>
    </template>

    <!-- Modal Alta / Edición de Personal Fijo del Sector -->
    <div v-if="modalPersonalAbierto" class="modal-backdrop" @click.self="cerrarModalPersonal">
      <div class="modal-card">
        <div class="modal-header">
          <h2>{{ personalEditandoId ? 'Modificar Menú de Personal Fijo' : 'Agregar Personal Fijo al Sector' }}</h2>
          <button type="button" class="btn-close" @click="cerrarModalPersonal">✕</button>
        </div>

        <form class="personal-form" @submit.prevent="guardarFichaPersonal">
          <div class="field">
            <label>DNI</label>
            <input
              v-model="formPersonal.dni"
              type="text"
              required
              :disabled="Boolean(personalEditandoId)"
              placeholder="Ej: 32123456"
            />
          </div>
          <div class="field">
            <label>Apellido</label>
            <input
              v-model="formPersonal.apellido"
              type="text"
              required
              :disabled="Boolean(personalEditandoId)"
            />
          </div>
          <div class="field">
            <label>Nombre</label>
            <input
              v-model="formPersonal.nombre"
              type="text"
              required
              :disabled="Boolean(personalEditandoId)"
            />
          </div>
          <div class="field">
            <label>Tipo de Menú</label>
            <select v-model="formPersonal.tipo_menu_id" required>
              <option v-for="m in opcionesTiposMenu" :key="m.id" :value="m.id">
                {{ m.nombre }}
              </option>
            </select>
          </div>

          <div class="modal-footer">
            <button type="button" class="btn-secondary" @click="cerrarModalPersonal">
              Cancelar
            </button>
            <button type="submit" class="btn-primary" :disabled="guardandoPersonal">
              {{ guardandoPersonal ? 'Guardando...' : 'Guardar Ficha' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
.pedido-form-page {
  max-width: 1180px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 20px;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.page-header h1 {
  font-size: 24px;
  font-weight: 700;
  color: #2c3e50;
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
  margin-bottom: 18px;
}

.config-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
  gap: 16px;
}

.preview-dias {
  margin-top: 14px;
  padding: 10px 14px;
  background: #f7fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 13px;
  color: #2d3748;
}

.fechas-inline {
  color: #4a5568;
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

.field input:disabled {
  background-color: #edf2f7;
  color: #718096;
  cursor: not-allowed;
}

.exclude-input {
  display: flex;
  gap: 8px;
}

.chips-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 6px;
}

.chip {
  background: #edf2f7;
  padding: 3px 8px;
  border-radius: 999px;
  font-size: 12px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.chip button {
  background: none;
  border: none;
  cursor: pointer;
  font-weight: bold;
}

.tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 14px;
}

.tab-btn {
  padding: 10px 16px;
  border: 1px solid #cbd5e0;
  background: #f7fafc;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
}

.tab-btn.active {
  background: #2c3e50;
  color: white;
  border-color: #2c3e50;
}

.tab-count {
  background: #42b883;
  color: white;
  border-radius: 999px;
  padding: 1px 8px;
  font-size: 12px;
}

.cupo-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.cupo-badges {
  display: flex;
  gap: 10px;
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
  padding: 2px 8px;
  font-size: 12px;
}

.builder-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 18px;
}

@media (max-width: 860px) {
  .builder-grid {
    grid-template-columns: 1fr;
  }
}

.panel-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
}

.builder-grid h3 {
  font-size: 16px;
  font-weight: 700;
  color: #2c3e50;
  margin: 0;
}

.masivas-actions {
  display: flex;
  gap: 6px;
}

.search-input {
  width: 100%;
  padding: 9px 12px;
  border: 1px solid #cbd5e0;
  border-radius: 6px;
  margin-bottom: 12px;
}

.lista-personal,
.seleccionados-list {
  max-height: 400px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.persona-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  cursor: pointer;
}

.persona-row:hover {
  background: #f7fafc;
}

.persona-row.selected {
  background: #f0fff4;
  border-color: #42b883;
}

.persona-row-actions {
  display: flex;
  align-items: center;
  gap: 6px;
}

.meta-text {
  font-size: 12px;
  color: #718096;
}

.seleccionado-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
}

.sel-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.orden-num {
  font-weight: 700;
  color: #718096;
}

.sel-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-remove {
  background: #fed7d7;
  color: #c53030;
  border: none;
  border-radius: 6px;
  padding: 6px 10px;
  cursor: pointer;
  font-weight: bold;
}

.btn-sm {
  padding: 5px 10px;
  border: none;
  border-radius: 5px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
}

.btn-xs {
  padding: 3px 7px;
  border: none;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
}

.btn-mass,
.btn-mass-active {
  background-color: #2b6cb0;
  color: white;
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

.badge {
  display: inline-block;
  padding: 2px 9px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
}

.badge-autorizado {
  background-color: #f0fff4;
  color: #2f855a;
}

.badge-excepcion {
  background-color: #fefcbf;
  color: #975a16;
}

.form-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 10px;
}

.btn-primary {
  background-color: #42b883;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background-color: #edf2f7;
  color: #2d3748;
  border: 1px solid #cbd5e0;
  padding: 9px 16px;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
}

.alert-error {
  background-color: #fff5f5;
  border: 1px solid #feb2b2;
  color: #c53030;
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 16px;
}

.alert-success {
  background-color: #f0fff4;
  border: 1px solid #9ae6b4;
  color: #2f855a;
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 16px;
}

.conflictos-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 10px;
}

.empty-state {
  text-align: center;
  padding: 24px;
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
  max-width: 460px;
  padding: 24px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.btn-close {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #718096;
}

.personal-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 10px;
}
</style>