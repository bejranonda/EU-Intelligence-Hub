# Feature Updates - Immediate Search & Auto-Translation

## Overview

Two new features have been implemented to enhance the keyword approval workflow:

1. **Immediate News Search with 3-Hour Cooldown**
2. **Automatic Keyword Translation**

## Feature 1: Immediate News Search

### Description

When a keyword is approved (either by AI or manually by admin), the system now automatically searches for news articles about that keyword immediately, rather than waiting for the next hourly scheduled scrape.

### How It Works

1. **Approval Triggers Search**: When a keyword is approved, a Celery task is triggered automatically
2. **3-Hour Cooldown Check**: Before searching, the system checks if the keyword was searched in the last 3 hours
   - If **YES** (searched recently): Skips the search and returns cooldown information
   - If **NO** (not searched or >3 hours ago): Proceeds with immediate search
3. **News Scraping**: Searches across all 12 European news sources for articles about the keyword
4. **Article Processing**: Processes found articles (sentiment analysis, keyword extraction, embedding generation)
5. **Timestamp Update**: Updates the `last_searched` field in the database

### API Endpoints

#### Automatic (via AI Processing)

```bash
POST /api/admin/keywords/suggestions/{suggestion_id}/process
```

When AI approves a keyword, it automatically triggers the search.

#### Manual Approval

```bash
POST /api/admin/keywords/suggestions/{suggestion_id}/approve?trigger_search=true
```

Parameters:
- `trigger_search` (optional, default: `true`): Whether to trigger immediate search

Response:
```json
{
  "success": true,
  "keyword": {
    "id": 123,
    "keyword_en": "Singapore",
    "keyword_th": "สิงคโปร์",
    "category": "country"
  },
  "message": "Keyword 'Singapore' approved and created and immediate search triggered",
  "search_triggered": true,
  "search_task_id": "abc-123-def"
}
```

### Cooldown Response

If a keyword was searched within the last 3 hours:

```json
{
  "status": "skipped",
  "keyword": "Singapore",
  "reason": "searched_recently",
  "last_searched": "2025-10-16T18:30:00",
  "minutes_since": 45,
  "cooldown_remaining_minutes": 135
}
```

### Database Changes

New column added to `keywords` table:

```sql
last_searched TIMESTAMP  -- Tracks when keyword was last searched for news
```

### Benefits

- **Faster Content Discovery**: New keywords get articles immediately instead of waiting up to 1 hour
- **Prevents Duplicate Searches**: 3-hour cooldown avoids wasting API quota
- **High Relevance**: Articles found via targeted search get relevance scores of 0.9-0.95 (higher than general scraping)

---

## Feature 2: Automatic Keyword Translation

### Description

When users submit keyword suggestions, they only need to provide the English version. The system automatically translates keywords to Thai (and other configured languages) using Gemini AI.

### How It Works

1. **User Submits English Only**: User provides only `keyword_en` in the suggestion
2. **Approval Process**: When keyword is approved (AI or manual), system checks for translation
3. **Auto-Translation**: If `keyword_th` is empty, AI translates the keyword
4. **Context-Aware**: Translation considers news/media context for accuracy
5. **Database Storage**: Translated version is stored alongside English version

### Translation API

The translation uses Gemini AI with a specialized prompt for news terminology:

```python
async def translate_keyword(
    keyword_en: str,
    target_languages: List[str] = ['th']
) -> Dict[str, str]
```

### Examples

| English Keyword | Thai Translation (Auto-generated) |
|-----------------|-----------------------------------|
| Singapore       | สิงคโปร์                          |
| Thailand        | ประเทศไทย                         |
| European Union  | สหภาพยุโรป                        |
| NATO            | นาโต้                             |

### Supported Languages

Current default: Thai (`th`)

Easily extensible to:
- German (`de`)
- French (`fr`)
- Spanish (`es`)

### Benefits

- **Simplified Input**: Users only need to know English
- **Consistency**: AI ensures consistent translation of terminology
- **News Context**: Translations are optimized for news/media context
- **Proper Nouns**: Handles country names, organizations, etc. correctly

---

## Usage Examples

### Example 1: Submit New Keyword (User)

```bash
POST /api/suggestions/
Content-Type: application/json

{
  "keyword_en": "Vietnam",
  "category": "country",
  "reason": "Want to track Vietnam-EU trade relations"
}
```

**Result**:
- System stores suggestion with only English version
- When approved, AI automatically translates to "เวียดนาม"
- Immediate news search triggered (if not searched in last 3 hours)

### Example 2: Manual Approval (Admin)

```bash
POST /api/admin/keywords/suggestions/5/approve?trigger_search=true
```

**What Happens**:
1. ✅ Keyword "Vietnam" gets auto-translated to "เวียดนาม"
2. ✅ Keyword created in database with both English and Thai
3. ✅ Immediate search triggered for Vietnam news
4. ✅ Articles found across 12 European sources
5. ✅ Articles processed and linked to keyword

