<!-- Page d'entrée de la recommandation. Responsable : A1 · Tâche 11. -->
<script setup>
import { computed, onBeforeUnmount, ref } from 'vue'

const emit = defineEmits(['recommandation'])

const adresseApi = (import.meta.env.VITE_API_URL || 'http://localhost:5000').replace(/\/$/, '')

const typesComposants = [
  { valeur: 'cpu', libelle: 'Processeur' },
  { valeur: 'carte_mere', libelle: 'Carte mère' },
  { valeur: 'ram', libelle: 'Mémoire vive' },
  { valeur: 'gpu', libelle: 'Carte graphique' },
  { valeur: 'alim', libelle: 'Alimentation' },
  { valeur: 'boitier', libelle: 'Boîtier' },
]

const usages = [
  { valeur: 'jeu', libelle: 'Jeu vidéo' },
  { valeur: 'montage', libelle: 'Montage vidéo' },
  { valeur: 'bureautique', libelle: 'Bureautique' },
]

const budget = ref(1200)
const usage = ref('jeu')
const typeCherche = ref('gpu')
const typeRecherche = ref('cpu')
const texteRecherche = ref('')
const composants = ref([])
const suggestions = ref([])
const rechercheEnCours = ref(false)
const envoiEnCours = ref(false)
const erreurRecherche = ref('')
const erreurEnvoi = ref('')
const message = ref('')

let temporisateurRecherche

const formulaireValide = computed(() => Number(budget.value) > 0 && usage.value && typeCherche.value)

// Choix temporaire : garder la recherche dans cette page jusqu'à l'arrivée du composant partagé A2.
// Il faudra le réutiliser ici et dans Ajouter ma config pour éviter deux recherches distinctes.
/**
 * Attend une courte pause de frappe avant de rechercher un composant.
 * @returns {void}
 * @example planifierRecherche() après la saisie de « 4070 » programme une recherche après 300 ms.
 */
function planifierRecherche() {
  clearTimeout(temporisateurRecherche)
  erreurRecherche.value = ''
  message.value = ''

  if (texteRecherche.value.trim().length === 0) {
    suggestions.value = []
    return
  }

  // Choix : attendre les 300 ms prévus par le guide plutôt que d'appeler l'API à chaque frappe.
  temporisateurRecherche = setTimeout(rechercherComposants, 300)
}

/**
 * Cherche les composants correspondant au texte dans le catalogue.
 * Le type et le texte proviennent des champs du formulaire.
 * @returns {Promise<void>} Met à jour les suggestions ou le message d'erreur.
 * @example rechercherComposants() affiche les cartes graphiques retournées pour « 4070 ».
 */
async function rechercherComposants() {
  rechercheEnCours.value = true
  erreurRecherche.value = ''

  const parametres = new URLSearchParams({
    type: typeRecherche.value,
    q: texteRecherche.value.trim(),
  })

  try {
    const reponse = await fetch(`${adresseApi}/api/composants?${parametres}`)
    if (!reponse.ok) {
      throw new Error('La recherche de composants sera disponible après l’intégration de l’API.')
    }

    const resultat = await reponse.json()
    suggestions.value = Array.isArray(resultat) ? resultat : []
  } catch (erreur) {
    suggestions.value = []
    erreurRecherche.value = erreur.message || 'Impossible de joindre le catalogue.'
  } finally {
    rechercheEnCours.value = false
  }
}

/**
 * Ajoute au formulaire la suggestion choisie par l'utilisateur.
 * @param {Object} composant Composant de l'API, ex. { id: 412, nom: "AMD Ryzen 5 7600", prix: 199 }.
 * @returns {void} Met à jour la liste des composants sélectionnés.
 * @example ajouterComposant({ id: 412, nom: "AMD Ryzen 5 7600", prix: 199 }) l'ajoute à la configuration.
 */
function ajouterComposant(composant) {
  const dejaAjoute = composants.value.some((element) => element.id === composant.id)
  if (!dejaAjoute) {
    composants.value.push({ ...composant, type: typeRecherche.value })
  }

  texteRecherche.value = ''
  suggestions.value = []
  erreurRecherche.value = ''
}

