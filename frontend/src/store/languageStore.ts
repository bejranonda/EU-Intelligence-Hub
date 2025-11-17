/**
 * Language state management using Zustand
 */
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { Language } from '../types';
import i18n from '../i18n/config';

interface LanguageState {
  language: Language;
  setLanguage: (language: Language) => void;
}

export const useLanguageStore = create<LanguageState>()(
  persist(
    (set) => ({
      language: 'en',
      setLanguage: (language) => {
        set({ language });
        // Sync with i18next
        i18n.changeLanguage(language);
      },
    }),
    {
      name: 'language-storage',
    }
  )
);
