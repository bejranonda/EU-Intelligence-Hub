# Multi-Language Implementation Guide

## Overview

The EU Intelligence Hub now supports **4 languages** across the entire application:
- **English (EN)** - Default
- **Thai (TH)**
- **German (DE)**
- **Danish (DA)**

The interface automatically adapts to the selected language, translating all UI elements, labels, and messages.

## Implementation Summary

### Frontend Changes

#### 1. i18n Configuration (`frontend/src/i18n/`)

**Files Created:**
- `config.ts` - i18next initialization
- `locales/en.json` - English translations (base)
- `locales/th.json` - Thai translations
- `locales/de.json` - German translations
- `locales/da.json` - Danish translations

**Translation Structure:**
```json
{
  "common": { ... },
  "header": { ... },
  "footer": { ... },
  "home": { ... },
  "keyword": { ... },
  "sentiment": { ... },
  "search": { ... },
  "upload": { ... },
  "suggest": { ... },
  "admin": { ... },
  "about": { ... },
  "methodology": { ... },
  "compare": { ... },
  "categories": { ... },
  "languages": { ... }
}
```

#### 2. Language Store (`frontend/src/store/languageStore.ts`)

**Updated Features:**
- Removed `toggleLanguage()` (was only EN/TH)
- Enhanced `setLanguage()` to sync with i18next
- Supports all 4 languages
- Persists selection in localStorage

```typescript
export const useLanguageStore = create<LanguageState>()(
  persist(
    (set) => ({
      language: 'en',
      setLanguage: (language) => {
        set({ language });
        i18n.changeLanguage(language); // Sync with i18next
      },
    }),
    { name: 'language-storage' }
  )
);
```

#### 3. Language Toggle Component (`frontend/src/components/LanguageToggle.tsx`)

**Before:** Simple toggle button (EN ↔ TH)
**After:** Dropdown menu with all languages

**Features:**
- Flag emojis for visual identification
- Native language names (English, ไทย, Deutsch, Dansk)
- Check mark for current selection
- Responsive (shows full name on desktop, code on mobile)

#### 4. Updated Components

**Core Components:**
- `Header.tsx` - Navigation, titles, menu items
- `Footer.tsx` - Footer text and links
- `HomePage.tsx` - Hero section, features, all UI text
- `KeywordCard.tsx` - Displays translated keyword based on language

**KeywordCard Language Logic:**
```typescript
const getKeywordText = () => {
  switch (language) {
    case 'th': return keyword.keyword_th || keyword.keyword_en;
    case 'de': return keyword.keyword_de || keyword.keyword_en;
    case 'da': return keyword.keyword_da || keyword.keyword_en;
    default: return keyword.keyword_en;
  }
};
```

#### 5. Type Definitions (`frontend/src/types/index.ts`)

**Updated:**
```typescript
export type Language = 'en' | 'th' | 'de' | 'da';

export interface Keyword {
  id: number;
  keyword_en: string;
  keyword_th?: string;
  keyword_de?: string;
  keyword_da?: string;  // New
  // ...
}
```

### Backend Changes

#### 1. Database Model (`backend/app/models/models.py`)

**Added Field:**
```python
class Keyword(Base):
    # ...
    keyword_da = Column(String(255))  # Danish
    # ...
```

#### 2. Database Schema (`backend/init_db.sql`)

**Updated Keywords Table:**
```sql
CREATE TABLE IF NOT EXISTS keywords (
    id SERIAL PRIMARY KEY,
    keyword_en VARCHAR(255) UNIQUE NOT NULL,
    keyword_th VARCHAR(255),
    keyword_de VARCHAR(255),
    keyword_da VARCHAR(255),  -- Danish
    keyword_fr VARCHAR(255),
    keyword_es VARCHAR(255),
    keyword_it VARCHAR(255),
    keyword_pl VARCHAR(255),
    keyword_sv VARCHAR(255),
    keyword_nl VARCHAR(255),
    -- ...
);
```

#### 3. Migration Script (`backend/migrations/add_danish_language_support.sql`)

**For Existing Databases:**
```sql
ALTER TABLE keywords ADD COLUMN IF NOT EXISTS keyword_da VARCHAR(255);
ALTER TABLE keyword_suggestions ADD COLUMN IF NOT EXISTS keyword_da VARCHAR(255);
```

## Usage Guide

### For Users

1. **Select Language:**
   - Click the globe icon (🌐) in the header
   - Choose from: English, ไทย, Deutsch, Dansk
   - Interface updates immediately

2. **Keyword Display:**
   - Keywords show in selected language (if translation exists)
   - Falls back to English if translation unavailable
   - English name always shown as subtitle

### For Developers

#### Adding New Translations

1. **Update JSON Files:**
```bash
# Add new key to all language files
frontend/src/i18n/locales/en.json
frontend/src/i18n/locales/th.json
frontend/src/i18n/locales/de.json
frontend/src/i18n/locales/da.json
```

