<template>
  <aside class="panel-card">
    <h2 class="panel-title">Entregas recientes</h2>
    <p class="panel-desc">Últimos movimientos de este turno.</p>

    <div v-if="entregas.length === 0" class="empty-state">
      Todavía no hay entregas registradas.
    </div>

    <ul v-else class="recent-list">
      <li v-for="ent in entregas" :key="ent.id" class="recent-item">
        <div>
          <div class="recent-name">{{ ent.persona }}</div>
          <div class="recent-meta">{{ ent.sector }} · {{ ent.comida }} ({{ ent.menu }})</div>
        </div>
        <span class="recent-time">{{ ent.hora }}</span>
      </li>
    </ul>
  </aside>
</template>

<script setup>
defineProps({
  entregas: { type: Array, default: () => [] },
})
</script>