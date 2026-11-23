<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { login, loginWithGoogle } from '@/services/auth'
import { obtenerRutaInicialPorRol } from '@/utils/roleRedirect.js'

const router = useRouter()
const route = useRoute()

const form = reactive({
  email: '',
  password: ''
})

const cargando = ref(false)
const mensajeError = ref('')
const googleBtnRef = ref(null)

let googleInicializado = false
let intervaloGoogle = null

function resolverDestinoPostLogin(usuario) {
  const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : ''

  if (redirect && redirect.startsWith('/') && redirect !== '/login') {
    return redirect
  }

  return obtenerRutaInicialPorRol(usuario?.rol)
}

async function manejarLogin() {
  mensajeError.value = ''

  if (!form.email || !form.password) {
    mensajeError.value = 'Por favor, completa todos los campos.'
    return
  }

  cargando.value = true

  try {
    const usuario = await login(form.email, form.password)
    router.push(resolverDestinoPostLogin(usuario))
  } catch (error) {
    mensajeError.value = error.message || 'Ocurrió un error al iniciar sesión.'
  } finally {
    cargando.value = false
  }
}

async function manejarRespuestaGoogle(response) {
  mensajeError.value = ''
  cargando.value = true

  try {
    const usuario = await loginWithGoogle(response.credential)
    router.push(resolverDestinoPostLogin(usuario))
  } catch (error) {
    mensajeError.value = error.message || 'No se pudo iniciar sesión con Google.'
  } finally {
    cargando.value = false
  }
}

function inicializarGoogle() {
  if (googleInicializado || !window.google || !googleBtnRef.value) return
  googleInicializado = true

  window.google.accounts.id.initialize({
    client_id: import.meta.env.VITE_GOOGLE_CLIENT_ID,
    callback: manejarRespuestaGoogle
  })

  window.google.accounts.id.renderButton(googleBtnRef.value, {
    theme: 'outline',
    size: 'large',
    text: 'signin_with',
    width: 318
  })
}

onMounted(() => {
  if (window.google) {
    inicializarGoogle()
  } else {
    intervaloGoogle = setInterval(() => {
      if (window.google) {
        clearInterval(intervaloGoogle)
        intervaloGoogle = null
        inicializarGoogle()
      }
    }, 100)
  }
})

onUnmounted(() => {
  if (intervaloGoogle) {
    clearInterval(intervaloGoogle)
    intervaloGoogle = null
  }
})
</script>

<template>
  <div class="login-container">
    <form class="login-card" @submit.prevent="manejarLogin">
      <h2>Iniciar Sesión</h2>
      
      <div class="form-group">
        <label for="email">Correo Electrónico</label>
        <input 
          id="email"
          type="email" 
          v-model="form.email" 
          placeholder="tu@correo.com" 
          autocomplete="email"
        />
      </div>

      <div class="form-group">
        <label for="password">Contraseña</label>
        <input 
          id="password"
          type="password" 
          v-model="form.password" 
          placeholder="••••••••" 
          autocomplete="current-password"
        />
      </div>

      <p v-if="mensajeError" class="error">{{ mensajeError }}</p>

      <button type="submit" :disabled="cargando">
        {{ cargando ? 'Iniciando sesión...' : 'Entrar' }}
      </button>

      <div class="divider">
        <span>o</span>
      </div>

      <div ref="googleBtnRef" class="google-btn-wrapper"></div>
    </form>
  </div>
</template>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 80vh;
  font-family: sans-serif;
}

.login-card {
  width: 100%;
  max-width: 380px;
  padding: 30px;
  border: 1px solid #e1e4e8;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  background: #ffffff;
}

h2 {
  margin-bottom: 24px;
  text-align: center;
  color: #2c3e50;
}

.form-group {
  margin-bottom: 16px;
  display: flex;
  flex-direction: column;
}

label {
  margin-bottom: 6px;
  font-size: 14px;
  font-weight: 600;
  color: #4a5568;
}

input {
  padding: 10px 12px;
  border: 1px solid #cbd5e0;
  border-radius: 6px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
}

input:focus {
  border-color: #42b883;
}

button {
  width: 100%;
  padding: 10px;
  background-color: #42b883;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
  margin-top: 10px;
}

button:hover:not(:disabled) {
  background-color: #35495e;
}

button:disabled {
  background-color: #a0aec0;
  cursor: not-allowed;
}

.divider {
  display: flex;
  align-items: center;
  text-align: center;
  margin: 18px 0;
  color: #718096;
  font-size: 13px;
}

.divider::before,
.divider::after {
  content: '';
  flex: 1;
  border-bottom: 1px solid #e2e8f0;
}

.divider span {
  padding: 0 10px;
}

.google-btn-wrapper {
  display: flex;
  justify-content: center;
}

.error {
  color: #e53e3e;
  font-size: 13px;
  margin-bottom: 12px;
  text-align: center;
}
</style>