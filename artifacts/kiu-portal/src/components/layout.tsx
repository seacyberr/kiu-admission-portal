import React, { useEffect, useState } from 'react';
import { Link, useLocation } from 'wouter';
import { useGetCurrentUser } from '@workspace/api-client-react';
import { LogOut, Menu, UserCircle, X, ChevronRight, GraduationCap, Building2 } from 'lucide-react';
import { Button } from './ui/shared';
import { motion, AnimatePresence } from 'framer-motion';

export function Layout({ children }: { children: React.ReactNode }) {
  const [location, setLocation] = useLocation();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const { data: user, isLoading } = useGetCurrentUser({ query: { retry: false } });

  // Close mobile menu on route change
  useEffect(() => {
    setIsMobileMenuOpen(false);
  }, [location]);

  const handleLogout = () => {
    localStorage.removeItem('kiu_token');
    localStorage.removeItem('kiu_user');
    window.location.href = '/login';
  };

  const getNavLinks = () => {
    if (!user) return [];
    if (user.role === 'admin') {
      return [
        { label: 'Dashboard', path: '/admin' },
        { label: 'Admissions', path: '/admin/admissions' },
        { label: 'Opportunities', path: '/admin/opportunities' },
      ];
    }
    if (user.role === 'finalist') {
      return [
        { label: 'Career Dashboard', path: '/career' },
        { label: 'Career Paths', path: '/career/paths' },
        { label: 'Opportunities', path: '/career/opportunities' },
      ];
    }
    return [
      { label: 'Admission Dashboard', path: '/dashboard' },
      { label: 'My Application', path: '/apply' },
    ];
  };

  const links = getNavLinks();

  return (
    <div className="min-h-screen flex flex-col bg-background selection:bg-accent/20">
      {/* Navbar */}
      <header className="sticky top-0 z-50 w-full border-b border-border/40 bg-white/80 backdrop-blur-xl transition-all">
        <div className="relative h-20 flex items-center">
          <Link href="/" className="absolute left-4 top-0 flex items-center gap-3 group pl-0">
            <div className="relative w-20 h-20 flex items-center justify-center overflow-hidden group-hover:scale-105 transition-transform">
              <img src={`${import.meta.env.BASE_URL}images/logo.png`} alt="KIU Logo" className="w-20 h-20 object-contain z-10" />
            </div>
            <div className="flex flex-col">
              <span className="text-[10px] uppercase tracking-wider text-muted-foreground font-semibold">Admissions & Careers</span>
            </div>
          </Link>

          {/* Desktop Nav */}
          <nav className="hidden md:flex items-center gap-8 absolute left-1/2 transform -translate-x-1/2">
            {links.map((link) => (
              <Link key={link.path} href={link.path} className={`text-sm font-semibold transition-colors hover:text-primary ${location === link.path ? 'text-primary' : 'text-muted-foreground'}`}>
                {link.label}
              </Link>
            ))}
          </nav>

          <div className="hidden md:flex items-center gap-4 absolute right-0 top-0 h-full">
            {!isLoading && !user && (
              <>
                <Link href="/login" className="text-sm font-semibold text-primary hover:text-primary/80 transition-colors">Sign In</Link>
                <Link href="/register">
                  <Button variant="accent" size="sm" className="rounded-full px-6">Apply Now</Button>
                </Link>
              </>
            )}
            {user && (
              <div className="flex items-center gap-4 border-l border-border pl-4">
                <div className="flex flex-col text-right">
                  <span className="text-sm font-bold text-foreground leading-none">{user.firstName} {user.lastName}</span>
                  <span className="text-xs text-muted-foreground capitalize">{user.role}</span>
                </div>
                <Button variant="ghost" size="icon" className="rounded-full bg-secondary text-secondary-foreground hover:bg-destructive/10 hover:text-destructive transition-colors" onClick={handleLogout} title="Logout">
                  <LogOut className="w-4 h-4" />
                </Button>
              </div>
            )}
          </div>

          {/* Mobile Menu Toggle */}
          <button className="md:hidden p-2 text-foreground" onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}>
            {isMobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
      </header>

      {/* Mobile Menu */}
      <AnimatePresence>
        {isMobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="md:hidden fixed inset-x-0 top-20 bg-background border-b border-border shadow-2xl z-40"
          >
            <div className="p-4 flex flex-col gap-2">
              {links.map((link) => (
                <Link key={link.path} href={link.path} className={`p-4 rounded-xl text-base font-semibold ${location === link.path ? 'bg-primary/10 text-primary' : 'text-foreground hover:bg-secondary'}`}>
                  {link.label}
                </Link>
              ))}
              {!user && (
                <div className="grid grid-cols-2 gap-4 mt-4 pt-4 border-t border-border">
                  <Link href="/login"><Button variant="outline" className="w-full">Sign In</Button></Link>
                  <Link href="/register"><Button variant="accent" className="w-full">Apply Now</Button></Link>
                </div>
              )}
              {user && (
                <Button variant="destructive" className="w-full mt-4" onClick={handleLogout}>Log Out</Button>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Content */}
      <main className="flex-1 w-full relative">
        {children}
      </main>

      {/* Footer */}
      <footer className="bg-primary text-primary-foreground py-12 mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 grid grid-cols-1 md:grid-cols-4 gap-8">
          <div className="col-span-1 md:col-span-2 space-y-4">
            <p className="text-primary-foreground/70 max-w-sm text-sm">
              Empowering the next generation of leaders. The KIU Portal manages both new admissions and finalist career opportunities in one unified platform.
            </p>
          </div>
          <div>
            <h4 className="font-bold mb-4 text-accent">Quick Links</h4>
            <ul className="space-y-2 text-sm text-primary-foreground/80">
              <li><Link href="/" className="hover:text-white transition-colors">Home</Link></li>
              <li><Link href="/register" className="hover:text-white transition-colors">Admissions</Link></li>
              <li><Link href="/login" className="hover:text-white transition-colors">Student Login</Link></li>
            </ul>
          </div>
          <div>
            <h4 className="font-bold mb-4 text-accent">Contact</h4>
            <ul className="space-y-2 text-sm text-primary-foreground/80">
              <li>Kansanga, Kampala, Uganda</li>
              <li>admissions@kiu.ac.ug</li>
              <li>+256 000 000 000</li>
            </ul>
          </div>
        </div>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-12 pt-8 border-t border-primary-foreground/10 text-xs text-primary-foreground/50 flex flex-col md:flex-row justify-between items-center">
          <p>© {new Date().getFullYear()} Kampala International University. All rights reserved.</p>
          <div className="flex gap-4 mt-4 md:mt-0">
            <span>Privacy Policy</span>
            <span>Terms of Service</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
