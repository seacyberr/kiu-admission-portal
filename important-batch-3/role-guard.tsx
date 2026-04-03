import { useEffect, type ReactNode } from "react";
import { useLocation } from "wouter";
import { useGetCurrentUser } from "@workspace/api-client-react";

type Role = "admin" | "applicant" | "finalist";

interface RoleGuardProps {
  roles: Role[];
  children: ReactNode;
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
      if (user.role === "admin") setLocation("/admin");
      else if (user.role === "finalist") setLocation("/career");
      else if (user.role === "applicant") setLocation("/dashboard");
      else setLocation("/login");
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
