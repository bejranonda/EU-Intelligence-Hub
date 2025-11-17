# EU Intelligence Hub - Complete Data Flow Explained

## Why Keyword Search Returns No Results - Deep Dive

This document explains exactly how data flows through the system and why your keyword search might be returning empty results.

---

## The Complete Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER INTERACTION                            │
│                                                                 │
│  1. User enters keyword: "Thailand tourism"                    │
│  2. Frontend calls: GET /api/search/articles?q=Thailand        │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND API (FastAPI)                        │
│                                                                 │
│  File: backend/app/api/search.py:20-140                        │
│                                                                 │
│  @router.get("/articles")                                      │
│  async def search_articles(q, ...):                            │
│      query_builder = db.query(Article)  # Line 45             │
│                                                                 │
│      if q:                                                      │
│          pattern = f"%{q}%"                                     │
│          query_builder = query_builder.filter(                 │
│              or_(                                               │
│                  Article.title.ilike(pattern),    # Line 59    │
│                  Article.summary.ilike(pattern),               │
│                  Article.full_text.ilike(pattern),             │
│              )                                                  │
│          )                                                      │
│                                                                 │
│      total = query_builder.count()  # Line 93                  │
│      articles = query_builder.offset(...).limit(...).all()     │
│                                                                 │
│  ⚠️ IF ARTICLES TABLE IS EMPTY → total=0, results=[]          │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   POSTGRESQL DATABASE                           │
│                                                                 │
│  Query: SELECT * FROM articles                                 │
│         WHERE title ILIKE '%Thailand%'                         │
│            OR summary ILIKE '%Thailand%'                       │
│            OR full_text ILIKE '%Thailand%';                    │
│                                                                 │
│  ⚠️ IF NO ROWS EXIST → Returns empty result set               │
└─────────────────────────────────────────────────────────────────┘
```

---

## How Articles Get Into The Database

For search to return results, articles must first be in the database. Here's how they get there:

### Method 1: Hourly Automated Scraping (Passive)

```
Every hour at :00 (controlled by Celery Beat)
│
├─> Celery Beat triggers: scrape_news task
│   File: backend/app/tasks/scraping.py:15-60
│
├─> Task calls: NewsScraper.scrape_all_sources()
│   File: backend/app/services/scraper.py:250-297
│
├─> Scraper calls: research_thailand_news_gemini()
│   File: backend/app/services/scraper.py:136-204
│
├─> Sends prompt to Gemini API:
│   "Search recent European news sources for Thailand articles..."
│   ⚠️ REQUIRES: Valid GEMINI_API_KEY
│
├─> Gemini returns JSON array of articles:
│   [
│     {
│       "title": "Thailand Tourism Surges...",
│       "source": "BBC",
│       "date": "2025-11-14",
│       "summary": "...",
│       "url": "https://..."
│     },
│     ...
│   ]
│
├─> Articles are processed:
│   1. Extract keywords using spaCy + Gemini
│      File: backend/app/services/keyword_extractor.py
│
│   2. Analyze sentiment using VADER + Gemini
│      File: backend/app/services/sentiment.py
│
│   3. Generate embeddings (384-dim vectors)
│      File: backend/app/services/embeddings.py
│
│   4. Classify as fact/opinion/mixed
│
├─> Store in database:
│   INSERT INTO articles (title, summary, source, sentiment_overall, ...)
│   INSERT INTO keyword_articles (keyword_id, article_id, relevance_score)
│
└─> ✓ Articles now searchable via /api/search/articles
```

**Timeline:** Runs every hour (01:00, 02:00, 03:00, etc.)

**Requirement:** `GEMINI_API_KEY` must be valid

---

### Method 2: Keyword-Triggered Immediate Search (Active)

```
User creates keyword suggestion
│
├─> POST /api/suggestions
│   {
│     "keyword_en": "Thailand tourism",
│     "category": "economy"
│   }
│
├─> Stored in keyword_suggestions table
│   status: "pending"
│
├─> Admin approves via: POST /api/admin/suggestions/{id}/approve
│   File: backend/app/api/admin_suggestions.py:200-280
│
├─> Triggers Celery task: search_keyword_immediately
│   File: backend/app/tasks/keyword_search.py:30-120
│
├─> Checks cooldown (3 hours between searches)
│   Query: SELECT last_searched FROM keywords WHERE id = ?
│
├─> If allowed, starts search:
│   1. Calls Gemini API: "Find recent articles about {keyword}"
│      ⚠️ REQUIRES: Valid GEMINI_API_KEY
│
│   2. For each article returned:
│      a. Fetch full text from URL
│      b. Extract keywords
│      c. Analyze sentiment
│      d. Generate embedding
│      e. Store in database
│
├─> Updates keyword:
│   UPDATE keywords SET last_searched = NOW()
│
└─> ✓ Articles associated with this keyword are now in database
```

**Timeline:** Immediate (5-10 minutes processing time)

**Trigger:** Admin approves keyword suggestion

**Requirement:** `GEMINI_API_KEY` must be valid

---

### Method 3: Scheduled Queue Processing (Batch)

```
Every 30 minutes:
├─> populate_keyword_queue task
│   File: backend/app/tasks/keyword_search.py:150-200
│
│   Selects keywords to search based on:
│   - Priority (recently mentioned keywords)
│   - Last searched timestamp (>3 hours ago)
│   - Daily quota (max 250 searches/day)
│
└─> Adds to keyword_search_queue table

