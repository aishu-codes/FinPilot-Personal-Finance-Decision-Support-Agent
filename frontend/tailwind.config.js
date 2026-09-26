/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        finance: {
          dark: '#0F172A',
          card: '#1E293B',
          primary: '#10B981',
          accent: '#3B82F6',
          purple: '#8B5CF6',
          warning: '#F59E0B',
          danger: '#EF4444'
        }
      }
    },
  },
  plugins: [],
}
