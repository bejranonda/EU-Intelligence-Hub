# AI-Powered Keyword Management Workflow

Complete guide to the automated keyword suggestion, approval, and management system.

## Overview

The system uses Gemini AI to intelligently manage keyword suggestions with:
- **Automatic significance evaluation**
- **Duplicate detection and merging**
- **Searchability assessment**
- **Alternative keyword suggestions**
- **Automated approval workflow**

---

## How It Works

### 1. Keyword Suggestion Process

**User submits keyword via `/api/suggestions/` endpoint:**
```
POST /api/suggestions/
{
  "keyword_en": "Singapore",
  "keyword_th": "สิงคโปร์",
  "category": "country",
  "reason": "Important ASEAN partner"
}
```

**Status: `pending`** - Stored for AI evaluation

---

### 2. Automated AI Processing (Daily at 2:00 AM UTC)

**Celery Task: `process_pending_suggestions`**

For each pending suggestion, AI evaluates:

#### A. **Significance Evaluation**
```
Is this keyword worth tracking?
- International relevance
- News frequency
- Geopolitical importance
```

**Output:**
- `is_significant`: true/false
- `confidence`: 0.0-1.0
- `searchability`: easy/moderate/difficult
- `news_potential`: high/medium/low
- `suggested_alternatives`: ["alt1", "alt2"]
- `reasoning`: "explanation"

#### B. **Duplicate Detection**
```
Does this keyword already exist (similar)?
- Vector similarity search (>85%)
- Finds: "Singapore", "Republic of Singapore", "SG"
```

#### C. **Merge Analysis**
If similar keywords found:
```
Should they be merged?
- Merge: Same entity/concept
- Keep separate: Distinct despite similarity
```

**Output:**
- `should_merge`: true/false
- `merge_with`: "existing keyword"
- `reasoning`: "explanation"

---

### 3. Decision Flow

```
┌─────────────────────┐
│ Keyword Suggested   │
│  Status: pending    │
└──────────┬──────────┘
           │
           ▼
    ┌──────────────┐
    │ AI Evaluates │
    │ Significance │
    └──────┬───────┘
           │
           ▼
    ┌──────────────────┐
    │ Is Significant?  │◄─── Confidence > 0.6
    └─────┬────────┬───┘
          │        │
        NO│        │YES
          │        │
          ▼        ▼
    ┌──────────┐  ┌─────────────────┐
    │ REJECTED │  │ Check Duplicates│
    └──────────┘  └────────┬────────┘
                           │
                           ▼
                    ┌──────────────────┐
                    │ Similar Found?   │
                    └─────┬────────┬───┘
                          │        │
                        NO│        │YES
                          │        │
                          ▼        ▼
                   ┌──────────┐  ┌──────────────┐
                   │Searchable│  │Should Merge? │
                   └────┬─────┘  └─────┬────┬───┘
                        │              │    │
           ┌────────────┼──────────┐   │    │
           │            │          │   │YES │NO
         Easy       Moderate   Difficult│   │
           │            │          │    │   │
           ▼            ▼          ▼    ▼   ▼
    ┌──────────┐ ┌──────────┐ ┌────────┐ ┌────┐ ┌────────┐
    │ APPROVED │ │ APPROVED │ │PENDING │ │MERGE│ │APPROVED│
    │Create KW │ │Create KW │ │+suggest│ │ D  │ │Create  │
    └──────────┘ └──────────┘ └────────┘ └────┘ └────────┘
                                alternatives
```

---

## Automated Schedules

### Daily Tasks (2:00 AM UTC)
**`process_pending_suggestions`**
- Processes all pending keyword suggestions
- Auto-approves significant keywords
- Merges duplicates
- Suggests alternatives for difficult keywords

### Weekly Tasks (Monday 3:00 AM UTC)
**`review_keyword_performance`**
- Checks if approved keywords are finding articles
- Flags keywords with no articles in 30 days
- Suggests removal or alternatives

### Hourly Tasks (Every hour)
**`scrape_news`**
- Searches for news about ALL approved keywords
- Currently searches: Every hour
- **New sources added**: 12 total sources
  - BBC, Reuters, Deutsche Welle, France24
  - The Guardian, EuroNews
  - **NEW**: Politico Europe, Euractiv, The Local
  - **NEW**: Al Jazeera English, CNBC Europe, Financial Times

---

## News Source Expansion

### Current Sources (12 Total)

| Source | Coverage | Language |
|--------|----------|----------|
| **BBC** | Global | EN |
| **Reuters** | Global | EN |
| **Deutsche Welle (DW)** | European | EN/DE |
| **France24** | European | EN/FR |
| **The Guardian** | UK/Europe | EN |
| **EuroNews** | Pan-European | Multiple |
| **Politico Europe** | EU Politics | EN |
| **Euractiv** | EU Affairs | Multiple |
| **The Local** | Local European | EN |
| **Al Jazeera English** | Global/ME | EN |
| **CNBC Europe** | Business/Economy | EN |
| **Financial Times** | Business/Finance | EN |

### Search Frequency

**For approved keywords:**
- **Every hour** automatic search across all 12 sources
- Gemini AI searches recent news (last 48 hours)
- Extracts: title, summary, date, source, URL

---

## Manual Admin Control

