<script setup>
import { onMounted } from 'vue'
import { RouterView } from 'vue-router'
import { useConfigStore } from '@/stores/config'
import { fetchConfiguration } from '@/services/config'
import MantenimientoView from '@/views/MantenimientoView.vue'

const config = useConfigStore()

onMounted(async () => {
  if (!config.cargada) {
    try {
      await fetchConfiguration()
    } catch {
      config.cargada = true
    }
  }
})
</script>

<template>
  <MantenimientoView v-if="config.mantenimiento" />
  <RouterView v-else-if="config.cargada" />
</template>