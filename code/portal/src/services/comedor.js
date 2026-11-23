import { ref } from 'vue'
import { apiFetch, ApiError } from './api'

export const apiCaida = ref(false)

async function ejecutarConEstadoRed(fn) {
  try {
    const data = await fn()
    apiCaida.value = false
    return data
  } catch (err) {
    if (err instanceof ApiError && err.status === 0) {
      apiCaida.value = true
      throw new Error('Se perdió la conexión con el servidor. Verificá la red e intentá nuevamente.')
    }
    throw err
  }
}

export const comedorService = {
  async verificarHealth() {
    try {
      await apiFetch('/health')
      apiCaida.value = false
      return true
    } catch {
      apiCaida.value = true
      return false
    }
  },

  async buscarAutorizados({ fecha, dni, nya, sectorId, tipoComida } = {}) {
    return ejecutarConEstadoRed(async () => {
      const params = new URLSearchParams()
      const fechaConsulta = fecha || new Date().toISOString().split('T')[0]
      params.append('fecha', fechaConsulta)

      if (dni) params.append('dni', dni)
      if (nya) params.append('nya', nya)
      if (sectorId) params.append('sector', sectorId)
      if (tipoComida) params.append('tipo_comida', tipoComida)

      return await apiFetch(`/authorized-meals?${params.toString()}`)
    })
  },

  async registrarEntrega({ fecha, personasIds, tipoComida, responsableId = null, tercero = null }) {
    return ejecutarConEstadoRed(async () => {
      const fechaConsulta = fecha || new Date().toISOString().split('T')[0]
      const payload = {
        fecha: fechaConsulta,
        personas: personasIds,
        tipo_comida: tipoComida,
        ...(responsableId ? { responsable_id: responsableId } : {}),
        ...(tercero ? { responsable_tercero: tercero } : {}),
      }

      return await apiFetch('/deliveries', {
        method: 'POST',
        body: payload,
      })
    })
  },

  async obtenerResumenDia(fecha = null) {
    return ejecutarConEstadoRed(async () => {
      const params = new URLSearchParams()
      const fechaConsulta = fecha || new Date().toISOString().split('T')[0]
      params.append('fecha', fechaConsulta)

      return await apiFetch(`/daily-summary?${params.toString()}`)
    })
  },

  async obtenerSectores() {
    return ejecutarConEstadoRed(async () => {
      return await apiFetch('/sectores/activos')
    })
  },
}