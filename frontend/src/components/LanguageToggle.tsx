/**
 * Language toggle component
 */
import { Globe } from 'lucide-react';
import { Button } from './ui/button';
import { useLanguageStore } from '../store/languageStore';

export function LanguageToggle() {
  const { language, toggleLanguage } = useLanguageStore();

  return (
    <Button
      variant="outline"
      size="sm"
      onClick={toggleLanguage}
      className="gap-2"
    >
      <Globe className="h-4 w-4" />
      {language === 'en' ? 'EN' : 'TH'}
    </Button>
  );
}