/**
 * Retire du formulaire un composant déjà sélectionné.
 * @param {number|string} id Identifiant de la pièce, ex. 412 pour le Ryzen 5 7600.
 * @returns {void} Met à jour la liste des composants sélectionnés.
 * @example retirerComposant(412) enlève le Ryzen 5 7600 de la liste.
 */
function retirerComposant(id) {
  composants.value = composants.value.filter((composant) => composant.id !== id)
}

/**
 * Envoie les choix de l'utilisateur à la méthode de recommandation par contenu.
 * @returns {Promise<void>} Émet la réponse JSON au composant parent ou affiche une erreur.
 * @example envoyerRecommandation() envoie un budget de 1200, l'usage « jeu » et le type « gpu ».
 */
async function envoyerRecommandation() {
  if (!formulaireValide.value || envoiEnCours.value) return

  envoiEnCours.value = true
  erreurEnvoi.value = ''
  message.value = ''

  const demande = {
    composants: composants.value.map((composant) => composant.id),
    budget: Number(budget.value),
    usage: usage.value,
    type_cherche: typeCherche.value,
  }

  try {
    const reponse = await fetch(`${adresseApi}/api/recommend/content`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(demande),
    })
    const resultat = await reponse.json()

    if (!reponse.ok) {
      throw new Error(resultat.erreur || 'La recommandation n’a pas pu être calculée.')
    }

    message.value = 'Recommandation reçue.'
    emit('recommandation', resultat)
  } catch (erreur) {
    erreurEnvoi.value = erreur.message || 'Impossible de joindre le service de recommandation.'
  } finally {
    envoiEnCours.value = false
  }
}

/**
 * Annule une recherche différée si l'utilisateur quitte la page.
 * @returns {void}
 * @example nettoyerRecherche() annule le minuteur programmé après « 4070 ».
 */
function nettoyerRecherche() {
  clearTimeout(temporisateurRecherche)
}

onBeforeUnmount(nettoyerRecherche)
</script>

<template>
  <main class="page-saisie">
    <header class="entete">
      <p class="sur-titre">RigMatch · Configuration PC</p>
      <h1>Que souhaitez-vous améliorer ?</h1>
      <p class="introduction">
        Indiquez votre budget, votre usage et les composants que vous possédez déjà.
      </p>
    </header>

    <form class="formulaire" @submit.prevent="envoyerRecommandation">
      <section class="bloc-formulaire" aria-labelledby="titre-projet">
        <h2 id="titre-projet">Votre projet</h2>

        <label for="budget">Budget maximal</label>
        <input
          id="budget"
          v-model.number="budget"
          type="number"
          min="1"
          step="1"
          required
        />

        <label for="usage">Usage principal</label>
        <select id="usage" v-model="usage" required>
          <option v-for="option in usages" :key="option.valeur" :value="option.valeur">
            {{ option.libelle }}
          </option>
        </select>

        <label for="type-cherche">Composant à recommander</label>
        <select id="type-cherche" v-model="typeCherche" required>
          <option v-for="type in typesComposants" :key="type.valeur" :value="type.valeur">
            {{ type.libelle }}
          </option>
        </select>
      </section>

      <section class="bloc-formulaire" aria-labelledby="titre-composants">
        <h2 id="titre-composants">Composants que vous possédez</h2>
        <p class="aide">Vous pouvez continuer sans en ajouter si vous partez de zéro.</p>

        <label for="type-composant">Type de composant</label>
        <select id="type-composant" v-model="typeRecherche" @change="planifierRecherche">
          <option v-for="type in typesComposants" :key="type.valeur" :value="type.valeur">
            {{ type.libelle }}
          </option>
        </select>

        <label for="recherche-composant">Rechercher dans le catalogue</label>
        <input
          id="recherche-composant"
          v-model="texteRecherche"
          type="search"
          autocomplete="off"
          placeholder="Ex. Ryzen 5 7600 ou RTX 4070"
          @input="planifierRecherche"
        />

        <p v-if="rechercheEnCours" class="etat" role="status">Recherche en cours…</p>
        <p v-if="erreurRecherche" class="erreur" role="alert">{{ erreurRecherche }}</p>

        <ul v-if="suggestions.length" class="suggestions" aria-label="Suggestions de composants">
          <li v-for="suggestion in suggestions" :key="suggestion.id">
            <button type="button" @click="ajouterComposant(suggestion)">
              <span>{{ suggestion.nom }}</span>
              <span>{{ suggestion.prix == null ? 'Prix inconnu' : `${suggestion.prix} $` }}</span>
            </button>
          </li>
        </ul>

        <ul v-if="composants.length" class="composants-selectionnes" aria-label="Composants sélectionnés">
          <li v-for="composant in composants" :key="composant.id">
            <span>
              {{ typesComposants.find((type) => type.valeur === composant.type)?.libelle }} ·
              {{ composant.nom }}
            </span>
            <button
              type="button"
              :aria-label="`Retirer ${composant.nom}`"
              @click="retirerComposant(composant.id)"
            >
              Retirer
            </button>
          </li>
        </ul>
      </section>

      <p v-if="erreurEnvoi" class="erreur" role="alert">{{ erreurEnvoi }}</p>
      <p v-if="message" class="etat" role="status">{{ message }}</p>

      <button class="bouton-principal" type="submit" :disabled="!formulaireValide || envoiEnCours">
        {{ envoiEnCours ? 'Recherche de recommandations…' : 'Trouver un composant' }}
      </button>
    </form>
  </main>
