/**
 * Language state management using Zustand
 */
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { Language } from '../types';

interface LanguageState {
  language: Language;
  setLanguage: (language: Language) => void;
  toggleLanguage: () => void;
}

export const useLanguageStore = create<LanguageState>()(
  persist(
    (set) => ({
      language: 'en',
      setLanguage: (language) => set({ language }),
      toggleLanguage: () =>
        set((state) => ({
          language: state.language === 'en' ? 'th' : 'en',
        })),
    }),
    {
      name: 'language-storage',
    }
  )
);
