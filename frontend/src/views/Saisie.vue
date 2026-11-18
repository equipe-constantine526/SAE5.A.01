<!-- Page d'entrée de la recommandation. Responsable : A1 · Tâche 11. -->
<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import RechercheComposant from '../components/RechercheComposant.vue'

const emit = defineEmits(['recommandation'])

const adresseApi = (import.meta.env.VITE_API_URL || 'http://localhost:5000').replace(/\/$/, '')
const cleSauvegarde = 'maConfig'

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
const composants = ref([])
const envoiEnCours = ref(false)
const erreurEnvoi = ref('')
const erreurSauvegarde = ref('')
const message = ref('')

const typesDejaPossedes = computed(() => (
  new Set(composants.value.map((composant) => composant.type))
))
const typeChercheDejaPossede = computed(() => (
  typesDejaPossedes.value.has(typeCherche.value)
))
const typesRechercheDisponibles = computed(() => (
  typesComposants.filter((type) => type.valeur !== typeCherche.value)
))
const formulaireValide = computed(() => (
  Number(budget.value) > 0
  && usage.value
  && typeCherche.value
  && !typeChercheDejaPossede.value
))

watch(typeCherche, (nouveauType) => {
  if (typeRecherche.value === nouveauType) {
    // Choix : garder la recherche utilisable sans supprimer la pièce que l'utilisateur possède.
    typeRecherche.value = typesComposants.find((type) => type.valeur !== nouveauType)?.valeur || ''
  }
})

/**
 * Restaure le formulaire depuis le stockage local du navigateur.
 * @returns {void} Met à jour les champs si une sauvegarde valide existe.
 * @example restaurerSaisie() remet un budget de 1200 et le Ryzen 5 7600 sélectionné.
 */
function restaurerSaisie() {
  try {
    const texteSauvegarde = localStorage.getItem(cleSauvegarde)
    if (!texteSauvegarde) return

    const sauvegarde = JSON.parse(texteSauvegarde)
    if (!sauvegarde || typeof sauvegarde !== 'object') {
      throw new Error('La sauvegarde n’a pas le bon format.')
    }

    const budgetSauvegarde = Number(sauvegarde.budget)
    if (Number.isFinite(budgetSauvegarde) && budgetSauvegarde > 0) {
      budget.value = budgetSauvegarde
    }

    if (usages.some((option) => option.valeur === sauvegarde.usage)) {
      usage.value = sauvegarde.usage
    }

    if (typesComposants.some((type) => type.valeur === sauvegarde.type_cherche)) {
      typeCherche.value = sauvegarde.type_cherche
    }

    if (Array.isArray(sauvegarde.composants)) {
      composants.value = sauvegarde.composants
        .filter((composant) => (
          composant
          && Number.isInteger(Number(composant.id))
          && Number(composant.id) > 0
          && typeof composant.nom === 'string'
          && typesComposants.some((type) => type.valeur === composant.type)
        ))
        .map((composant) => ({
          id: Number(composant.id),
          nom: composant.nom,
          prix: composant.prix,
          type: composant.type,
        }))
    }
  } catch {
    erreurSauvegarde.value = 'La sauvegarde locale est illisible ou inaccessible. Vous pouvez continuer sans elle.'
  }
}

/**
 * Enregistre les choix du formulaire dans le navigateur.
 * @returns {void} Écrit les valeurs utiles ou affiche un message si le stockage est bloqué.
 * @example enregistrerSaisie() sauvegarde le budget 1200, l'usage « jeu » et les pièces choisies.
 */
function enregistrerSaisie() {
  const sauvegarde = {
    budget: budget.value,
    usage: usage.value,
    type_cherche: typeCherche.value,
    // Choix : garder nom et type avec l'id pour réafficher les pièces sans refaire une recherche au rechargement.
    composants: composants.value.map((composant) => ({
      id: composant.id,
      nom: composant.nom,
      prix: composant.prix,
      type: composant.type,
    })),
  }

  try {
    localStorage.setItem(cleSauvegarde, JSON.stringify(sauvegarde))
    erreurSauvegarde.value = ''
  } catch {
    erreurSauvegarde.value = 'La sauvegarde locale est indisponible. Votre saisie reste utilisable jusqu’à la fermeture de la page.'
  }
}

