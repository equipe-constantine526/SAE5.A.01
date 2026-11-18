<!-- Point d'entrée des pages de saisie et de résultats. Responsable : gardien du dépôt · Tâche 34. -->
<script setup>
import { ref } from 'vue'
import Resultats from './views/Resultats.vue'
import Saisie from './views/Saisie.vue'

const resultats = ref(null)

/**
 * Affiche les résultats transmis par le formulaire après la réponse de l'API.
 * @param {{resultats?: Array}} reponse Réponse JSON de la recommandation.
 * @returns {void}
 */
function afficherResultats(reponse) {
  if (!Array.isArray(reponse?.resultats)) return

  resultats.value = reponse.resultats
}

/**
 * Revient au formulaire pour modifier la configuration.
 * @returns {void}
 */
function revenirALaSaisie() {
  resultats.value = null
}
</script>

<template>
  <Saisie
    v-if="resultats === null"
    @recommandation="afficherResultats"
  />
  <div v-else class="conteneur-resultats">
    <div class="actions-resultats">
      <button class="bouton-retour" type="button" @click="revenirALaSaisie">
        Modifier ma configuration
      </button>
    </div>
    <Resultats :resultats="resultats" />
  </div>
</template>

<style>
html,
body,
#app {
  min-height: 100%;
  margin: 0;
}

html,
body {
  overflow-x: clip;
}

body {
  background: var(--color-papier);
  color: var(--color-encre);
  font-family: var(--font-body);
  font-synthesis: none;
}

*,
*::before,
*::after {
  box-sizing: border-box;
}

.actions-resultats {
  display: flex;
  justify-content: flex-end;
  padding: 0.9rem clamp(1rem, 4vw, 3rem);
  background: var(--color-papier);
}

.bouton-retour {
  padding: 0.6rem 0.9rem;
  border: 1px solid var(--color-bordeaux);
  border-radius: var(--radius-card);
  background: var(--color-bordeaux);
  color: var(--color-citron);
  font: inherit;
  font-weight: 700;
  white-space: nowrap;
  cursor: pointer;
}

.bouton-retour:hover {
  background: var(--color-bordeaux-hover);
}

.bouton-retour:focus-visible {
  outline: 3px solid var(--color-focus);
  outline-offset: 3px;
}

.bouton-retour:active {
  background: var(--color-orange);
  color: var(--color-orange-ink);
}

.bouton-retour:disabled {
  border-color: var(--color-desactive);
  background: var(--color-desactive);
  color: var(--color-encre-desactive);
  cursor: not-allowed;
}
</style>
