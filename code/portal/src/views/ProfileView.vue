<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { fetchMe, logout } from '@/services/auth'
import { obtenerRutaInicialPorRol } from '@/utils/roleRedirect.js'
import { manejarErrorApi } from '@/utils/apiErrorHandler.js'

const router = useRouter()
const auth = useAuthStore()

const actualizando = ref(false)
const cerrandoSesion = ref(false)
const error = ref('')
const aviso = ref('')

const usuario = computed(() => auth.user)

const nombreCompleto = computed(() => {
  if (!usuario.value) return 'Usuario'
  return [usuario.value.nombre, usuario.value.apellido].filter(Boolean).join(' ') || 'Usuario'
})

const permisos = computed(() =>
  Array.isArray(usuario.value?.permisos) ? usuario.value.permisos : []
)

async function refrescarPerfil() {
  actualizando.value = true
  error.value = ''
  aviso.value = ''
  try {
    await fetchMe()
    aviso.value = 'Datos de sesión actualizados desde el servidor.'
  } catch (err) {
    error.value = await manejarErrorApi(err, router, {
      mensajePorDefecto: 'No se pudieron actualizar los datos del perfil.',
    })
  } finally {
    actualizando.value = false
  }
}

function irAInicio() {
  router.push(obtenerRutaInicialPorRol(usuario.value?.rol))
}

async function manejarLogout() {
  cerrandoSesion.value = true
  error.value = ''
  try {
    await logout()
    await router.push({ name: 'login' })
  } catch (err) {
    error.value = await manejarErrorApi(err, router, {
      mensajePorDefecto: 'No se pudo cerrar la sesión.',
    })
  } finally {
    cerrandoSesion.value = false
  }
}

onMounted(() => {
  if (auth.isAuthenticated && !auth.user) {
    refrescarPerfil()
  }
})
</script>

<template>
  <div class="perfil-page">
    <header class="page-header">
      <div>
        <h1>Perfil de Usuario</h1>
        <p class="subtitle">Información de tu cuenta, rol asignado y permisos activos en la web.</p>
      </div>
      <div class="header-actions">
        <button type="button" class="btn-secondary" @click="irAInicio">
          Ir a mi inicio
        </button>
        <button
          type="button"
          class="btn-secondary"
          :disabled="actualizando"
          @click="refrescarPerfil"
        >
          {{ actualizando ? 'Actualizando...' : 'Actualizar datos' }}
        </button>
        <button
          type="button"
          class="btn-danger"
          :disabled="cerrandoSesion"
          @click="manejarLogout"
        >
          {{ cerrandoSesion ? 'Saliendo...' : 'Cerrar sesión' }}
        </button>
      </div>
    </header>

    <div v-if="error" class="alert alert-error">{{ error }}</div>
    <div v-if="aviso" class="alert alert-success">{{ aviso }}</div>

    <section v-if="usuario" class="card">
      <div class="perfil-top">
        <div class="avatar">
          {{ (usuario.nombre?.[0] || usuario.email?.[0] || 'U').toUpperCase() }}
        </div>
        <div>
          <h2>{{ nombreCompleto }}</h2>
          <p class="email">{{ usuario.email }}</p>
        </div>
        <span class="badge-rol">{{ usuario.rol || 'Sin rol' }}</span>
      </div>

      <dl class="datos-grid">
        <div class="dato-item">
          <dt>ID de Usuario</dt>
          <dd>{{ usuario.id ?? '—' }}</dd>
        </div>
        <div class="dato-item">
          <dt>Rol</dt>
          <dd>{{ usuario.rol ?? '—' }}</dd>
        </div>
        <div class="dato-item">
          <dt>Sector ID</dt>
          <dd>{{ usuario.sector_id ?? 'No asignado' }}</dd>
        </div>
      </dl>

      <div class="permisos-section">
        <h3>Permisos asignados</h3>
        <div v-if="permisos.length > 0" class="permisos-list">
          <span v-for="permiso in permisos" :key="permiso" class="permiso-tag">
            {{ permiso }}
          </span>
        </div>
        <p v-else class="muted">Este usuario no tiene permisos listados.</p>
      </div>
    </section>

    <section v-else class="card empty-state">
      Cargando información del perfil...
    </section>
  </div>
</template>

<style scoped>
.perfil-page {
  max-width: 860px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 20px;
}

.page-header h1 {
  font-size: 24px;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 4px;
}

.subtitle {
  color: #4a5568;
  font-size: 14px;
  margin: 0;
}

.header-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.perfil-top {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 14px;
  padding-bottom: 20px;
  border-bottom: 1px solid #edf2f7;
}

.avatar {
  width: 52px;
  height: 52px;
  border-radius: 999px;
  background-color: #2c3e50;
  color: #ffffff;
  font-weight: 700;
  font-size: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.perfil-top h2 {
  margin: 0;
  font-size: 19px;
  color: #2c3e50;
}

.email {
  margin: 2px 0 0;
  color: #4a5568;
  font-size: 14px;
}

.badge-rol {
  margin-left: auto;
  background-color: #ebf8ff;
  color: #2b6cb0;
  padding: 5px 12px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 700;
}

.datos-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 14px;
  margin: 20px 0;
}

.dato-item {
  background: #f7fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 12px 14px;
}

.dato-item dt {
  font-size: 12px;
  font-weight: 600;
  color: #718096;
  margin-bottom: 4px;
}

.dato-item dd {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  color: #2d3748;
}

.permisos-section h3 {
  font-size: 15px;
  font-weight: 700;
  color: #2c3e50;
  margin: 0 0 10px;
}

.permisos-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.permiso-tag {
  background-color: #f0fff4;
  border: 1px solid #9ae6b4;
  color: #2f855a;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
}

.muted {
  color: #718096;
  font-size: 14px;
  margin: 0;
}

.btn-secondary {
  background-color: #edf2f7;
  color: #2d3748;
  border: 1px solid #cbd5e0;
  padding: 8px 14px;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
}

.btn-secondary:disabled,
.btn-danger:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-danger {
  background-color: #e53e3e;
  color: #ffffff;
  border: none;
  padding: 8px 14px;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
}

.alert {
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 16px;
  font-size: 14px;
}

.alert-error {
  background-color: #fff5f5;
  border: 1px solid #feb2b2;
  color: #c53030;
}

.alert-success {
  background-color: #f0fff4;
  border: 1px solid #9ae6b4;
  color: #2f855a;
}

.empty-state {
  text-align: center;
  color: #718096;
  padding: 32px;
}
</style>