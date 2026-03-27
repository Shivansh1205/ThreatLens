/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#0B0F19', /* deep navy / charcoal */
        panel: '#111827', /* slightly lighter for cards */
        'panel-hover': '#1F2937',
        border: '#1F2937',
        primary: {
          DEFAULT: '#3B82F6', // Blue
          glow: 'rgba(59, 130, 246, 0.5)'
        },
        danger: {
          DEFAULT: '#EF4444', // Red
          glow: 'rgba(239, 68, 68, 0.5)'
        },
        warning: {
          DEFAULT: '#F59E0B', // Amber
        },
        success: {
          DEFAULT: '#10B981', // Emerald
        },
        accent: {
          DEFAULT: '#8B5CF6', // Purple
          glow: 'rgba(139, 92, 246, 0.5)'
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        'glow-primary': '0 0 15px rgba(59, 130, 246, 0.3)',
        'glow-danger': '0 0 15px rgba(239, 68, 68, 0.3)',
        'glow-accent': '0 0 15px rgba(139, 92, 246, 0.3)',
      }
    },
  },
  plugins: [],
}
