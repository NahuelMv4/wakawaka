<script setup>
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";

const API_BASE = "http://127.0.0.1:5000";
const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

const idPedido = route.params.id;
const detallePedido = ref(null);
const solicitudes = ref([]);
const cargando = ref(false);
const errorMsg = ref("");

function headers() {
  const h = { Accept: "application/json", "Content-Type": "application/json" };
  const token =
    authStore?.token ||
    localStorage.getItem("access_token") ||
    localStorage.getItem("token");
  if (token) h.Authorization = `Bearer ${token}`;
  return h;
}

async function cargarSolicitudes() {
  cargando.value = true;
  errorMsg.value = "";
  try {
    const res = await fetch(`${API_BASE}/api/authorizations/${idPedido}`, {
      headers: headers(),
      credentials: "include",
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.error || "Error al cargar solicitudes.");
    detallePedido.value = data;
    solicitudes.value = (data.solicitudes_comida || []).map((s) => ({
      ...s,
      autorizada: Boolean(s.autorizada),
      rechazada: false,
    }));
  } catch (e) {
    errorMsg.value = e.message;
  } finally {
    cargando.value = false;
  }
}

async function autorizarSolicitud(s) {
  errorMsg.value = "";
  try {
    const res = await fetch(`${API_BASE}/api/solicitudes-comida/${s.id}/autorizar`, {
      method: "PATCH",
      headers: headers(),
      credentials: "include",
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.error || "No se pudo autorizar la solicitud.");
    s.autorizada = true;
    s.rechazada = false;
  } catch (e) {
    errorMsg.value = e.message;
  }
}

async function rechazarSolicitud(s) {
  s.autorizada = false;
  s.rechazada = true;
  // TODO: conectar rechazo con endpoint/motivo en backend
}

onMounted(cargarSolicitudes);
</script>

<template>
  <section class="detalle-solicitudes">
    <div class="cabecera">
      <button type="button" class="btn-volver" @click="router.push({ name: 'autorizacion' })">
        &lsaquo; Volver
      </button>
      <h2>Solicitudes del Pedido #{{ idPedido }}</h2>
    </div>

    <p v-if="errorMsg" class="error">{{ errorMsg }}</p>
    <p v-else-if="cargando">Cargando...</p>

    <div v-else class="tabla-wrap">
      <table>
        <thead>
          <tr>
            <th>#</th>
            <th>Persona</th>
            <th>DNI</th>
            <th>Fecha</th>
            <th>Condición</th>
            <th>Menú</th>
            <th>Estado</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="s in solicitudes" :key="s.id">
            <td>#{{ s.id }}</td>
            <td>{{ s.persona_nombre }}</td>
            <td>{{ s.dni || "-" }}</td>
            <td>{{ s.fecha_comida || detallePedido?.fecha || "-" }}</td>
            <td>{{ s.condicion }}</td>
            <td>{{ s.tipo_menu_nombre || s.tipo_menu_id }}</td>
            <td>
              <span class="badge" :class="s.autorizada ? 'ok' : s.rechazada ? 'rechazada' : 'pendiente'">
                {{ s.autorizada ? "Autorizada" : s.rechazada ? "Rechazada" : "Pendiente" }}
              </span>
            </td>
            <td class="acciones">
              <button type="button" class="btn-ok" :disabled="s.autorizada" @click="autorizarSolicitud(s)">
                Autorizar
              </button>
              <button type="button" class="btn-no" :disabled="s.rechazada" @click="rechazarSolicitud(s)">
                Rechazar
              </button>
            </td>
          </tr>
          <tr v-if="!solicitudes.length">
            <td colspan="8" class="vacio">Sin solicitudes para mostrar.</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>

<style scoped>
.detalle-solicitudes { padding: 1rem; }
.cabecera { display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem; }
.cabecera h2 { margin: 0; font-size: 1.25rem; }
.tabla-wrap { overflow-x: auto; border: 1px solid #d3dadd; border-radius: 8px; background: #fff; }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 0.6rem 0.75rem; border-bottom: 1px solid #e5ecee; text-align: left; white-space: nowrap; }
th { background: #eef4f8; font-weight: 600; }
.acciones { display: flex; gap: 0.4rem; }
button { border: 0; border-radius: 6px; padding: 0.35rem 0.65rem; cursor: pointer; font-weight: 500; }
button:disabled { opacity: 0.45; cursor: not-allowed; }
.btn-volver { background: #e4eff7; color: #0b4f80; }
.btn-ok { background: #2e7d32; color: #fff; }
.btn-no { background: #c62828; color: #fff; }
.badge { padding: 0.2rem 0.5rem; border-radius: 999px; font-size: 0.8rem; font-weight: 600; }
.badge.ok { background: #e3f5e6; color: #1e6026; }
.badge.pendiente { background: #fff4d6; color: #855a00; }
.badge.rechazada { background: #fde3e3; color: #9b1c1c; }
.error { color: #b91c1c; font-weight: 500; }
.vacio { text-align: center; color: #64748b; padding: 1.25rem; }
</style>