### API Endpoints

#### 1. **View Pending Suggestions**
```bash
GET /api/admin/keywords/suggestions/pending?limit=50
```

**Response:**
```json
{
  "pending_suggestions": [
    {
      "id": 1,
      "keyword_en": "Singapore",
      "votes": 5,
      "status": "pending",
      "created_at": "2025-01-15T10:00:00"
    }
  ],
  "total": 1
}
```

#### 2. **Trigger AI Processing**
```bash
POST /api/admin/keywords/suggestions/{id}/process
```

**Response:**
```json
{
  "success": true,
  "result": {
    "action": "approved",
    "keyword_id": 42,
    "evaluation": {
      "is_significant": true,
      "confidence": 0.9,
      "searchability": "easy",
      "news_potential": "high"
    },
    "reasoning": ["Approved: Major ASEAN country with frequent EU coverage"]
  }
}
```

#### 3. **Manual Approve** (Bypass AI)
```bash
POST /api/admin/keywords/suggestions/{id}/approve
```

#### 4. **Manual Reject**
```bash
POST /api/admin/keywords/suggestions/{id}/reject?reason=Too broad
```

#### 5. **Get Statistics**
```bash
GET /api/admin/keywords/suggestions/stats
```

**Response:**
```json
{
  "total_suggestions": 50,
  "by_status": {
    "pending": 10,
    "approved": 25,
    "rejected": 10,
    "merged": 5
  },
  "top_pending": [...]
}
```

---

## Examples

### Example 1: Easy Keyword (Approved)
```
Input: "Vietnam"
Category: country

AI Evaluation:
✓ Significant: Yes (confidence: 0.95)
✓ Searchability: easy
✓ News Potential: high
✓ Similar keywords: None

Result: APPROVED → Created keyword_id: 5
Next: Hourly news search starts immediately
```

### Example 2: Difficult Keyword (Pending + Alternatives)
```
Input: "Southeast Asian diplomatic relations"
Category: topic

AI Evaluation:
✓ Significant: Yes (confidence: 0.75)
✗ Searchability: difficult (too broad)
✓ News Potential: medium

Suggested Alternatives:
- "ASEAN diplomacy"
- "Southeast Asia foreign policy"
- "ASEAN-EU relations"

Result: PENDING with suggestions
Next: Wait for user/admin to choose alternative
```

### Example 3: Duplicate (Merged)
```
Input: "Republic of Singapore"

AI Evaluation:
✓ Similar keywords found: "Singapore" (similarity: 0.92)
✓ Should merge: Yes
✓ Merge with: "Singapore"

Result: MERGED
Next: No new keyword created, suggestion marked as merged
```

### Example 4: Not Significant (Rejected)
```
Input: "Random niche blog"

AI Evaluation:
✗ Significant: No (confidence: 0.3)
✗ Searchability: difficult
✗ News Potential: low
Reasoning: "Not relevant for European news monitoring"

Result: REJECTED
Next: Suggestion archived
```

---

## Best Practices

### For Users Suggesting Keywords

1. **Be Specific**: "Vietnam economy" > "economy"
2. **Provide Context**: Use the "reason" field
3. **Check Duplicates**: Search existing keywords first
4. **Vote**: Upvote similar suggestions instead of duplicating

### For Admins

1. **Review AI Decisions**: Check `/api/admin/keywords/suggestions/stats` weekly
2. **Process High-Vote Suggestions**: Manually review suggestions with 10+ votes
3. **Monitor Performance**: Check keyword performance reports
4. **Adjust Thresholds**: May need to adjust confidence thresholds based on results

---

## Troubleshooting

### Keyword Not Finding Articles

**Check:**
1. Is keyword too specific/niche?
2. Run manual search test via Gemini
3. Consider alternatives or broaden keyword
4. Check if keyword is misspelled

**Solution:**
```bash
# Review performance
GET /api/admin/keywords/suggestions/stats

# If inactive, suggest alternatives
POST /api/admin/keywords/suggestions/{id}/reject?reason=No articles found
```

### Too Many Pending Suggestions

**Trigger manual processing:**
```bash
POST /api/admin/keywords/suggestions/{id}/process
```

Or wait for daily automatic processing at 2:00 AM UTC.

---

## Configuration

### Adjust Processing Schedule

Edit `backend/app/tasks/celery_app.py`:

```python
celery_app.conf.beat_schedule = {
    'process-keyword-suggestions': {
        'task': 'app.tasks.keyword_management.process_pending_suggestions',
        'schedule': crontab(hour=2, minute=0),  # Change time here
    },
}
```

### Adjust Similarity Threshold

Edit `backend/app/services/keyword_approval.py`:

```python
similarity_threshold = 0.85  # 0.0-1.0 (higher = more strict)
```

---

## Summary

✅ **Automated**: AI processes suggestions daily
✅ **Intelligent**: Evaluates significance and searchability
✅ **Efficient**: Merges duplicates automatically
✅ **Helpful**: Suggests alternatives for difficult keywords
✅ **Expandable**: Now searches 12 European news sources
✅ **Frequent**: Hourly news searches for all approved keywords
✅ **Controllable**: Admin can override AI decisions

**Result**: Smart, automated keyword management that grows intelligently with user input while maintaining quality and avoiding duplicates.
