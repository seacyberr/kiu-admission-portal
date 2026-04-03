/** Routes that do not require an authenticated session for API 401 handling. */
export const PUBLIC_PATH_PREFIXES = [
  "/",
  "/login",
  "/register",
  "/verify-otp",
  "/forgot-password",
  "/reset-password",
];

export function isPublicPath(pathname: string): boolean {
  return PUBLIC_PATH_PREFIXES.some(
    (p) => pathname === p || (p !== "/" && pathname.startsWith(p + "/")),
  );
}
