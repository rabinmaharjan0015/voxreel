import type { Config } from "tailwindcss";
export default {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#07070C",       // canvas — deepest layer
        panel: "#0F0F18",     // elevated surface
        line: "rgba(255,255,255,0.08)",
      },
      fontFamily: { display: ["var(--font-display)"], sans: ["var(--font-sans)"] },
      backgroundImage: { brand: "linear-gradient(120deg,#8B5CF6,#EC4899 55%,#F59E0B)" },
      keyframes: {
        float: { "0%,100%": { transform: "translateY(0)" }, "50%": { transform: "translateY(-14px)" } },
        shimmer: { "100%": { transform: "translateX(100%)" } },
        "fade-up": {
          "0%": { opacity: "0", transform: "translateY(12px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        "fade-in": { "0%": { opacity: "0" }, "100%": { opacity: "1" } },
      },
      animation: {
        float: "float 9s ease-in-out infinite",
        shimmer: "shimmer 1.8s ease-in-out infinite",
        "fade-up": "fade-up 0.5s ease-out both",
        "fade-in": "fade-in 0.4s ease-out both",
      },
    },
  },
  plugins: [],
} satisfies Config;
