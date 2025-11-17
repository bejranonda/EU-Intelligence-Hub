# Troubleshooting Playbook - EU Intelligence Hub

Quick reference guide for diagnosing and fixing common issues.

---

## 🔥 Quick Diagnostic Commands

```bash
# 1. Check all validation at once
python3 validate_project.py

# 2. Test Gemini API specifically
python3 test_gemini_api.py

# 3. Check running services health
python3 check_system_health.py

# 4. Check Docker services
docker compose ps

# 5. Check article count in database
curl http://localhost:8000/api/search/articles | jq '.pagination.total'
```

---

## 🎯 Issue: "Keyword search returns no results"

### Diagnostic Checklist

```bash
# Step 1: Are there any articles?
curl http://localhost:8000/api/search/articles | jq '.pagination.total'
```

**If result is 0:** No articles in database → See "No Articles" section below

**If result is > 0:** Articles exist but don't match search → Try different search terms

---

## 📦 Issue: "No articles in database"

### Root Causes & Fixes

#### Cause 1: Gemini API Key Not Configured

**Check:**
```bash
cat .env | grep GEMINI_API_KEY
# Should NOT show: your_gemini_api_key_here
```

**Test:**
```bash
python3 test_gemini_api.py
```

**Fix:**
```bash
# 1. Get API key from https://makersuite.google.com/app/apikey
# 2. Edit .env
nano .env

# 3. Update line:
GEMINI_API_KEY=AIzaSyD9X8kFq2...your-actual-key...

# 4. Restart services
docker compose restart backend celery_worker
```

#### Cause 2: Services Not Running

**Check:**
```bash
docker compose ps
```

**Fix:**
```bash
# Start all services
docker compose up -d

# Wait for services to be healthy
sleep 30

# Verify
python3 check_system_health.py
```

#### Cause 3: Celery Worker Not Processing

**Check:**
```bash
docker compose logs celery_worker | tail -50
```

**Look for:**
- ✅ "celery@... ready."
- ✅ "connected to redis://..."
- ❌ Errors or exceptions

**Fix:**
```bash
# Restart Celery worker
docker compose restart celery_worker

# Watch logs
docker compose logs -f celery_worker
```

#### Cause 4: No Keywords Approved Yet

**Check:**
```bash
curl http://localhost:8000/api/keywords/ | jq '.pagination.total'
```

**Fix:**
```bash
# Create and approve a keyword via API
curl -X POST http://localhost:8000/api/suggestions \
  -H "Content-Type: application/json" \
  -d '{"keyword_en": "Thailand", "category": "general"}'

# Approve it (replace ID with actual ID)
curl -X POST http://localhost:8000/api/admin/suggestions/1/approve \
  -u admin:your_admin_password

# Monitor processing
docker compose logs -f celery_worker
```

---

## 🐳 Issue: "Docker services won't start"

### Port Conflicts

**Error:** "port is already allocated"

**Check what's using the port:**
```bash
# PostgreSQL (5432)
sudo lsof -i :5432

# Redis (6379)
sudo lsof -i :6379

# Backend (8000)
sudo lsof -i :8000

# Frontend (3000)
sudo lsof -i :3000
```

**Fix:**
```bash
# Option 1: Stop conflicting service
sudo systemctl stop postgresql
sudo systemctl stop redis-server

# Option 2: Change ports in docker-compose.yml
# Edit docker-compose.yml and change port mappings
```

### Container Failures

**Check logs:**
```bash
# View all logs
docker compose logs

# View specific service
docker compose logs postgres
docker compose logs backend
docker compose logs celery_worker
```

**Common errors and fixes:**

| Error | Service | Fix |
|-------|---------|-----|
| "pg_isready: connection refused" | postgres | `docker compose restart postgres` |
| "ECONNREFUSED" to postgres | backend | Wait for postgres to be fully ready |
| "ModuleNotFoundError" | backend | Rebuild: `docker compose up -d --build backend` |
| "Cannot connect to Redis" | celery_worker | `docker compose restart redis` |
| "ImportError" | any Python | Check requirements.txt installed |

---

## 🔌 Issue: "Cannot connect to backend API"

### Check Backend Status

```bash
# Is backend running?
docker compose ps backend

# Check backend logs
docker compose logs backend | tail -50

# Test health endpoint
curl http://localhost:8000/health
```

### Common Backend Errors

#### Error: "ModuleNotFoundError: No module named 'fastapi'"

**Fix:**
```bash
# Rebuild backend container
docker compose up -d --build backend

# Or install manually (if not using Docker)
cd backend
pip install -r requirements.txt
```

