import { useState, useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useLocation, useSearch, Link } from "wouter";
import { Button, Card, Input, Label } from "@/components/ui/shared";
import { useToast } from "@/hooks/use-toast";
import { Eye, EyeOff, ArrowLeft, CheckCircle } from "lucide-react";
import { apiPost, ApiError } from '@/services/api';

const resetSchema = z.object({
  code: z.string().min(6, "Code must be 6 digits").max(6, "Code must be 6 digits"),
  password: z
    .string()
    .min(8, "Password must be at least 8 characters")
    .regex(/[A-Z]/, "Password must contain at least one uppercase letter")
    .regex(/[a-z]/, "Password must contain at least one lowercase letter")
    .regex(/[0-9]/, "Password must contain at least one digit"),
  confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"],
});

type ResetForm = z.infer<typeof resetSchema>;

export default function ResetPassword() {
  const [, navigate] = useLocation();
  const searchParams = useSearch();
  const { toast } = useToast();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [resetSuccess, setResetSuccess] = useState(false);

  // Get email from URL params
  const email = new URLSearchParams(searchParams).get("email") || "";

  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
  } = useForm<ResetForm>({
    resolver: zodResolver(resetSchema),
  });

  const password = watch("password", "");

  // Redirect if no email in URL
  useEffect(() => {
    if (!email) {
      navigate("/forgot-password");
    }
  }, [email, navigate]);

  const onSubmit = async (data: ResetForm) => {
    setIsSubmitting(true);
    try {
      await apiPost('/auth/reset-password', {
        email: email,
        code: data.code,
        password: data.password,
      });

      setResetSuccess(true);
      toast({
        title: "Password reset successful",
        description: "You can now login with your new password.",
      });
    } catch (err) {
      if (err instanceof ApiError) {
        toast({
          title: "Error",
          description: err.message || "Failed to reset password",
          variant: "destructive",
        });
      } else {
        toast({
          title: "Error",
          description: "Network error. Please try again.",
          variant: "destructive",
        });
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!email) {
    return null;
  }

  if (resetSuccess) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary/5 via-background to-accent/5 flex items-center justify-center p-4">
        <Card className="w-full max-w-md p-8">
          <div className="text-center">
            <div className="w-16 h-16 bg-success/20 text-success rounded-full flex items-center justify-center mx-auto mb-6">
              <CheckCircle className="w-8 h-8" />
            </div>
            <h1 className="text-2xl font-display font-bold text-foreground mb-4">
              Password Reset Complete
            </h1>
            <p className="text-muted-foreground mb-6">
              Your password has been successfully reset. You can now login with your new password.
            </p>
            <Link href="/login">
              <Button className="w-full">Go to Login</Button>
            </Link>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary/5 via-background to-accent/5 flex items-center justify-center p-4">
      <Card className="w-full max-w-md p-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-display font-bold text-primary mb-2">
            Reset Password
          </h1>
          <p className="text-muted-foreground">
            Enter the 6-digit code sent to{" "}
            <span className="font-semibold text-foreground">{email}</span>{" "}
            and your new password.
          </p>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="code">Reset Code</Label>
            <Input
              id="code"
              type="text"
              placeholder="Enter 6-digit code"
              maxLength={6}
              {...register("code")}
              className={errors.code ? "border-destructive" : ""}
            />
            {errors.code && (
              <p className="text-sm text-destructive">{errors.code.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="password">New Password</Label>
            <div className="relative">
              <Input
                id="password"
                type={showPassword ? "text" : "password"}
                placeholder="Enter new password"
                {...register("password")}
                className={errors.password ? "border-destructive pr-10" : "pr-10"}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
              >
                {showPassword ? (
                  <EyeOff className="w-4 h-4" />
                ) : (
                  <Eye className="w-4 h-4" />
                )}
              </button>
            </div>
            {errors.password && (
              <p className="text-sm text-destructive">{errors.password.message}</p>
            )}
            
            {/* Password strength indicators */}
            {password && (
              <div className="space-y-1 text-xs">
                <div className={`flex items-center gap-2 ${password.length >= 8 ? "text-success" : "text-muted-foreground"}`}>
                  <div className={`w-1.5 h-1.5 rounded-full ${password.length >= 8 ? "bg-success" : "bg-muted"}`} />
                  At least 8 characters
                </div>
                <div className={`flex items-center gap-2 ${/[A-Z]/.test(password) ? "text-success" : "text-muted-foreground"}`}>
                  <div className={`w-1.5 h-1.5 rounded-full ${/[A-Z]/.test(password) ? "bg-success" : "bg-muted"}`} />
                  One uppercase letter
                </div>
                <div className={`flex items-center gap-2 ${/[a-z]/.test(password) ? "text-success" : "text-muted-foreground"}`}>
                  <div className={`w-1.5 h-1.5 rounded-full ${/[a-z]/.test(password) ? "bg-success" : "bg-muted"}`} />
                  One lowercase letter
                </div>
                <div className={`flex items-center gap-2 ${/[0-9]/.test(password) ? "text-success" : "text-muted-foreground"}`}>
                  <div className={`w-1.5 h-1.5 rounded-full ${/[0-9]/.test(password) ? "bg-success" : "bg-muted"}`} />
                  One number
                </div>
              </div>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="confirmPassword">Confirm New Password</Label>
            <div className="relative">
              <Input
                id="confirmPassword"
                type={showConfirmPassword ? "text" : "password"}
                placeholder="Confirm new password"
                {...register("confirmPassword")}
                className={errors.confirmPassword ? "border-destructive pr-10" : "pr-10"}
              />
              <button
                type="button"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
              >
                {showConfirmPassword ? (
                  <EyeOff className="w-4 h-4" />
                ) : (
                  <Eye className="w-4 h-4" />
                )}
              </button>
            </div>
            {errors.confirmPassword && (
              <p className="text-sm text-destructive">{errors.confirmPassword.message}</p>
            )}
          </div>

          <Button type="submit" className="w-full" isLoading={isSubmitting}>
            Reset Password
          </Button>

          <div className="text-center">
            <Link
              href="/forgot-password"
              className="inline-flex items-center text-sm text-muted-foreground hover:text-primary transition-colors"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Forgot Password
            </Link>
          </div>
        </form>
      </Card>
    </div>
  );
}