import { useAuthStore } from "@/stores/auth"
import { apiFetch } from "./api"

const ROLES_PERMITIDOS_WEB = [
  'Jefe de Servicio',
  'Servicio de Alimentación',
  'Sector Comedor'
]

function validarAccesoWeb(usuario) {
  if (usuario.bloqueado === true || usuario.activo === false) {
    throw new Error('Tu usuario se encuentra bloqueado o inactivo. Contacta al Administrador.')
  }

  const rolUsuario = usuario.rol

  if (rolUsuario === 'Administrador') {
    throw new Error('Los usuarios con rol Administrador no tienen acceso a la aplicación web.')
  }

  if (!ROLES_PERMITIDOS_WEB.includes(rolUsuario)) {
    throw new Error('Tu rol no tiene permisos para acceder a la aplicación web.')
  }
}

export async function fetchMe() {
  const usuario = await apiFetch('/auth/me')
  validarAccesoWeb(usuario)
  useAuthStore().setUser(usuario)
  return usuario
}

export async function login(email, password) {
  const auth = useAuthStore()

  const data = await apiFetch('/auth/login', {
    method: 'POST',
    body: { email, password }
  })
  auth.setToken(data.access_token)

  try {
    return await fetchMe()
  } catch (error) {
    auth.clearSession()
    throw error
  }
}

export async function loginWithGoogle(credential) {
  const auth = useAuthStore()

  try {
    const data = await apiFetch('/auth/google', {
      method: 'POST',
      body: { credential }
    })
    auth.setToken(data.access_token)

    return await fetchMe()
  } catch (error) {
    auth.clearSession()
    if (error.status === 404) {
      throw new Error('Tu cuenta de Google no está registrada en el sistema. Debes solicitar el alta al Administrador.')
    }
    throw error
  }
}

export async function logout() {
  try {
    await apiFetch('/auth/logout', { method: 'POST' })
  } finally {
    useAuthStore().clearSession()
  }
}