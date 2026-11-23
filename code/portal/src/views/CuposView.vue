<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";

const router = useRouter();
const authStore = useAuthStore();
const API_BASE = "http://127.0.0.1:5000";

const cupos = ref([]);
const cargando = ref(false);
const errorMsg = ref("");
const feedbackMsg = ref("");

const busqueda = ref({ sector_id: "", tipo_comida_id: "" });
const editId = ref(null);
const editCant = ref(0);

function buildHeaders(includeJson = false) {
  const headers = { Accept: "application/json" };
  if (includeJson) headers["Content-Type"] = "application/json";
  const token =
    authStore?.token ||
    localStorage.getItem("access_token") ||
    localStorage.getItem("token");
  if (token) headers.Authorization = `Bearer ${token}`;
  return headers;
}

async function cargarCupos() {
  cargando.value = true;
  errorMsg.value = "";
  try {
    const params = new URLSearchParams();
    if (busqueda.value.sector_id) params.set("sector_id", busqueda.value.sector_id);
    if (busqueda.value.tipo_comida_id) params.set("tipo_comida_id", busqueda.value.tipo_comida_id);

    const qs = params.toString();
    const url = `${API_BASE}/api/quotas/${qs ? `?${qs}` : ""}`;
    const res = await fetch(url, {
      headers: buildHeaders(false),
      credentials: "include",
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.error || "Error al cargar cupos.");
    cupos.value = data.data || data.cupos || [];
  } catch (err) {
    errorMsg.value = err.message;
  } finally {
    cargando.value = false;
  }
}

function limpiarBusqueda() {
  busqueda.value = { sector_id: "", tipo_comida_id: "" };
  cargarCupos();
}

async function actualizarCupo(id) {
  errorMsg.value = "";
  feedbackMsg.value = "";
  try {
    const res = await fetch(`${API_BASE}/api/quotas/${id}`, {
      method: "PUT",
      headers: buildHeaders(true),
      credentials: "include",
      body: JSON.stringify({ cantidad: Number(editCant.value) }),
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.error || "No se pudo actualizar el cupo.");

    feedbackMsg.value = "Cupo actualizado correctamente.";
    editId.value = null;
    await cargarCupos();
  } catch (err) {
    errorMsg.value = err.message;
  }
}

onMounted(cargarCupos);
</script>

<template>
  <section class="cupos-view">
    <header class="encabezado">
      <h2>Administración de Cupos por Sector</h2>
      <button type="button" class="btn-limpiar" @click="router.back()">
        &lsaquo; Volver a Autorizaciones
      </button>
    </header>

    <p v-if="feedbackMsg" class="alerta-ok">{{ feedbackMsg }}</p>
    <p v-if="errorMsg" class="alerta-error">{{ errorMsg }}</p>

    <form class="barra-filtros" @submit.prevent="cargarCupos">
      <input v-model.trim="busqueda.sector_id" type="number" min="1" placeholder="Buscar por ID Sector" />
      <input v-model.trim="busqueda.tipo_comida_id" type="number" min="1" placeholder="Buscar por ID Comida" />
      <button type="submit" class="btn-buscar">Buscar</button>
      <button type="button" class="btn-limpiar" @click="limpiarBusqueda">Limpiar</button>
    </form>

    <p v-if="cargando">Cargando cupos...</p>

    <table v-else class="tabla-cupos">
      <thead>
        <tr>
          <th>Sector</th>
          <th>Comida</th>
          <th>Cupo</th>
          <th>Acción</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="c in cupos" :key="c.id">
          <td>{{ c.sector?.nombre || `Sector #${c.sector_id}` }}</td>
          <td>{{ c.tipo_comida?.nombre || `Comida #${c.tipo_comida_id}` }}</td>
          <td>
            <input v-if="editId === c.id" v-model="editCant" type="number" min="0" />
            <strong v-else>{{ c.cantidad }}</strong>
          </td>
          <td class="acciones">
            <template v-if="editId === c.id">
              <button type="button" class="btn-autorizar" @click="actualizarCupo(c.id)">Guardar</button>
              <button type="button" class="btn-limpiar" @click="editId = null">Cancelar</button>
            </template>
            <button v-else type="button" class="btn-limpiar" @click="editId = c.id; editCant = c.cantidad">
              Editar
            </button>
          </td>
        </tr>
        <tr v-if="cupos.length === 0">
          <td colspan="4" class="sin-datos">No hay cupos registrados.</td>
        </tr>
      </tbody>
    </table>
  </section>
</template>

<style scoped>
.cupos-view { padding: 1.25rem; display: flex; flex-direction: column; gap: 1rem; }
.encabezado { display: flex; justify-content: space-between; align-items: center; }
.barra-filtros, .acciones { display: flex; gap: 0.5rem; flex-wrap: wrap; align-items: center; }
.barra-filtros input { padding: 0.45rem 0.6rem; border: 1px solid #cbd5e1; border-radius: 4px; }
.tabla-cupos { width: 100%; border-collapse: collapse; }
.tabla-cupos th, .tabla-cupos td { padding: 0.65rem 0.75rem; border-bottom: 1px solid #e2e8f0; text-align: left; }
.tabla-cupos th { background: #f8fafc; }
.btn-limpiar { padding: 0.45rem 0.8rem; border: 1px solid #cbd5e1; background: #f1f5f9; border-radius: 4px; cursor: pointer; }
.btn-buscar { padding: 0.45rem 0.8rem; border: none; background: #1d4ed8; color: #fff; border-radius: 4px; cursor: pointer; }
.btn-autorizar { padding: 0.45rem 0.8rem; border: none; background: #15803d; color: #fff; border-radius: 4px; cursor: pointer; }
.alerta-ok { padding: 0.75rem; background: #dcfce7; color: #166534; border-radius: 4px; margin: 0; }
.alerta-error { padding: 0.75rem; background: #fee2e2; color: #991b1b; border-radius: 4px; margin: 0; }
.sin-datos { text-align: center; color: #64748b; padding: 1.5rem; }
</style>