2. **Use in Components:**
```typescript
import { useTranslation } from 'react-i18next';

function MyComponent() {
  const { t } = useTranslation();

  return (
    <div>
      <h1>{t('mySection.title')}</h1>
      <p>{t('mySection.description')}</p>
    </div>
  );
}
```

#### Adding a New Language

1. **Create Translation File:**
```bash
# Copy English as base
cp frontend/src/i18n/locales/en.json frontend/src/i18n/locales/NEW_LANG.json
# Translate all values
```

2. **Update i18n Config:**
```typescript
// frontend/src/i18n/config.ts
import newLangTranslations from './locales/NEW_LANG.json';

i18n.init({
  resources: {
    // ...
    NEW_LANG: {
      translation: newLangTranslations,
    },
  },
});
```

3. **Update Language Type:**
```typescript
// frontend/src/types/index.ts
export type Language = 'en' | 'th' | 'de' | 'da' | 'NEW_LANG';
```

4. **Update LanguageToggle:**
```typescript
// frontend/src/components/LanguageToggle.tsx
const languages = [
  // ...
  { code: 'NEW_LANG', label: 'Native Name', flag: '🏴' },
];
```

5. **Update Backend:**
```python
# backend/app/models/models.py
keyword_NEW_LANG = Column(String(255))
```

```sql
-- backend/init_db.sql
keyword_NEW_LANG VARCHAR(255),
```

## Translation Coverage

### Complete Translation Files

All JSON files contain translations for:

| Section | Keys | Coverage |
|---------|------|----------|
| Common | 13 | Buttons, actions, pagination |
| Header | 8 | Navigation menu |
| Footer | 5 | Footer text |
| Home | 17 | Hero, features, search |
| Keyword | 10 | Details, labels |
| Sentiment | 13 | Sentiment labels |
| Search | 8 | Search interface |
| Upload | 8 | Upload form |
| Suggest | 10 | Suggestion form |
| Admin | 15 | Admin interface |
| About | 5 | About page |
| Methodology | 6 | Methodology page |
| Compare | 5 | Comparison tool |
| Categories | 7 | Content categories |
| Languages | 4 | Language names |

**Total:** ~134 translation keys per language

## Database Migration

### For Existing Installations

Run the migration to add Danish support:

```bash
# Using Docker
docker compose exec postgres psql -U newsadmin -d news_intelligence -f /app/migrations/add_danish_language_support.sql

# Or manually
psql -U newsadmin -d news_intelligence -f backend/migrations/add_danish_language_support.sql
```

## Testing Checklist

- [ ] Language dropdown shows all 4 languages
- [ ] Selection persists on page reload
- [ ] Header/Footer translate correctly
- [ ] HomePage hero section translates
- [ ] Keywords display in selected language
- [ ] Category labels translate
- [ ] Sentiment labels translate
- [ ] Search placeholders translate
- [ ] Button labels translate
- [ ] Error messages translate
- [ ] Pagination text translates
- [ ] No hardcoded English text visible

## Known Limitations

1. **Article Content:** News articles remain in original language (scraped content)
2. **Dynamic Content:** Some generated content from AI may be in English
3. **Fallback:** If translation missing, shows English by default
4. **Right-to-Left:** No RTL language support yet (Arabic, Hebrew, etc.)

## Future Enhancements

1. **More Languages:** French, Spanish, Italian (already have DB fields)
2. **Auto-Detection:** Browser language auto-selection
3. **Per-Article Translation:** AI-powered article translation
4. **Search in Native Language:** Search news in selected language
5. **Voice Output:** Text-to-speech in selected language

## Technical Details

### Libraries Used

- **i18next:** ^23.7.6 - Core i18n framework
- **react-i18next:** ^13.5.0 - React bindings for i18next
- **Zustand:** ^4.4.7 - State management for language selection

### Performance

- **Bundle Size:** ~150KB for all 4 translation files (compressed)
- **Load Time:** Translations loaded synchronously on app start
- **Switching Speed:** Instant (no network requests)
- **Caching:** Translations cached in memory

### Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- All modern mobile browsers

## Troubleshooting

### Translations Not Showing

1. **Check i18n initialization:**
```typescript
// main.tsx should import config
import './i18n/config';
```

2. **Verify JSON syntax:**
```bash
# Validate JSON files
jq empty frontend/src/i18n/locales/*.json
```

3. **Check language store:**
```typescript
// In component
const { language } = useLanguageStore();
console.log('Current language:', language);
```

### Language Not Persisting

- Check localStorage: Key = `language-storage`
- Clear browser cache and localStorage
- Verify Zustand persist middleware

### Missing Translations

- Add missing keys to all JSON files
- Restart development server
- Check console for i18next warnings

## Support

For issues or questions:
1. Check this documentation
2. Review translation JSON files
3. Check browser console for errors
4. File issue on GitHub

---

**Last Updated:** 2024-11-17
**Version:** 2.0.0
**Languages Supported:** English, Thai, German, Danish
