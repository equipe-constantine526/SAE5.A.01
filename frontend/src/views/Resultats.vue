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
const configurationActuelle = ref(null)

const composantsExistants = computed(() => {
  const composants = configurationActuelle.value?.composants
  if (!Array.isArray(composants)) return []

  return composants.filter((composant) => composant && typeof composant === 'object')
})

const nomsTypes = {
  cpu: 'Processeur',
  carte_mere: 'Carte mère',
  ram: 'Mémoire vive',
  gpu: 'Carte graphique',
  alim: 'Alimentation',
  boitier: 'Boîtier',
}

const nomsUsages = {
  jeu: 'Jeu vidéo',
  montage: 'Montage vidéo',
  bureautique: 'Bureautique',
}

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

/**
 * Arrondit un indice à deux décimales pour l'affichage sans toucher au score calculé.
 * @param {number|string} valeur Indice reçu de l'API, par exemple `0.781243`.
 * @returns {string|number} Valeur arrondie (`"0.78"`) ou valeur d'origine si elle n'est pas numérique.
 * @example formaterNombre(0.781243) renvoie `"0.78"`.
 */
function formaterNombre(valeur) {
  if (valeur === null || valeur === undefined || valeur === '') return valeur

  const nombre = Number(valeur)
  return Number.isFinite(nombre) ? nombre.toFixed(2) : valeur
}

/**
 * Affiche ou masque le détail de la recommandation sélectionnée.
 * @param {Object} piece Composant recommandé, par exemple une Radeon RX 9060 XT.
 * @returns {void} Met à jour le composant dont le détail est ouvert.
 * @example basculerDetail(piece) ouvre son détail ; un second clic le referme.
 */
function basculerDetail(piece) {
  pieceSelectionnee.value = pieceSelectionnee.value?.id === piece.id ? null : piece
}

const detailCaracteristiques = computed(() => {
  if (!pieceSelectionnee.value) return []

  const caracteristiques = pieceSelectionnee.value.caracteristiques || {}
  return Object.entries(caracteristiques)
    .filter(([nom, valeur]) => nom !== 'source' && valeur !== null && valeur !== '')
    .map(([nom, valeur]) => ({
      nom: nomsCaracteristiques[nom] || nom,
      valeur: typeof valeur === 'boolean'
        ? (valeur ? 'Oui' : 'Non')
        : ['perf', 'tflops'].includes(nom)
          ? formaterNombre(valeur)
          : valeur,
    }))
})

