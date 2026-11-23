import { useConfigStore } from '@/stores/config'
import { apiFetch } from './api'

export async function fetchConfiguration() {
  const config = useConfigStore()
  const data = await apiFetch('/configuration')
  config.setConfiguracion(data)
  return data
}