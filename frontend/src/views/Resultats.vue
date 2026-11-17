<!-- Page de résultats et de détail des recommandations. Responsable : B2 · tâche 23. -->
<script setup>
import { computed, onMounted, ref } from 'vue'

const props = defineProps({
  resultats: {
    type: Array,
    default: () => [],
  },
})

const pieceSelectionnee = ref(null)
const composantsExistants = ref([])

const nomsCaracteristiques = {
  type: 'Type de pièce',
  famille: 'Famille',
  perf: 'Indice de performance',
  microarchitecture: 'Microarchitecture',
  nb_coeurs: 'Nombre de cœurs',
  frequence_boost: 'Fréquence boost (GHz)',
  socket: 'Socket',
  type_ram: 'Type de mémoire vive',
  type_ram_verifie: 'Type de mémoire vérifié',
  format: 'Format',
  chipset: 'Chipset',
  tflops: 'Puissance de calcul (TFLOPS)',
  alim_conseillee_w: 'Alimentation conseillée (W)',
  conso_w: 'Consommation (W)',
  puissance_w: 'Puissance (W)',
}

const nomsRegles = {
  perf_prix: 'Performance / prix',
  equilibre: 'Équilibre CPU / GPU',
  alim: 'Alimentation',
  budget: 'Budget',
}

const detailCaracteristiques = computed(() => {
  if (!pieceSelectionnee.value) return []

  const caracteristiques = pieceSelectionnee.value.caracteristiques || {}
  return Object.entries(caracteristiques)
    .filter(([nom, valeur]) => nom !== 'source' && valeur !== null && valeur !== '')
    .map(([nom, valeur]) => ({
      nom: nomsCaracteristiques[nom] || nom,
      valeur: typeof valeur === 'boolean' ? (valeur ? 'Oui' : 'Non') : valeur,
    }))
})

const detailScore = computed(() => {
  if (!pieceSelectionnee.value) return []

  const detail = pieceSelectionnee.value.detail || {}
  return Object.entries(detail).map(([nom, valeur]) => ({
    nom: nomsRegles[nom] || nom,
    valeur,
  }))
})

const prixTotal = computed(() => {
  if (!pieceSelectionnee.value) return null

  const prix = [
    ...composantsExistants.value.map((composant) => composant.prix),
    pieceSelectionnee.value.prix,
  ]
  const prixConnus = prix.filter((valeur) => (
    valeur !== null
    && valeur !== undefined
    && valeur !== ''
    && Number.isFinite(Number(valeur))
  ))
  const total = prixConnus.reduce((somme, valeur) => somme + Number(valeur), 0)

  return {
    montant: total,
    complet: prixConnus.length === prix.length,
  }
})

onMounted(() => {
  try {
    const sauvegarde = JSON.parse(localStorage.getItem('maConfig') || 'null')
    if (!Array.isArray(sauvegarde?.composants)) return

    composantsExistants.value = sauvegarde.composants
      .filter((composant) => composant && typeof composant === 'object')
  } catch {
    composantsExistants.value = []
  }
})
</script>

<template>
  <main class="page-resultats">
    <header class="entete-resultats">
      <h1>Résultats de la recommandation</h1>
      <p>Les pièces sont classées selon leur score.</p>
    </header>

    <p v-if="props.resultats.length === 0" class="message-vide">
      Aucune recommandation à afficher.
    </p>

    <ol v-else class="liste-resultats">
      <li
        v-for="(piece, index) in props.resultats"
        :key="piece.id"
        class="carte-resultat"
      >
        <span class="rang">{{ index + 1 }}.</span>
        <h2>{{ piece.nom }}</h2>
        <p>Prix : <strong>{{ piece.prix }} $</strong></p>
        <p>Score : <strong>{{ piece.score }}</strong></p>
        <button
          type="button"
          class="bouton-detail"
          :aria-expanded="pieceSelectionnee?.id === piece.id"
          @click="pieceSelectionnee = piece"
        >
          Voir le détail
        </button>
      </li>
    </ol>

    <section v-if="pieceSelectionnee" class="detail-piece" aria-live="polite">
      <h2>Détail de {{ pieceSelectionnee.nom }}</h2>

      <h3>Caractéristiques</h3>
      <dl v-if="detailCaracteristiques.length" class="liste-detail">
        <template v-for="caracteristique in detailCaracteristiques" :key="caracteristique.nom">
          <dt>{{ caracteristique.nom }}</dt>
          <dd>{{ caracteristique.valeur }}</dd>
        </template>
      </dl>
      <p v-else>Aucune caractéristique détaillée n'est disponible.</p>

      <h3>Détail du score</h3>
      <dl v-if="detailScore.length" class="liste-detail">
        <template v-for="regle in detailScore" :key="regle.nom">
          <dt>{{ regle.nom }}</dt>
          <dd>{{ regle.valeur }}</dd>
        </template>
      </dl>
      <p v-else>Le détail des règles n'est pas fourni pour cette recommandation.</p>

      <footer v-if="prixTotal" class="prix-total">
        <strong>Prix total de la configuration : {{ prixTotal.montant.toFixed(2) }} $</strong>
        <p v-if="!prixTotal.complet">
          Certains prix sont inconnus : le total affiché est partiel.
        </p>
      </footer>
    </section>
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

.carte-resultat,
.detail-piece {
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

.bouton-detail {
  margin-top: 0.75rem;
  padding: 0.5rem 0.75rem;
  border: 0;
  border-radius: 0.35rem;
  background: #1d4ed8;
  color: white;
  cursor: pointer;
}

.detail-piece {
  margin-top: 1.5rem;
}

.liste-detail {
  display: grid;
  grid-template-columns: minmax(180px, 1fr) 2fr;
  gap: 0.5rem 1rem;
}

.liste-detail dt {
  font-weight: 600;
}

.liste-detail dd {
  margin: 0;
}

.prix-total {
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid #d1d5db;
}

.prix-total p {
  margin-bottom: 0;
}

.message-vide {
  padding: 1rem;
  border-radius: 0.5rem;
  background: #f3f4f6;
}
</style>
