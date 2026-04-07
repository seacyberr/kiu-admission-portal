/**
 * apps/kiu-portal/src/pages/auth/login.tsx
 *
 * FIX: The previous implementation called the logout API whenever an
 * authenticated user visited /login. This caused silent session destruction
 * if a user accidentally navigated here (e.g. from a bookmark or browser
 * history). Users who were logged in would be unexpectedly signed out.
 *
 * Correct behaviour: redirect authenticated users to the dashboard immediately.
 * Only unauthenticated users should see the login form.
 */

import { useEffect } from "react";
import { useLocation } from "wouter";
import { useAuth } from "@/hooks/useAuth";
import { LoginForm } from "@/components/auth/LoginForm";
import { Spinner } from "@/components/ui/spinner";

export default function LoginPage() {
  const { user, isLoading } = useAuth();
  const [, navigate] = useLocation();

  useEffect(() => {
    // If the user is already authenticated, send them to the dashboard.
    // Do NOT log them out — they may have arrived here accidentally.
    if (!isLoading && user) {
      const destination =
        user.role === "admin" ? "/admin/dashboard" : "/applicant/dashboard";
      navigate(destination, { replace: true });
    }
  }, [user, isLoading, navigate]);

  // While we're checking auth status, show a neutral loading state
  // so the login form doesn't flash briefly before redirect.
  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <Spinner />
      </div>
    );
  }

  // Authenticated users are being redirected above — don't render the form.
  if (user) {
    return null;
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4">
      <div className="w-full max-w-md">
        <LoginForm />
      </div>
    </div>
  );
}
