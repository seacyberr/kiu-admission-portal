import { useState, useEffect } from 'react';
import { useLocation, Link } from 'wouter';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button, Input, Label, Card } from '@/components/ui/shared';
import { useToast } from '@/hooks/use-toast';
import { ArrowLeft } from 'lucide-react';
import { motion } from 'framer-motion';

const loginSchema = z.object({
  email: z.string().email("Invalid email address"),
  password: z.string().min(1, "Password is required"),
});

type LoginForm = z.infer<typeof loginSchema>;

const BASE = import.meta.env.BASE_URL.replace(/\/$/, "");

export default function Login() {
  const [, setLocation] = useLocation();
  const { toast } = useToast();

  // BUG FIX: replaced loginMutation (which was defined but never called, making
  // isPending always false) with local state that accurately tracks the request.
  const [isLoading, setIsLoading] = useState(false);

  // If user is already authenticated redirect them away from the login page.
  // Per the changelog: visiting /login while authenticated clears the session
  // so the user can sign in with different credentials.
  useEffect(() => {
    const userStr = localStorage.getItem("kiu_user");
    if (!userStr) return;
    try {
      const user = JSON.parse(userStr);
      // Clear stale local state and let /api/auth/me validate the session.
      // If the session cookie is still valid the user will be redirected by
      // the RoleGuard on the target page.  If it's expired they stay on /login.
      localStorage.removeItem("kiu_user");
      // Call logout to clear the httpOnly cookie too
      fetch(`${BASE}/api/auth/logout`, { method: "POST", credentials: "include" }).catch(() => {});
    } catch {
      localStorage.removeItem("kiu_user");
    }
  }, []);

  const { register, handleSubmit, formState: { errors } } = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginForm) => {
    setIsLoading(true);
    try {
      const res = await fetch(`${BASE}/api/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify(data),
      });
      const json = await res.json();

      if (res.status === 403 && json.needsVerification) {
        localStorage.setItem("kiu_pending_email", json.email);
        toast({
          title: "Email not verified",
          description: "A new OTP has been sent. Please verify your account.",
          variant: "destructive",
        });
        setLocation("/verify-otp");
        return;
      }

      if (!res.ok) {
        toast({
          title: "Login failed",
          description: json.message || "Invalid credentials",
          variant: "destructive",
        });
        return;
      }

      // Access token is now in httpOnly cookie set by the server.
      // Store user object for UI-only purposes (role, display name etc.)
      localStorage.setItem("kiu_user", JSON.stringify(json.user));
      toast({ title: "Welcome back!", description: "Logged in successfully." });

      if (json.user.role === "admin") setLocation("/admin");
      else if (json.user.role === "finalist") setLocation("/career");
      else setLocation("/dashboard");
    } catch {
      toast({
        title: "Network error",
        description: "Could not connect to the server.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-[90vh] flex items-center justify-center p-4 relative overflow-hidden">
      <div className="absolute inset-0 z-0 opacity-40 mix-blend-multiply">
        <img
          src={`${import.meta.env.BASE_URL}images/abstract-academic.png`}
          alt=""
          className="w-full h-full object-cover"
        />
      </div>

      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="w-full max-w-md relative z-10"
      >
        <Link
          href="/"
          className="inline-flex items-center text-sm font-semibold text-muted-foreground hover:text-primary mb-6 transition-colors"
        >
          <ArrowLeft className="w-4 h-4 mr-2" /> Back to Home
        </Link>

        <Card className="p-8 shadow-2xl shadow-primary/10 border-white/50 bg-white/80 backdrop-blur-xl">
          <div className="text-center mb-8">
            <div className="w-36 h-36 bg-white rounded-2xl mx-auto mb-4 flex items-center justify-center shadow-lg border border-border">
              <img
                src={`${import.meta.env.BASE_URL}images/logo.png`}
                alt="Logo"
                className="w-32 h-32 object-contain"
              />
            </div>
            <h1 className="text-3xl font-display font-bold text-primary">Welcome Back</h1>
            <p className="text-muted-foreground mt-2">Sign in to access your portal</p>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
            <div className="space-y-2">
              <Label htmlFor="email">Email Address</Label>
              <Input
                id="email"
                type="email"
                placeholder="student@example.com"
                {...register("email")}
                className={errors.email ? "border-destructive" : ""}
              />
              {errors.email && <p className="text-xs text-destructive">{errors.email.message}</p>}
            </div>

            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <Label htmlFor="password">Password</Label>
                <Link
                  href="/forgot-password"
                  className="text-xs font-semibold text-primary hover:underline"
                >
                  Forgot password?
                </Link>
              </div>
              <Input
                id="password"
                type="password"
                {...register("password")}
                className={errors.password ? "border-destructive" : ""}
              />
              {errors.password && (
                <p className="text-xs text-destructive">{errors.password.message}</p>
              )}
            </div>

            {/* BUG FIX: was loginMutation.isPending (always false) — now correctly
                reflects the local fetch state via isLoading */}
            <Button type="submit" className="w-full py-6 text-lg" isLoading={isLoading}>
              Sign In
            </Button>
          </form>

          <div className="mt-8 text-center text-sm text-muted-foreground">
            Don't have an account?{" "}
            <Link href="/register" className="font-bold text-primary hover:underline">
              Register here
            </Link>
          </div>
        </Card>
      </motion.div>
    </div>
  );
}