#### Error: "sqlalchemy.exc.OperationalError"

**Database connection failed**

**Fix:**
```bash
# Check DATABASE_URL in .env
cat .env | grep DATABASE_URL

# Should be: postgresql://newsadmin:PASSWORD@postgres:5432/news_intelligence

# Restart database
docker compose restart postgres

# Wait for it to be ready
docker compose exec postgres pg_isready -U newsadmin
```

#### Error: "Connection refused" on localhost:8000

**Backend not listening**

**Fix:**
```bash
# Check if port is bound
netstat -tuln | grep 8000

# Restart backend
docker compose restart backend

# Check logs for startup errors
docker compose logs backend
```

---

## 🗄️ Issue: "Database problems"

### Cannot connect to database

**Check:**
```bash
# Is PostgreSQL running?
docker compose ps postgres

# Can we connect?
docker compose exec postgres psql -U newsadmin -d news_intelligence -c "SELECT version();"
```

**Fix:**
```bash
# Restart PostgreSQL
docker compose restart postgres

# Check logs
docker compose logs postgres

# Verify data persists
docker volume ls | grep postgres_data
```

### Database is empty

**Check:**
```bash
# Count tables
docker compose exec postgres psql -U newsadmin -d news_intelligence -c "\dt"

# Count articles
docker compose exec postgres psql -U newsadmin -d news_intelligence -c "SELECT COUNT(*) FROM articles;"
```

**Fix:**
```bash
# Re-run initialization
docker compose exec postgres psql -U newsadmin -d news_intelligence -f /docker-entrypoint-initdb.d/init_db.sql

# Or recreate database
docker compose down
docker volume rm eu-intelligence-hub_postgres_data
docker compose up -d
```

### pgvector extension missing

**Check:**
```bash
docker compose exec postgres psql -U newsadmin -d news_intelligence -c "SELECT * FROM pg_extension WHERE extname = 'vector';"
```

**Fix:**
```bash
# Install pgvector
docker compose exec postgres psql -U newsadmin -d news_intelligence -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

---

## 🔄 Issue: "Celery tasks not processing"

### Check Celery Status

```bash
# Check worker
docker compose logs celery_worker | tail -50

# Check beat scheduler
docker compose logs celery_beat | tail -50

# Check Redis (broker)
docker compose exec redis redis-cli ping
# Should return: PONG
```

### View Task Queue

```bash
# Check if tasks are queued
docker compose exec redis redis-cli LLEN celery

# View queued tasks
docker compose exec redis redis-cli LRANGE celery 0 -1
```

### Force Task Execution

```bash
# Trigger news scraping manually
docker compose exec backend python -c "
from app.tasks.scraping import scrape_news
result = scrape_news.delay()
print(f'Task ID: {result.id}')
"

# Watch worker process it
docker compose logs -f celery_worker
```

### Reset Celery

```bash
# Flush all tasks
docker compose exec redis redis-cli FLUSHALL

# Restart workers
docker compose restart celery_worker celery_beat
```

---

## 🌐 Issue: "Frontend problems"

### Frontend won't load

**Check:**
```bash
# Is frontend running?
docker compose ps frontend

# Check logs
docker compose logs frontend | tail -50

# Test connection
curl http://localhost:3000
```

**Fix:**
```bash
# Restart frontend
docker compose restart frontend

# Rebuild (if React errors)
docker compose up -d --build frontend
```

### API calls fail from frontend

**Error:** "Network request failed" or CORS error

**Check:**
```bash
# Is REACT_APP_API_URL correct?
docker compose exec frontend printenv REACT_APP_API_URL
# Should be: http://localhost:8000
```

**Fix:**
```bash
# Update .env
echo "REACT_APP_API_URL=http://localhost:8000" >> .env

# Rebuild frontend
docker compose up -d --build frontend
```

---

## 🔑 Issue: "Gemini API problems"

### API key invalid

**Symptoms:**
- test_gemini_api.py fails
- Scraper logs show authentication errors

**Fix:**
```bash
# 1. Verify key format (should start with AIza)
cat .env | grep GEMINI_API_KEY

# 2. Get new key
# Visit: https://makersuite.google.com/app/apikey

# 3. Update .env
nano .env

# 4. Restart services
docker compose restart backend celery_worker
```

### Quota exceeded

**Error:** "Resource has been exhausted (e.g. check quota)"

**Check usage:**
- Visit: https://makersuite.google.com/app/apikey
- View quota limits

**Fix:**
```bash
# Option 1: Wait (free tier resets)
# - 60 requests/minute limit
# - 1,500 requests/day limit