Every 15 minutes:
├─> process_keyword_queue task
│   File: backend/app/tasks/keyword_search.py:220-280
│
├─> Processes up to 15 queued keywords
│
├─> For each keyword:
│   1. Search using Gemini (same as Method 2)
│   2. Process articles
│   3. Store in database
│   4. Update queue status
│
└─> ✓ Articles added to database
```

**Timeline:** Continuous background processing

**Requirement:** `GEMINI_API_KEY` must be valid

---

## Critical Dependencies Chain

For keyword search to work, ALL of these must be true:

```
1. GEMINI_API_KEY is configured and valid
   Location: .env file
   Check: python3 test_gemini_api.py
   ↓
2. PostgreSQL is running
   Port: 5432
   Check: docker compose ps postgres
   ↓
3. Redis is running
   Port: 6379
   Check: docker compose ps redis
   ↓
4. Backend API is running
   Port: 8000
   Check: curl http://localhost:8000/health
   ↓
5. Celery worker is running
   Check: docker compose ps celery_worker
   ↓
6. Celery beat is running
   Check: docker compose ps celery_beat
   ↓
7. At least one keyword exists
   Check: psql -c "SELECT COUNT(*) FROM keywords;"
   ↓
8. At least one article exists
   Check: psql -c "SELECT COUNT(*) FROM articles;"
   ↓
9. Articles are associated with keywords
   Check: psql -c "SELECT COUNT(*) FROM keyword_articles;"
   ↓
10. ✓ Search returns results!
```

---

## Code Path for Search Query

### 1. User searches for "Thailand"

**Frontend:** `frontend/src/pages/SearchPage.tsx`
```typescript
const searchArticles = async (query: string) => {
  const response = await apiClient.searchArticles(query);
  // response.results contains articles
};
```

### 2. API Client makes request

**Frontend:** `frontend/src/api/client.ts`
```typescript
searchArticles(query: string) {
  return this.get(`/api/search/articles?q=${query}`);
}
```

### 3. Backend receives request

**Backend:** `backend/app/api/search.py:20-140`
```python
@router.get("/articles")
async def search_articles(
    q: Optional[str] = Query(None),  # q = "Thailand"
    ...
):
    query_builder = db.query(Article)  # Start query

    if q:
        pattern = f"%{q}%"  # "%Thailand%"
        query_builder = query_builder.filter(
            or_(
                Article.title.ilike(pattern),
                Article.summary.ilike(pattern),
                Article.full_text.ilike(pattern),
            )
        )

    total = query_builder.count()  # Execute COUNT(*)
    articles = query_builder.offset(offset).limit(page_size).all()  # Execute SELECT

    return {"results": articles, "total": total}
