import { useTranslation } from 'react-i18next';

export function Footer() {
  const { t } = useTranslation();

  return (
    <footer className="border-t border-border bg-muted/30 mt-auto">
      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div>
            <h3 className="font-semibold mb-3 text-foreground">AfroKen</h3>
            <p className="text-sm text-muted-foreground">
              {t('home.hero.subtitle')}
            </p>
          </div>

          <div>
            <h3 className="font-semibold mb-3 text-foreground">Quick Links</h3>
            <ul className="space-y-2 text-sm">
              <li>
                <a
                  href="#"
                  className="text-muted-foreground hover:text-primary smooth-transition focus-ring"
                  aria-label={t('footer.privacy')}
                >
                  {t('footer.privacy')}
                </a>
              </li>
              <li>
                <a
                  href="#"
                  className="text-muted-foreground hover:text-primary smooth-transition focus-ring"
                  aria-label={t('footer.terms')}
                >
                  {t('footer.terms')}
                </a>
              </li>
              <li>
                <a
                  href="#"
                  className="text-muted-foreground hover:text-primary smooth-transition focus-ring"
                  aria-label={t('footer.accessibility')}
                >
                  {t('footer.accessibility')}
                </a>
              </li>
              <li>
                <a
                  href="#"
                  className="text-muted-foreground hover:text-primary smooth-transition focus-ring"
                  aria-label={t('footer.openData')}
                >
                  {t('footer.openData')}
                </a>
              </li>
            </ul>
          </div>

          <div>
            <h3 className="font-semibold mb-3 text-foreground">{t('nav.dashboard')}</h3>
            <p className="text-sm text-muted-foreground">
              Ministry of ICT & Digital Economy
            </p>
            <p className="text-sm text-muted-foreground mt-2">
              Powered by AfroKen AI
            </p>
          </div>
        </div>

        <div className="border-t border-border mt-8 pt-6 text-center text-sm text-muted-foreground">
          <p>{t('footer.copyright')}</p>
        </div>
      </div>
    </footer>
  );
}
