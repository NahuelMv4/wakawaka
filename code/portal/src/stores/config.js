import { ref } from 'vue'
import { defineStore } from 'pinia'

export const useConfigStore = defineStore('config', () => {
  const cargada = ref(false)
  const paginacion = ref(25)
  const horarioCorte = ref('18:00')
  const horariosComidas = ref([])
  const mantenimiento = ref(false)
  const mensajeMantenimiento = ref('El sistema se encuentra en mantenimiento programado.')

  function setConfiguracion(data) {
    paginacion.value = data.paginacion ?? 25
    horarioCorte.value = data.horario_corte ?? '18:00'
    horariosComidas.value = data.horarios_comidas ?? []
    mantenimiento.value = Boolean(data.mantenimiento)
    if (data.mensaje_mantenimiento) {
      mensajeMantenimiento.value = data.mensaje_mantenimiento
    }
    cargada.value = true
  }

  function activarMantenimiento(mensaje) {
    mantenimiento.value = true
    if (mensaje) {
      mensajeMantenimiento.value = mensaje
    }
    cargada.value = true
  }

  return {
    cargada,
    paginacion,
    horarioCorte,
    horariosComidas,
    mantenimiento,
    mensajeMantenimiento,
    setConfiguracion,
    activarMantenimiento,
  }
})