### Example 3: AI Processing (Scheduled)

Daily at 2:00 AM UTC, the system:
1. Processes all pending suggestions with AI
2. For approved keywords:
   - Auto-translates if needed
   - Creates keyword in database
   - Triggers immediate search (respecting cooldown)

---

## Technical Details

### New Files

1. **backend/app/tasks/keyword_search.py** (230 lines)
   - Celery task: `search_keyword_immediately(keyword_id)`
   - 3-hour cooldown logic
   - Targeted news scraping
   - High-relevance article processing

2. **backend/migrations/add_last_searched_column.sql**
   - Database migration script
   - Adds `last_searched` column to keywords table

### Modified Files

1. **backend/app/models/models.py**
   - Added `last_searched` field to Keyword model

2. **backend/app/services/keyword_approval.py**
   - Added `translate_keyword()` method (70 lines)
   - Updated `process_suggestion()` to auto-translate and trigger search

3. **backend/app/api/admin.py**
   - Updated `approve_suggestion_manually()` with translation and search
   - Added `trigger_search` parameter

4. **backend/app/tasks/celery_app.py**
   - Import `keyword_search` task for Celery registration

5. **backend/init_db.sql**
   - Added `last_searched` column to schema

### Configuration

No configuration changes needed. Features work out of the box with existing settings.

### Environment Variables

Uses existing `GEMINI_API_KEY` for translation.

---

## Monitoring

### Check Keyword Search History

```sql
SELECT
  keyword_en,
  last_searched,
  EXTRACT(EPOCH FROM (NOW() - last_searched))/3600 as hours_since_search,
  search_count
FROM keywords
WHERE last_searched IS NOT NULL
ORDER BY last_searched DESC;
```

### Check Translation Quality

Translations are logged:

```
INFO: Auto-translated 'Singapore' to Thai: สิงคโปร์
```

### Celery Task Monitoring

Monitor immediate search tasks:

```bash
docker compose logs celery_worker | grep "search_keyword_immediately"
```

---

## FAQ

### Q: What if translation fails?

A: The keyword is still created with the English version. Thai version remains null. Admin can manually add translation later.

### Q: Can I disable automatic search trigger?

A: Yes, when manually approving via API:

```bash
POST /api/admin/keywords/suggestions/5/approve?trigger_search=false
```

### Q: What happens if a keyword is searched twice within 3 hours?

A: The second search is skipped with a response indicating:
- When it was last searched
- How many minutes ago
- How many minutes until cooldown expires

### Q: Can I manually trigger a search for an existing keyword?

A: Yes, you can call the Celery task directly:

```python
from app.tasks.keyword_search import search_keyword_immediately
task = search_keyword_immediately.delay(keyword_id)
```

Or via Celery CLI:

```bash
docker compose exec celery_worker celery call app.tasks.keyword_search.search_keyword_immediately --args='[123]'
```

### Q: How do I add more translation languages?

A: Update the `translate_keyword()` call in `keyword_approval.py`:

```python
translations = await self.translate_keyword(
    suggestion.keyword_en,
    ['th', 'de', 'fr']  # Add more language codes
)
```

Then add corresponding fields to the Keyword model.

---

## Testing

### Test Translation

```bash
# Via Python shell
docker compose exec backend python
>>> from app.services.keyword_approval import keyword_approval_service
>>> import asyncio
>>> result = asyncio.run(keyword_approval_service.translate_keyword("Japan", ["th"]))
>>> print(result)
{'th': 'ญี่ปุ่น'}
```

### Test Immediate Search

```bash
# Create and approve a keyword suggestion
curl -X POST http://localhost:8000/api/suggestions/ \
  -H "Content-Type: application/json" \
  -d '{"keyword_en": "Malaysia", "category": "country"}'

# Approve it (triggers search)
curl -X POST http://localhost:8000/api/admin/keywords/suggestions/1/approve?trigger_search=true
```

Check logs:
```bash
docker compose logs celery_worker | grep Malaysia
```

---

## Future Enhancements

Potential improvements:

1. **Configurable Cooldown**: Make 3-hour cooldown configurable per keyword category
2. **Search Priority**: High-voted suggestions get immediate search even within cooldown
3. **Translation Caching**: Cache common translations to reduce API calls
4. **Multiple Languages**: Extend auto-translation to German, French, Spanish
5. **Search Analytics**: Track which keywords find the most articles

---

## Support

For issues or questions:
- Check logs: `docker compose logs backend` and `docker compose logs celery_worker`
- Review [KEYWORD_WORKFLOW.md](KEYWORD_WORKFLOW.md) for overall workflow
- See [DEPLOYMENT.md](DEPLOYMENT.md) for production setup

---

**Last Updated**: 2025-10-16
**Version**: 1.0
