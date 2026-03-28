import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{js,ts,jsx,tsx,mdx}", "./components/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      keyframes: {
        "fade-in-up": {
          "0%": { opacity: "0", transform: "translateY(8px)" },
          "100%": { opacity: "1", transform: "translateY(0)" }
        }
      },
      animation: {
        "fade-in-up": "fade-in-up 360ms ease-out"
      },
      boxShadow: {
        vignette: "inset 0 0 160px rgba(2, 6, 23, 0.9)",
        glow: "0 0 15px rgba(59, 130, 246, 0.2)"
      }
    }
  },
  plugins: []
};

export default config;
