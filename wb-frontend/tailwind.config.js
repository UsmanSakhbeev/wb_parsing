/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],

  theme: {
    extend: {
      colors: {
        primary: "#7c3aed",
        secondary: "#06b6d4",
      },
    },
  },

  plugins: [],
};

