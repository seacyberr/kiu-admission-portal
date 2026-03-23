import { useLocation, Link } from 'wouter';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useRegisterUser } from '@workspace/api-client-react';
import { Button, Input, Label, Card } from '@/components/ui/shared';
import { useToast } from '@/hooks/use-toast';
import { ArrowLeft, User, GraduationCap } from 'lucide-react';
import { motion } from 'framer-motion';

const registerSchema = z.object({
  firstName: z.string().min(2, "First name is required"),
  lastName: z.string().min(2, "Last name is required"),
  email: z.string().email("Invalid email address"),
  phone: z.string().min(10, "Phone number is required"),
  nationalId: z.string().optional(),
  password: z.string().min(6, "Password must be at least 6 characters"),
  role: z.enum(["applicant", "finalist"], { required_error: "Please select an account type" }),
});

type RegisterForm = z.infer<typeof registerSchema>;

export default function Register() {
  const [, setLocation] = useLocation();
  const { toast } = useToast();
  const registerMutation = useRegisterUser();

  const { register, handleSubmit, watch, setValue, formState: { errors } } = useForm<RegisterForm>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      role: 'applicant'
    }
  });

  const selectedRole = watch('role');

  const onSubmit = (data: RegisterForm) => {
    // Cast to expected API role type since UI hides 'admin' registration
    const payload = { ...data, role: data.role as "applicant" | "finalist" | "admin" };
    
    registerMutation.mutate({ data: payload }, {
      onSuccess: (res) => {
        localStorage.setItem('kiu_token', res.token);
        localStorage.setItem('kiu_user', JSON.stringify(res.user));
        toast({ title: "Account created!", description: "Welcome to KIU Portal." });
        
        if (res.user.role === 'finalist') setLocation('/career');
        else setLocation('/dashboard');
      },
      onError: (err: any) => {
        toast({ 
          title: "Registration failed", 
          description: err.message || "An error occurred", 
          variant: "destructive" 
        });
      }
    });
  };

  return (
    <div className="min-h-[90vh] flex items-center justify-center p-4 relative py-12">
      <div className="absolute inset-0 z-0 opacity-40 mix-blend-multiply fixed">
        <img src={`${import.meta.env.BASE_URL}images/abstract-academic.png`} alt="" className="w-full h-full object-cover" />
      </div>
      
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-2xl relative z-10"
      >
        <Link href="/" className="inline-flex items-center text-sm font-semibold text-muted-foreground hover:text-primary mb-6 transition-colors">
          <ArrowLeft className="w-4 h-4 mr-2" /> Back to Home
        </Link>
        
        <Card className="p-8 shadow-2xl shadow-primary/10 border-white/50 bg-white/90 backdrop-blur-xl">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-display font-bold text-primary">Create Account</h1>
            <p className="text-muted-foreground mt-2">Join the KIU community today</p>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            
            {/* Role Selection */}
            <div className="grid grid-cols-2 gap-4">
              <div 
                onClick={() => setValue('role', 'applicant')}
                className={`p-4 rounded-xl border-2 cursor-pointer transition-all flex flex-col items-center gap-2 ${selectedRole === 'applicant' ? 'border-primary bg-primary/5 shadow-md text-primary' : 'border-border hover:border-primary/40 text-muted-foreground'}`}
              >
                <User className="w-8 h-8" />
                <span className="font-semibold">New Applicant</span>
                <span className="text-xs text-center">Applying for a new program</span>
              </div>
              <div 
                onClick={() => setValue('role', 'finalist')}
                className={`p-4 rounded-xl border-2 cursor-pointer transition-all flex flex-col items-center gap-2 ${selectedRole === 'finalist' ? 'border-accent bg-accent/10 shadow-md text-accent-foreground' : 'border-border hover:border-accent/40 text-muted-foreground'}`}
              >
                <GraduationCap className="w-8 h-8" />
                <span className="font-semibold">Current Finalist</span>
                <span className="text-xs text-center">Enrolled in final year</span>
              </div>
            </div>

            <div className="grid md:grid-cols-2 gap-5">
              <div className="space-y-2">
                <Label>First Name</Label>
                <Input {...register("firstName")} className={errors.firstName ? "border-destructive" : ""} />
                {errors.firstName && <p className="text-xs text-destructive">{errors.firstName.message}</p>}
              </div>
              <div className="space-y-2">
                <Label>Last Name</Label>
                <Input {...register("lastName")} className={errors.lastName ? "border-destructive" : ""} />
                {errors.lastName && <p className="text-xs text-destructive">{errors.lastName.message}</p>}
              </div>
            </div>

            <div className="grid md:grid-cols-2 gap-5">
              <div className="space-y-2">
                <Label>Email Address</Label>
                <Input type="email" {...register("email")} className={errors.email ? "border-destructive" : ""} />
                {errors.email && <p className="text-xs text-destructive">{errors.email.message}</p>}
              </div>
              <div className="space-y-2">
                <Label>Phone Number</Label>
                <Input {...register("phone")} className={errors.phone ? "border-destructive" : ""} />
                {errors.phone && <p className="text-xs text-destructive">{errors.phone.message}</p>}
              </div>
            </div>

            <div className="grid md:grid-cols-2 gap-5">
              <div className="space-y-2">
                <Label>National ID / Passport (Optional)</Label>
                <Input {...register("nationalId")} />
              </div>
              <div className="space-y-2">
                <Label>Password</Label>
                <Input type="password" {...register("password")} className={errors.password ? "border-destructive" : ""} />
                {errors.password && <p className="text-xs text-destructive">{errors.password.message}</p>}
              </div>
            </div>

            <Button type="submit" className="w-full py-6 text-lg mt-4" isLoading={registerMutation.isPending}>
              Create Account
            </Button>
          </form>

          <div className="mt-8 text-center text-sm text-muted-foreground">
            Already have an account?{' '}
            <Link href="/login" className="font-bold text-primary hover:underline">
              Sign in here
            </Link>
          </div>
        </Card>
      </motion.div>
    </div>
  );
}
