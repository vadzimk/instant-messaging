import daisyui from 'daisyui';

/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      transitionTimingFunction: {
        'custom-cubic': 'cubic-bezier(0, 0, 0.2, 1)',
      },
      backgroundColor: {
        'custom-fallback-bc': 'var(--fallback-bc,oklch(var(--bc)/0.2))',
      },
    },
  },
  plugins: [daisyui],
}
