# Troubleshooting: Empty Keywords & Suggestions

## Issue: No keywords showing on homepage, cannot create suggestions

### Symptoms
- Homepage shows "Loading keywords..." but no keywords appear
- Error message: "Error loading keywords"
- Cannot submit keyword suggestions
- "Show more" pagination doesn't work

---

## Root Cause

The database may not have any initial keywords loaded. The initialization SQL only runs during first Docker setup, and if the database schema already exists, keywords won't be re-inserted.

---

## Solution

### Option 1: Initialize Keywords (Recommended)

**For Docker Environment:**

```bash
# 1. Connect to backend container
docker exec -it euint_backend bash

# 2. Run the initialization script
python scripts/init_keywords.py

# 3. Exit
exit
```

**For Local Python Environment:**

```bash
cd backend
python ../scripts/init_keywords.py
```

This will:
- Create database tables if they don't exist
- Insert 20 sample keywords (Thailand, Vietnam, Singapore, etc.)
- Display all keywords in the database
- Verify initialization success

### Option 2: Manual Database Insertion

**Using psql:**

```bash
# Connect to database
psql -h localhost -U euint_user -d euint_dev

# Insert keywords
INSERT INTO keywords (keyword_en, keyword_th, category, popularity_score) VALUES
('Thailand', 'ประเทศไทย', 'Country', 100.0),
('Vietnam', 'เวียดนาม', 'Country', 90.0),
('Singapore', 'สิงคโปร์', 'Country', 85.0),
('Indonesia', 'อินโดนีเซีย', 'Country', 80.0),
('ASEAN', 'อาเซียน', 'Organization', 75.0),
('COVID-19', 'โควิด-19', 'Health', 95.0),
('Climate Change', 'การเปลี่ยนแปลงสภาพอากาศ', 'Environment', 70.0);

# Verify
SELECT COUNT(*) FROM keywords;
SELECT * FROM keywords LIMIT 5;

# Exit psql
\q
```

### Option 3: Add Keywords via API (After Backend Starts)

**Step 1:** Create a suggestion (this creates the keyword indirectly)

```bash
curl -X POST http://localhost:8000/api/suggestions/ \
  -H "Content-Type: application/json" \
  -d '{
    "keyword_en": "Thailand",
    "keyword_th": "ประเทศไทย",
    "category": "Country",
    "reason": "Southeast Asia country"
  }'
```

**Step 2:** Wait for admin to approve the suggestion (or manually set status to 'approved')

---

## Verification Steps

### 1. Check Database has Keywords

```bash
# In Docker
docker exec -it euint_postgres psql -U euint_user -d euint_dev -c "SELECT COUNT(*) FROM keywords;"

# Should return: count > 0
```

### 2. Test API Endpoint

```bash
# Should return keywords
curl http://localhost:8000/api/keywords/?limit=10
```

Expected response:
```json
{
  "results": [
    {
      "id": 1,
      "keyword_en": "Thailand",
      "keyword_th": "ประเทศไทย",
      "category": "Country",
      "article_count": 0,
      "created_at": "2025-10-17T..."
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 20,
    "total_pages": 1
  }
}
```

### 3. Check Frontend Logs

In browser console (F12 → Console tab):
```javascript
// Should show successful keyword fetches
// Look for any errors like "Error loading keywords"
```

### 4. Test Suggestion Endpoint

```bash
curl -X POST http://localhost:8000/api/suggestions/ \
  -H "Content-Type: application/json" \
  -d '{
    "keyword_en": "New Test Keyword",
    "category": "Test"
  }'
```

Expected response:
```json
{
  "success": true,
  "suggestion": {
    "id": 1,
    "keyword_en": "New Test Keyword",
    "category": "Test",
    "status": "pending",
    "votes": 1,
    "created_at": "2025-10-17T..."
  },
  "message": "Thank you for your suggestion!"
}
```

---

## Debugging

### Enable Debug Logging

**Backend:**
```bash
# Check backend logs
docker logs euint_backend

# Look for:
# - "Error searching keywords"
# - "Error creating suggestion"
# - "Database health check failed"
```

**Frontend:**
```javascript
// In browser console, check:
1. Network requests to /api/keywords/
   - Status code (200 = good, 400 = bad request, 500 = server error)
   - Response structure
   - Any error messages

2. Application state
   - Check if keywords are being fetched
   - Check if error occurred
```

### Common Errors

**Error: "Error loading keywords"**
- Check: Database has keywords
- Check: API is running on port 8000
- Check: No firewall blocking access

**Error 400 from API**
- Check: Query parameters are correct (q, page, page_size, language)
- Check: API expects `page` not `skip`
- Check: page_size must be <= 100

**Error 500 from API**
- Check: Backend logs for specific error
- Check: Database connection is working
- Check: Database tables exist and have correct schema

---

## Full Setup from Scratch

If nothing works, reset and rebuild:

```bash
# 1. Stop containers
docker-compose down -v

# 2. Remove volumes to reset database
docker volume rm euint_postgres_data euint_redis_data

# 3. Rebuild and start
docker-compose up -d

# 4. Wait for services to start (30 seconds)
sleep 30

# 5. Initialize keywords
docker exec -it euint_backend python scripts/init_keywords.py

# 6. Verify
curl http://localhost:8000/api/keywords/

# 7. Check frontend
# Open http://localhost:3000 in browser
# Should now show keywords
```

---

## Preventive Measures

### For Future Deployments

1. **Add health check before starting frontend:**
   ```bash
   # Wait for API to be ready with keywords
   until curl -s http://backend:8000/api/keywords/ | grep -q "results"; do
     echo "Waiting for keywords..."
     sleep 5
   done
   ```

2. **Auto-initialize on backend startup:**
   Add to backend/app/main.py startup event:
   ```python
   @app.on_event("startup")
   async def startup_event():
       # ... existing code ...
       # Initialize keywords if table is empty
       from scripts.init_keywords import init_keywords
       init_keywords()
   ```

3. **Database migration script:**
   Create and run migrations to ensure schema is complete

---

## Success Indicators

✅ All of these should show keywords:
- `/api/keywords/` endpoint returns results
- Homepage displays keyword cards
- Can click on keywords to see details
- Suggestion form works and accepts submissions
- Database shows keywords: `SELECT COUNT(*) FROM keywords;` > 0

✅ If all checks pass, functionality is working correctly.

---

## Performance Note

If keywords are loaded but frontend is slow:
1. Check network latency: DevTools → Network tab
2. Check if API response is large (> 10MB, reduce page_size)
3. Check browser console for JavaScript errors

---

**Last Updated:** 2025-10-17  
**For Support:** Check logs with `docker logs euint_backend` and `docker logs euint_frontend`
