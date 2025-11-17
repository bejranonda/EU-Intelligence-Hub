/**
 * i18n configuration for multi-language support
 */
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import enTranslations from './locales/en.json';
import thTranslations from './locales/th.json';
import deTranslations from './locales/de.json';
import daTranslations from './locales/da.json';

// Initialize i18next
i18n
  .use(initReactI18next) // passes i18n down to react-i18next
  .init({
    resources: {
      en: {
        translation: enTranslations,
      },
      th: {
        translation: thTranslations,
      },
      de: {
        translation: deTranslations,
      },
      da: {
        translation: daTranslations,
      },
    },
    lng: 'en', // default language
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false, // react already safes from xss
    },
  });

export default i18n;