</template>

<style scoped>
.page-saisie {
  width: min(100% - 2rem, 46rem);
  margin: 0 auto;
  padding: 3rem 0;
  color: #1c2734;
  font-family: system-ui, sans-serif;
}

.entete {
  margin-bottom: 2rem;
}

.sur-titre {
  color: #386b5b;
  font-size: 0.8rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

h1,
h2,
p {
  margin-top: 0;
}

h1 {
  margin-bottom: 0.5rem;
  font-size: clamp(1.8rem, 5vw, 2.6rem);
}

h2 {
  margin-bottom: 1rem;
  font-size: 1.2rem;
}

.introduction,
.aide,
.etat {
  color: #586575;
}

.formulaire {
  display: grid;
  gap: 1.25rem;
}

.bloc-formulaire {
  display: grid;
  gap: 0.65rem;
  padding: 1.4rem;
  border: 1px solid #d9e0e7;
  border-radius: 0.9rem;
  background: #fff;
}

.bloc-formulaire h2,
.bloc-formulaire .aide {
  margin-bottom: 0.25rem;
}

label {
  margin-top: 0.35rem;
  font-size: 0.92rem;
  font-weight: 650;
}

input,
select {
  width: 100%;
  min-height: 2.8rem;
  padding: 0.65rem 0.75rem;
  border: 1px solid #b9c4ce;
  border-radius: 0.5rem;
  background: #fff;
  color: inherit;
  font: inherit;
}

input:focus,
select:focus,
button:focus-visible {
  outline: 3px solid #9bd3bd;
  outline-offset: 2px;
}

.suggestions,
.composants-selectionnes {
  display: grid;
  gap: 0.4rem;
  margin: 0;
  padding: 0;
  list-style: none;
}

.suggestions button,
.composants-selectionnes li {
  display: flex;
  width: 100%;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.7rem;
  border: 1px solid #d9e0e7;
  border-radius: 0.5rem;
  background: #f8fafb;
  color: inherit;
  text-align: left;
}

.suggestions button {
  cursor: pointer;
  font: inherit;
}

.suggestions button:hover {
  border-color: #386b5b;
  background: #eef7f2;
}

.composants-selectionnes li button {
  flex: 0 0 auto;
  border: 0;
  background: transparent;
  color: #8c342b;
  cursor: pointer;
  font: inherit;
  font-size: 0.9rem;
}

.erreur {
  margin: 0;
  color: #9f2f25;
}

.etat {
  margin: 0;
}

.bouton-principal {
  min-height: 3rem;
  padding: 0.75rem 1.2rem;
  border: 0;
  border-radius: 0.6rem;
  background: #245c4b;
  color: #fff;
  cursor: pointer;
  font: inherit;
  font-weight: 700;
}

.bouton-principal:disabled {
  background: #8e9b96;
  cursor: not-allowed;
}
</style>