# Option 2: Reduce scraping frequency
# Edit .env:
SCRAPING_INTERVAL_HOURS=2  # Change from 1 to 2

# Restart
docker compose restart celery_beat
```

---

## 🔍 Debugging Commands Reference

### View Logs

```bash
# All services
docker compose logs

# Specific service
docker compose logs backend
docker compose logs celery_worker
docker compose logs postgres

# Follow logs (live)
docker compose logs -f backend

# Last N lines
docker compose logs --tail=100 backend

# With timestamps
docker compose logs --timestamps backend
```

### Database Queries

```bash
# Connect to database
docker compose exec postgres psql -U newsadmin -d news_intelligence

# Quick queries:
# Count articles
SELECT COUNT(*) FROM articles;

# Count keywords
SELECT COUNT(*) FROM keywords;

# View recent articles
SELECT id, title, source, published_date FROM articles ORDER BY published_date DESC LIMIT 5;

# Check article-keyword associations
SELECT COUNT(*) FROM keyword_articles;

# Exit: \q
```

### Redis Inspection

```bash
# Connect to Redis
docker compose exec redis redis-cli

# Check connection
PING

# View Celery queue length
LLEN celery

# List all keys
KEYS *

# Exit: exit
```

### Service Restart

```bash
# Restart specific service
docker compose restart backend

# Restart multiple
docker compose restart backend celery_worker

# Restart all
docker compose restart

# Stop and start (full reset)
docker compose down
docker compose up -d
```

### Resource Monitoring

```bash
# Check container resource usage
docker stats

# Check disk space
docker system df

# Clean up unused resources
docker system prune
```

---

## 🚨 Emergency Reset

If everything is broken and you want to start fresh:

```bash
# ⚠️ WARNING: This deletes all data!

# 1. Stop all services
docker compose down

# 2. Remove volumes (deletes database)
docker volume rm eu-intelligence-hub_postgres_data
docker volume rm eu-intelligence-hub_redis_data

# 3. Clean Docker system
docker system prune -a

# 4. Rebuild and start
docker compose up -d --build

# 5. Wait for services
sleep 60

# 6. Run validation
python3 check_system_health.py
```

---

## 📋 Pre-Flight Checklist

Before reporting an issue, verify:

- [ ] .env file exists and has real Gemini API key
- [ ] Docker is installed and running
- [ ] All services are up: `docker compose ps`
- [ ] Backend health check passes: `curl http://localhost:8000/health`
- [ ] Database is accessible: `docker compose exec postgres pg_isready`
- [ ] Redis is accessible: `docker compose exec redis redis-cli ping`
- [ ] Celery worker is running: `docker compose logs celery_worker | grep ready`
- [ ] No port conflicts: `netstat -tuln | grep -E '(3000|5432|6379|8000)'`
- [ ] Validation script passes: `python3 validate_project.py`

---

## 🆘 Getting Help

If you're still stuck:

1. **Run full diagnostic:**
   ```bash
   python3 validate_project.py > diagnostic.txt
   python3 check_system_health.py >> diagnostic.txt
   docker compose logs > docker_logs.txt
   ```

2. **Check documentation:**
   - README.md - Project overview
   - INSTALLATION.md - Setup guide
   - DATA_FLOW_EXPLAINED.md - How data flows
   - PROJECT_VALIDATION_REPORT.md - Detailed validation

3. **Common issues solved:**
   - No results → Check DATA_FLOW_EXPLAINED.md
   - Services won't start → Check INSTALLATION.md
   - API errors → Check PROJECT_VALIDATION_REPORT.md

---

## 🎓 Understanding Log Messages

### Good Signs (Backend)

```
INFO:     Application startup complete
INFO:     Uvicorn running on http://0.0.0.0:8000
Database connection pool created successfully
```

### Good Signs (Celery Worker)

```
[2025-11-14 10:00:00] celery@... ready.
Connected to redis://redis:6379/0
```

### Good Signs (Celery Beat)

```
Scheduler: Sending due task scrape_news
Beat: Scheduler running...
```

### Warning Signs

```
WARNING: GEMINI_API_KEY not configured  ← Fix API key
WARNING: No articles scraped  ← API key issue
OperationalError: could not connect  ← Database down
ConnectionError: Redis  ← Redis down
```

### Error Signs

```
ModuleNotFoundError  ← Missing dependencies
ImportError  ← Package installation failed
sqlalchemy.exc.OperationalError  ← Database error
google.api_core.exceptions.InvalidArgument  ← API key invalid
```

---

**Last Updated:** 2025-11-14
**Version:** 1.0
