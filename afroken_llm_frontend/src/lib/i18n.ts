import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

// Import translations
import enTranslation from '../locales/en/translation.json';
import swTranslation from '../locales/sw/translation.json';
import shengTranslation from '../locales/sheng/translation.json';

const resources = {
  en: { translation: enTranslation },
  sw: { translation: swTranslation },
  sheng: { translation: shengTranslation },
};

i18n
  .use(initReactI18next)
  .init({
    resources,
    lng: localStorage.getItem('language') || 'en',
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false,
    },
  });

export default i18n;
