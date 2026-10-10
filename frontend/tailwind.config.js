/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        background: '#0a0d14',
        surface: {
          DEFAULT: '#0f141f',
          subtle: '#141b29',
          elevated: '#1a2335',
          active: '#202b40',
        },
        border: {
          subtle: '#1a2233',
          DEFAULT: '#222f46',
          strong: '#2f4160',
        },
        foreground: {
          DEFAULT: '#e6edf3',
          muted: '#8b9bb4',
          subtle: '#5a6b85',
        },
        accent: {
          DEFAULT: '#0284c7', // Sky-600
          hover: '#0369a1',
          light: '#38bdf8',
          subtle: 'rgba(2, 132, 199, 0.12)',
        },
        status: {
          open: '#38bdf8',
          running: '#f59e0b',
          completed: '#10b981',
          failed: '#ef4444',
          neutral: '#64748b',
          malicious: '#ef4444',
          suspicious: '#f59e0b',
          benign: '#10b981',
          unknown: '#64748b',
          inferred: '#a855f7',
          observed: '#0ea5e9',
        }
      },
      fontFamily: {
        sans: [
          'Inter',
          '-apple-system',
          'BlinkMacSystemFont',
          '"Segoe UI"',
          'Roboto',
          'sans-serif',
        ],
        mono: [
          '"JetBrains Mono"',
          '"Fira Code"',
          'Consolas',
          'monospace',
        ],
      },
      fontSize: {
        '2xs': '0.6875rem', // 11px
      },
    },
  },
  plugins: [],
}
