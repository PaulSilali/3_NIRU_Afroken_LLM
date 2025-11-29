import { Link, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Menu, X, Sparkles, LogIn } from 'lucide-react';
import { useEffect, useState } from 'react';
import { Button } from '@/components/ui/button';
import { LanguageSwitcher } from './LanguageSwitcher';
import { NavLink } from '@/components/NavLink';
import { ThemeToggle } from '@/components/ThemeToggle';

export function Header() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);
  const isAuthenticated = !!localStorage.getItem('authToken');

  useEffect(() => {
    if (typeof window === 'undefined') return;
    const onScroll = () => {
      setIsScrolled(window.scrollY > 12);
    };
    window.addEventListener('scroll', onScroll);
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  return (
    <header
      className={`sticky top-0 z-50 border-b border-border/50 bg-background/80 backdrop-blur-xl transition-all duration-300 ${
        isScrolled ? 'shadow-elegant bg-background/95' : ''
      }`}
    >
      <nav
        className={`container mx-auto flex items-center justify-between px-4 transition-all duration-300 ${
          isScrolled ? 'h-16' : 'h-20'
        }`}
        role="navigation"
        aria-label="Main navigation"
      >
        <div className="flex items-center gap-8">
          <Link
            to="/"
            className="group flex items-center gap-3 rounded-full px-2 py-1 focus-ring"
            aria-label="AfroKen home"
          >
            <div className="relative flex h-11 w-11 items-center justify-center rounded-2xl bg-gradient-to-br from-primary to-accent shadow-lg transition-all duration-300 group-hover:shadow-glow group-hover:scale-110">
              <span className="font-display text-2xl font-bold text-white">A</span>
              <Sparkles className="absolute -right-1 -top-1 h-4 w-4 text-amber-300 drop-shadow-sm" />
            </div>
            <div className="flex flex-col">
              <span className="hidden font-display text-xl font-semibold tracking-tight text-foreground sm:inline">
                AfroKen
              </span>
              <span className="hidden text-[0.65rem] font-semibold uppercase tracking-[0.18em] text-muted-foreground/80 sm:inline">
                Citizen Service Copilot
              </span>
            </div>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden h-8 w-px bg-border/60 md:block" aria-hidden="true" />

          <div className="hidden items-center gap-2 rounded-full bg-muted/40 px-2 py-1 shadow-sm ring-1 ring-border/40 md:flex">
            <NavLink
              to="/"
              end
              className="smooth-transition relative rounded-full px-4 py-2 text-sm font-medium text-muted-foreground hover:bg-background hover:text-primary focus-ring"
              activeClassName="bg-background text-primary shadow-xs after:absolute after:left-4 after:right-4 after:-bottom-1 after:h-0.5 after:rounded-full after:bg-primary"
            >
              {t('nav.home')}
            </NavLink>
            <NavLink
              to="/services"
              className="smooth-transition relative rounded-full px-4 py-2 text-sm font-medium text-muted-foreground hover:bg-background hover:text-primary focus-ring"
              activeClassName="bg-background text-primary shadow-xs after:absolute after:left-4 after:right-4 after:-bottom-1 after:h-0.5 after:rounded-full after:bg-primary"
            >
              Services
            </NavLink>
            <NavLink
              to="/about"
              className="smooth-transition relative rounded-full px-4 py-2 text-sm font-medium text-muted-foreground hover:bg-background hover:text-primary focus-ring"
              activeClassName="bg-background text-primary shadow-xs after:absolute after:left-4 after:right-4 after:-bottom-1 after:h-0.5 after:rounded-full after:bg-primary"
            >
              {t('nav.about')}
            </NavLink>
            <NavLink
              to="/dashboard"
              className="smooth-transition relative rounded-full px-4 py-2 text-sm font-medium text-muted-foreground hover:bg-background hover:text-primary focus-ring"
              activeClassName="bg-background text-primary shadow-xs after:absolute after:left-4 after:right-4 after:-bottom-1 after:h-0.5 after:rounded-full after:bg-primary"
            >
              {t('nav.dashboard')}
            </NavLink>
            <NavLink
              to="/settings"
              className="smooth-transition relative rounded-full px-4 py-2 text-sm font-medium text-muted-foreground hover:bg-background hover:text-primary focus-ring"
              activeClassName="bg-background text-primary shadow-xs after:absolute after:left-4 after:right-4 after:-bottom-1 after:h-0.5 after:rounded-full after:bg-primary"
            >
              {t('nav.settings')}
            </NavLink>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {/* Login/Admin Button - positioned before theme toggle */}
          {isAuthenticated ? (
            <Button
              variant="outline"
              size="sm"
              onClick={() => navigate('/admin')}
              className="hidden md:flex gap-2"
            >
              <Sparkles className="w-4 h-4" />
              Admin
            </Button>
          ) : (
            <Button
              variant="outline"
              size="icon"
              onClick={() => navigate('/login')}
              className="focus-ring"
              aria-label="Login"
            >
              <LogIn className="h-5 w-5" />
            </Button>
          )}
          
          <ThemeToggle />
          <LanguageSwitcher />

          {/* Mobile menu button */}
          <Button
            variant="ghost"
            size="icon"
            className="md:hidden focus-ring"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-label={mobileMenuOpen ? 'Close menu' : 'Open menu'}
            aria-expanded={mobileMenuOpen}
          >
            {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </Button>
        </div>
      </nav>

      {/* Mobile Navigation */}
      {mobileMenuOpen && (
        <div
          className="border-t border-border bg-background/95 shadow-sm md:hidden"
          role="navigation"
          aria-label="Mobile navigation"
        >
          <div className="container mx-auto flex flex-col gap-2 px-4 py-4">
            <NavLink
              to="/"
              end
              className="smooth-transition rounded-lg px-3 py-2 text-sm font-medium text-muted-foreground hover:bg-muted hover:text-foreground focus-ring"
              activeClassName="bg-muted text-foreground"
              onClick={() => setMobileMenuOpen(false)}
            >
              {t('nav.home')}
            </NavLink>
            <NavLink
              to="/services"
              className="smooth-transition rounded-lg px-3 py-2 text-sm font-medium text-muted-foreground hover:bg-muted hover:text-foreground focus-ring"
              activeClassName="bg-muted text-foreground"
              onClick={() => setMobileMenuOpen(false)}
            >
              Services
            </NavLink>
            <NavLink
              to="/about"
              className="smooth-transition rounded-lg px-3 py-2 text-sm font-medium text-muted-foreground hover:bg-muted hover:text-foreground focus-ring"
              activeClassName="bg-muted text-foreground"
              onClick={() => setMobileMenuOpen(false)}
            >
              {t('nav.about')}
            </NavLink>
            <NavLink
              to="/dashboard"
              className="smooth-transition rounded-lg px-3 py-2 text-sm font-medium text-muted-foreground hover:bg-muted hover:text-foreground focus-ring"
              activeClassName="bg-muted text-foreground"
              onClick={() => setMobileMenuOpen(false)}
            >
              {t('nav.dashboard')}
            </NavLink>
            <NavLink
              to="/settings"
              className="smooth-transition rounded-lg px-3 py-2 text-sm font-medium text-muted-foreground hover:bg-muted hover:text-foreground focus-ring"
              activeClassName="bg-muted text-foreground"
              onClick={() => setMobileMenuOpen(false)}
            >
              {t('nav.settings')}
            </NavLink>
            {!isAuthenticated && (
              <Button
                variant="outline"
                className="w-full justify-start gap-2"
                onClick={() => {
                  setMobileMenuOpen(false);
                  navigate('/login');
                }}
              >
                <LogIn className="w-4 h-4" />
                Login
              </Button>
            )}
            {isAuthenticated && (
              <Button
                variant="outline"
                className="w-full justify-start gap-2"
                onClick={() => {
                  setMobileMenuOpen(false);
                  navigate('/admin');
                }}
              >
                <Sparkles className="w-4 h-4" />
                Admin Dashboard
              </Button>
            )}
          </div>
        </div>
      )}
    </header>
  );
}
