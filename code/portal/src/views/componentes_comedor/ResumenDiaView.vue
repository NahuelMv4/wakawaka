<script setup>
import { ref, computed, onMounted } from 'vue'
import { comedorService } from '../../services/comedor.js'
import '@/assets/resumenDia.css'

const resumen = ref([])
const cargando = ref(false)
const error = ref(null)

const totalEntregadoHoy = computed(() => {
  return resumen.value.reduce((acc, bloque) => acc + (bloque.subtotal_entregados || 0), 0)
})

async function cargarResumen() {
  cargando.value = true
  error.value = null
  try {
    resumen.value = await comedorService.obtenerResumenDia()
  } catch (err) {
    error.value = err.message
  } finally {
    cargando.value = false
  }
}

onMounted(() => {
  cargarResumen()
})
</script>

<template>
  <section class="resumen-wrapper">
    <div class="resumen-topbar">
      <h2 class="resumen-title">Resumen de entregas del día</h2>

      <button type="button" class="btn-refresh" :disabled="cargando" @click="cargarResumen">
        <span :class="['refresh-icon', { spinning: cargando }]">↻</span>
        {{ cargando ? 'Actualizando...' : 'Actualizar' }}
      </button>
    </div>

    <div v-if="!error && resumen.length > 0" class="total-banner">
      <span class="total-label">Total entregado hoy</span>
      <strong class="total-value">{{ totalEntregadoHoy }}</strong>
    </div>

    <div v-if="cargando && resumen.length === 0" class="estado-box">
      <div class="spinner-border text-primary mb-2" role="status"></div>
      <p class="mb-0">Cargando resumen...</p>
    </div>

    <div v-else-if="error" class="estado-box estado-error">
      <strong>No se pudo cargar el resumen</strong>
      <p class="mb-2">{{ error }}</p>
      <button type="button" class="btn-refresh" @click="cargarResumen">Reintentar</button>
    </div>

    <div v-else-if="resumen.length === 0" class="estado-box">
      <p class="mb-0">No hay entregas registradas para hoy.</p>
    </div>

    <!-- Tarjetas por comida -->
    <div v-else class="comidas-grid">
      <article v-for="bloque in resumen" :key="bloque.comida" class="comida-card">
        <header class="comida-card-header">
          <h3 class="comida-nombre">{{ bloque.comida }}</h3>
          <span class="comida-total-pill">{{ bloque.subtotal_entregados }} entregadas</span>
        </header>

        <table class="resumen-table">
          <thead>
            <tr>
              <th>Tipo de menú</th>
              <th class="col-num">Entregados</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="menu in bloque.menus" :key="menu.tipo_menu">
              <td class="menu-name">{{ menu.tipo_menu }}</td>
              <td class="col-num">
                <span :class="['pill', menu.entregados > 0 ? 'pill-success' : 'pill-muted']">
                  {{ menu.entregados }}
                </span>
              </td>
            </tr>
            <tr v-if="!bloque.menus || bloque.menus.length === 0">
              <td colspan="2" class="empty-row">Sin entregas en este turno</td>
            </tr>
          </tbody>
        </table>
      </article>
    </div>
  </section>
</template>