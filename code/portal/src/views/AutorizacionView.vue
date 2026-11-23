<script setup>
import { ref, computed, onMounted, watch } from "vue";
import { useAuthStore } from "@/stores/auth";
import { useRouter } from "vue-router";

const router = useRouter();

const API_BASE = "http://127.0.0.1:5000";
const authStore = useAuthStore();

// Navegación temporal: "dia" | "semana" | "todos"
const modoPeriodo = ref("dia");
const fechaSeleccionada = ref(new Date().toISOString().slice(0, 10));
const fechasConPedidos = ref([]);

// Datos de pedidos
const pedidos = ref([]);
const cargando = ref(false);
const errorMsg = ref("");
const feedbackMsg = ref("");
const procesandoId = ref(null);

// Filtros de pedidos
const filtros = ref({
  sector_id: "",
  tipo_comida_id: "",
  tipo_menu_id: "",
  condicion: "",
  estado: "",
});

// Modal de rechazo con motivo obligatorio
const pedidoRechazo = ref(null);
const motivoRechazo = ref("");
const enviandoRechazo = ref(false);

function buildHeaders(includeJson = false) {
  const headers = { Accept: "application/json" };
  if (includeJson) {
    headers["Content-Type"] = "application/json";
  }
  const token =
    authStore?.token ||
    localStorage.getItem("access_token") ||
    localStorage.getItem("token");
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  return headers;
}

function toIsoDate(dateObj) {
  return dateObj.toISOString().slice(0, 10);
}

function shiftDate(isoDate, deltaDays) {
  const [y, m, d] = isoDate.split("-").map(Number);
  const dt = new Date(Date.UTC(y, m - 1, d + deltaDays));
  return toIsoDate(dt);
}

const rangoSemana = computed(() => {
  const [y, m, d] = fechaSeleccionada.value.split("-").map(Number);
  const dt = new Date(Date.UTC(y, m - 1, d));
  const diaSemana = dt.getUTCDay();
  const diffLunes = diaSemana === 0 ? -6 : 1 - diaSemana;
  const lunes = new Date(Date.UTC(y, m - 1, d + diffLunes));
  const domingo = new Date(
    Date.UTC(lunes.getUTCFullYear(), lunes.getUTCMonth(), lunes.getUTCDate() + 6)
  );
  return {
    desde: toIsoDate(lunes),
    hasta: toIsoDate(domingo),
  };
});

function esPasada(isoDate) {
  const hoy = new Date().toISOString().slice(0, 10);
  return Boolean(isoDate && isoDate < hoy);
}

function puedeEditarPedido(pedido) {
  if (!pedido || pedido.solo_lectura || esPasada(pedido.fecha)) return false;
  if (pedido.tiene_entregas) return false;
  if (procesandoId.value === pedido.id) return false;
  const estado = String(pedido.estado || "").trim().toLowerCase();
  return !["autorizado", "parcialmente autorizado", "rechazado"].includes(estado);
}

function navegarPeriodo(delta) {
  if (modoPeriodo.value === "todos") {
    modoPeriodo.value = "dia";
  }
  const paso = modoPeriodo.value === "semana" ? delta * 7 : delta;
  fechaSeleccionada.value = shiftDate(fechaSeleccionada.value, paso);
}

function irAHoy() {
  modoPeriodo.value = "dia";
  fechaSeleccionada.value = new Date().toISOString().slice(0, 10);
}

function construirQueryParams(incluirFormatoCsv = null) {
  const params = new URLSearchParams();
  if (modoPeriodo.value === "dia" && fechaSeleccionada.value) {
    params.set("fecha", fechaSeleccionada.value);
  } else if (modoPeriodo.value === "semana") {
    params.set("fecha_desde", rangoSemana.value.desde);
    params.set("fecha_hasta", rangoSemana.value.hasta);
  }

  for (const [k, v] of Object.entries(filtros.value)) {
    if (v !== "" && v !== null && v !== undefined) {
      params.set(k, v);
    }
  }
  if (incluirFormatoCsv) {
    params.set("formato", incluirFormatoCsv);
  }
  return params.toString();
}

