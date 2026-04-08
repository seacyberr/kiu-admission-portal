import { useEffect, type ReactNode, useRef } from "react";
import { useLocation } from "wouter";
import { useGetCurrentUser } from "@workspace/api-client-react";
import { apiGet } from "../services/api";

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
      try {
        await apiGet(`${BASE}/api/admission/applications/mine`);
        return '/dashboard';
      } catch (e) {
        return '/apply';
      }
    }
    
    if (user.role === 'finalist') {
      try {
        await apiGet(`${BASE}/api/career/my-profile`);
        return '/career';
      } catch (e) {
        return '/career/profile';
      }
    }
  } catch {
    // On error, fall through to default redirects
  }
  
  return '/dashboard';
}

export function RoleGuard({ roles, children }: RoleGuardProps) {
  const [, setLocation] = useLocation();
  const { data: user, isLoading } = useGetCurrentUser({ query: { retry: false } });
  const hasRedirected = useRef(false);

  useEffect(() => {
    if (isLoading || hasRedirected.current) return;

    const abortController = new AbortController();
    
    async function handleRedirect() {
      if (!user) {
        hasRedirected.current = true;
        setLocation("/login");
        return;
      }
      
      if (!roles.includes(user.role as Role)) {
        hasRedirected.current = true;
        // Use conditional redirect based on user's data status
        const path = await getRedirectPath(user);
        if (!abortController.signal.aborted) {
          setLocation(path);
        }
      }
    }

    handleRedirect();

    return () => {
      abortController.abort();
    };
  }, [isLoading, user, roles, setLocation]);

  if (isLoading || user === undefined) {
    return <div className="p-8 text-center text-muted-foreground">Loading...</div>;
  }

  if (!user || !roles.includes(user.role as Role)) {
    return null;
  }

  return <>{children}</>;
}
