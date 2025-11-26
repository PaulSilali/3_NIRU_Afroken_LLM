import { useTranslation } from 'react-i18next';
import heroBackground from '@/assets/hero-background.jpg';

export function Footer() {
  const { t } = useTranslation();

  return (
    <footer className="relative mt-auto border-t border-border overflow-hidden">
      {/* Background image with overlay */}
      <div 
        className="absolute inset-0 bg-cover bg-center bg-no-repeat opacity-20"
        style={{ backgroundImage: `url(${heroBackground})` }}
        aria-hidden="true"
      />
      <div className="absolute inset-0 bg-gradient-to-b from-background/95 via-background/90 to-background/95" aria-hidden="true" />
      
      {/* Kenya flag-inspired accent bar */}
      <div className="relative h-1 w-full bg-[linear-gradient(to_right,#006600_0%,#006600_33%,#ffffff_33%,#ffffff_66%,#bb0000_66%,#bb0000_100%)]" />
      
      <div className="relative container mx-auto px-4 py-12">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 lg:gap-12">
          <div className="relative">
            <h3 className="mb-4 font-display text-xl font-bold text-foreground">
              AfroKen
            </h3>
            <p className="max-w-sm text-sm leading-relaxed text-foreground/80">
              {t('home.hero.subtitle')}
            </p>
          </div>

          <div className="relative">
            <h3 className="mb-4 text-xs font-semibold uppercase tracking-[0.16em] text-foreground">
              Quick Links
            </h3>
            <ul className="space-y-2.5 text-sm">
              <li>
                <a
                  href="/legal/privacy"
                  className="text-foreground/70 hover:text-primary smooth-transition focus-ring inline-block"
                  aria-label={t('footer.privacy')}
                >
                  {t('footer.privacy')}
                </a>
              </li>
              <li>
                <a
                  href="/legal/terms"
                  className="text-foreground/70 hover:text-primary smooth-transition focus-ring inline-block"
                  aria-label={t('footer.terms')}
                >
                  {t('footer.terms')}
                </a>
              </li>
              <li>
                <a
                  href="/accessibility"
                  className="text-foreground/70 hover:text-primary smooth-transition focus-ring inline-block"
                  aria-label={t('footer.accessibility')}
                >
                  {t('footer.accessibility')}
                </a>
              </li>
              <li>
                <a
                  href="/open-data"
                  className="text-foreground/70 hover:text-primary smooth-transition focus-ring inline-block"
                  aria-label={t('footer.openData')}
                >
                  {t('footer.openData')}
                </a>
              </li>
            </ul>
          </div>

          <div className="relative">
            <h3 className="mb-4 text-xs font-semibold uppercase tracking-[0.16em] text-foreground">
              {t('nav.dashboard')}
            </h3>
            <p className="text-sm text-foreground/80 leading-relaxed">
              Ministry of ICT & Digital Economy
            </p>
            <p className="mt-3 text-sm text-foreground/80 leading-relaxed">
              Powered by AfroKen AI
            </p>
          </div>
        </div>

        <div className="relative mt-10 space-y-2 border-t border-border/50 pt-8 text-center">
          <p className="text-sm font-medium text-foreground/90">{t('footer.copyright')}</p>
          <p className="text-sm text-foreground/70">Built for Kenyan citizens 🇰🇪 • Hosted in Kenya-first regions</p>
        </div>
      </div>
    </footer>
  );
}
