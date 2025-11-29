import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Eye, EyeOff, LogIn } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';
import { Card } from '@/components/ui/card';
import { toast } from 'sonner';
import { Header } from '@/components/Header';
import { Footer } from '@/components/Footer';

export default function Login() {
  const navigate = useNavigate();
  const [showPassword, setShowPassword] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleDemoLogin = () => {
    setEmail('admin@afroken.go.ke');
    setPassword('AdminPass#2025');
    toast.info('Demo credentials filled. Click Sign in to continue.');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    // Simulate login (replace with actual API call)
    setTimeout(() => {
      // For demo, accept any credentials or demo credentials
      if (
        (email === 'admin@afroken.go.ke' && password === 'AdminPass#2025') ||
        email.includes('@') && password.length > 0
      ) {
        toast.success('Login successful! Redirecting to admin dashboard...');
        // Store auth token (in real app, get from API)
        localStorage.setItem('authToken', 'demo-token');
        localStorage.setItem('userEmail', email);
        navigate('/admin');
      } else {
        toast.error('Invalid credentials. Please try again.');
      }
      setIsLoading(false);
    }, 1000);
  };

  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-br from-background via-muted/20 to-background">
      <Header />
      
      <div className="flex-1 flex items-center justify-center p-4">
        <div className="sm:mx-auto sm:w-full sm:max-w-6xl w-full">
        <div className="text-center mb-10">
          <div className="mx-auto h-24 w-24 flex items-center justify-center rounded-2xl bg-gradient-to-br from-primary to-accent shadow-lg mb-4">
            <span className="font-display text-4xl font-bold text-white">A</span>
          </div>
          <h1 className="mt-6 text-center text-3xl font-bold text-foreground">
            Welcome to AfroKen LLM
          </h1>
          <p className="mt-2 text-muted-foreground">Admin Portal</p>
        </div>

        <div className="mt-4 flex justify-center px-4 sm:px-0">
          <div className="relative bg-card rounded-lg shadow-lg p-8 w-full max-w-md border border-border">
            {/* Demo Credentials Sticker */}
            <div className="hidden md:block absolute rotate-2 transform" style={{ top: '50%', right: '-150px', transform: 'translateY(-50%) rotate(2deg)' }}>
              <div className="bg-amber-50 dark:bg-amber-950 border border-amber-300 dark:border-amber-700 rounded-xl shadow-md px-4 py-3 text-sm text-amber-900 dark:text-amber-100">
                <p className="font-semibold uppercase text-xs tracking-wide text-amber-700 dark:text-amber-300">
                  Demo Admin
                </p>
                <p className="mt-1 font-mono text-xs">admin@afroken.go.ke</p>
                <p className="font-mono text-xs">AdminPass#2025</p>
                <button
                  type="button"
                  onClick={handleDemoLogin}
                  className="mt-2 w-full rounded-md bg-amber-600 hover:bg-amber-700 text-white text-xs font-semibold py-1 transition-colors"
                >
                  Use Demo Login
                </button>
              </div>
            </div>

            <div className="text-center mb-6">
              <h2 className="text-2xl font-semibold text-foreground">Please Login</h2>
              <p className="mt-2 text-sm text-muted-foreground">
                to Manage your System
              </p>
            </div>

            <form className="space-y-6" onSubmit={handleSubmit}>
              <div className="space-y-2">
                <Label htmlFor="email">Email Address</Label>
                <Input
                  type="email"
                  id="email"
                  name="email"
                  placeholder="Enter your email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="w-full"
                />
              </div>

              <div className="space-y-2 relative">
                <Label htmlFor="password">Password</Label>
                <Input
                  type={showPassword ? 'text' : 'password'}
                  id="password"
                  name="password"
                  placeholder="Enter your password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="w-full pr-10"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center pt-7 text-muted-foreground hover:text-foreground"
                >
                  {showPassword ? (
                    <EyeOff className="h-5 w-5" />
                  ) : (
                    <Eye className="h-5 w-5" />
                  )}
                </button>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="remember"
                    checked={rememberMe}
                    onCheckedChange={(checked) => setRememberMe(checked as boolean)}
                  />
                  <Label htmlFor="remember" className="text-sm font-medium cursor-pointer">
                    Remember me
                  </Label>
                </div>
                <a
                  href="/forgot-password"
                  className="text-sm font-medium text-primary hover:underline"
                >
                  Forgot password?
                </a>
              </div>

              <Button
                type="submit"
                className="w-full"
                disabled={isLoading}
              >
                {isLoading ? (
                  'Signing in...'
                ) : (
                  <>
                    <LogIn className="w-4 h-4" />
                    Sign in
                  </>
                )}
              </Button>

              <p className="text-center text-sm text-muted-foreground">
                Don't have an account?{' '}
                <a href="/register" className="font-medium text-primary hover:underline">
                  Contact Administrator
                </a>
              </p>
            </form>
          </div>
        </div>
        </div>
      </div>
      
      <Footer />
    </div>
  );
}

