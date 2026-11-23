<template>
  <div class="kiosk-container">
    <header class="kiosk-header">
      <div class="brand">
        <div class="brand-icon" aria-hidden="true">🍴</div>
        <div>
          <h1 class="brand-title">Sector Comedor</h1>
          <span class="brand-subtitle">Entrega de Pedidos</span>
        </div>
      </div>

      <div class="header-actions">
        <div class="status-pill" title="Fecha actual">
          <span>📅</span>
          <span>{{ fechaFormateada }}</span>
        </div>
        <div class="status-pill" title="Hora actual">
          <span>🕒</span>
          <span>{{ horaFormateada }}</span>
        </div>
        <button type="button" class="btn-logout" @click="cerrarSesion">
          <span>↪</span> Cerrar sesión
        </button>
      </div>
    </header>

    <div v-if="apiCaida" class="feedback-banner error" role="alert">
      <span class="feedback-icon">⚠</span>
      <span>Se perdió la conexión con el servidor. Verificá la red e intentá nuevamente.</span>
      <button type="button" class="btn-mode-toggle" @click="reintentarConexion">
        Reintentar
      </button>
    </div>

    <nav class="main-tabs" aria-label="Vistas principales">
      <button
        type="button"
        class="tab-btn"
        :class="{ active: vistaActiva === 'entrega' }"
        @click="vistaActiva = 'entrega'"
      >
        Entrega
      </button>
      <button
        type="button"
        class="tab-btn"
        :class="{ active: vistaActiva === 'resumen' }"
        @click="abrirResumenDia"
      >
        Resumen del día
      </button>
    </nav>

    <main v-if="vistaActiva === 'entrega'" class="entrega-view">
      <div class="selectors-bar">
        <div class="pill-group" role="group" aria-label="Comida en curso">
          <button
            v-for="comida in comidas"
            :key="comida.id"
            type="button"
            class="pill-option"
            :class="{ active: comidaSeleccionada === comida.id }"
            @click="seleccionarComida(comida.id)"
          >
            {{ comida.label }}
          </button>
        </div>

        <div class="pill-group" role="group" aria-label="Modo de retiro">
          <button
            type="button"
            class="pill-option"
            :class="{ active: modoRetiro === 'individual' }"
            @click="cambiarModo('individual')"
          >
            Persona individual
          </button>
          <button
            type="button"
            class="pill-option"
            :class="{ active: modoRetiro === 'sector' }"
            @click="cambiarModo('sector')"
          >
            Grupo por sector
          </button>
        </div>
      </div>

      <div v-if="mensajeFeedback" class="feedback-banner" :class="mensajeFeedback.tipo" role="alert">
        <span class="feedback-icon">{{ mensajeFeedback.tipo === 'success' ? '✔' : '⚠' }}</span>
        <span>{{ mensajeFeedback.texto }}</span>
      </div>

      <div class="workspace-grid">
        <RetiroIndividualPanel
          v-if="modoRetiro === 'individual'"
          ref="individualRef"
          :comida-seleccionada="comidaSeleccionada"
          @entrega-registrada="onEntregaIndividual"
          @feedback="mensajeFeedback = $event"
          @actividad="reiniciarInactividad"
        />

        <RetiroGrupalPanel
          v-else-if="modoRetiro === 'sector'"
          ref="grupalRef"
          :comida-seleccionada="comidaSeleccionada"
          :sectores="sectores"
          @entrega-grupal-registrada="onEntregaGrupal"
          @feedback="mensajeFeedback = $event"
          @actividad="reiniciarInactividad"
        />

        <EntregasRecientesAside :entregas="entregasRecientes" />
      </div>
    </main>

    <ResumenDiaView v-else/>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { comedorService, apiCaida } from '@/services/comedor'
import RetiroIndividualPanel from './componentes_comedor/RetiroIndividualPanel.vue'
import RetiroGrupalPanel from './componentes_comedor/RetiroGrupalPanel.vue'
import EntregasRecientesAside from './componentes_comedor/EntregasRecientesAside.vue'
import ResumenDiaView from './componentes_comedor/ResumenDiaView.vue'
import '@/assets/comedorKiosco.css'

