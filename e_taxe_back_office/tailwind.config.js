/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{html,ts}",
  ],
  theme: {
    extend: {
      colors : {
        main : "rgba(12, 82, 156, 1)",
        secondary: "rgba(255,255,255,1)",
        background : "rgba(245, 246, 250, 1)",
        'main-text-color' : "rgba(32, 34, 36, 1)",
        'secondary-text-color' : "rgba(43, 48, 52, 0.4)",
        'border-color' : "rgba(215, 215, 215, 1)",
        'background-secondary' : "rgba(242, 242, 242, 1)",
      }
    },
  },
  plugins: [],
}
