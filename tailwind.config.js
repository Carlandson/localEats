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
    extend: {
      colors: {
        'brand': {
          'primary': 'var(--primary-color)',
          'secondary': 'var(--secondary-color)',
          'hover': 'var(--hover-color)',
        }
      },
      boxShadow: {
        'input-focus': '0 0 0 3px rgba(147, 197, 253, 0.5)'

      }
    },
  },
  variants: {
    extend: {
      boxShadow: ['focus'],
    }
  },
  plugins: [],
  safelist: [
    'h-[50vh]',
    'h-64 sm:h-80 md:h-96 lg:h-[600px]',
    {
      pattern: /bg-(slate|gray|zinc|neutral|stone|red|orange|amber|yellow|lime|green|emerald|teal|cyan|sky|blue|indigo|violet|purple|fuchsia|pink|rose)-(50|100|200|300|400|500|600|700|800|900)/,
    },
    {
      pattern: /text-(slate|gray|zinc|neutral|stone|red|orange|amber|yellow|lime|green|emerald|teal|cyan|sky|blue|indigo|violet|purple|fuchsia|pink|rose)-(50|100|200|300|400|500|600|700|800|900)/,
    },
    // Add any other color utilities you want to safelist
  ],
};