async function cargarFechas() {
  try {
    const res = await fetch(`${API_BASE}/api/authorization-dates`, {
      headers: buildHeaders(false),
      credentials: "include",
    });
    if (!res.ok) return;
    const data = await res.json();
    fechasConPedidos.value = data.dates || [];
  } catch (err) {
    console.error("Error cargando fechas:", err);
  }
}

async function cargarPedidos() {
  cargando.value = true;
  errorMsg.value = "";
  try {
    const qs = construirQueryParams();
    const res = await fetch(`${API_BASE}/api/authorizations?${qs}`, {
      headers: buildHeaders(false),
      credentials: "include",
    });

    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(
        errData.message ||
          errData.error ||
          `Error ${res.status} al cargar los pedidos.`
      );
    }

    const data = await res.json();
    pedidos.value = data.pedidos || [];
  } catch (err) {
    errorMsg.value = err.message || "Error de conexión con el servidor.";
  } finally {
    cargando.value = false;
  }
}

async function manejarRespuestaConcurrencia(res, data) {
  if (res.status === 409) {
    errorMsg.value =
      data.error ||
      data.message ||
      "El pedido fue modificado o rechazado por otro usuario. Recargando datos...";
    await Promise.all([cargarPedidos(), cargarFechas()]);
    return true;
  }
  return false;
}

async function autorizarTodoElPedido(pedido) {
  if (!pedido || !puedeEditarPedido(pedido)) return;

  procesandoId.value = pedido.id;
  errorMsg.value = "";
  feedbackMsg.value = "";

  try {
    const res = await fetch(`${API_BASE}/api/authorizations/${pedido.id}`, {
      method: "PUT",
      headers: buildHeaders(true),
      credentials: "include",
      body: JSON.stringify({
        autorizada: true,
        estado: "Autorizado",
      }),
    });

    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      throw new Error(data.error || data.message || "Error al autorizar el pedido.");
    }

    feedbackMsg.value = `Pedido #${pedido.id} autorizado.`;
    await cargarPedidos();
  } catch (err) {
    errorMsg.value = err.message;
  } finally {
    procesandoId.value = null;
  }
}


function irADetalleSolicitudes(pedidoId) {
  if (!pedidoId) return;
  router.push({
    name: "autorizacion-pedido-solicitudes",
    params: { id: pedidoId },
  });
}


function abrirRechazo(pedido) {
  if (!pedido || !puedeEditarPedido(pedido)) return;
  pedidoRechazo.value = pedido;
  motivoRechazo.value = "";
  errorMsg.value = "";
}

function cerrarRechazo() {
  pedidoRechazo.value = null;
  motivoRechazo.value = "";
}

async function confirmarRechazo() {
  if (!pedidoRechazo.value) return;
  const motivo = motivoRechazo.value.trim();
  if (!motivo) {
    errorMsg.value = "El motivo del rechazo es obligatorio.";
    return;
  }

  enviandoRechazo.value = true;
  errorMsg.value = "";
  feedbackMsg.value = "";

  try {
    const res = await fetch(
      `${API_BASE}/api/authorizations/${pedidoRechazo.value.id}/reject`,
      {
        method: "PUT",
        headers: buildHeaders(true),
        credentials: "include",
        body: JSON.stringify({
          motivo_rechazo: motivo,
          actualizado_en: pedidoRechazo.value.actualizado_en ?? null,
        }),
      }
    );
    const data = await res.json().catch(() => ({}));
    if (await manejarRespuestaConcurrencia(res, data)) return;

    if (!res.ok) {
      throw new Error(
        data.error || data.message || "Error al rechazar el pedido."
      );
    }

    feedbackMsg.value =
      data.mensaje || `Pedido #${pedidoRechazo.value.id} rechazado.`;
    cerrarRechazo();
    await Promise.all([cargarPedidos(), cargarFechas()]);
  } catch (err) {
    errorMsg.value = err.message;
  } finally {
    enviandoRechazo.value = false;
  }
}

