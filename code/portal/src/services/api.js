import { useAuthStore } from '@/stores/auth'
import { useConfigStore } from '@/stores/config'

const API_URL = import.meta.env.VITE_API_URL

if (!API_URL) {
  throw new Error('No hay API_URL definido en .env')
}

export class ApiError extends Error {
  constructor(status, message, data = null) {
    super(message)
    this.status = status
    // Preservar el cuerpo JSON completo del error para mostrar detalles en formularios
    this.data = data
  }
}

// Agregue que se desempaquete mensajes de error simples, anidados, con prefijo 'error: {...}' o de validacion marshmallow
function formatearErrorApi(data) {
  let raw = data?.mensaje ?? data?.error ?? data?.msg
  if (!raw) return 'Error inesperado'

  // Si el backend serializo un diccionario como string JSON (con o sin prefijo "error:") se parsea
  if (typeof raw === 'string') {
    const sinPrefijo = raw.replace(/^error:\s*/i, '').trim()
    if (sinPrefijo.startsWith('{') && sinPrefijo.endsWith('}')) {
      try {
        raw = JSON.parse(sinPrefijo)
      } catch {
        return raw
      }
    } else {
      return raw
    }
  }

  if (typeof raw === 'object') {
    if (typeof raw.error === 'string') {
      const partes = [raw.error]
      if (Array.isArray(raw.fechas) && raw.fechas.length > 0) {
        partes.push(`Fechas: ${raw.fechas.join(', ')}`)
      }
      if (Array.isArray(raw.conflictos) && raw.conflictos.length > 0) {
        const lista = raw.conflictos.map((c) => `${c.comida} (${c.fecha})`).join(', ')
        partes.push(`Conflictos: ${lista}`)
      }
      return partes.join(' — ')
    }

    return Object.entries(raw)
      .map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(', ') : typeof v === 'object' ? JSON.stringify(v) : v}`)
      .join(' | ')
  }

  return String(raw)
}

export async function apiFetch(path, { method = 'GET', body } = {}) {
  const auth = useAuthStore()
  const config = useConfigStore()

  const options = { method, headers: {} }
  if (auth.token) options.headers.Authorization = `Bearer ${auth.token}`

  if (body !== undefined) {
    options.headers['Content-Type'] = 'application/json'
    options.body = JSON.stringify(body)
  }

  let response
  try {
    response = await fetch(`${API_URL}${path}`, options)
  } catch {
    throw new ApiError(0, 'No hay conexion con la API')
  }

  if (response.status === 401) {
    auth.clearSession()
  }

  if (!response.ok) {
    const data = await response.json().catch(() => ({}))
    // Modifique para que Extraer mensaje legible cuando data.error es un objeto estructurado o validacion marshmallow
    const mensaje = formatearErrorApi(data)

    if (response.status === 503) {
      config.activarMantenimiento(mensaje)
    }

    throw new ApiError(response.status, mensaje, data)
  }

  return response.status === 204 ? null : response.json()
}