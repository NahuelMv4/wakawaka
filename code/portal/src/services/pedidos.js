import { apiFetch } from './api'

export function listarPedidos(filtros = {}) {
  const params = new URLSearchParams()
  if (filtros.page) params.set('page', filtros.page)
  if (filtros.estado) params.set('estado', filtros.estado)
  if (filtros.tipo_comida_id) params.set('tipo_comida_id', filtros.tipo_comida_id)
  if (filtros.tipo_menu_id) params.set('tipo_menu_id', filtros.tipo_menu_id)
  if (filtros.fecha_desde) params.set('fecha_desde', filtros.fecha_desde)
  if (filtros.fecha_hasta) params.set('fecha_hasta', filtros.fecha_hasta)

  const query = params.toString()
  return apiFetch(`/requests/${query ? `?${query}` : ''}`)
}

export function obtenerPedido(id) {
  return apiFetch(`/requests/${id}`)
}

export function crearPedidos(payload) {
  return apiFetch('/requests/', {
    method: 'POST',
    body: payload,
  })
}

export function actualizarPedido(id, payload) {
  return apiFetch(`/requests/${id}`, {
    method: 'PUT',
    body: payload,
  })
}

export function eliminarPedido(id) {
  return apiFetch(`/requests/${id}`, {
    method: 'DELETE',
  })
}

export async function obtenerPersonalDisponible() {
  const primera = await apiFetch('/personnel/?page=1')
  if (Array.isArray(primera)) return primera

  const items = [...(primera.data || primera.items || [])]
  const totalPages = primera.pages || 1

  for (let page = 2; page <= totalPages; page += 1) {
    const siguiente = await apiFetch(`/personnel/?page=${page}`)
    items.push(...(siguiente.data || siguiente.items || []))
  }

  return items
}

export function crearPersonalSector(payload) {
  return apiFetch('/personnel/', {
    method: 'POST',
    body: payload,
  })
}

export function actualizarPersonalSector(id, payload) {
  return apiFetch(`/personnel/${id}`, {
    method: 'PATCH',
    body: payload,
  })
}

export function eliminarPersonalSector(id) {
  return apiFetch(`/personnel/${id}`, {
    method: 'DELETE',
  })
}

export async function obtenerTiposMenu() {
  return [
    { id: 1, nombre: 'General' },
    { id: 2, nombre: 'Vegetariano' },
    { id: 3, nombre: 'Celíaco' },
    { id: 4, nombre: 'Diabético' },
  ]
}

export function obtenerCuposSector() {
  return apiFetch('/quotas/')
}

export function obtenerConfiguracionSistema() {
  return apiFetch('/configuration')
}