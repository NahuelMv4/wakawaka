<template>
  <section class="panel-card">
    <h2 class="panel-title">Retiro grupal por sector</h2>
    <p class="panel-desc">Seleccioná un sector y marcá las viandas autorizadas pendientes a retirar.</p>

    <div class="sector-controls">
      <select v-model="sectorSeleccionado" class="sector-select" @change="cargarPersonasSector">
        <option value="">Seleccionar sector...</option>
        <option v-for="sec in sectores" :key="sec.id" :value="sec.id">
          {{ sec.nombre }}
        </option>
      </select>
    </div>

    <div v-if="personasSector.length" class="sector-list">
      <label
        v-for="p in personasSector"
        :key="p.id"
        class="sector-item"
        :class="{ disabled: p.estado !== 'autorizado' }"
      >
        <input
          v-model="seleccionadosSector"
          type="checkbox"
          :value="p.id"
          :disabled="p.estado !== 'autorizado'"
          class="touch-checkbox"
        />
        <div class="sector-item-info">
          <strong>{{ p.nombre }} {{ p.apellido }}</strong>
          <span>DNI {{ p.dni }} · Menú {{ p.tipo_menu }}</span>
        </div>
        <span class="status-badge" :class="mapearEstado(p.estado).clase">
          {{ mapearEstado(p.estado).icono }} {{ mapearEstado(p.estado).texto }}
        </span>
      </label>

      <div v-if="seleccionadosSector.length > 1" class="responsable-box">
        <label class="responsable-label">Responsable del retiro (obligatorio):</label>
        <select v-model="responsableId" class="sector-select">
          <option value="">Elegir entre los seleccionados...</option>
          <option v-for="id in seleccionadosSector" :key="id" :value="id">
            {{ buscarNombrePorId(id) }}
          </option>
          <option value="tercero">Otra persona (tercero por DNI)</option>
        </select>

        <div v-if="responsableId === 'tercero'" class="tercero-inputs">
          <input v-model="terceroDni" type="text" inputmode="numeric" placeholder="DNI del responsable" class="search-input" />
          <input v-model="terceroNombre" type="text" placeholder="Nombre y apellido" class="search-input" />
        </div>
      </div>
    </div>

    <button
      type="button"
      class="btn-deliver"
      :disabled="seleccionadosSector.length === 0 || cargando || apiCaida"
      @click="confirmarEntregaGrupal"
    >
      ✓ Entregar {{ seleccionadosSector.length }} vianda(s)
    </button>
  </section>
</template>

<script setup>
import { ref, watch } from 'vue'
import { comedorService, apiCaida } from '@/services/comedor'

const props = defineProps({
  comidaSeleccionada: { type: String, required: true },
  sectores: { type: Array, default: () => [] },
})

const emit = defineEmits(['entrega-grupal-registrada', 'feedback', 'actividad'])

const cargando = ref(false)
const sectorSeleccionado = ref('')
const personasSector = ref([])
const seleccionadosSector = ref([])
const responsableId = ref('')
const terceroDni = ref('')
const terceroNombre = ref('')

function mapearEstado(estado) {
  if (estado === 'autorizado') return { clase: 'badge-ok', icono: '✓', texto: 'Autorizado' }
  if (estado === 'entregado') return { clase: 'badge-done', icono: '✔✔', texto: 'Ya entregado' }
  return { clase: 'badge-no', icono: '✕', texto: 'No autorizado' }
}

async function cargarPersonasSector() {
  emit('actividad')
  seleccionadosSector.value = []
  responsableId.value = ''
  if (!sectorSeleccionado.value) {
    personasSector.value = []
    return
  }
  try {
    personasSector.value = await comedorService.buscarAutorizados({
      sectorId: sectorSeleccionado.value,
      tipoComida: props.comidaSeleccionada,
    })
  } catch (err) {
    emit('feedback', { tipo: 'error', texto: err.message })
  }
}

function buscarNombrePorId(id) {
  const p = personasSector.value.find((item) => item.id === id)
  return p ? `${p.nombre} ${p.apellido}` : ''
}

async function confirmarEntregaGrupal() {
  const entregadas = personasSector.value.filter((p) => seleccionadosSector.value.includes(p.id))
  emit('feedback', { tipo: 'success', texto: 'Entrega grupal registrada correctamente.' })
  emit('entrega-grupal-registrada', entregadas)
  seleccionadosSector.value = []
  emit('actividad')
  cargando.value = true
  try {
    await comedorService.registrarEntrega({
      personasIds: seleccionadosSector.value,
      tipoComida: props.comidaSeleccionada,
      responsableId: responsableId.value !== 'tercero' ? responsableId.value : null,
      tercero: responsableId.value === 'tercero' ? { dni: terceroDni.value, nombre: terceroNombre.value } : null,
    })
    emit('feedback', { tipo: 'success', texto: 'Entrega grupal registrada correctamente.' })
    emit('entrega-grupal-registrada')
    seleccionadosSector.value = []
    await cargarPersonasSector()
  } catch (err) {
    emit('feedback', { tipo: 'error', texto: err.message })
  } finally {
    cargando.value = false
  }
}

function limpiarSeleccion() {
  seleccionadosSector.value = []
}

watch(() => props.comidaSeleccionada, () => {
  if (sectorSeleccionado.value) cargarPersonasSector()
})

defineExpose({ limpiarSeleccion })
</script>