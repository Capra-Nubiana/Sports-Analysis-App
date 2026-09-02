/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
      colors: {
        primary: {
          50: "#e0f8f8",
          100: "#b3eded",
          200: "#80dfe0",
          300: "#4dd1d2",
          400: "#26c6c8",
          500: "#03b3b3",
          600: "#029f9e",
          700: "#02898a",
          800: "#016e6f",
          900: "#015152",
          950: "#003233",
        },
        slate: {
          850: '#151e2e',
          900: '#0f172a',
          950: '#020617',
        }
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-out',
        'slide-up': 'slideUp 0.4s ease-out forwards',
        'pulse-glow': 'pulseGlow 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        pulseGlow: {
          '0%, 100%': { opacity: '1', boxshadow: '0 0 15px rgba(3, 179, 179, 0.5)' },
          '50%': { opacity: '.5', boxshadow: '0 0 5px rgba(3, 179, 179, 0.2)' },
        }
      }
    },
  },
  plugins: [],
}
