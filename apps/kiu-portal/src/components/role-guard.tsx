import { useEffect, type ReactNode } from "react";
import { useLocation } from "wouter";
import { useGetCurrentUser } from "@workspace/api-client-react";

type Role = "admin" | "applicant" | "finalist";

interface RoleGuardProps {
  roles: Role[];
  children: ReactNode;
}

const BASE = import.meta.env.BASE_URL.replace(/\/$/, "");

/**
 * Determine the correct redirect path for a user based on their role and data status.
 * - Applicants without an application → /apply (new-applicant guidance)
 * - Applicants with an application → /dashboard
 * - Finalists without a profile → /career/profile
 * - Finalists with a profile → /career
 * - Others → their default dashboard
 */
async function getRedirectPath(user: { role: string }): Promise<string> {
  if (user.role === 'admin') return '/admin';
  
  try {
    if (user.role === 'applicant') {
      const res = await fetch(`${BASE}/api/admission/applications/mine`, {
        credentials: 'include',
      });
      if (res.ok) return '/dashboard';
      return '/apply';
    }
    
    if (user.role === 'finalist') {
      const res = await fetch(`${BASE}/api/career/my-profile`, {
        credentials: 'include',
      });
      if (res.ok) return '/career';
      return '/career/profile';
    }
  } catch {
    // On error, fall through to default redirects
  }
  
  return '/dashboard';
}

export function RoleGuard({ roles, children }: RoleGuardProps) {
  const [, setLocation] = useLocation();
  const { data: user, isLoading } = useGetCurrentUser({ query: { retry: false } });

  useEffect(() => {
    if (isLoading) return;
    if (!user) {
      setLocation("/login");
      return;
    }
    if (!roles.includes(user.role as Role)) {
      // Use conditional redirect based on user's data status
      getRedirectPath(user).then(setLocation);
    }
  }, [isLoading, user, roles, setLocation]);

  if (isLoading) {
    return <div className="p-8 text-center text-muted-foreground">Loading...</div>;
  }

  if (!user || !roles.includes(user.role as Role)) {
    return null;
  }

  return <>{children}</>;
}
