import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Menu, X } from 'lucide-react';
import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { LanguageSwitcher } from './LanguageSwitcher';
import { NavLink } from '@/components/NavLink';

export function Header() {
  const { t } = useTranslation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <header className="border-b border-border/50 glass-effect sticky top-0 z-50 shadow-elegant">
      <nav className="container mx-auto px-4 h-20 flex items-center justify-between" role="navigation" aria-label="Main navigation">
        <div className="flex items-center gap-8">
          <Link to="/" className="flex items-center gap-3 focus-ring rounded group" aria-label="AfroKen home">
            <div className="w-11 h-11 rounded-2xl gradient-primary flex items-center justify-center shadow-lg group-hover:shadow-glow group-hover:scale-110 transition-all duration-300">
              <span className="text-white font-bold text-2xl">A</span>
            </div>
            <span className="font-display font-bold text-2xl hidden sm:inline bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">AfroKen</span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-6">
            <NavLink
              to="/"
              end
              className="text-sm font-medium text-muted-foreground hover:text-primary smooth-transition focus-ring px-3 py-2 rounded-lg hover:bg-primary/5"
              activeClassName="text-primary bg-primary/10"
            >
              {t('nav.home')}
            </NavLink>
            <NavLink
              to="/services"
              className="text-sm font-medium text-muted-foreground hover:text-primary smooth-transition focus-ring px-3 py-2 rounded-lg hover:bg-primary/5"
              activeClassName="text-primary bg-primary/10"
            >
              Services
            </NavLink>
            <NavLink
              to="/about"
              className="text-sm font-medium text-muted-foreground hover:text-primary smooth-transition focus-ring px-3 py-2 rounded-lg hover:bg-primary/5"
              activeClassName="text-primary bg-primary/10"
            >
              {t('nav.about')}
            </NavLink>
            <NavLink
              to="/dashboard"
              className="text-sm font-medium text-muted-foreground hover:text-primary smooth-transition focus-ring px-3 py-2 rounded-lg hover:bg-primary/5"
              activeClassName="text-primary bg-primary/10"
            >
              {t('nav.dashboard')}
            </NavLink>
            <NavLink
              to="/settings"
              className="text-sm font-medium text-muted-foreground hover:text-primary smooth-transition focus-ring px-3 py-2 rounded-lg hover:bg-primary/5"
              activeClassName="text-primary bg-primary/10"
            >
              {t('nav.settings')}
            </NavLink>
          </div>
        </div>

        <div className="flex items-center gap-4">
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
          <div className="md:hidden border-t border-border bg-background" role="navigation" aria-label="Mobile navigation">
            <div className="container mx-auto px-4 py-4 flex flex-col gap-4">
              <NavLink
                to="/"
                end
                className="text-sm font-medium text-muted-foreground hover:text-foreground smooth-transition focus-ring"
                activeClassName="text-foreground"
                onClick={() => setMobileMenuOpen(false)}
              >
                {t('nav.home')}
              </NavLink>
              <NavLink
                to="/services"
                className="text-sm font-medium text-muted-foreground hover:text-foreground smooth-transition focus-ring"
                activeClassName="text-foreground"
                onClick={() => setMobileMenuOpen(false)}
              >
                Services
              </NavLink>
              <NavLink
                to="/about"
                className="text-sm font-medium text-muted-foreground hover:text-foreground smooth-transition focus-ring"
                activeClassName="text-foreground"
                onClick={() => setMobileMenuOpen(false)}
              >
                {t('nav.about')}
              </NavLink>
              <NavLink
                to="/dashboard"
                className="text-sm font-medium text-muted-foreground hover:text-foreground smooth-transition focus-ring"
                activeClassName="text-foreground"
                onClick={() => setMobileMenuOpen(false)}
              >
                {t('nav.dashboard')}
              </NavLink>
              <NavLink
                to="/settings"
                className="text-sm font-medium text-muted-foreground hover:text-foreground smooth-transition focus-ring"
                activeClassName="text-foreground"
                onClick={() => setMobileMenuOpen(false)}
              >
                {t('nav.settings')}
              </NavLink>
            </div>
          </div>
        )}
    </header>
  );
}
