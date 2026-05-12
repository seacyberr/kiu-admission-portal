import { createRoot } from "react-dom/client";
import App from "./App";
import { AuthProvider } from "./context/AuthProvider";
import { ThemeProvider } from "./context/ThemeProvider";
import "./index.css";

// Register service worker for offline capability
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js')
      .then((registration) => {
        // Check for updates
        registration.addEventListener('updatefound', () => {
          const newWorker = registration.installing;
          if (newWorker) {
            newWorker.addEventListener('statechange', () => {
              if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                // New content is available - reload to activate
                window.location.reload();
              }
            });
          }
        });
      })
      .catch(() => {
        // Silent fail - service worker not critical for functionality
      });
  });
}

createRoot(document.getElementById("root")!).render(
  <ThemeProvider>
    <AuthProvider>
      <App />
    </AuthProvider>
  </ThemeProvider>
);
