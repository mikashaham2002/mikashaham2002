/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        './app/templates/**/*.html',
    ],
    theme: {
      extend: {
        fontFamily: {
            sans: ['Public Sans', 'sans-serif'],
        },
        colors: {
            'ncc':'#131f48',
            'ncc-bright':'#3a61e0',
            'ncc-light':'#d0d2da',
            'ncc-medium':'#424c6d',
            'ncc-soft': '#515873',
            'black': '#0d0d0d',
        },
        backgroundColor: {
            'ncc':'#131f48',
            'ncc-bright':'#3a61e0',
            'ncc-deep':'#25316a',
            'ncc-light':'#d0d2da',
            'ncc-xlight':'#f7f7fa',
            'ncc-medium':'#424c6d',
        },
        borderColor: {
            'ncc-light':'#d0d2da',
            'ncc-xlight':'#f7f7fa',
        },
        fontSize: {
            base: '14.5px',
        },
      },
    },
    plugins: [],
  }