watch([budget, usage, typeCherche, composants], enregistrerSaisie, { deep: true })
onMounted(restaurerSaisie)

/**
 * Ajoute au formulaire la suggestion choisie par l'utilisateur.
 * @param {Object} composant Composant de l'API, ex. { id: 412, nom: "AMD Ryzen 5 7600", prix: 199 }.
 * @returns {void} Met à jour la liste des composants sélectionnés.
 * @example ajouterComposant({ id: 412, nom: "AMD Ryzen 5 7600", prix: 199 }) l'ajoute à la configuration.
 */
function ajouterComposant(composant) {
  if (typeRecherche.value === typeCherche.value) return

  const dejaAjoute = composants.value.some((element) => element.id === composant.id)
  if (!dejaAjoute) {
    // Choix : le parent ajoute le type sélectionné, car l'API renvoie la fiche sans type de recherche.
    composants.value.push({ ...composant, type: typeRecherche.value })
  }
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
  enregistrerSaisie()

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

</script>

<template>
  <main class="page-saisie">
    <aside class="panneau-identite" aria-labelledby="titre-page">
      <div class="marque">
        <span class="marque-symbole" aria-hidden="true">⇄</span>
        <span class="marque-nom">RigMatch</span>
        <span class="marque-separateur">Configuration PC</span>
      </div>

      <div class="contenu-identite">
        <p class="sur-titre">VOTRE CONFIGURATION, EN TOUTE SÉRÉNITÉ</p>
        <h1 id="titre-page">Que souhaitez-vous <span>améliorer&nbsp;?</span></h1>
        <p class="introduction">
          Indiquez votre budget, votre usage et les composants que vous possédez déjà.
        </p>
      </div>

      <div class="repere-identite" aria-label="Budget, usage et compatibilité">
        <span class="repere-point" aria-hidden="true"></span>
        <p>Budget <span>·</span> Usage <span>·</span> Compatibilité</p>
      </div>
    </aside>

    <section class="zone-formulaire" aria-label="Configurer votre recommandation">
      <div class="visuel-page" aria-hidden="true"></div>

      <div class="contenu-formulaire">
        <form class="formulaire" @submit.prevent="envoyerRecommandation">
          <section class="bloc-formulaire" aria-labelledby="titre-projet">
            <h2 id="titre-projet">Votre projet</h2>

            <div class="grille-projet">
              <div class="champ-formulaire">
                <label for="budget">Budget maximal</label>
                <input
                  id="budget"
                  v-model.number="budget"
                  type="number"
                  min="1"
                  step="1"
                  required
                />
              </div>

              <div class="champ-formulaire">
                <label for="usage">Usage principal</label>
                <select id="usage" v-model="usage" required>
                  <option v-for="option in usages" :key="option.valeur" :value="option.valeur">
                    {{ option.libelle }}
                  </option>
                </select>
              </div>

              <div class="champ-formulaire champ-complet">
                <label for="type-cherche">Composant à recommander</label>
                <select id="type-cherche" v-model="typeCherche" required>
                  <option
                    v-for="type in typesComposants"
                    :key="type.valeur"
                    :value="type.valeur"
                    :disabled="typesDejaPossedes.has(type.valeur)"
                  >
                    {{ type.libelle }}{{ typesDejaPossedes.has(type.valeur) ? ' · déjà possédé' : '' }}
                  </option>
                </select>
                <p v-if="typeChercheDejaPossede" class="erreur" role="alert">
                  Vous possédez déjà un composant de ce type. Retirez-le ou choisissez un autre type à recommander.
                </p>
              </div>
            </div>
          </section>

          <section class="bloc-formulaire" aria-labelledby="titre-composants">
            <h2 id="titre-composants">Composants que vous possédez</h2>
            <p class="aide">Vous pouvez continuer sans en ajouter si vous partez de zéro.</p>

            <div class="champ-formulaire">
              <label for="type-composant">Type de composant</label>
              <select id="type-composant" v-model="typeRecherche">
                <option v-for="type in typesRechercheDisponibles" :key="type.valeur" :value="type.valeur">
                  {{ type.libelle }}
                </option>
              </select>
            </div>

            <p class="libelle-recherche">Rechercher dans le catalogue</p>
            <RechercheComposant
              :type="typeRecherche"
              @select="ajouterComposant"
            />

            <ul
              v-if="composants.length"
              class="composants-selectionnes"
              aria-label="Composants sélectionnés"
            >
              <li v-for="composant in composants" :key="composant.id">
                <span class="icone-composant" aria-hidden="true">
                  <svg viewBox="0 0 32 32" focusable="false">
                    <g v-if="composant.type === 'cpu'">
                      <rect x="9" y="9" width="14" height="14" rx="2" />
                      <rect x="13" y="13" width="6" height="6" rx="1" />
                      <path d="M12 5v4m8-4v4m-8 14v4m8-4v4M5 12h4m14 0h4M5 20h4m14 0h4" />
                    </g>
                    <g v-else-if="composant.type === 'carte_mere'">
                      <rect x="6" y="5" width="20" height="22" rx="2" />
                      <rect x="12" y="10" width="8" height="8" rx="1" />
                      <path d="M9 9h2m9 12h3m-12-1h3m9-10h1M9 23h2" />
                    </g>
                    <g v-else-if="composant.type === 'ram'">
                      <path d="M5 10h22v10H5zM9 10V7h3v3m3-3h3v3m3-3h3v3M9 20v3m4-3v3m4-3v3m4-3v3" />
                    </g>
                    <g v-else-if="composant.type === 'gpu'">
                      <rect x="4" y="9" width="22" height="13" rx="2" />
                      <circle cx="15" cy="15.5" r="4" />
                      <path d="M15 11.5v2m0 4v2m-4-4h2m4 0h2M4 12H2v7h2m22-7h3v7h-3M9 22v3h3v-3m3 0v3h3v-3" />
                    </g>
                    <g v-else-if="composant.type === 'alim'">
                      <rect x="5" y="7" width="22" height="18" rx="2" />
                      <circle cx="15" cy="16" r="5" />
                      <path d="M15 11v3m0 4v3m-5-5h3m4 0h3M23 11h1" />
                    </g>
                    <g v-else-if="composant.type === 'boitier'">
                      <rect x="9" y="4" width="14" height="24" rx="2" />
                      <rect x="12" y="8" width="8" height="11" rx="1" />
                      <circle cx="16" cy="23" r="1.5" />
                    </g>
                  </svg>
                </span>
                <span class="nom-composant">
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
          <p v-if="erreurSauvegarde" class="erreur" role="alert">{{ erreurSauvegarde }}</p>
          <p v-if="message" class="etat" role="status">{{ message }}</p>

          <button class="bouton-principal" type="submit" :disabled="!formulaireValide || envoiEnCours">
            <span>{{ envoiEnCours ? 'Recherche…' : 'Trouver un composant' }}</span>
            <span class="fleche-bouton" aria-hidden="true">→</span>
          </button>
        </form>
      </div>
    </section>
  </main>
</template>

<style scoped>
/* Hallmark · pre-emit critique: P5 H5 E4 S5 R4 V4
 * Hallmark · genre: modern-minimal · macrostructure: Split Workbench
 * theme: RigMatch bordeaux / citron / orange · studied: yes · DNA-source: image reference
 */
.page-saisie {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  width: 100%;
  min-height: 100dvh;
  color: var(--color-encre);
  background: var(--color-papier);
  font-family: var(--font-body);
  font-synthesis: none;
}

.panneau-identite {
  display: flex;
  min-width: 0;
  min-height: 27rem;
  flex-direction: column;
  justify-content: space-between;
  gap: var(--space-xl);
  padding: clamp(1.5rem, 6vw, 3rem);
  background: var(--color-bordeaux);
  color: var(--color-texte-sombre);
}

.marque {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  min-width: 0;
  line-height: 1;
}

.marque-symbole {
  color: var(--color-citron);
  font-size: 1.6rem;
  line-height: 1;
}

.marque-nom {
  color: var(--color-texte-sombre);
  font-size: 1.05rem;
  font-weight: 700;
}

.marque-separateur {
  margin-inline-start: 0.4rem;
  padding-inline-start: 0.8rem;
  border-inline-start: 1px solid var(--color-regle-sombre);
  color: var(--color-texte-sombre-doux);
  font-size: 0.78rem;
}

.contenu-identite {
  width: 100%;
  max-width: 36rem;
  margin-block: auto;
  padding-block: var(--space-xl);
}

.sur-titre {
  margin: 0 0 var(--space-md);
  color: var(--color-citron);
  font-size: 0.8rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  line-height: 1.35;
  text-transform: uppercase;
}

h1 {
  max-width: 11ch;
  margin: 0;
  color: var(--color-citron);
  font-family: var(--font-display);
  font-size: clamp(2.5rem, 4vw, 4rem);
  font-weight: 400;
  letter-spacing: -0.045em;
  line-height: 0.98;
  overflow-wrap: anywhere;
}

h1 span {
  display: block;
}

.introduction {
  max-width: 38ch;
  margin: var(--space-md) 0 0;
  color: var(--color-texte-sombre-doux);
  font-size: 1rem;
  line-height: 1.65;
}

.repere-identite {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  padding-top: var(--space-md);
  border-top: 1px solid var(--color-regle-sombre);
}

.repere-point {
  width: 0.55rem;
  height: 0.55rem;
  flex: 0 0 auto;
  border-radius: 50%;
  background: var(--color-orange);
}

.repere-identite p {
  margin: 0;
  color: var(--color-texte-sombre);
  font-size: 0.9rem;
  line-height: 1.4;
}

.repere-identite p span {
  padding-inline: 0.35rem;
  color: var(--color-orange);
}

.zone-formulaire {
  min-width: 0;
  padding: 0;
  background: var(--color-papier);
}

.visuel-page {
  position: relative;
  width: 100%;
  max-width: 68rem;
  aspect-ratio: 16 / 9;
  margin-inline: auto;
  background: url('../assets/images/pcbuild.jpg') center / cover no-repeat;
}

.visuel-page::before,
.visuel-page::after {
  position: absolute;
  inset: 0;
  content: "";
  pointer-events: none;
}

.visuel-page::before {
  background: url('../assets/images/pcbuild.jpg') center / cover no-repeat;
  filter: blur(12px);
  mask-image: linear-gradient(to bottom, transparent 58%, #000 82%);
  opacity: 0.65;
}

.visuel-page::after {
  background: linear-gradient(
    to bottom,
    transparent 52%,
    rgb(251 249 245 / 72%) 78%,
    var(--color-papier) 100%
  );
}

.contenu-formulaire {
  width: 100%;
  max-width: 54rem;
  margin-inline: auto;
  padding: clamp(1.5rem, 5vw, 3rem) clamp(1rem, 5vw, 3rem);
}

.formulaire {
  display: grid;
  width: 100%;
  gap: 0;
}

.bloc-formulaire {
  display: grid;
  gap: var(--space-sm);
  min-width: 0;
  padding-block: var(--space-lg);
  border-bottom: 1px solid var(--color-regle);
}

.bloc-formulaire:first-child {
  padding-top: 0;
}

.bloc-formulaire h2 {
  margin: 0 0 var(--space-xs);
  color: var(--color-bordeaux);
  font-family: var(--font-display);
  font-size: clamp(1.6rem, 2vw, 2rem);
  font-weight: 700;
  letter-spacing: -0.025em;
  line-height: 1.15;
}

.grille-projet {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: var(--space-md);
}

.champ-formulaire {
  display: grid;
  gap: 0.5rem;
  min-width: 0;
}

.champ-complet {
  grid-column: 1 / -1;
}

.libelle-recherche,
label {
  margin: 0;
  color: var(--color-encre);
  font-size: 0.92rem;
  font-weight: 650;
}

.aide {
  max-width: 55ch;
  margin: -0.4rem 0 var(--space-xs);
  color: var(--color-encre-douce);
  font-size: 0.95rem;
  line-height: 1.55;
}

input,
select {
  box-sizing: border-box;
  width: 100%;
  min-height: 3rem;
  padding: 0.7rem 0.85rem;
  border-radius: var(--radius-input);
  outline: 2px solid transparent;
  outline-offset: 2px;
  background: var(--color-bordeaux);
  color: var(--color-orange);
  font: 400 1rem/1.4 var(--font-body);
}

select option {
  background: var(--color-papier);
  color: var(--color-orange);
}

input:focus-visible,
select:focus-visible {
  outline-color: var(--color-focus);
}

.composants-selectionnes {
  display: grid;
  gap: var(--space-xs);
  margin: 0;
  padding: 0;
  list-style: none;
}

.composants-selectionnes li {
  display: flex;
  width: 100%;
  min-width: 0;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.7rem;
  border: 1px solid var(--color-orange);
  border-radius: var(--radius-card);
  background: var(--color-orange);
  color: var(--color-orange-ink);
  text-align: left;
}

.icone-composant {
  display: grid;
  width: 2rem;
  height: 2rem;
  flex: 0 0 auto;
  place-items: center;
  color: var(--color-bordeaux);
}

.icone-composant svg {
  display: block;
  width: 100%;
  height: 100%;
  fill: none;
  stroke: currentColor;
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-width: 1.7;
}

.nom-composant {
  min-width: 0;
  overflow-wrap: anywhere;
}

.composants-selectionnes li button {
  flex: 0 0 auto;
  border: 0;
  background: transparent;
  color: var(--color-bordeaux);
  cursor: pointer;
  font: 600 0.9rem/1.2 var(--font-body);
  white-space: nowrap;
}

.composants-selectionnes li button:hover {
  text-decoration: underline;
}

.composants-selectionnes li button:focus-visible,
.bouton-principal:focus-visible {
  outline: 2px solid var(--color-focus);
  outline-offset: 3px;
}

.erreur {
  margin: 0;
  color: var(--color-erreur);
  font-size: 0.95rem;
  line-height: 1.5;
}

.etat {
  margin: 0;
  color: var(--color-encre-douce);
  font-size: 0.95rem;
  line-height: 1.5;
}

.bouton-principal {
  display: flex;
  width: 100%;
  min-height: 3.25rem;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-sm);
  margin-top: var(--space-lg);
  padding: 0.8rem 1.1rem;
  border: 0;
  border-radius: var(--radius-card);
  outline: 2px solid transparent;
  outline-offset: 3px;
  background: var(--color-bordeaux);
  color: var(--color-citron);
  cursor: pointer;
  font: 700 1rem/1.2 var(--font-body);
  text-align: left;
}

.bouton-principal:hover:not(:disabled) {
  background: var(--color-bordeaux-hover);
}

.bouton-principal:active:not(:disabled) {
  background: var(--color-bordeaux-hover);
}

.bouton-principal:disabled {
  background: var(--color-desactive);
  color: var(--color-encre-desactive);
  cursor: not-allowed;
}

.fleche-bouton {
  flex: 0 0 auto;
  color: var(--color-citron);
  font-size: 1.2rem;
  line-height: 1;
}

@media (min-width: 42rem) {
  .grille-projet {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (min-width: 64rem) {
  .page-saisie {
    grid-template-columns: minmax(24rem, 38vw) minmax(0, 1fr);
  }

  .panneau-identite {
    position: sticky;
    top: 0;
    min-height: 100dvh;
    align-self: start;
    padding: clamp(2.25rem, 4vw, 4.5rem);
  }

  .contenu-identite {
    padding-block: var(--space-2xl);
  }

  .contenu-formulaire {
    width: 100%;
    max-width: 54rem;
    margin-block: auto;
    padding: clamp(1.5rem, 3vw, 2.5rem) clamp(2rem, 6vw, 6rem) clamp(3rem, 6vw, 6rem);
  }
}

@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    scroll-behavior: auto !important;
  }
}
</style>