```

### 4. Database executes query

**PostgreSQL:**
```sql
SELECT COUNT(*) FROM articles
WHERE title ILIKE '%Thailand%'
   OR summary ILIKE '%Thailand%'
   OR full_text ILIKE '%Thailand%';
-- Result: 0 (if no articles exist)

SELECT * FROM articles
WHERE title ILIKE '%Thailand%'
   OR summary ILIKE '%Thailand%'
   OR full_text ILIKE '%Thailand%'
LIMIT 20 OFFSET 0;
-- Result: [] (if no articles exist)
```

### 5. Response flows back

```
Backend returns:
{
  "results": [],  ← Empty because database is empty
  "pagination": {
    "total": 0,   ← No articles match
    "page": 1,
    "total_pages": 0
  }
}
↓
Frontend displays: "No results found"
```

---

## Why Your Search Returns Nothing

Based on code analysis, here are the **only possible reasons**:

### Reason 1: No Articles in Database (Most Common)
```sql
SELECT COUNT(*) FROM articles;
-- Returns: 0
```

**Why?**
- Gemini API key is missing/invalid → Scraper can't fetch articles
- Services haven't run yet → No automated scraping completed
- No keywords approved → No targeted searches triggered

**Fix:**
1. Configure Gemini API key in .env
2. Start services: `docker compose up -d`
3. Wait for hourly scraping OR approve a keyword manually

### Reason 2: Articles Exist But Don't Match Search Term
```sql
SELECT COUNT(*) FROM articles;
-- Returns: 100

SELECT COUNT(*) FROM articles WHERE title ILIKE '%Thailand%';
-- Returns: 0
```

**Why?**
- Articles are about other topics
- Search term doesn't match article content

**Fix:**
- Search for terms that exist in articles
- Check what articles exist: `SELECT DISTINCT source FROM articles;`
- Browse all articles: `GET /api/search/articles` (no query)

### Reason 3: Database Connection Failed
```
Backend logs show:
  sqlalchemy.exc.OperationalError: could not connect to server
```

**Why?**
- PostgreSQL not running
- DATABASE_URL incorrect in .env
- Network issues

**Fix:**
- Check: `docker compose ps postgres`
- Restart: `docker compose restart postgres`
- Verify: `docker compose logs postgres`

### Reason 4: Backend API Not Running
```
Frontend shows:
  Error: Network request failed
  Cannot connect to http://localhost:8000
```

**Why?**
- Backend container stopped
- Port 8000 blocked

**Fix:**
- Check: `docker compose ps backend`
- Restart: `docker compose restart backend`
- Logs: `docker compose logs backend`

---

## How to Debug Your Specific Issue

### Step 1: Check if articles exist

```bash
# Method A: Via API
curl http://localhost:8000/api/search/articles | jq '.pagination.total'

# Method B: Via Database
docker compose exec postgres psql -U newsadmin -d news_intelligence -c "SELECT COUNT(*) FROM articles;"
```

**If count is 0:**
- Articles have not been fetched yet
- Go to Step 2

**If count is > 0:**
- Articles exist but search term doesn't match
- Try: `curl http://localhost:8000/api/search/articles` (no query) to see what exists

### Step 2: Check Gemini API key

```bash
python3 test_gemini_api.py
```

**If test fails:**
- API key is missing or invalid
- Fix: Update `GEMINI_API_KEY` in .env
- Retry test

**If test passes:**
- API key is valid
- Go to Step 3

### Step 3: Check if services are running

```bash
python3 check_system_health.py
```

**If services are down:**
- Start: `docker compose up -d`
- Wait 2 minutes for services to initialize
- Retry health check

**If services are up:**
- Go to Step 4

