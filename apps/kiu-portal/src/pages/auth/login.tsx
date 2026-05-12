import { useState, useEffect } from 'react';
import { useLocation, Link } from 'wouter';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button, Input, Label, Card } from '@/components/ui/shared';
import { useToast } from '@/hooks/use-toast';
import { motion } from 'framer-motion';
import { Eye, EyeOff } from 'lucide-react';
import { useQueryClient } from '@tanstack/react-query';
import { apiPost, ApiError } from '@/services/api';

const loginSchema = z.object({
  email: z.string().email("Invalid email address"),
  password: z.string().min(1, "Password is required"),
});

type LoginForm = z.infer<typeof loginSchema>;

// Using apiPost from services/api which handles JSend format properly

export default function Login() {
  const [, setLocation] = useLocation();
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  /**
   * BUG FIX — root cause of the navigation-logout loop.
   *
   * The previous version called /api/auth/logout whenever a logged-in user
   * arrived at the login page, then removed kiu_user from localStorage.
   * This created a fatal chain:
   *
   *   JWT expires (15 min)
   *   → any API call returns 401
   *   → fetch-patch.ts redirects to /login
   *   → login.tsx calls logout (clears httpOnly cookie + localStorage)
   *   → user is permanently wiped on every navigation after 15 min
   *
   * Correct behaviour (original): if kiu_user is present, redirect the user
   * to their dashboard.  Let the RoleGuard and /api/auth/me decide whether
   * the session is truly valid.  Only an explicit logout should clear state.
   */
  useEffect(() => {
    const userStr = localStorage.getItem("kiu_user");
    if (userStr) {
      try {
        const user = JSON.parse(userStr);
        // Prevent infinite render loop: only redirect if we are actually on login page
        if (window.location.pathname === "/login" || window.location.pathname === "/") {
          if (user.role === "admin") setLocation("/admin");
          else if (user.role === "finalist") setLocation("/career");
          else setLocation("/dashboard");
        }
      } catch {
        localStorage.removeItem("kiu_user");
      }
    }
  }, [setLocation]);

  const { register, handleSubmit, formState: { errors } } = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginForm) => {
    setIsLoading(true);
    try {
      const responseData = await apiPost<{ user: { role: string; email: string }; needsVerification?: boolean }>('/auth/login', data);

      // Handle unverified account
      if (responseData.needsVerification) {
        localStorage.setItem("kiu_pending_email", responseData.user.email);
        toast({
          title: "Email not verified",
          description: "A new OTP has been sent. Please verify your account.",
          variant: "destructive",
        });
        setLocation("/verify-otp");
        return;
      }

      // Access token is now in httpOnly cookie set by the server.
      // Store user object for UI-only purposes (role, display name etc.)
      const user = responseData.user;
      localStorage.setItem("kiu_user", JSON.stringify(user));
      queryClient.setQueryData(["me"], user);
      queryClient.invalidateQueries({ queryKey: ["me"] });
      toast({ title: "Welcome back!", description: "Logged in successfully." });

      if (user.role === "admin") setLocation("/admin");
      else if (user.role === "finalist") setLocation("/career");
      else setLocation("/dashboard");
    } catch (err) {
      if (err instanceof ApiError) {
        toast({
          title: "Login failed",
          description: err.message,
          variant: "destructive",
        });
      } else {
        toast({
          title: "Network error",
          description: "Could not connect to the server.",
          variant: "destructive",
        });
      }
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
                placeholder="your@email.com"
                autoComplete="email"
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
              <div className="relative">
                <Input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  autoComplete="current-password"
                  {...register("password")}
                  className={`${errors.password ? "border-destructive" : ""} pr-10`}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
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

          <div className="mt-6 text-center text-sm text-muted-foreground">
            New to KIU?{' '}
            <Link href="/register" className="font-bold text-primary hover:underline">
              Create account
            </Link>
          </div>

          <div className="mt-4 text-center">
            <Link href="/" className="inline-flex items-center text-sm font-semibold text-muted-foreground hover:text-primary transition-colors">
              ← Back to homepage
            </Link>
          </div>

        </Card>
        </motion.div>
    </div>
  );
}
