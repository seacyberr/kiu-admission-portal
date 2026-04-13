import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import path from "path";

const rawPort = process.env.PORT ?? "5173";
const port = Number(rawPort);
if (Number.isNaN(port) || port <= 0) {
  throw new Error(`Invalid PORT value: "${rawPort}"`);
}

let basePath = process.env.BASE_PATH ?? "/";
if (!basePath.endsWith("/")) basePath += "/";

/**
 * Flask API runs on 5001 (see DEPLOYMENT.md and run.py).
 * Override with VITE_API_PROXY_TARGET env var if needed.
 * CORRECTION from previous patch: was incorrectly set to 5000.
 */
const apiProxyTarget =
  process.env.VITE_API_PROXY_TARGET ?? "http://kiu-api-dev:5001";

/**
 * FIX: Vite proxy strips/mangles httpOnly cookie attributes (Secure, SameSite)
 * when forwarding Flask Set-Cookie headers over HTTP localhost. This causes the
 * browser to silently reject the auth cookie, requiring hard-reload to bypass
 * the cached 401 response.
 */
import type { IncomingMessage } from "http";

function cookieProxyFix(proxy: { on: (event: string, callback: (res: IncomingMessage) => void) => void }) {
  proxy.on("proxyRes", (proxyRes: IncomingMessage) => {
    const sc = proxyRes.headers["set-cookie"];
    if (Array.isArray(sc)) {
      proxyRes.headers["set-cookie"] = sc.map((c) =>
        c.replace(/;\s*Secure/gi, "").replace(/SameSite=None/gi, "SameSite=Lax")
      );
    }
  });
}

const apiProxy = {
  "/api": {
    target: apiProxyTarget,
    changeOrigin: true,
    secure: false,
    cookieDomainRewrite: "localhost",
    cookiePathRewrite: "/",
    configure: cookieProxyFix,
  },
};

export default defineConfig({
  base: basePath,
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: { "@": path.resolve(import.meta.dirname, "src") },
    dedupe: ["react", "react-dom"],
  },
  root: path.resolve(import.meta.dirname),
  build: {
    outDir: path.resolve(import.meta.dirname, "dist/public"),
    emptyOutDir: true,
    minify: "esbuild",
    sourcemap: process.env.NODE_ENV === "production" ? false : "hidden",
    cssMinify: true,
    reportCompressedSize: true,
    chunkSizeWarningLimit: 500,
    rollupOptions: {
      output: {
        manualChunks: {
          "vendor-react": ["react", "react-dom"],
          "vendor-radix": [
            "@radix-ui/react-dialog",
            "@radix-ui/react-label",
            "@radix-ui/react-slot",
            "@radix-ui/react-toast",
            "@radix-ui/react-tooltip",
          ],
          "vendor-query": ["@tanstack/react-query"],
          "vendor-form": ["react-hook-form", "@hookform/resolvers", "zod"],
          "vendor-router": ["wouter"],
          "vendor-utils": ["clsx", "tailwind-merge", "class-variance-authority", "date-fns"],
        },
        compact: true,
      },
      treeshake: {
        preset: "recommended",
        annotations: true,
        tryCatchDeoptimization: false,
      },
    },
  },
  esbuild: { legalComments: "none" },
  server: {
    port,
    host: "0.0.0.0",
    allowedHosts: true,
    // Prevent browser from caching 401 responses between page loads
    headers: { "Cache-Control": "no-store" },
    fs: { strict: true, deny: ["**/.*"] },
    proxy: apiProxy,
  },
  preview: {
    port,
    host: "0.0.0.0",
    allowedHosts: true,
    proxy: apiProxy,
  },
});
