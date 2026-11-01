import { defineConfig } from "astro/config";
import node from "@astrojs/node";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  devToolbar: { enabled: false },
  output: "server",
  adapter: node({ mode: "standalone" }),
  vite: { plugins: [tailwindcss()] },
  server: { host: "127.0.0.1", port: 4321 },
});
