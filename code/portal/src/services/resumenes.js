import { apiFetch } from './api'

function construirQuery(filtros = {}) {
  const params = new URLSearchParams()

  for (const [clave, valor] of Object.entries(filtros)) {
    if (valor === undefined || valor === null || valor === '') continue

    params.set(
      clave,
      Array.isArray(valor) ? valor.join(',') : valor
    )
  }

  const query = params.toString()
  return query ? `?${query}` : ''
}

export function obtenerResumenPedidos(filtros = {}) {
  return apiFetch(`/summaries/requests${construirQuery(filtros)}`)
}

export function obtenerResumenAutorizaciones(filtros = {}) {
  return apiFetch(`/summaries/authorizations${construirQuery(filtros)}`)
}

export function obtenerResumenEntregas(filtros = {}) {
  return apiFetch(`/summaries/deliveries${construirQuery(filtros)}`)
}

export function obtenerTiposComida() {
  return apiFetch('/tipos-comida/').then(res =>
    Array.isArray(res) ? res : res?.data || []
  )
}