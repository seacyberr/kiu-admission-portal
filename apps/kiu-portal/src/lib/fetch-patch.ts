/**
 * Monkey-patches window.fetch to:
 *  1. Always send credentials (httpOnly cookie) on same-origin /api calls.
 *  2. On 401 from a protected API endpoint, attempt a silent token refresh
 *     before giving up and redirecting to /login.
 *
 * BUG FIX (navigation logout): The original implementation hard-redirected to
 * /login on any non-/me 401.  With a 15-minute JWT this triggered on virtually
 * every navigation after the first quarter-hour, then my broken login.tsx
 * called logout on arrival, wiping the session permanently.
 *
 * The fix: try /api/auth/refresh first.  If it succeeds, replay the original
 * request.  Only redirect when refresh itself fails.
 */
import { isPublicPath } from "./is-public-path";

const _originalFetch = window.fetch;

// Single in-flight refresh promise shared across concurrent 401s
let _refreshPromise: Promise<boolean> | null = null;

async function tryRefresh(): Promise<boolean> {
  if (_refreshPromise) return _refreshPromise;

  _refreshPromise = _originalFetch("/api/auth/refresh", {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({}),
  })
    .then(async (r) => {
      if (r.ok) {
        const json = await r.json().catch(() => ({}));
        if (json.user) {
          localStorage.setItem("kiu_user", JSON.stringify(json.user));
        }
        return true;
      }
      return false;
    })
    .catch(() => false)
    .finally(() => {
      _refreshPromise = null;
    });

  return _refreshPromise;
}

window.fetch = async (input: RequestInfo | URL, init?: RequestInit) => {
  const url =
    typeof input === "string"
      ? input
      : input instanceof URL
        ? input.href
        : (input as Request).url;

  const isApi = url.includes("/api/");
  const isAuthEndpoint =
    url.includes("/api/auth/me") ||
    url.includes("/api/auth/refresh") ||
    url.includes("/api/auth/login") ||
    url.includes("/api/auth/logout");

  const nextInit: RequestInit = {
    ...init,
    credentials: init?.credentials ?? "include",
  };

  let response = await _originalFetch(input, nextInit);

  // For protected API endpoints that return 401, try a silent token refresh
  // before falling back to the login redirect.
  if (
    response.status === 401 &&
    isApi &&
    !isAuthEndpoint &&
    !isPublicPath(window.location.pathname)
  ) {
    const refreshed = await tryRefresh();

    if (refreshed) {
      // Token refreshed — replay the original request with updated cookies
      response = await _originalFetch(input, nextInit);
    }

    // If still 401 after refresh attempt, clear stale state and redirect
    if (response.status === 401) {
      localStorage.removeItem("kiu_user");
      window.location.href = "/login";
    }
  }

  return response;
};

export {};
