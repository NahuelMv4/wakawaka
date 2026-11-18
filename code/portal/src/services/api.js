import { useAuthStore } from "@/stores/auth";

const API_URL = import.meta.env.VITE_API_URL

if(!API_URL) {
  throw new Error('No hay API_URL definido en .env')
}

export class ApiError extends Error {
  constructor(status, message) {
    super(message)
    this.status = status
  }
}

export async function apiFetch(path, { method= 'GET', body} = {}) {
  const auth = useAuthStore()

  const options = { method, headers: {}}
  if(auth.token) options.headers.Authorization = `Bearer ${auth.token}`

  if(body !== undefined) {
    options.headers['Content-Type'] = 'application/json'
    options.body = JSON.stringify(body)
  }

  let response
  try {
    response = await fetch(`${API_URL}${path}`, options)
  } catch {
    throw new ApiError(0, 'No hay conexion con la API')
  }

  if(response.status === 401) auth.clearSession()

  if(!response.ok) {
    const data = await response.json().catch(() => ({}))
    throw new ApiError(response.status, data.error ?? data.msg ?? 'Error inesperado')
  }

  // Si no se trae un cuerpo de respuesta queda null
  return response.status === 204 ? null : response.json()
}