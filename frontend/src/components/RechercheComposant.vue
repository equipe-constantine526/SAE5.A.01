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