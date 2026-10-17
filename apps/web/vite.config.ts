import { reactRouter } from "@react-router/dev/vite";
import { defineConfig, loadEnv } from "vite";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "ABOGALIA_");

  return {
    plugins: [reactRouter()],
    server: {
      host: "127.0.0.1",
      port: 5190,
      strictPort: true,
      proxy: {
        "/api": {
          target: env.ABOGALIA_API_PROXY_TARGET || "http://127.0.0.1:8090",
        },
      },
    },
  };
});
