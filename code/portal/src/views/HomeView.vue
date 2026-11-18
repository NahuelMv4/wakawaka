<script setup>
import { RouterLink, RouterView, useRouter } from 'vue-router'
import { logout } from '@/services/auth' 

const router = useRouter()

async function manejarCerrarSesion() {
  await logout()
  router.push({ name: 'login' })
}
</script>

<template>
  <div class="admin-layout">
    <aside class="sidebar">
      <h2>Mi Aplicación</h2>
      
      <nav class="menu">
        <RouterLink :to="{ name: 'dashboard' }">📊 Dashboard</RouterLink>
        <RouterLink :to="{ name: 'perfil' }">👤 Mi Perfil</RouterLink>
      </nav>

      <div class="sidebar-footer">
        <button @click="manejarCerrarSesion" class="btn-logout">Cerrar Sesión</button>
      </div>
    </aside>

    <main class="content-area">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
.admin-layout {
  display: flex;
  width: 100vw;
  height: 100vh;
  font-family: sans-serif;
  background-color: #f7fafc;
  overflow: hidden;
}

.sidebar {
  width: 260px;
  min-width: 260px;
  background-color: #2c3e50;
  color: white;
  display: flex;
  flex-direction: column;
  padding: 20px;
  box-sizing: border-box;
}

.sidebar h2 {
  font-size: 20px;
  margin-bottom: 30px;
  text-align: center;
  color: #42b883;
}

.menu {
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex-grow: 1;
}

.menu a {
  color: #cbd5e0;
  text-decoration: none;
  padding: 12px 16px;
  border-radius: 8px;
  transition: all 0.2s;
  font-weight: 500;
}

.menu a:hover {
  background-color: rgba(255, 255, 255, 0.08);
  color: white;
}

.menu a.router-link-exact-active {
  background-color: #42b883;
  color: white;
}

.sidebar-footer {
  border-top: 1px solid #3e4c59;
  padding-top: 15px;
}

.btn-logout {
  width: 100%;
  padding: 10px;
  background-color: #e53e3e;
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-logout:hover {
  background-color: #c53030;
}

.content-area {
  flex-grow: 1;
  padding: 40px;
  overflow-y: auto;
  background-color: #ffffff; 
  color: #2d3748; 
}
</style>