async function descargarCsv(tipoListado) {
  errorMsg.value = "";
  try {
    const qs = construirQueryParams("csv");
    const endpoint =
      tipoListado === "personas"
        ? `/api/authorized-meals?${qs}`
        : `/api/summaries/authorizations?${qs}`;

    const res = await fetch(`${API_BASE}${endpoint}`, {
      method: "GET",
      headers: buildHeaders(false),
      credentials: "include",
    });
    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.error || "No se pudo exportar el archivo CSV.");
    }

    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download =
      tipoListado === "personas"
        ? "personas_autorizadas.csv"
        : "totales_por_sector.csv";
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  } catch (err) {
    errorMsg.value = err.message;
  }
}

function irACupos() {
  router.push({ name: "autorizacion-cupos" });
}

function limpiarFiltros() {
  filtros.value = {
    sector_id: "",
    tipo_comida_id: "",
    tipo_menu_id: "",
    condicion: "",
    estado: "",
  };
}

onMounted(() => {
  cargarFechas();
  cargarPedidos();
});

watch(
  [modoPeriodo, fechaSeleccionada, filtros],
  () => {
    cargarPedidos();
  },
  { deep: true }
);
</script>

<template>
  <section class="autorizacion-view">
    <header class="encabezado">  
      <div>
        <h2>Módulo de Autorización — Servicio de Alimentación</h2>
        <p class="subtitulo">
          Consulta, autorización masiva, rechazo con motivo y exportación CSV
        </p>
      </div>
      <button type="button" class="btn-limpiar" @click="irACupos">
        Gestionar cupos
      </button> 
    </header>

    <p v-if="feedbackMsg" class="alerta-ok">{{ feedbackMsg }}</p>
    <p v-if="errorMsg" class="alerta-error">{{ errorMsg }}</p>

    <div class="panel-fechas">
      <div class="controles-periodo">
        <button type="button" class="btn-limpiar" @click="navegarPeriodo(-1)">
          &lsaquo; Anterior
        </button>
        <button type="button" class="btn-limpiar" @click="irAHoy">Hoy</button>
        <button type="button" class="btn-limpiar" @click="navegarPeriodo(1)">
          Siguiente &rsaquo;
        </button>

        <button
          type="button"
          class="chip-fecha"
          :class="{ activa: modoPeriodo === 'dia' }"
          @click="modoPeriodo = 'dia'"
        >
          Vista Diaria
        </button>
        <button
          type="button"
          class="chip-fecha"
          :class="{ activa: modoPeriodo === 'semana' }"
          @click="modoPeriodo = 'semana'"
        >
          Vista Semanal
        </button>
        <button
          type="button"
          class="chip-fecha"
          :class="{ activa: modoPeriodo === 'todos' }"
          @click="modoPeriodo = 'todos'"
        >
          Todos los pedidos
        </button>

        <label for="fecha-pedido"><strong>Fecha base:</strong></label>
        <input
          id="fecha-pedido"
          type="date"
          v-model="fechaSeleccionada"
          @change="modoPeriodo = 'dia'"
        />

        <span v-if="modoPeriodo === 'semana'" class="rango-badge">
          Semana: {{ rangoSemana.desde }} a {{ rangoSemana.hasta }}
        </span>
        <span
          v-else-if="modoPeriodo === 'dia' && esPasada(fechaSeleccionada)"
          class="solo-lectura"
        >
          Período anterior (Solo lectura)
        </span>
      </div>

      <div class="fechas-marcadas" v-if="fechasConPedidos.length > 0">
        <span>Días con pedidos:</span>
        <button
          v-for="item in fechasConPedidos"
          :key="item.fecha"
          type="button"
          class="chip-fecha"
          :class="{
            activa: modoPeriodo === 'dia' && fechaSeleccionada === item.fecha,
            pasada: item.solo_lectura,
          }"
          @click="modoPeriodo = 'dia'; fechaSeleccionada = item.fecha"
        >
          {{ item.fecha }}
          <small v-if="item.solo_lectura">(Solo lectura)</small>
        </button>
      </div>
    </div>

    <div class="barra-filtros">
      <input
        v-model.trim="filtros.sector_id"
        type="number"
        min="1"
        placeholder="ID Sector"
      />
      <input
        v-model.trim="filtros.tipo_comida_id"
        type="number"
        min="1"
        placeholder="ID Comida"
      />
      <input
        v-model.trim="filtros.tipo_menu_id"
        type="number"
        min="1"
        placeholder="ID Menú"
      />

      <select v-model="filtros.condicion">
        <option value="">Todas las condiciones</option>
        <option value="Regular">Regular</option>
        <option value="Excepción">Excepción</option>
      </select>

      <select v-model="filtros.estado">
        <option value="">Todos los estados</option>
        <option value="Confirmado">Confirmado (Pendiente)</option>
        <option value="Autorizado">Autorizado</option>
        <option value="Rechazado">Rechazado</option>
      </select>

      <button type="button" class="btn-limpiar" @click="limpiarFiltros">
        Limpiar filtros
      </button>

      <div class="export-grupo">
        <button
          type="button"
          class="btn-accion btn-regulares"
          @click="descargarCsv('personas')"
        >
          CSV Personas Autorizadas
        </button>
        <button
          type="button"
          class="btn-accion btn-autorizar"
          @click="descargarCsv('sectores')"
        >
          CSV Totales por Sector
        </button>
      </div>
    </div>

    <p v-if="cargando" class="estado-carga">Cargando pedidos...</p>

    <div v-else class="tabla-contenedor">
      <table class="tabla-pedidos">
        <thead>
          <tr>
            <th># Pedido</th>
            <th>Fecha</th>
            <th>Sector</th>
            <th>Comida</th>
            <th>Cant. Pedidas</th>
            <th>Cant. Autorizadas</th>
            <th>Estado</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="p in pedidos"
            :key="p.id"
            :class="{
              'fila-confirmada':
                String(p.estado || '').toLowerCase() === 'confirmado',
            }"
          >
            <td><strong>#{{ p.id }}</strong></td>
            <td>{{ p.fecha }}</td>
            <td>{{ p.sector_nombre || `Sector #${p.sector_id}` }}</td>
            <td>{{ p.tipo_comida_nombre || `Comida #${p.tipo_comida_id}` }}</td>
            <td>{{ p.cantidad_pedida }}</td>
            <td>{{ p.cantidad_autorizada }}</td>
            <td>
              <span
                class="badge"
                :class="`estado-${String(p.estado || '').toLowerCase()}`"
              >
                {{ p.estado }}
              </span>
              <small v-if="p.motivo_rechazo" class="motivo-texto">
                — {{ p.motivo_rechazo }}
              </small>
            </td>
            <td class="acciones-celda">
              <template v-if="puedeEditarPedido(p)">
                <button type="button"class="btn-limpiar" @click="irADetalleSolicitudes(p.id)">
                  Ver solicitudes
                </button>
                <button type="button" class="btn-accion btn-autorizar" @click="autorizarTodoElPedido(p)">
                  Autorizar
                </button>
                <button type="button" class="btn-accion btn-rechazar" @click="abrirRechazo(p)">
                  Rechazar
                </button>
              </template>
              <span
                v-else-if="String(p.estado || '').toLowerCase() === 'autorizado'"
                class="editable"
              >
                Autorizado
              </span>
              <span v-else class="solo-lectura">Solo lectura</span>
            </td>
          </tr>

          <tr v-if="pedidos.length === 0">
            <td colspan="8" class="sin-datos">
              No hay pedidos registrados para la selección y filtros actuales.
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="pedidoRechazo" class="modal-backdrop" @click.self="cerrarRechazo">
      <div class="modal-card modal-chico">
        <h3>Rechazar Pedido #{{ pedidoRechazo.id }}</h3>
        <p class="subtitulo">
          Indicá el motivo del rechazo (obligatorio). Se rechazará el pedido completo.
        </p>

        <textarea
          v-model="motivoRechazo"
          rows="4"
          class="textarea-motivo"
          placeholder="Escribí el motivo del rechazo..."
        />

        <div class="modal-footer">
          <button type="button" class="btn-limpiar" @click="cerrarRechazo">
            Cancelar
          </button>
          <button
            type="button"
            class="btn-accion btn-rechazar"
            :disabled="enviandoRechazo || !motivoRechazo.trim()"
            @click="confirmarRechazo"
          >
            {{ enviandoRechazo ? "Rechazando..." : "Confirmar rechazo" }}
          </button>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.autorizacion-view {
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.encabezado {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.encabezado h2 {
  margin: 0;
}

.subtitulo {
  margin: 0.25rem 0 0;
  color: #555;
  font-size: 0.92rem;
}

.controles-periodo,
.export-grupo,
.modal-footer {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem;
}

.panel-fechas {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding: 0.85rem;
  background: #f6f8fa;
  border: 1px solid #dce1e6;
  border-radius: 6px;
}

.fechas-marcadas {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.4rem;
}

.chip-fecha {
  padding: 0.35rem 0.7rem;
  border: 1px solid #b8c2cc;
  border-radius: 999px;
  background: #fff;
  cursor: pointer;
  font-size: 0.85rem;
}

.chip-fecha.activa {
  background: #1d4ed8;
  color: #fff;
  border-color: #1d4ed8;
}

.chip-fecha.pasada {
  opacity: 0.8;
}

.rango-badge {
  font-size: 0.85rem;
  font-weight: 600;
  color: #1e3a8a;
  background: #dbeafe;
  padding: 0.25rem 0.6rem;
  border-radius: 4px;
}

.barra-filtros {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
  align-items: center;
}

.barra-filtros input,
.barra-filtros select {
  padding: 0.45rem 0.6rem;
  border: 1px solid #cbd5e1;
  border-radius: 4px;
  background: #fff;
}

.btn-limpiar {
  padding: 0.45rem 0.8rem;
  border: 1px solid #cbd5e1;
  background: #f1f5f9;
  border-radius: 4px;
  cursor: pointer;
}

.alerta-ok {
  padding: 0.75rem;
  background: #dcfce7;
  color: #166534;
  border: 1px solid #86efac;
  border-radius: 4px;
  margin: 0;
}

.alerta-error {
  padding: 0.75rem;
  background: #fee2e2;
  color: #991b1b;
  border: 1px solid #fca5a5;
  border-radius: 4px;
  margin: 0;
}

.estado-carga {
  color: #475569;
}

.tabla-contenedor {
  overflow-x: auto;
}

.tabla-pedidos {
  width: 100%;
  border-collapse: collapse;
}

.tabla-pedidos th,
.tabla-pedidos td {
  padding: 0.65rem 0.75rem;
  border-bottom: 1px solid #e2e8f0;
  text-align: left;
}

.tabla-pedidos th {
  background: #f8fafc;
  font-weight: 600;
}

.fila-confirmada {
  background-color: #fffbeb;
}

.badge {
  display: inline-block;
  padding: 0.2rem 0.55rem;
  border-radius: 999px;
  font-size: 0.82rem;
  font-weight: 600;
  background: #e2e8f0;
}

.estado-confirmado {
  background: #fef3c7;
  color: #92400e;
}

.estado-autorizado {
  background: #dcfce7;
  color: #166534;
}

.estado-rechazado {
  background: #fee2e2;
  color: #991b1b;
}

.motivo-texto {
  display: block;
  color: #991b1b;
  margin-top: 0.2rem;
}

.solo-lectura {
  color: #64748b;
  font-size: 0.88rem;
}

.editable {
  color: #15803d;
  font-weight: 600;
  font-size: 0.88rem;
}

.acciones-celda {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}

.btn-accion {
  padding: 0.35rem 0.6rem;
  border: 1px solid transparent;
  border-radius: 4px;
  font-size: 0.82rem;
  cursor: pointer;
}

.btn-accion:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-autorizar {
  background: #15803d;
  color: #fff;
}

.btn-regulares {
  background: #1d4ed8;
  color: #fff;
}

.btn-rechazar {
  background: #b91c1c;
  color: #fff;
}

.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.55);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  z-index: 50;
}

.modal-card {
  background: #fff;
  border-radius: 8px;
  padding: 1.25rem;
  width: 100%;
  max-height: 88vh;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.modal-chico {
  max-width: 480px;
}

.textarea-motivo {
  width: 100%;
  padding: 0.6rem;
  border: 1px solid #cbd5e1;
  border-radius: 4px;
  font: inherit;
}

.modal-footer {
  justify-content: flex-end;
}

.sin-datos {
  text-align: center;
  color: #64748b;
  padding: 1.5rem;
}
</style>