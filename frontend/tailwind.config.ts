import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        surface: { DEFAULT: "#0f1419", card: "#1a2332", border: "#2d3a4f" },
        accent: { DEFAULT: "#3b82f6", hover: "#2563eb" },
      },
    },
  },
  plugins: [],
};

export default config;
