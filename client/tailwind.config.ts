import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
      colors: {
        ho: {
          bg: "#0a0a0f",
          surface: "#12121a",
          card: "#1a1a26",
          border: "#2a2a3a",
          text: "#e4e4ef",
          muted: "#8888a0",
          accent: "#2a7a6a",
          "accent-light": "#3d9b88",
          navy: "#1b2f4a",
          gold: "#b8965a",
          green: "#22c55e",
          yellow: "#eab308",
          red: "#ef4444",
          teal: "#5b9e91",
        },
      },
    },
  },
  plugins: [],
} satisfies Config;
