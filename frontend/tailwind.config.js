/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        isa: {
          excellent: '#22c55e',
          acceptable: '#eab308',
          intervention: '#f97316',
          risk: '#ef4444',
        },
      },
    },
  },
  plugins: [],
}
