<template>
  <section class="panel-card">
    <h2 class="panel-title">Retiro individual</h2>
    <p class="panel-desc">Buscá por DNI o por nombre y apellido. Una sola vianda por persona.</p>

    <div class="search-box">
      <input
        v-model="busqueda"
        type="text"
        :inputmode="usarTecladoNumerico ? 'none' : 'text'"
        :maxlength="usarTecladoNumerico ? 8 : 60"
        :readonly="usarTecladoNumerico"
        class="search-input"
        :placeholder="usarTecladoNumerico ? 'Ingresá DNI con el teclado táctil...' : 'Ingresá nombre o apellido...'"
        @input="validarEntrada"
        @keyup.enter="buscarPersona"
      />
      <button type="button" class="btn-mode-toggle" @click="alternarModoTeclado">
        {{ usarTecladoNumerico ? '123' : 'ABC' }}
      </button>
      <button type="button" class="btn-search" :disabled="cargando || apiCaida" @click="buscarPersona">
        🔍 Buscar
      </button>
    </div>

    <div class="numpad-grid" role="group" aria-label="Teclado numérico">
      <button v-for="n in ['1','2','3']" :key="n" type="button" class="num-key" @click="agregarDigito(n)">{{ n }}</button>
      <button type="button" class="num-key action-key" @click="borrarUltimo">⌫</button>

      <button v-for="n in ['4','5','6']" :key="n" type="button" class="num-key" @click="agregarDigito(n)">{{ n }}</button>
      <button type="button" class="num-key action-key" @click="limpiarBusqueda">Limpiar</button>

      <button v-for="n in ['7','8','9']" :key="n" type="button" class="num-key" @click="agregarDigito(n)">{{ n }}</button>
      <button type="button" class="num-key" @click="agregarDigito('0')">0</button>
    </div>

    <!-- Lista de coincidencias múltiples -->
    <div v-if="resultadosBusqueda.length > 1" class="sector-list" style="margin-top: 14px;">
      <p class="panel-desc" style="margin-bottom: 8px;">
        Se encontraron {{ resultadosBusqueda.length }} personas. Seleccioná una para entregar:
      </p>
      <div
        v-for="item in resultadosBusqueda"
        :key="item.id"
        class="sector-item"
        :style="personaActual?.id === item.id ? 'border-color: #16a34a; background-color: #f0fdf4; cursor: pointer;' : 'cursor: pointer;'"
        @click="seleccionarPersona(item)"
      >
        <div class="sector-item-info">
          <strong>{{ item.nombre }} {{ item.apellido }}</strong>
          <span>DNI {{ item.dni }} · {{ item.sector }}</span>
        </div>
        <div class="person-badges">
          <span class="status-badge" :class="mapearEstado(item.estado).clase">
            {{ mapearEstado(item.estado).icono }} {{ mapearEstado(item.estado).texto }}
          </span>
          <span v-if="item.tipo_menu" class="menu-badge">{{ item.tipo_menu }}</span>
        </div>
      </div>
    </div>

    <!-- Ficha de la persona seleccionada -->
    <div v-if="personaActual" class="person-card">
      <div class="person-info">
        <div class="avatar">{{ obtenerIniciales(personaActual.nombre, personaActual.apellido) }}</div>
        <div>
          <div class="person-name">{{ personaActual.nombre }} {{ personaActual.apellido }}</div>
          <div class="person-meta">{{ personaActual.sector }} · DNI {{ personaActual.dni }}</div>
        </div>
      </div>

      <div class="person-badges">
        <span class="status-badge" :class="estadoComidaActual.clase">
          {{ estadoComidaActual.icono }} {{ estadoComidaActual.texto }}
        </span>
        <span v-if="personaActual.tipo_menu" class="menu-badge">{{ personaActual.tipo_menu }}</span>
      </div>
    </div>

    <button
      type="button"
      class="btn-deliver"
      :disabled="!puedeEntregarIndividual || cargando || apiCaida"
      @click="abrirModalConfirmacion"
    >
      ✓ Entregar vianda
    </button>
    <!-- Pop-up de confirmación de entrega individual -->
<div v-if="mostrarModalConfirmacion && personaActual" class="modal-overlay" @click.self="cerrarModalConfirmacion">
  <div class="modal-card" role="dialog" aria-modal="true" aria-labelledby="modal-titulo">
    <h3 id="modal-titulo" class="panel-title">Confirmar entrega de vianda</h3>
    <p class="panel-desc">Verificá los datos antes de registrar el retiro:</p>

    <div class="modal-detalle">
      <div class="detalle-fila">
        <span>Personal:</span>
        <strong>{{ personaActual.nombre }} {{ personaActual.apellido }}</strong>
      </div>
      <div class="detalle-fila">
        <span>DNI:</span>
        <strong>{{ personaActual.dni }}</strong>
      </div>
      <div class="detalle-fila">
        <span>Sector:</span>
        <strong>{{ personaActual.sector }}</strong>
      </div>
      <div class="detalle-fila">
        <span>Comida:</span>
        <strong style="text-transform: capitalize;">{{ comidaSeleccionada }}</strong>
      </div>
      <div class="detalle-fila">
        <span>Tipo de menú:</span>
        <strong>{{ personaActual.tipo_menu || 'General' }}</strong>
      </div>
    </div>

    <div class="modal-acciones">
      <button
        type="button"
        class="btn-mode-toggle"
        :disabled="cargando"
        @click="cerrarModalConfirmacion"
      >
        Cancelar ({{ segundosRestantes }}s)
      </button>
      <button
        type="button"
        class="btn-deliver"
        style="margin-top: 0; width: auto; flex: 1;"
        :disabled="cargando || apiCaida"
        @click="confirmarEntregaIndividual"
      >
        {{ cargando ? 'Registrando...' : '✓ Confirmar entrega' }}
      </button>
    </div>
  </div>
