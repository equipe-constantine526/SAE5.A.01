// Configuration du projet Vue. Responsable : gardien du dépôt · Tâche 34.
// Choix : Vite lance et construit le frontend sans ajouter un routeur au squelette.
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0',
    port: 5173,
  },
})
