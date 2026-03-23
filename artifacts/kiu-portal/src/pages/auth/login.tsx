import { useState } from 'react';
import { useLocation, Link } from 'wouter';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useLoginUser } from '@workspace/api-client-react';
import { Button, Input, Label, Card } from '@/components/ui/shared';
import { useToast } from '@/hooks/use-toast';
import { ArrowLeft } from 'lucide-react';
import { motion } from 'framer-motion';

const loginSchema = z.object({
  email: z.string().email("Invalid email address"),
  password: z.string().min(1, "Password is required"),
});

type LoginForm = z.infer<typeof loginSchema>;

export default function Login() {
  const [, setLocation] = useLocation();
  const { toast } = useToast();
  const loginMutation = useLoginUser();

  const { register, handleSubmit, formState: { errors } } = useForm<LoginForm>({
    resolver: zodResolver(loginSchema)
  });

  const onSubmit = (data: LoginForm) => {
    loginMutation.mutate({ data }, {
      onSuccess: (res) => {
        localStorage.setItem('kiu_token', res.token);
        localStorage.setItem('kiu_user', JSON.stringify(res.user));
        toast({ title: "Welcome back!", description: "Logged in successfully." });
        
        // Redirect based on role
        if (res.user.role === 'admin') setLocation('/admin');
        else if (res.user.role === 'finalist') setLocation('/career');
        else setLocation('/dashboard');
      },
      onError: (err: any) => {
        toast({ 
          title: "Login failed", 
          description: err.message || "Invalid credentials", 
          variant: "destructive" 
        });
      }
    });
  };

  return (
    <div className="min-h-[90vh] flex items-center justify-center p-4 relative overflow-hidden">
      <div className="absolute inset-0 z-0 opacity-40 mix-blend-multiply">
        <img src={`${import.meta.env.BASE_URL}images/abstract-academic.png`} alt="" className="w-full h-full object-cover" />
      </div>
      
      <motion.div 
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="w-full max-w-md relative z-10"
      >
        <Link href="/" className="inline-flex items-center text-sm font-semibold text-muted-foreground hover:text-primary mb-6 transition-colors">
          <ArrowLeft className="w-4 h-4 mr-2" /> Back to Home
        </Link>
        
        <Card className="p-8 shadow-2xl shadow-primary/10 border-white/50 bg-white/80 backdrop-blur-xl">
          <div className="text-center mb-8">
            <div className="w-16 h-16 bg-primary rounded-2xl mx-auto mb-4 flex items-center justify-center shadow-lg">
              <img src={`${import.meta.env.BASE_URL}images/logo.png`} alt="Logo" className="w-10 h-10 object-contain" />
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
                <Link href="#" className="text-xs font-semibold text-primary hover:underline">Forgot password?</Link>
              </div>
              <Input 
                id="password" 
                type="password" 
                {...register("password")}
                className={errors.password ? "border-destructive" : ""}
              />
              {errors.password && <p className="text-xs text-destructive">{errors.password.message}</p>}
            </div>

            <Button 
              type="submit" 
              className="w-full py-6 text-lg" 
              isLoading={loginMutation.isPending}
            >
              Sign In
            </Button>
          </form>

          <div className="mt-8 text-center text-sm text-muted-foreground">
            Don't have an account?{' '}
            <Link href="/register" className="font-bold text-primary hover:underline">
              Register here
            </Link>
          </div>
        </Card>
      </motion.div>
    </div>
  );
}
