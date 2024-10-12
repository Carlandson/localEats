/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './restaurants/templates/**/*.html', // Adjust according to your template structure
    './restaurants/static/**/*.js',      // Adjust this pattern to target your JavaScript files
    './restaurants/static/**/*.html',     // If you have any HTML files in static
    './static/css/**/*.css',
    './static/**/*.html',
  ],
  theme: {
    extend: {},
  },
  plugins: [],
  safelist: [
    {
      pattern: /bg-(slate|gray|zinc|neutral|stone|red|orange|amber|yellow|lime|green|emerald|teal|cyan|sky|blue|indigo|violet|purple|fuchsia|pink|rose)-(50|100|200|300|400|500|600|700|800|900)/,
    },
    {
      pattern: /text-(slate|gray|zinc|neutral|stone|red|orange|amber|yellow|lime|green|emerald|teal|cyan|sky|blue|indigo|violet|purple|fuchsia|pink|rose)-(50|100|200|300|400|500|600|700|800|900)/,
    },
    // Add any other color utilities you want to safelist
  ],
};