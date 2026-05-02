import type { Config } from 'tailwindcss'

export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        'primary-container': '#5e5ce6',
        secondary: '#c8c6c8',
        'on-surface-variant': '#c7c4d7',
        error: '#ffb4ab',
        'error-container': '#93000a',
        'on-primary': '#1800a7',
        'secondary-container': '#474649',
        surface: '#13131b',
        'surface-container-lowest': '#0e0d15',
        'surface-container-low': '#1b1b23',
        'surface-container': '#1f1f27',
        'surface-container-high': '#2a2932',
        'surface-container-highest': '#34343d',
        'on-surface': '#e4e1ed',
        'outline-variant': '#464554',
        primary: '#c2c1ff',
        'inverse-primary': '#4d4ad5',
        'on-primary-container': '#f4f1ff',
        background: '#13131b',
        'on-background': '#e4e1ed',
        tertiary: '#ffb786',
        'tertiary-container': '#ae5600',
      },
      borderRadius: {
        DEFAULT: '0.25rem',
        lg: '0.5rem',
        xl: '0.75rem',
        full: '9999px',
      },
      fontFamily: {
        sans: ['Manrope', '-apple-system', 'sans-serif'],
        display: ['SF Pro Display', '-apple-system', 'sans-serif'],
      },
    },
  },
  plugins: [],
} satisfies Config
