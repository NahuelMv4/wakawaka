<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { obtenerRutaInicialPorRol } from '@/utils/roleRedirect.js'

const router = useRouter()
const auth = useAuthStore()

function volverAInicio() {
  router.push(obtenerRutaInicialPorRol(auth.user?.rol))
}
</script>

<template>
  <div class="acceso-denegado-page">
    <div class="card">
      <h2>Acceso denegado</h2>
      <p>Tu rol actual (<strong>{{ auth.user?.rol || 'Desconocido' }}</strong>) no tiene permiso para ver esta sección.</p>
      <button type="button" class="btn-primary" @click="volverAInicio">
        Ir a mi pantalla inicial
      </button>
    </div>
  </div>
</template>