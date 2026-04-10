/**
 * Professional App Layout - Main application shell
 * Clean, modern design with proper navigation structure
 */
import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'wouter';
import { 
  LayoutDashboard, 
  GraduationCap, 
  Briefcase, 
  User, 
  LogOut,
  Menu,
  X,
  Phone,
  Mail,
  MapPin
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

import { KIU_CONTACT } from '@/shared/config/contact';
import { useAuth } from '@/features/auth/hooks/useAuth';
import { Button } from '@/shared/components/ui/Button';
import { Avatar } from '@/shared/components/ui/Avatar';

interface NavItem {
  label: string;
  path: string;
  icon: React.ReactNode;
  roles: string[];
}

const navigation: NavItem[] = [
  { label: 'Dashboard', path: '/dashboard', icon: <LayoutDashboard className="w-5 h-5" />, roles: ['applicant'] },
  { label: 'Apply', path: '/apply', icon: <GraduationCap className="w-5 h-5" />, roles: ['applicant'] },
  { label: 'Career', path: '/career', icon: <Briefcase className="w-5 h-5" />, roles: ['finalist'] },
  { label: 'Profile', path: '/profile', icon: <User className="w-5 h-5" />, roles: ['applicant', 'finalist', 'admin'] },
];

export const AppLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [location] = useLocation();
  const { user, logout, isAuthenticated } = useAuth();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);

  // Track scroll for header styling
  useEffect(() => {
    const handleScroll = () => setIsScrolled(window.scrollY > 10);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Close mobile menu on route change
  useEffect(() => {
    setIsMobileMenuOpen(false);
  }, [location]);

  const userNavItems = navigation.filter(item => user && item.roles.includes(user.role));

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      {/* Professional Header */}
      <header 
        className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
          isScrolled 
            ? 'bg-white/95 backdrop-blur-md shadow-sm border-b border-slate-200' 
            : 'bg-white border-b border-slate-100'
        }`}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <Link href="/" className="flex items-center gap-3 group">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-indigo-700 rounded-xl flex items-center justify-center shadow-lg group-hover:shadow-xl transition-shadow">
                <span className="text-white font-bold text-lg">K</span>
              </div>
              <div className="hidden sm:block">
                <h1 className="text-lg font-bold text-slate-900 leading-tight">
                  {KIU_CONTACT.shortName}
                </h1>
                <p className="text-xs text-slate-500">Admission Portal</p>
              </div>
            </Link>

            {/* Desktop Navigation */}
            <nav className="hidden md:flex items-center gap-1">
              {userNavItems.map((item) => (
                <Link
                  key={item.path}
                  href={item.path}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                    location === item.path
                      ? 'bg-blue-50 text-blue-700'
                      : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
                  }`}
                >
                  {item.icon}
                  {item.label}
                </Link>
              ))}
            </nav>

            {/* User Menu */}
            <div className="flex items-center gap-3">
              {isAuthenticated && user ? (
                <>
                  <div className="hidden sm:flex items-center gap-3">
                    <div className="text-right">
                      <p className="text-sm font-medium text-slate-900">{user.full_name}</p>
                      <p className="text-xs text-slate-500 capitalize">{user.role}</p>
                    </div>
                    <Avatar name={user.full_name} className="w-9 h-9" />
                  </div>
                  <Button 
                    variant="ghost" 
                    size="sm" 
                    onClick={logout}
                    className="text-slate-500 hover:text-red-600"
                  >
                    <LogOut className="w-5 h-5" />
                  </Button>
                </>
              ) : (
                <div className="flex items-center gap-2">
                  <Link href="/login">
                    <Button variant="ghost" size="sm">Sign In</Button>
                  </Link>
                  <Link href="/register">
                    <Button size="sm" className="bg-blue-600 hover:bg-blue-700">Get Started</Button>
                  </Link>
                </div>
              )}

              {/* Mobile Menu Toggle */}
              <button
                onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                className="md:hidden p-2 text-slate-600 hover:bg-slate-100 rounded-lg"
              >
                {isMobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
              </button>
            </div>
          </div>
        </div>

        {/* Mobile Navigation */}
        <AnimatePresence>
          {isMobileMenuOpen && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="md:hidden border-t border-slate-100 bg-white"
            >
              <div className="px-4 py-3 space-y-1">
                {userNavItems.map((item) => (
                  <Link
                    key={item.path}
                    href={item.path}
                    className={`flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium ${
                      location === item.path
                        ? 'bg-blue-50 text-blue-700'
                        : 'text-slate-600 hover:bg-slate-50'
                    }`}
                  >
                    {item.icon}
                    {item.label}
                  </Link>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </header>

      {/* Main Content */}
      <main className="flex-1 pt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {children}
        </div>
      </main>

      {/* Professional Footer */}
      <footer className="bg-slate-900 text-slate-300">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            {/* Brand */}
            <div className="col-span-1 md:col-span-1">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center">
                  <span className="text-white font-bold text-lg">K</span>
                </div>
                <span className="text-white font-bold text-lg">{KIU_CONTACT.shortName}</span>
              </div>
              <p className="text-sm text-slate-400 leading-relaxed">
                {KIU_CONTACT.fullName} - Empowering the next generation of leaders through quality education.
              </p>
            </div>

            {/* Quick Links */}
            <div>
              <h4 className="text-white font-semibold mb-4">Quick Links</h4>
              <ul className="space-y-2 text-sm">
                <li><Link href="/" className="hover:text-white transition-colors">Home</Link></li>
                <li><Link href="/programs" className="hover:text-white transition-colors">Programs</Link></li>
                <li><Link href="/apply" className="hover:text-white transition-colors">Apply Now</Link></li>
                <li><a href={KIU_CONTACT.website} target="_blank" rel="noopener" className="hover:text-white transition-colors">Main Website</a></li>
              </ul>
            </div>

            {/* Resources */}
            <div>
              <h4 className="text-white font-semibold mb-4">Resources</h4>
              <ul className="space-y-2 text-sm">
                <li><Link href="/fees" className="hover:text-white transition-colors">Fee Structure</Link></li>
                <li><Link href="/requirements" className="hover:text-white transition-colors">Entry Requirements</Link></li>
                <li><Link href="/faq" className="hover:text-white transition-colors">FAQs</Link></li>
                <li><Link href="/contact" className="hover:text-white transition-colors">Contact Us</Link></li>
              </ul>
            </div>

            {/* Contact Info */}
            <div>
              <h4 className="text-white font-semibold mb-4">Contact</h4>
              <ul className="space-y-3 text-sm">
                <li className="flex items-start gap-3">
                  <MapPin className="w-5 h-5 text-blue-400 shrink-0 mt-0.5" />
                  <span>{KIU_CONTACT.mainCampus.location}</span>
                </li>
                <li className="flex items-center gap-3">
                  <Phone className="w-5 h-5 text-blue-400 shrink-0" />
                  <a href={`tel:${KIU_CONTACT.phone}`} className="hover:text-white transition-colors">
                    {KIU_CONTACT.phone}
                  </a>
                </li>
                <li className="flex items-center gap-3">
                  <Mail className="w-5 h-5 text-blue-400 shrink-0" />
                  <a href={`mailto:${KIU_CONTACT.email}`} className="hover:text-white transition-colors">
                    {KIU_CONTACT.email}
                  </a>
                </li>
              </ul>
            </div>
          </div>

          {/* Bottom Bar */}
          <div className="mt-12 pt-8 border-t border-slate-800 flex flex-col md:flex-row justify-between items-center gap-4">
            <p className="text-sm text-slate-500">
              &copy; {new Date().getFullYear()} {KIU_CONTACT.fullName}. All rights reserved.
            </p>
            <div className="flex items-center gap-6 text-sm text-slate-500">
              <Link href="/privacy" className="hover:text-slate-300 transition-colors">Privacy Policy</Link>
              <Link href="/terms" className="hover:text-slate-300 transition-colors">Terms of Service</Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};
