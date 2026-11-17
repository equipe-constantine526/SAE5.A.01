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

body {
  background: #f4f7f6;
}

*,
*::before,
*::after {
  box-sizing: border-box;
}

.actions-resultats {
  max-width: 900px;
  margin: 0 auto;
  padding: 1.5rem 1rem 0;
}

.bouton-retour {
  padding: 0.6rem 0.9rem;
  border: 0;
  border-radius: 0.4rem;
  background: #2f5f4e;
  color: #fff;
  cursor: pointer;
}
</style>
