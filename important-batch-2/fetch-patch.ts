/**
 * Ensures same-origin API calls send cookies (httpOnly session) and handles 401 on protected pages.
 */
import { isPublicPath } from "./is-public-path";

const originalFetch = window.fetch;

window.fetch = async (input: RequestInfo | URL, init?: RequestInit) => {
  const url = typeof input === "string" ? input : input instanceof URL ? input.href : input.url;
  const isApi = url.includes("/api/");
  const isAuthMe = url.includes("/api/auth/me");

  const nextInit: RequestInit = {
    ...init,
    credentials: init?.credentials ?? "include",
  };

  const response = await originalFetch(input, nextInit);

  // Let React Query handle /me 401 (session check); redirect on other API 401s when on a protected page.
  if (
    response.status === 401 &&
    isApi &&
    !isAuthMe &&
    !isPublicPath(window.location.pathname)
  ) {
    localStorage.removeItem("kiu_user");
    window.location.href = "/login";
  }

  return response;
};

export {};
