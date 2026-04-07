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
if (!basePath.endsWith("/")) {
  basePath += "/";
}

/**
 * Flask API proxy target.
 * Default: 5000 (Flask default). Override with VITE_API_PROXY_TARGET if needed.
 * FIX: was incorrectly defaulting to 5001 — Flask runs on 5000.
 */
const apiProxyTarget =
  process.env.VITE_API_PROXY_TARGET ?? "http://127.0.0.1:5000";

/**
 * FIX: httpOnly cookie proxy bug (Vite + Flask).
 * Vite's proxy strips/mangles Set-Cookie attributes (Secure, SameSite) when
 * forwarding responses from the Flask backend to the browser over HTTP.
 * This causes the browser to reject the auth cookie silently, requiring a
 * hard reload to bypass the cache. This proxyRes handler fixes the cookie
 * attributes in-flight so the browser always accepts the session cookie.
 */
function cookieProxyFix() {
  return {
    configure: (proxy: import("http-proxy").Server) => {
      proxy.on("proxyRes", (proxyRes) => {
        const sc = proxyRes.headers["set-cookie"];
        if (Array.isArray(sc)) {
          proxyRes.headers["set-cookie"] = sc.map((c) =>
            c
              .replace(/;\s*Secure/gi, "")
              .replace(/SameSite=None/gi, "SameSite=Lax")
          );
        }
      });
    },
  };
}

const apiProxy = {
  "/api": {
    target: apiProxyTarget,
    changeOrigin: true,
    secure: false,
    cookieDomainRewrite: "localhost",
    cookiePathRewrite: "/",
    ...cookieProxyFix(),
  },
};

export default defineConfig({
  base: basePath,

  plugins: [
    react(),
    tailwindcss(),
    // NOTE: Replit-specific plugins (@replit/vite-plugin-runtime-error-modal,
    // cartographer, dev-banner) removed — they break on non-Replit environments
    // and add unnecessary weight to dev startup.
  ],

  resolve: {
    alias: {
      "@": path.resolve(import.meta.dirname, "src"),
    },
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
    // FIX: raised from 250 to 500 — the 250 limit triggered constant false
    // warnings for normal vendor chunks (React + Radix UI alone exceed 250KB).
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
          "vendor-utils": [
            "clsx",
            "tailwind-merge",
            "class-variance-authority",
            "date-fns",
          ],
        },
        compact: true,
        hoistTransitiveImports: true,
      },
      treeshake: {
        preset: "recommended",
        annotations: true,
        tryCatchDeoptimization: false,
      },
    },
  },

  esbuild: {
    legalComments: "none",
  },

  server: {
    port,
    host: "0.0.0.0",
    allowedHosts: true,
    // Disable browser cache in dev — prevents stale 401s from being replayed
    // on normal reload, which was causing the "must hard-reload to stay logged in" bug.
    headers: {
      "Cache-Control": "no-store",
    },
    proxy: apiProxy,
    fs: {
      strict: true,
      deny: ["**/.*"],
    },
  },

  preview: {
    port,
    host: "0.0.0.0",
    allowedHosts: true,
    proxy: apiProxy,
  },
});
