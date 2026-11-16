<script setup>
import { ref } from 'vue'

const props = defineProps({
  type: {
    type: String,
    required: true
  },
  modelValue: {
    type: [Number, String],
    default: null
  },
  libelleInitial: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:modelValue', 'select'])

const recherche = ref(props.libelleInitial)

// Efface le champ et réinitialise la sélection.
function effacerRecherche() {
  recherche.value = ''
  emit('update:modelValue', null)
}
</script>

<template>
  <div class="recherche-composant">
    <div class="champ-conteneur">
      <input
        v-model="recherche"
        type="text"
        placeholder="Rechercher un composant..."
        autocomplete="off"
        role="combobox"
        aria-label="Rechercher un composant"
      />

      <button
        v-if="recherche"
        type="button"
        class="bouton-effacer"
        aria-label="Effacer la recherche"
        title="Effacer"
        @click="effacerRecherche"
      >
        ✕
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onBeforeUnmount } from 'vue'

const props = defineProps({
  type: {
    type: String,
    required: true
  },
  modelValue: {
    type: [Number, String],
    default: null
  },
  libelleInitial: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:modelValue', 'select'])

const adresseApi = (
  import.meta.env.VITE_API_URL || 'http://localhost:5000'
).replace(/\/$/, '')

const recherche = ref(props.libelleInitial)
const suggestions = ref([])
const chargement = ref(false)
const erreur = ref('')
const rechercheEffectuee = ref(false)

let temporisateur = null
let controller = null

// Prépare la recherche après 300 ms sans frappe.
function planifierRecherche() {
  clearTimeout(temporisateur)

  if (controller) {
    controller.abort()
    controller = null
  }

  emit('update:modelValue', null)

  suggestions.value = []
  erreur.value = ''
  chargement.value = false
  rechercheEffectuee.value = false

  const texte = recherche.value.trim()

  if (!texte) return

  temporisateur = setTimeout(() => {
    rechercherComposants(texte)
  }, 300)
}

// Recherche les composants dans le catalogue via l'API.
async function rechercherComposants(texte) {
  const requete = new AbortController()
  controller = requete
  chargement.value = true
  erreur.value = ''

  const parametres = new URLSearchParams({
    type: props.type,
    q: texte
  })

  try {
    const reponse = await fetch(
      `${adresseApi}/api/composants?${parametres}`,
      { signal: requete.signal }
    )

    const donnees = await reponse.json()

    if (!reponse.ok) {
      throw new Error(
        donnees.erreur || 'Erreur lors de la recherche.'
      )
    }

    // Ignore les réponses des anciennes recherches.
    if (controller !== requete) return

    suggestions.value = Array.isArray(donnees) ? donnees : []
    rechercheEffectuee.value = true

  } catch (e) {
    if (e.name !== 'AbortError' && controller === requete) {
      erreur.value = e.message || 'Impossible de contacter le serveur.'
      suggestions.value = []
    }
  } finally {
    if (controller === requete) {
      chargement.value = false
      controller = null
    }
  }
}

// Efface le champ et réinitialise la sélection.
function effacerRecherche() {
  clearTimeout(temporisateur)

  if (controller) {
    controller.abort()
    controller = null
  }

  recherche.value = ''
  suggestions.value = []
  erreur.value = ''
  chargement.value = false
  rechercheEffectuee.value = false

  emit('update:modelValue', null)
}

// Nettoie les requêtes lorsque le composant est détruit.
onBeforeUnmount(() => {
  clearTimeout(temporisateur)

  if (controller) {
    controller.abort()
  }
})
</script>

<template>
  <div class="recherche-composant">
    <div class="champ-conteneur">
      <input
        v-model="recherche"
        type="text"
        placeholder="Rechercher un composant..."
        autocomplete="off"
        role="combobox"
        aria-label="Rechercher un composant"
        :aria-expanded="suggestions.length > 0"
        @input="planifierRecherche"
      />

      <button
        v-if="recherche"
        type="button"
        class="bouton-effacer"
        aria-label="Effacer la recherche"
        title="Effacer"
        @click="effacerRecherche"
      >
        ✕
      </button>
    </div>

    <!-- Chargement -->
    <p v-if="chargement" class="message" role="status">
      Recherche en cours...
    </p>

    <!-- Erreur -->
    <p v-if="erreur" class="erreur" role="alert">
      {{ erreur }}
    </p>
  </div>
</template>

<script setup>
import { ref, onBeforeUnmount } from 'vue'

const props = defineProps({
  type: {
    type: String,
    required: true
  },
  modelValue: {
    type: [Number, String],
    default: null
  },
  libelleInitial: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:modelValue', 'select'])

const adresseApi = (
  import.meta.env.VITE_API_URL || 'http://localhost:5000'
).replace(/\/$/, '')

const recherche = ref(props.libelleInitial)
const suggestions = ref([])
const chargement = ref(false)
const erreur = ref('')
const rechercheEffectuee = ref(false)

let temporisateur = null
let controller = null

// Prépare la recherche après 300 ms sans frappe.
function planifierRecherche() {
  clearTimeout(temporisateur)

  if (controller) {
    controller.abort()
    controller = null
  }

  emit('update:modelValue', null)

  suggestions.value = []
  erreur.value = ''
  chargement.value = false
  rechercheEffectuee.value = false

  const texte = recherche.value.trim()

  if (!texte) return

  temporisateur = setTimeout(() => {
    rechercherComposants(texte)
  }, 300)
}

// Recherche les composants dans le catalogue via l'API.
async function rechercherComposants(texte) {
  const requete = new AbortController()
  controller = requete
  chargement.value = true
  erreur.value = ''

  const parametres = new URLSearchParams({
    type: props.type,
    q: texte
  })

  try {
    const reponse = await fetch(
      `${adresseApi}/api/composants?${parametres}`,
      { signal: requete.signal }
    )

    const donnees = await reponse.json()

    if (!reponse.ok) {
      throw new Error(
        donnees.erreur || 'Erreur lors de la recherche.'
      )
    }

    // Ignore les réponses des anciennes recherches.
    if (controller !== requete) return

    suggestions.value = Array.isArray(donnees) ? donnees : []
    rechercheEffectuee.value = true

  } catch (e) {
    if (e.name !== 'AbortError' && controller === requete) {
      erreur.value = e.message || 'Impossible de contacter le serveur.'
      suggestions.value = []
    }
  } finally {
    if (controller === requete) {
      chargement.value = false
      controller = null
    }
  }
}

// Sélectionne une suggestion et transmet son identifiant au parent.
function selectionner(composant) {
  clearTimeout(temporisateur)

  if (controller) {
    controller.abort()
    controller = null
  }

  recherche.value = composant.nom
  suggestions.value = []
  chargement.value = false
  erreur.value = ''
  rechercheEffectuee.value = false

  emit('update:modelValue', composant.id)
  emit('select', composant)
}

// Efface le champ et réinitialise la sélection.
function effacerRecherche() {
  clearTimeout(temporisateur)

  if (controller) {
    controller.abort()
    controller = null
  }

  recherche.value = ''
  suggestions.value = []
  erreur.value = ''
  chargement.value = false
  rechercheEffectuee.value = false

  emit('update:modelValue', null)
}

// Nettoie les requêtes lorsque le composant est détruit.
onBeforeUnmount(() => {
  clearTimeout(temporisateur)

  if (controller) {
    controller.abort()
  }
})
</script>

<template>
  <div class="recherche-composant">
    <div class="champ-conteneur">
      <input
        v-model="recherche"
        type="text"
        placeholder="Rechercher un composant..."
        autocomplete="off"
        role="combobox"
        aria-label="Rechercher un composant"
        :aria-expanded="suggestions.length > 0"
        @input="planifierRecherche"
      />

      <button
        v-if="recherche"
        type="button"
        class="bouton-effacer"
        aria-label="Effacer la recherche"
        title="Effacer"
        @click="effacerRecherche"
      >
        ✕
      </button>
    </div>

    <!-- Chargement -->
    <p v-if="chargement" class="message" role="status">
      Recherche en cours...
    </p>

    <!-- Erreur -->
    <p v-if="erreur" class="erreur" role="alert">
      {{ erreur }}
    </p>

    <!-- Suggestions -->
    <ul
      v-if="suggestions.length > 0"
      class="suggestions"
      role="listbox"
      aria-label="Suggestions de composants"
    >
      <li
        v-for="composant in suggestions"
        :key="composant.id"
        role="option"
      >
        <button
          type="button"
          @click="selectionner(composant)"
        >
          <span class="nom">{{ composant.nom }}</span>

          <span class="infos-droite">
            <span class="badge-type">{{ props.type }}</span>

            <span class="prix">
              {{
                composant.prix == null
                  ? 'Prix inconnu'
                  : `${composant.prix} $`
              }}
            </span>
          </span>
        </button>
      </li>
    </ul>

    <!-- Aucun résultat -->
    <p
      v-if="
        rechercheEffectuee &&
        !chargement &&
        !erreur &&
        suggestions.length === 0
      "
      class="message"
    >
      Aucun composant trouvé.
    </p>
  </div>
</template>
<script setup>
import { ref, watch, onBeforeUnmount } from 'vue'

const props = defineProps({
  type: {
    type: String,
    required: true
  },
  modelValue: {
    type: [Number, String],
    default: null
  },
  libelleInitial: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:modelValue', 'select'])

const adresseApi = (
  import.meta.env.VITE_API_URL || 'http://localhost:5000'
).replace(/\/$/, '')

const recherche = ref(props.libelleInitial)
const suggestions = ref([])
const chargement = ref(false)
const erreur = ref('')
const rechercheEffectuee = ref(false)
const indexActif = ref(-1)

let temporisateur = null
let controller = null

// Prépare la recherche après 300 ms sans frappe.
function planifierRecherche() {
  clearTimeout(temporisateur)

  if (controller) {
    controller.abort()
    controller = null
  }

  emit('update:modelValue', null)

  suggestions.value = []
  erreur.value = ''
  chargement.value = false
  rechercheEffectuee.value = false
  indexActif.value = -1

  const texte = recherche.value.trim()

  if (!texte) return

  temporisateur = setTimeout(() => {
    rechercherComposants(texte)
  }, 300)
}

// Recherche les composants dans le catalogue via l'API.
async function rechercherComposants(texte) {
  const requete = new AbortController()
  controller = requete
  chargement.value = true
  erreur.value = ''

  const parametres = new URLSearchParams({
    type: props.type,
    q: texte
  })

  try {
    const reponse = await fetch(
      `${adresseApi}/api/composants?${parametres}`,
      { signal: requete.signal }
    )

    const donnees = await reponse.json()

    if (!reponse.ok) {
      throw new Error(
        donnees.erreur || 'Erreur lors de la recherche.'
      )
    }

    // Ignore les réponses des anciennes recherches.
    if (controller !== requete) return

    suggestions.value = Array.isArray(donnees) ? donnees : []
    rechercheEffectuee.value = true
    indexActif.value = suggestions.value.length > 0 ? 0 : -1

  } catch (e) {
    if (e.name !== 'AbortError' && controller === requete) {
      erreur.value = e.message || 'Impossible de contacter le serveur.'
      suggestions.value = []
      indexActif.value = -1
    }
  } finally {
    if (controller === requete) {
      chargement.value = false
      controller = null
    }
  }
}

// Sélectionne une suggestion et transmet son identifiant au parent.
function selectionner(composant) {
  clearTimeout(temporisateur)

  if (controller) {
    controller.abort()
    controller = null
  }

  recherche.value = composant.nom
  suggestions.value = []
  chargement.value = false
  erreur.value = ''
  rechercheEffectuee.value = false
  indexActif.value = -1

  emit('update:modelValue', composant.id)
  emit('select', composant)
}

// Gère la navigation au clavier dans la liste des suggestions.
function gererClavier(evenement) {
  if (evenement.key === 'Escape') {
    suggestions.value = []
    indexActif.value = -1
    return
  }

  if (suggestions.value.length === 0) return

  if (evenement.key === 'ArrowDown') {
    evenement.preventDefault()
    indexActif.value = (indexActif.value + 1) % suggestions.value.length
  } else if (evenement.key === 'ArrowUp') {
    evenement.preventDefault()
    indexActif.value =
      (indexActif.value - 1 + suggestions.value.length) % suggestions.value.length
  } else if (evenement.key === 'Enter' && indexActif.value >= 0) {
    evenement.preventDefault()
    selectionner(suggestions.value[indexActif.value])
  }
}

// Efface le champ et réinitialise la sélection.
function effacerRecherche() {
  clearTimeout(temporisateur)

  if (controller) {
    controller.abort()
    controller = null
  }

  recherche.value = ''
  suggestions.value = []
  erreur.value = ''
  chargement.value = false
  rechercheEffectuee.value = false
  indexActif.value = -1

  emit('update:modelValue', null)
}

// Réinitialise la recherche lorsque le type change.
watch(() => props.type, effacerRecherche)

// Met à jour le libellé affiché si le parent fournit un nom initial.
watch(() => props.libelleInitial, (nouveauLibelle) => {
  if (nouveauLibelle && props.modelValue !== null) {
    recherche.value = nouveauLibelle
  }
})

// Vide le champ texte si le parent réinitialise la sélection à null.
watch(() => props.modelValue, (nouvelleValeur) => {
  if (nouvelleValeur === null) {
    recherche.value = ''
    suggestions.value = []
    rechercheEffectuee.value = false
    indexActif.value = -1
  }
})

// Nettoie les requêtes lorsque le composant est détruit.
onBeforeUnmount(() => {
  clearTimeout(temporisateur)

  if (controller) {
    controller.abort()
  }
})
</script>

<template>
  <div class="recherche-composant">
    <div class="champ-conteneur">
      <input
        v-model="recherche"
        type="text"
        placeholder="Rechercher un composant..."
        autocomplete="off"
        role="combobox"
        aria-label="Rechercher un composant"
        :aria-expanded="suggestions.length > 0"
        @input="planifierRecherche"
        @keydown="gererClavier"
      />

      <button
        v-if="recherche"
        type="button"
        class="bouton-effacer"
        aria-label="Effacer la recherche"
        title="Effacer"
        @click="effacerRecherche"
      >
        ✕
      </button>
    </div>

    <!-- Chargement -->
    <p v-if="chargement" class="message" role="status">
      Recherche en cours...
    </p>

    <!-- Erreur -->
    <p v-if="erreur" class="erreur" role="alert">
      {{ erreur }}
    </p>

    <!-- Suggestions -->
    <ul
      v-if="suggestions.length > 0"
      class="suggestions"
      role="listbox"
      aria-label="Suggestions de composants"
    >
      <li
        v-for="(composant, index) in suggestions"
        :key="composant.id"
        role="option"
        :aria-selected="index === indexActif"
      >
        <button
          type="button"
          :class="{ actif: index === indexActif }"
          @mouseenter="indexActif = index"
          @click="selectionner(composant)"
        >
          <span class="nom">{{ composant.nom }}</span>

          <span class="infos-droite">
            <span class="badge-type">{{ props.type }}</span>

            <span class="prix">
              {{
                composant.prix == null
                  ? 'Prix inconnu'
                  : `${composant.prix} $`
              }}
            </span>
          </span>
        </button>
      </li>
    </ul>

    <!-- Aucun résultat -->
    <p
      v-if="
        rechercheEffectuee &&
        !chargement &&
        !erreur &&
        suggestions.length === 0
      "
      class="message"
    >
      Aucun composant trouvé.
    </p>
  </div>
</template>