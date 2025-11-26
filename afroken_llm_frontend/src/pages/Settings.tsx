import { useTranslation } from 'react-i18next';
import { Header } from '@/components/Header';
import { Footer } from '@/components/Footer';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Language } from '@/types';
import { useChatStore } from '@/store/chatStore';
import { toast } from 'sonner';

export default function Settings() {
  const { t, i18n } = useTranslation();
  const { language, setLanguage } = useChatStore();

  const handleLanguageChange = (lang: Language) => {
    i18n.changeLanguage(lang);
    setLanguage(lang);
    toast.success('Language updated');
  };

  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      
      <main className="flex-1 container mx-auto px-4 py-8">
        <div className="max-w-2xl mx-auto space-y-8">
          <div>
            <h1 className="text-3xl font-bold mb-2">{t('settings.title')}</h1>
            <p className="text-muted-foreground">
              Manage your preferences and accessibility options
            </p>
          </div>

          {/* Language Settings */}
          <Card>
            <CardHeader>
              <CardTitle>{t('settings.language.title')}</CardTitle>
              <CardDescription>{t('settings.language.description')}</CardDescription>
            </CardHeader>
            <CardContent>
              <RadioGroup value={language} onValueChange={(value) => handleLanguageChange(value as Language)}>
                <div className="flex items-center space-x-2 p-3 rounded-lg hover:bg-muted/50 smooth-transition">
                  <RadioGroupItem value="en" id="lang-en" />
                  <Label htmlFor="lang-en" className="flex-1 cursor-pointer">
                    <div>
                      <p className="font-medium">English</p>
                      <p className="text-sm text-muted-foreground">Use English for all interactions</p>
                    </div>
                  </Label>
                </div>
                <div className="flex items-center space-x-2 p-3 rounded-lg hover:bg-muted/50 smooth-transition">
                  <RadioGroupItem value="sw" id="lang-sw" />
                  <Label htmlFor="lang-sw" className="flex-1 cursor-pointer">
                    <div>
                      <p className="font-medium">Kiswahili</p>
                      <p className="text-sm text-muted-foreground">Tumia Kiswahili kwa mazungumzo yote</p>
                    </div>
                  </Label>
                </div>
                <div className="flex items-center space-x-2 p-3 rounded-lg hover:bg-muted/50 smooth-transition">
                  <RadioGroupItem value="sheng" id="lang-sheng" />
                  <Label htmlFor="lang-sheng" className="flex-1 cursor-pointer">
                    <div>
                      <p className="font-medium">Sheng</p>
                      <p className="text-sm text-muted-foreground">Tumia Sheng kwa conversation zote</p>
                    </div>
                  </Label>
                </div>
              </RadioGroup>
            </CardContent>
          </Card>

          {/* Accessibility Settings */}
          <Card>
            <CardHeader>
              <CardTitle>{t('settings.accessibility.title')}</CardTitle>
              <CardDescription>Enhance your experience with accessibility features</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label htmlFor="high-contrast">{t('settings.accessibility.highContrast')}</Label>
                  <p className="text-sm text-muted-foreground">
                    Increase contrast for better visibility
                  </p>
                </div>
                <Switch
                  id="high-contrast"
                  onCheckedChange={(checked) => {
                    toast.info(checked ? 'High contrast enabled' : 'High contrast disabled');
                  }}
                />
              </div>
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label htmlFor="large-text">{t('settings.accessibility.largeText')}</Label>
                  <p className="text-sm text-muted-foreground">
                    Use larger text throughout the application
                  </p>
                </div>
                <Switch
                  id="large-text"
                  onCheckedChange={(checked) => {
                    toast.info(checked ? 'Large text enabled' : 'Large text disabled');
                  }}
                />
              </div>
            </CardContent>
          </Card>

          {/* Information Card */}
          <Card>
            <CardHeader>
              <CardTitle>About AfroKen</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-muted-foreground">
                AfroKen is an AI-powered citizen service copilot designed to help Kenyan citizens access
                government services more easily. Built with accessibility and multilingual support at its core.
              </p>
              <div className="pt-4 border-t border-border">
                <p className="text-xs text-muted-foreground">Version 1.0.0</p>
                <p className="text-xs text-muted-foreground">© 2025 Ministry of ICT & Digital Economy</p>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>

      <Footer />
    </div>
  );
}
