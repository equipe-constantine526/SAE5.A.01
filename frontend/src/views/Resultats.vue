<!-- Page qui affiche les recommandations classées. Responsable : B1 · tâche 22. -->
<script setup>
defineProps({
  resultats: {
    type: Array,
    default: () => [],
  },
})
</script>

<template>
  <main class="page-resultats">
    <header class="entete-resultats">
      <h1>Résultats de la recommandation</h1>
      <p>Les pièces sont classées selon leur score.</p>
    </header>

    <p v-if="resultats.length === 0" class="message-vide">
      Aucune recommandation à afficher.
    </p>

    <ol v-else class="liste-resultats">
      <li
        v-for="(piece, index) in resultats"
        :key="piece.id"
        class="carte-resultat"
      >
        <span class="rang">{{ index + 1 }}.</span>
        <h2>{{ piece.nom }}</h2>
        <p>Prix : <strong>{{ piece.prix }} $</strong></p>
        <p>Score : <strong>{{ piece.score }}</strong></p>
      </li>
    </ol>
  </main>
</template>

<style scoped>
.page-resultats {
  max-width: 900px;
  margin: 0 auto;
  padding: 2rem 1rem;
  color: #1f2937;
}

.entete-resultats {
  margin-bottom: 1.5rem;
}

.entete-resultats h1 {
  margin-bottom: 0.5rem;
}

.liste-resultats {
  display: grid;
  gap: 1rem;
  padding-left: 2rem;
}

.carte-resultat {
  padding: 1rem 1.25rem;
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  background: #ffffff;
}

.carte-resultat h2 {
  margin: 0.25rem 0 0.75rem;
  font-size: 1.1rem;
}

.carte-resultat p {
  margin: 0.25rem 0;
}

.rang {
  color: #4b5563;
  font-weight: 700;
}

.message-vide {
  padding: 1rem;
  border-radius: 0.5rem;
  background: #f3f4f6;
}
</style>
