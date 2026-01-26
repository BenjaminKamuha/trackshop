/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    '../../templates/**/*.html',   // templates globaux
    '../templates/**/*.html',      // templates de l’app theme
    '../../**/templates/**/*.html' // TOUTES les apps Django
  ],
  darkMode: 'class',   // ⚠️ OBLIGATOIRE
  theme: {
    extend: {},
  },
  plugins: [],
}
