import { useAuthStore } from "@/stores/auth"
import { apiFetch } from "./api"

export async function fetchMe() {
  const usuario = await apiFetch('/auth/me')
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

  // GET /api/auth/me
  return await fetchMe()
}

export async function logout() {
  try {
    await apiFetch('/auth/logout', { method: 'POST' })
  } finally {
    useAuthStore().clearSession()
  }
}