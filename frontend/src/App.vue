<!-- Point d'entrée de l'application Vue. Responsable : gardien du dépôt · Tâche 34. -->
<script setup>
import Saisie from './views/Saisie.vue'
</script>

<template>
  <Saisie />
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
</style>
