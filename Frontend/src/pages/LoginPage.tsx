import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { loginSchema, type LoginFormData } from '@/lib/validation';
import { useAuth } from '@/contexts/AuthContext';
import { toast } from 'sonner';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Shield, Eye, EyeOff } from 'lucide-react';
import nyaradzoLogo from '@/assets/nyaradzo-logo.png';
import { motion } from 'framer-motion';

export default function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const [showPassword, setShowPassword] = useState(false);
  const { login, isLoading, error, fieldErrors, clearError, isAuthenticated } = useAuth();
  const { register, handleSubmit, formState: { errors }, setError, clearErrors } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });

  useEffect(() => {
    if (isLoading) return;
    if (!isAuthenticated) return;
    
    const from = location.state?.from?.pathname || '/dashboard';
    navigate(from, { replace: true });
  }, [isAuthenticated, isLoading, navigate, location.state]);

  // Update form errors when fieldErrors change
  useEffect(() => {
    if (Object.keys(fieldErrors).length > 0) {
      Object.entries(fieldErrors).forEach(([field, messages]) => {
        setError(field as keyof LoginFormData, {
          type: 'manual',
          message: messages[0]
        });
      });
    } else {
      clearErrors();
    }
  }, [fieldErrors, setError, clearErrors]);

  const onSubmit = async (data: LoginFormData) => {
    try {
      clearError();
      await login(data);
      
      toast.success('Login successful!', {
        description: 'Redirecting to dashboard...',
        duration: 2000,
      });
      
      setTimeout(() => {
        const from = location.state?.from?.pathname || '/dashboard';
        navigate(from, { replace: true });
      }, 500);
    } catch (err: any) {
      // Error is already set in AuthContext (error and fieldErrors)
      // Form will display specific field errors or general error message
      // No need to show additional toast for auth failures
      console.log('Auth error caught, displaying in form');
    }
  };

  return (
    <div className="min-h-screen flex">
      {/* Left panel - branding */}
      <div className="hidden lg:flex lg:w-1/2 relative overflow-hidden items-center justify-center" style={{ background: 'var(--gradient-brand)' }}>
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-20 left-20 w-96 h-96 rounded-full bg-accent blur-3xl" />
          <div className="absolute bottom-20 right-20 w-64 h-64 rounded-full bg-accent blur-3xl" />
        </div>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="relative z-10 text-center px-12"
        >
          <img src={nyaradzoLogo} alt="Nyaradzo" className="h-28 w-28 mx-auto mb-8" />
          <h1 className="text-4xl font-display font-bold text-primary-foreground mb-4">Nyaradzo Funeral Assurance</h1>
          <p className="text-primary-foreground/70 text-lg max-w-md mx-auto font-sans">
            Policy Management System — Comprehensive insurance management with AI-powered churn prediction analytics.
          </p>
          <div className="mt-10 flex items-center justify-center gap-6 text-primary-foreground/50 text-sm font-sans">
            <div className="flex items-center gap-2"><Shield className="h-4 w-4" /> Secure</div>
            <div className="w-px h-4 bg-primary-foreground/20" />
            <div>5,000+ Policies</div>
            <div className="w-px h-4 bg-primary-foreground/20" />
            <div>Real-time Analytics</div>
          </div>
        </motion.div>
      </div>

      {/* Right panel - login */}
      <div className="flex-1 flex items-center justify-center p-8 bg-background">
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="w-full max-w-sm"
        >
          <div className="lg:hidden flex items-center gap-3 mb-8">
            <img src={nyaradzoLogo} alt="Nyaradzo" className="h-10 w-10" />
            <h2 className="text-lg font-bold font-display text-foreground">Nyaradzo PMS</h2>
          </div>
          
          <h2 className="text-2xl font-bold font-display text-foreground">Welcome back</h2>
          <p className="text-sm text-muted-foreground mt-1 mb-8">Sign in to your management account</p>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
            <div className="space-y-2">
              <Label htmlFor="email" className="text-sm font-medium">Email Address</Label>
              <Input
                id="email"
                type="email"
                placeholder="admin@nyaradzo.co.zw"
                {...register('email')}
                className={(errors.email || fieldErrors.email) ? 'border-destructive' : ''}
              />
              {errors.email && <p className="text-xs text-destructive">{errors.email.message}</p>}
              {fieldErrors.email && !errors.email && <p className="text-xs text-destructive">{fieldErrors.email[0]}</p>}
            </div>

            <div className="space-y-2">
              <Label htmlFor="password" className="text-sm font-medium">Password</Label>
              <div className="relative">
                <Input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  placeholder="••••••••"
                  {...register('password')}
                  className={(errors.password || fieldErrors.password) ? 'border-destructive pr-10' : 'pr-10'}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                >
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
              {errors.password && <p className="text-xs text-destructive">{errors.password.message}</p>}
              {fieldErrors.password && !errors.password && <p className="text-xs text-destructive">{fieldErrors.password[0]}</p>}
            </div>

            {error && !errors.email && !errors.password && (
              <div className="mt-4 p-3 bg-destructive/10 border border-destructive/30 rounded-md">
                <p className="text-xs text-destructive text-center font-medium">{error}</p>
              </div>
            )}

            {/* 
            <div className="flex items-center justify-between">
              <label className="flex items-center gap-2 text-sm text-muted-foreground cursor-pointer">
                <input type="checkbox" className="rounded border-input" />
                Remember me
              </label>
              <a href="#" className="text-sm text-accent font-medium hover:underline">Forgot password?</a>
            </div>
            */}

            <Button type="submit" className="w-full h-11 bg-primary text-primary-foreground hover:bg-primary/90 font-semibold" disabled={isLoading}>
              {isLoading ? 'Signing in...' : 'Sign In'}
            </Button>
          </form>

          <p className="text-xs text-center text-muted-foreground mt-8">
            © 2025 Nyaradzo Funeral Assurance. All rights reserved.
          </p>
        </motion.div>
      </div>
    </div>
  );
}