### Step 4: Trigger manual article fetch

```bash
# Method A: Approve a keyword (via API)
curl -X POST http://localhost:8000/api/admin/suggestions/1/approve \
  -H "Content-Type: application/json" \
  -u admin:your_admin_password

# Method B: Wait for hourly scraping
# Check celery beat logs:
docker compose logs -f celery_beat

# Look for: "Scheduler: Sending due task scrape_news"
```

### Step 5: Monitor article processing

```bash
# Watch Celery worker process articles
docker compose logs -f celery_worker

# Look for:
# - "Task search_keyword_immediately[...]"
# - "Processing article: ..."
# - "Article saved: id=123"
```

### Step 6: Verify articles were added

```bash
# Check article count (should be > 0 now)
curl http://localhost:8000/api/search/articles | jq '.pagination.total'

# Try search again
curl "http://localhost:8000/api/search/articles?q=Thailand" | jq '.pagination.total'
```

---

## Expected Timeline After Fixing

```
T+0min:  Configure GEMINI_API_KEY in .env
T+1min:  docker compose up -d
T+2min:  All services healthy (check_system_health.py passes)
T+5min:  Access http://localhost:3000
T+5min:  Create keyword suggestion "Thailand tourism"
T+6min:  Admin approves keyword
T+7min:  Celery worker starts processing
T+10min: Articles fetched from Gemini
T+12min: Articles processed (sentiment, keywords, embeddings)
T+15min: Articles saved to database
T+15min: ✓ Search for "Thailand" returns results!
```

**OR** (if waiting for automatic scraping):

```
T+0min:  Configure GEMINI_API_KEY in .env
T+1min:  docker compose up -d
T+Xmin:  Wait until next hour (:00)
T+Xmin:  Celery beat triggers scrape_news
T+X+5min: Articles fetched and processed
T+X+10min: ✓ Search returns results!
```

---

## Testing The Full Flow

### Test 1: Empty Database → Articles Appear

```bash
# 1. Verify database is empty
curl http://localhost:8000/api/search/articles | jq '.pagination.total'
# Expected: 0

# 2. Create keyword
curl -X POST http://localhost:8000/api/suggestions \
  -H "Content-Type: application/json" \
  -d '{"keyword_en": "Thailand", "category": "general"}'

# 3. Approve it (triggers immediate search)
curl -X POST http://localhost:8000/api/admin/suggestions/1/approve \
  -u admin:your_password

# 4. Watch processing
docker compose logs -f celery_worker
# Wait for "Article saved" messages

# 5. Search again
curl http://localhost:8000/api/search/articles?q=Thailand | jq '.pagination.total'
# Expected: > 0
```

### Test 2: Verify Sentiment Analysis

```bash
# Get article with sentiment data
curl http://localhost:8000/api/search/articles?q=Thailand&page_size=1 | jq '.results[0].sentiment'

# Expected output:
# {
#   "overall": 0.45,
#   "classification": "positive"
# }
```

### Test 3: Verify Semantic Search

```bash
# Search using embeddings (similar meaning)
curl "http://localhost:8000/api/search/semantic?q=tourism+growth" | jq '.pagination.total'

# Expected: Articles about tourism even if exact words don't match
```

---

## Summary

**The search returns no results because:**

1. ❌ GEMINI_API_KEY not configured → Scraper can't fetch articles
2. ❌ No articles in database → Nothing to search
3. ❌ Services not running → Can't process requests

**The fix is:**

1. ✅ Add Gemini API key to .env
2. ✅ Start Docker services: `docker compose up -d`
3. ✅ Add and approve keywords OR wait for hourly scraping
4. ✅ Wait 5-15 minutes for processing
5. ✅ Search works!

**Validation scripts:**

- `python3 validate_project.py` - Check configuration
- `python3 test_gemini_api.py` - Test Gemini connection
- `python3 check_system_health.py` - Verify services

---

**Last Updated:** 2025-11-14