</div>
  </section>
</template>

<script setup>
import { ref, computed, watch, onUnmounted } from 'vue'
import { comedorService, apiCaida } from '@/services/comedor'

const mostrarModalConfirmacion = ref(false)
const segundosRestantes = ref(30)
let modalTimerInterval = null

function abrirModalConfirmacion() {
  if (!puedeEntregarIndividual.value) return
  emit('actividad')
  detenerTimerModal()
  segundosRestantes.value = 30
  mostrarModalConfirmacion.value = true

  modalTimerInterval = setInterval(() => {
    segundosRestantes.value -= 1
    if (segundosRestantes.value <= 0) {
      cerrarModalConfirmacion()
    }
  }, 1000)
}

function cerrarModalConfirmacion() {
  if (cargando.value) return
  detenerTimerModal()
  emit('actividad')
  mostrarModalConfirmacion.value = false
}

onUnmounted(() => {
  detenerTimerModal()
})

function detenerTimerModal() {
  if (modalTimerInterval) {
    clearInterval(modalTimerInterval)
    modalTimerInterval = null
  }
}

const props = defineProps({
  comidaSeleccionada: { type: String, required: true },
})

const emit = defineEmits(['entrega-registrada', 'feedback', 'actividad'])

const busqueda = ref('')
const usarTecladoNumerico = ref(true)
const cargando = ref(false)
const personaActual = ref(null)
const resultadosBusqueda = ref([])

function mapearEstado(estado) {
  if (estado === 'autorizado') return { clase: 'badge-ok', icono: '✓', texto: 'Autorizado' }
  if (estado === 'entregado') return { clase: 'badge-done', icono: '✔✔', texto: 'Ya entregado' }
  return { clase: 'badge-no', icono: '✕', texto: 'No autorizado' }
}

const estadoComidaActual = computed(() =>
  personaActual.value ? mapearEstado(personaActual.value.estado) : null
)

const puedeEntregarIndividual = computed(
  () => personaActual.value && personaActual.value.estado === 'autorizado'
)

function obtenerIniciales(nombre, apellido) {
  return `${nombre?.[0] || ''}${apellido?.[0] || ''}`.toUpperCase()
}

function agregarDigito(digito) {
  emit('actividad')
  usarTecladoNumerico.value = true
  if (!/^\d*$/.test(busqueda.value)) busqueda.value = ''
  if (busqueda.value.length < 8) busqueda.value += digito
}

function borrarUltimo() {
  emit('actividad')
  busqueda.value = busqueda.value.slice(0, -1)
}

function limpiarBusqueda() {
  emit('actividad')
  busqueda.value = ''
  personaActual.value = null
  resultadosBusqueda.value = []
  emit('feedback', null)
}

function validarEntrada() {
  emit('actividad')
  if (usarTecladoNumerico.value) {
    busqueda.value = busqueda.value.replace(/\D/g, '').slice(0, 8)
  }
}

function alternarModoTeclado() {
  emit('actividad')
  usarTecladoNumerico.value = !usarTecladoNumerico.value
  limpiarBusqueda()
}

function seleccionarPersona(item) {
  emit('actividad')
  personaActual.value = item
  emit('feedback', null)
}

async function buscarPersona() {
  emit('actividad')
  const termino = busqueda.value.trim()
  if (!termino) return

  cargando.value = true
  emit('feedback', null)
  personaActual.value = null
  resultadosBusqueda.value = []

  try {
    const esDni = /^\d+$/.test(termino)
    const resultados = await comedorService.buscarAutorizados({
      dni: esDni ? termino : null,
      nya: !esDni ? termino : null,
      tipoComida: props.comidaSeleccionada,
    })

    resultadosBusqueda.value = resultados || []

    if (resultadosBusqueda.value.length === 0) {
      emit('feedback', { tipo: 'error', texto: 'No se encontró ninguna persona con ese criterio.' })
    } else if (resultadosBusqueda.value.length === 1) {
      personaActual.value = resultadosBusqueda.value[0]
    }
  } catch (err) {
    emit('feedback', { tipo: 'error', texto: err.message })
  } finally {
    cargando.value = false
  }
}

async function confirmarEntregaIndividual() {
  if (!puedeEntregarIndividual.value) return
  detenerTimerModal()
  cargando.value = true
  try {
    await comedorService.registrarEntrega({
      personasIds: [personaActual.value.id],
      tipoComida: props.comidaSeleccionada,
    })

    personaActual.value = { ...personaActual.value, estado: 'entregado', entregado: true }
    resultadosBusqueda.value = resultadosBusqueda.value.map((r) =>
      r.id === personaActual.value.id ? personaActual.value : r
    )
    mostrarModalConfirmacion.value = false
    emit('entrega-registrada', personaActual.value)
    emit('feedback', {
      tipo: 'success',
      texto: `Entrega registrada para ${personaActual.value.nombre} ${personaActual.value.apellido}.`,
    })

    if (resultadosBusqueda.value.length <= 1) {
      setTimeout(limpiarBusqueda, 3000)
    }
  } catch (err) {
    mostrarModalConfirmacion.value = false
    emit('feedback', { tipo: 'error', texto: err.message })
  } finally {
    cargando.value = false
  }
}

// Re-busca automáticamente si el operador cambia de Desayuno a Almuerzo con algo escrito
watch(() => props.comidaSeleccionada, () => {
  if (busqueda.value.trim()) buscarPersona()
})

defineExpose({ limpiarBusqueda })
</script>