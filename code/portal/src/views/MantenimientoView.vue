<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useConfigStore } from '@/stores/config'
import { fetchConfiguration } from '@/services/config'
import { manejarErrorApi } from '@/utils/apiErrorHandler.js'

const router = useRouter()
const config = useConfigStore()
const verificando = ref(false)
const aviso = ref('')
const error = ref('')

async function reintentar() {
  verificando.value = true
  aviso.value = ''
  error.value = ''
  try {
    await fetchConfiguration()
    if (config.mantenimiento) {
      aviso.value = 'El sistema continúa en mantenimiento. Intentá nuevamente en unos minutos.'
    } else {
      await router.push({ name: 'dashboard' })
    }
  } catch (err) {
    error.value = await manejarErrorApi(err, router, {
      mensajePorDefecto: 'No se pudo verificar el estado del sistema.',
    })
  } finally {
    verificando.value = false
  }
}
</script>

<template>
  <div class="min-vh-100 d-flex align-items-center justify-content-center bg-light p-3">
    <div class="card shadow-sm text-center p-4" style="max-width: 480px; width: 100%">
      <div class="card-body">
        <h2 class="text-danger fw-bold mb-3">Sitio en Mantenimiento</h2>
        <p class="fs-5 text-body mb-4">{{ config.mensajeMantenimiento }}</p>

        <p v-if="aviso" class="text-muted small mb-3">{{ aviso }}</p>

        <button
          type="button"
          class="btn btn-primary"
          :disabled="verificando"
          @click="reintentar"
        >
          {{ verificando ? 'Verificando...' : 'Reintentar' }}
        </button>
      </div>
    </div>
  </div>
</template>