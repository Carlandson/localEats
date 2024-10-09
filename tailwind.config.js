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
};