const vistaActiva = ref('entrega')
const modoRetiro = ref('individual')
const comidas = [
  { id: 'desayuno', label: 'Desayuno' },
  { id: 'almuerzo', label: 'Almuerzo' },
  { id: 'merienda', label: 'Merienda' },
  { id: 'cena', label: 'Cena' },
]
const comidaSeleccionada = ref('desayuno')

const ahora = ref(new Date())
let relojInterval = null
let inactividadTimeout = null

const individualRef = ref(null)
const grupalRef = ref(null)

const mensajeFeedback = ref(null)
const entregasRecientes = ref([])
const sectores = ref([])
const resumenDia = ref([])
const cargandoResumen = ref(false)

const fechaFormateada = computed(() => {
  const texto = ahora.value.toLocaleDateString('es-AR', {
    weekday: 'long',
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  })
  return texto.charAt(0).toUpperCase() + texto.slice(1).replace(',', '')
})

const horaFormateada = computed(() =>
  ahora.value.toLocaleTimeString('es-AR', { hour: '2-digit', minute: '2-digit' })
)

function preseleccionarComidaPorHora() {
  const h = new Date().getHours()
  if (h >= 6 && h < 11) comidaSeleccionada.value = 'desayuno'
  else if (h >= 11 && h < 15) comidaSeleccionada.value = 'almuerzo'
  else if (h >= 15 && h < 19) comidaSeleccionada.value = 'merienda'
  else comidaSeleccionada.value = 'cena'
}

async function reintentarConexion() {
  const ok = await comedorService.verificarHealth()
  if (ok) mensajeFeedback.value = null
}

function abrirResumenDia() {
  reiniciarInactividad()
  vistaActiva.value = 'resumen'
}

function seleccionarComida(id) {
  reiniciarInactividad()
  comidaSeleccionada.value = id
}

function cambiarModo(modo) {
  reiniciarInactividad()
  modoRetiro.value = modo
  mensajeFeedback.value = null
}

function onEntregaIndividual(persona) {
  entregasRecientes.value.unshift({
    id: Date.now(),
    persona: `${persona.nombre} ${persona.apellido}`,
    sector: persona.sector,
    comida: comidas.find((c) => c.id === comidaSeleccionada.value)?.label,
    menu: persona.tipo_menu,
    hora: horaFormateada.value,
  })
}

async function cargarSectores() {
  try {
    sectores.value = await comedorService.obtenerSectores()
  } catch (err) {
    mensajeFeedback.value = { tipo: 'error', texto: err.message }
  }
}

function onEntregaGrupal(personas) {
  const comidaLabel = comidas.find((c) => c.id === comidaSeleccionada.value)?.label
  personas.forEach((persona) => {
    entregasRecientes.value.unshift({
      id: `${Date.now()}-${persona.id || persona.solicitud_id}`,
      persona: `${persona.nombre} ${persona.apellido}`,
      sector: persona.sector,
      comida: comidaLabel,
      menu: persona.tipo_menu,
      hora: horaFormateada.value,
    })
  })
}

function cerrarSesion() {
  localStorage.removeItem('token')
  localStorage.removeItem('refresh_token')
  window.location.href = '/login'
}

function reiniciarInactividad() {
  clearTimeout(inactividadTimeout)
  inactividadTimeout = setTimeout(() => {
    individualRef.value?.limpiarBusqueda()
    grupalRef.value?.limpiarSeleccion()
  }, 60000)
}

onMounted(() => {
  preseleccionarComidaPorHora()
  cargarSectores()
  relojInterval = setInterval(() => {
    ahora.value = new Date()
  }, 1000)
  reiniciarInactividad()
})

onUnmounted(() => {
  clearInterval(relojInterval)
  clearTimeout(inactividadTimeout)
})
</script>