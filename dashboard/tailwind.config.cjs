/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: "#f0f9ff",
          100: "#e0f2fe",
          500: "#03b3b3",
          600: "#02898a",
          700: "#026d6d",
          900: "#023b3b",
        },
        secondary: {
          500: "#f59e42",
          600: "#e58325",
          700: "#c25a1a",
        },
        field: {
          100: "#fef8f0",
          200: "#f3e8d2",
        },
      },
    },
  },
  plugins: [],
}