const detailScore = computed(() => {
  if (!pieceSelectionnee.value) return []

  const detail = pieceSelectionnee.value.detail || {}
  return Object.entries(detail).map(([nom, valeur]) => ({
    nom: nomsRegles[nom] || nom,
    valeur: formaterNombre(valeur),
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
    if (!sauvegarde || typeof sauvegarde !== 'object') return

    configurationActuelle.value = sauvegarde
  } catch {
    configurationActuelle.value = null
  }
})
</script>

<template>
  <main class="page-resultats">
    <aside class="panneau-resultats" aria-labelledby="titre-resultats">
      <div class="marque-resultats" aria-label="RigMatch">
        <span class="symbole-marque" aria-hidden="true">⇄</span>
        <span class="nom-marque">RigMatch</span>
        <span class="separateur-marque">Recommandation PC</span>
      </div>

      <div class="introduction-resultats">
        <p class="sur-titre">VOTRE CONFIGURATION, EN TOUTE SÉRÉNITÉ</p>
        <h1 id="titre-resultats">Résultats de la recommandation</h1>
        <p>Les pièces sont classées selon leur score.</p>
      </div>

      <section class="resume-configuration" aria-label="Configuration actuelle">
        <p class="sur-titre-contenu">VOTRE CONFIGURATION</p>
        <p v-if="!configurationActuelle" class="configuration-indisponible">
          La configuration n'est pas disponible.
        </p>
        <template v-else>
          <dl class="parametres-configuration">
            <div>
              <dt>Budget</dt>
              <dd>
                {{ configurationActuelle.budget ?? 'Non indiqué' }}
                {{ configurationActuelle.budget != null ? '$' : '' }}
              </dd>
            </div>
            <div>
              <dt>Usage</dt>
              <dd>{{ nomsUsages[configurationActuelle.usage] || 'Non indiqué' }}</dd>
            </div>
            <div>
              <dt>Composant recherché</dt>
              <dd>{{ nomsTypes[configurationActuelle.type_cherche] || 'Non indiqué' }}</dd>
            </div>
          </dl>

          <div class="resume-composants">
            <h2>Composants possédés</h2>
            <p v-if="!composantsExistants.length" class="configuration-indisponible">
              Aucun composant ajouté.
            </p>
            <ul v-else>
              <li v-for="composant in composantsExistants" :key="composant.id">
                <span>{{ nomsTypes[composant.type] || 'Composant' }}</span>
                <strong>{{ composant.nom }}</strong>
              </li>
            </ul>
          </div>
        </template>
      </section>

      <div class="repere-resultats">
        <span class="repere-point" aria-hidden="true"></span>
        <span>
          {{ props.resultats.length }} recommandation{{ props.resultats.length > 1 ? 's' : '' }}
        </span>
      </div>
    </aside>

    <section class="contenu-resultats" aria-label="Composants recommandés">
      <header class="entete-resultats">
        <p class="sur-titre-contenu">VOTRE CLASSEMENT</p>
      </header>

      <p v-if="props.resultats.length === 0" class="message-vide" role="status">
        Aucune recommandation à afficher.
      </p>

      <ol v-else class="liste-resultats">
        <li
          v-for="(piece, index) in props.resultats"
          :key="piece.id"
          class="carte-resultat"
          :class="{
            'carte-resultat-premiere': index === 0,
            'carte-resultat-selectionnee': pieceSelectionnee?.id === piece.id,
          }"
        >
          <span class="rang" aria-hidden="true">{{ index + 1 }}</span>
          <div class="contenu-carte">
            <p v-if="index === 0" class="badge-premiere">Meilleur score</p>
            <h2>{{ piece.nom }}</h2>
            <div class="metadonnees-resultat">
              <p><span>Prix</span><strong>{{ piece.prix }} $</strong></p>
              <p><span>Score</span><strong class="score-resultat">{{ formaterNombre(piece.score) }}</strong></p>
            </div>
            <button
              type="button"
              class="bouton-detail"
              :aria-expanded="pieceSelectionnee?.id === piece.id"
              :aria-controls="`detail-piece-${piece.id}`"
              @click="basculerDetail(piece)"
            >
              {{ pieceSelectionnee?.id === piece.id ? 'Masquer le détail' : 'Voir le détail' }}
              <span aria-hidden="true">{{ pieceSelectionnee?.id === piece.id ? '−' : '→' }}</span>
            </button>

            <section
              v-if="pieceSelectionnee?.id === piece.id"
              :id="`detail-piece-${piece.id}`"
              class="detail-piece"
              aria-live="polite"
            >
              <p class="sur-titre-contenu">FICHE DU COMPOSANT</p>
              <h3>Détail de {{ pieceSelectionnee.nom }}</h3>

              <h4>Caractéristiques</h4>
              <dl v-if="detailCaracteristiques.length" class="liste-detail">
                <template v-for="caracteristique in detailCaracteristiques" :key="caracteristique.nom">
                  <dt>{{ caracteristique.nom }}</dt>
                  <dd>{{ caracteristique.valeur }}</dd>
                </template>
              </dl>
              <p v-else>Aucune caractéristique détaillée n'est disponible.</p>

              <h4>Détail du score</h4>
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
          </div>
        </li>
      </ol>
    </section>
  </main>
</template>

<style scoped>
/* Hallmark · pre-emit critique: P5 H5 E4 S4 R5 V4
 * Hallmark · genre: modern-minimal · tone: technique rassurante
 * Anchor hue: bordeaux · structural fingerprint: Split Workbench
 */
.page-resultats {
  display: grid;
  grid-template-columns: minmax(17rem, 0.72fr) minmax(0, 1.28fr);
  min-height: calc(100dvh - 3.6rem);
  color: var(--color-encre);
  background: var(--color-papier);
  font-family: var(--font-body);
}

.panneau-resultats {
  display: flex;
  min-width: 0;
  flex-direction: column;
  justify-content: space-between;
  gap: var(--space-xl);
  padding: clamp(1.5rem, 5vw, 3rem);
  background: var(--color-bordeaux);
  color: var(--color-texte-sombre);
}

.marque-resultats {
  display: flex;
  min-width: 0;
  align-items: center;
  gap: 0.65rem;
  line-height: 1;
}

.symbole-marque {
  color: var(--color-citron);
  font-size: 1.6rem;
}

.nom-marque {
  color: var(--color-texte-sombre);
  font-size: 1.05rem;
  font-weight: 700;
}

.separateur-marque {
  margin-inline-start: 0.4rem;
  padding-inline-start: 0.8rem;
  border-inline-start: 1px solid var(--color-regle-sombre);
  color: var(--color-texte-sombre-doux);
  font-size: 0.78rem;
}

.introduction-resultats {
  width: 100%;
  max-width: 32rem;
  margin-block: auto;
  padding-block: var(--space-xl);
}

.sur-titre,
.sur-titre-contenu {
  margin: 0;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  line-height: 1.4;
}

.sur-titre {
  margin-bottom: var(--space-md);
  color: var(--color-citron);
}

.introduction-resultats h1 {
  min-width: 0;
  max-width: 10ch;
  margin: 0;
  color: var(--color-citron);
  font-family: var(--font-display);
  font-size: clamp(2.35rem, 4.2vw, 4.3rem);
  font-style: normal;
  font-weight: 500;
  letter-spacing: -0.055em;
  line-height: 0.98;
  overflow-wrap: anywhere;
}

.introduction-resultats > p:last-child {
  max-width: 26rem;
  margin: var(--space-md) 0 0;
  color: var(--color-texte-sombre-doux);
  font-size: 1rem;
  line-height: 1.6;
}

.repere-resultats {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  padding-top: var(--space-md);
  border-top: 1px solid var(--color-regle-sombre);
  color: var(--color-texte-sombre-doux);
  font-size: 0.9rem;
}

.repere-point {
  width: 0.55rem;
  height: 0.55rem;
  flex: 0 0 auto;
  border-radius: 50%;
  background: var(--color-citron);
}

.resume-configuration {
  min-width: 0;
  padding: 1rem;
  border: 1px solid var(--color-regle-sombre);
  border-radius: var(--radius-card);
  background: var(--color-bordeaux-hover);
}

.resume-configuration > .sur-titre-contenu {
  color: var(--color-citron);
}

.parametres-configuration {
  display: grid;
  gap: 0.5rem;
  margin: 0.85rem 0 0;
}

.parametres-configuration div {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 0.75rem;
}

.parametres-configuration dt {
  color: var(--color-texte-sombre-doux);
  font-size: 0.8rem;
}

.parametres-configuration dd {
  margin: 0;
  color: var(--color-texte-sombre);
  font-size: 0.85rem;
  font-weight: 700;
  text-align: end;
  overflow-wrap: anywhere;
}

.resume-composants {
  margin-top: 0.9rem;
  padding-top: 0.75rem;
  border-top: 1px solid var(--color-regle-sombre);
}

.resume-composants h2 {
  margin: 0 0 0.55rem;
  color: var(--color-texte-sombre);
  font-size: 0.85rem;
}

.resume-composants ul {
  display: grid;
  max-height: 12rem;
  gap: 0.6rem;
  margin: 0;
  padding: 0;
  overflow-y: auto;
  list-style: none;
}

.resume-composants li {
  display: grid;
  min-width: 0;
  gap: 0.15rem;
}

.resume-composants li span {
  color: var(--color-texte-sombre-doux);
  font-size: 0.72rem;
}

.resume-composants li strong {
  color: var(--color-texte-sombre);
  font-size: 0.82rem;
  font-weight: 600;
  overflow-wrap: anywhere;
}

.configuration-indisponible {
  margin: 0.7rem 0 0;
  color: var(--color-texte-sombre-doux);
  font-size: 0.82rem;
  line-height: 1.45;
}

.contenu-resultats {
  min-width: 0;
  width: 100%;
  max-width: 62rem;
  padding: clamp(1.25rem, 4vw, 3.5rem);
}

.entete-resultats {
  margin-bottom: var(--space-md);
  padding-bottom: 0.85rem;
  border-bottom: 1px solid var(--color-regle);
}

.sur-titre-contenu {
  color: var(--color-bordeaux);
}

.liste-resultats {
  display: grid;
  gap: 0.85rem;
  margin: 0;
  padding: 0;
  list-style: none;
}

.carte-resultat,
.message-vide {
  min-width: 0;
  border: 1px solid var(--color-regle);
  border-radius: var(--radius-card);
  background: var(--color-surface);
}

.carte-resultat {
  display: grid;
  grid-template-columns: 2.5rem minmax(0, 1fr);
  gap: 0.75rem;
  padding: 1rem;
}

.carte-resultat-premiere {
  border-inline-start: 4px solid var(--color-orange);
}

.carte-resultat-selectionnee {
  border-color: var(--color-bordeaux);
}

.rang {
  display: grid;
  width: 2.25rem;
  height: 2.25rem;
  place-items: center;
  border-radius: 50%;
  background: var(--color-bordeaux);
  color: var(--color-citron);
  font-size: 0.9rem;
  font-weight: 700;
}

.contenu-carte {
  min-width: 0;
}

.badge-premiere {
  display: inline-block;
  margin: 0 0 0.55rem;
  padding: 0.25rem 0.55rem;
  border-radius: var(--radius-input);
  background: var(--color-orange);
  color: var(--color-orange-ink);
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.carte-resultat h2 {
  margin: 0;
  color: var(--color-bordeaux);
  font-family: var(--font-display);
  font-size: clamp(1.05rem, 2vw, 1.3rem);
  font-style: normal;
  font-weight: 700;
  line-height: 1.25;
  overflow-wrap: anywhere;
}

.metadonnees-resultat {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem 1.25rem;
  margin-top: 0.7rem;
}

.metadonnees-resultat p {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  margin: 0;
  color: var(--color-encre-douce);
  font-size: 0.9rem;
}

.metadonnees-resultat strong {
  color: var(--color-encre);
  font-variant-numeric: tabular-nums;
}

.metadonnees-resultat .score-resultat {
  color: var(--color-bordeaux);
}

.bouton-detail {
  display: inline-flex;
  align-items: center;
  gap: 0.55rem;
  min-height: 2.75rem;
  margin-top: 0.85rem;
  padding: 0.55rem 0.8rem;
  border: 1px solid var(--color-bordeaux);
  border-radius: var(--radius-card);
  background: var(--color-bordeaux);
  color: var(--color-citron);
  font: inherit;
  font-size: 0.9rem;
  font-weight: 700;
  white-space: nowrap;
  cursor: pointer;
}

.bouton-detail:hover {
  border-color: var(--color-bordeaux-hover);
  background: var(--color-bordeaux-hover);
}

.bouton-detail:focus-visible {
  outline: 3px solid var(--color-focus);
  outline-offset: 3px;
}

.bouton-detail:active {
  border-color: var(--color-orange);
  background: var(--color-orange);
  color: var(--color-orange-ink);
}

.bouton-detail:disabled {
  border-color: var(--color-desactive);
  background: var(--color-desactive);
  color: var(--color-encre-desactive);
  cursor: not-allowed;
}

.detail-piece {
  min-width: 0;
  margin-top: var(--space-sm);
  padding-top: var(--space-sm);
  border-top: 1px solid var(--color-regle);
}

.detail-piece > .sur-titre-contenu {
  margin-bottom: 0.65rem;
}

.detail-piece h3 {
  margin: 0 0 var(--space-md);
  color: var(--color-bordeaux);
  font-family: var(--font-display);
  font-size: clamp(1.25rem, 2.5vw, 1.8rem);
  font-style: normal;
  overflow-wrap: anywhere;
}

.detail-piece h4 {
  margin: var(--space-md) 0 0.65rem;
  color: var(--color-bordeaux);
  font-size: 1rem;
}

.detail-piece > p:not(.sur-titre-contenu) {
  color: var(--color-encre-douce);
  line-height: 1.5;
}

.liste-detail {
  display: grid;
  grid-template-columns: minmax(0, 0.8fr) minmax(0, 1.2fr);
  gap: 0;
}

.liste-detail dt {
  padding: 0.65rem 0.75rem 0.65rem 0;
  border-bottom: 1px solid var(--color-regle);
  color: var(--color-encre-douce);
  font-size: 0.9rem;
}

.liste-detail dd {
  min-width: 0;
  margin: 0;
  padding: 0.65rem 0;
  border-bottom: 1px solid var(--color-regle);
  color: var(--color-encre);
  font-weight: 600;
  overflow-wrap: anywhere;
}

.prix-total {
  margin-top: var(--space-md);
  padding-top: var(--space-sm);
  border-top: 1px solid var(--color-regle);
  color: var(--color-bordeaux);
  line-height: 1.5;
}

.prix-total p {
  margin: 0.45rem 0 0;
  color: var(--color-encre-douce);
}

.message-vide {
  padding: var(--space-md);
  color: var(--color-encre-douce);
  line-height: 1.5;
}

@media (max-width: 52rem) {
  .page-resultats {
    grid-template-columns: minmax(0, 1fr);
  }

  .panneau-resultats {
    min-height: 19rem;
    gap: var(--space-lg);
    padding: clamp(1.25rem, 6vw, 2rem);
  }

  .introduction-resultats {
    padding-block: var(--space-md);
  }

  .introduction-resultats h1 {
    max-width: 14ch;
    font-size: clamp(2.2rem, 9vw, 3.7rem);
  }

  .contenu-resultats {
    padding: clamp(1rem, 5vw, 2rem);
  }
}

@media (max-width: 36rem) {
  .separateur-marque {
    margin-inline-start: 0.1rem;
    padding-inline-start: 0.55rem;
  }

  .carte-resultat {
    grid-template-columns: 2rem minmax(0, 1fr);
    gap: 0.65rem;
    padding: 0.8rem;
  }

  .rang {
    width: 1.9rem;
    height: 1.9rem;
  }

  .liste-detail {
    grid-template-columns: minmax(0, 1fr);
  }

  .liste-detail dt {
    padding: 0.7rem 0 0.15rem;
    border-bottom: 0;
  }

  .liste-detail dd {
    padding: 0 0 0.7rem;
  }
}
</style>
