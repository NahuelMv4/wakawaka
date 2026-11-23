import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import { useAuthStore } from '@/stores/auth'
import { useConfigStore } from '@/stores/config'
import { fetchMe } from '@/services/auth'
import { fetchConfiguration } from '@/services/config'
import { obtenerRutaInicialPorRol } from '@/utils/roleRedirect.js'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: LoginView,
    },
    {
      path: '/acceso-denegado',
      name: 'acceso-denegado',
      component: () => import('@/views/AccesoDenegadoView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/kiosco',
      name: 'kiosco-busqueda',
      component: () => import('@/views/ComedorKioscoView.vue'),
      meta: { requiresAuth: true, kioskMode: true },
    },
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          name: 'dashboard',
          component: () => import('@/views/DashboardView.vue'),
        },
        {
          path: 'perfil',
          name: 'perfil',
          component: () => import('@/views/ProfileView.vue'),
        },
        {
          path: 'pedidos',
          name: 'pedidos',
          component: () => import('@/views/PedidosView.vue'),
          meta: { roles: ['Jefe de Servicio'] },
        },
        {
          path: 'pedidos/nuevo',
          name: 'pedidos-nuevo',
          component: () => import('@/views/PedidoFormView.vue'),
          meta: { roles: ['Jefe de Servicio'] },
        },
        {
          path: 'pedidos/:id/editar',
          name: 'pedidos-editar',
          component: () => import('@/views/PedidoFormView.vue'),
          meta: { roles: ['Jefe de Servicio'] },
        },
        {
          path: 'reportes',
          name: 'reportes',
          component: () => import('@/views/ReportesView.vue'),
          meta: { roles: ['Servicio de Alimentación'] },
        },
        {
          path: 'autorizacion',
          name: 'autorizacion',
          component: () => import('@/views/AutorizacionView.vue'),
        },
        {
          path: 'autorizacion/pedidos/:id',
          name: 'autorizacion-pedido-solicitudes',
          component: () => import('@/views/PedidoSolicitudesView.vue'),
        },
        {
          path: 'autorizacion/cupos',
          name: 'autorizacion-cupos',
          component: () => import('@/views/CuposView.vue'),
        },
      ],
    },
  ],
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()
  const config = useConfigStore()

  if (!config.cargada) {
    try {
      await fetchConfiguration()
    } catch {
      // En caso de fallo el middleware maneja el estado
    }
  }

  if (config.mantenimiento) {
    return true
  }

  if (auth.isAuthenticated && !auth.user) {
    try {
      await fetchMe()
    } catch (err) {
      if (err?.status === 503) return true
      return { name: 'login' }
    }
  }

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { name: 'login' }
  }

  if (to.name === 'login' && auth.isAuthenticated) {
    if (!auth.user) {
      try {
        await fetchMe()
      } catch {
        return true
      }
    }
    return obtenerRutaInicialPorRol(auth.user?.rol)
  }

  const rolesPermitidos = to.matched
    .map((record) => record.meta?.roles)
    .find((roles) => Array.isArray(roles) && roles.length > 0)

  if (rolesPermitidos && !rolesPermitidos.includes(auth.user?.rol)) {
    return { name: 'acceso-denegado' }
  }
})

export default router