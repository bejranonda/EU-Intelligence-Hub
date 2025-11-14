# Quick Fix Guide - Get EU Intelligence Hub Working

**Problem:** Keyword search returns no results

**Root Cause:** Missing Gemini API key + Docker services not running

---

## 🔥 Critical Fix (Required)

### Step 1: Get Your Gemini API Key (5 minutes)

1. Go to: https://makersuite.google.com/app/apikey
2. Sign in with your Google account
3. Click **"Create API Key"** (free)
4. Copy the key (looks like: `AIzaSyD9X8kFq2...`)

### Step 2: Update .env File (1 minute)

```bash
cd /home/user/EU-Intelligence-Hub
nano .env
```

Find this line:
```
GEMINI_API_KEY=your_gemini_api_key_here
```

Replace with your actual key:
```
GEMINI_API_KEY=AIzaSyD9X8kFq2...your-key-here...Q3vN8
```

Save and exit (Ctrl+X, then Y, then Enter).

---

## 🐳 Install Docker (If Not Installed)

**Check if Docker is installed:**
```bash
docker --version
```

If you see "command not found", install Docker:

### Ubuntu/Debian:
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker
```

### macOS:
Download and install: https://www.docker.com/products/docker-desktop/

### Windows:
Download and install: https://www.docker.com/products/docker-desktop/

---

## 🚀 Start the Application (5 minutes)

```bash
cd /home/user/EU-Intelligence-Hub

# Start all services
docker compose up -d

# Wait for services to start (watch the logs)
docker compose logs -f

# When you see "Application startup complete", press Ctrl+C
```

---

## ✅ Verify Everything Works

### Run Validation Script:
```bash
python3 validate_project.py
```

You should see:
- ✅ PostgreSQL connection successful
- ✅ Redis connection successful
- ✅ Backend API is accessible
- ✅ Gemini API key is valid

### Access the Application:
- **Frontend:** http://localhost:3000
- **Backend API Docs:** http://localhost:8000/docs
- **Grafana Dashboard:** http://localhost:3001 (admin/admin)

---

## 🔍 Test Keyword Search

1. Open: http://localhost:3000
2. Click **"Suggest Keyword"**
3. Enter: "Thailand tourism"
4. Submit

5. Go to **Admin Panel** (if available) or wait for hourly auto-processing
6. Approve the keyword

7. Watch Celery worker process the search:
```bash
docker compose logs -f celery_worker
```

8. Wait 5-10 minutes for articles to be fetched
9. Search for "Thailand tourism" - you should now see results!

---

## 🐛 Quick Troubleshooting

### "Port already in use" error:
```bash
# Check what's using port 5432 (PostgreSQL)
sudo lsof -i :5432

# Stop the service and try again
sudo systemctl stop postgresql
docker compose up -d
```

### "Cannot connect to Docker daemon":
```bash
# Start Docker service
sudo systemctl start docker

# Or on macOS/Windows, start Docker Desktop
```

### "Permission denied" when running docker:
```bash
sudo usermod -aG docker $USER
newgrp docker
```

### Still no results after keyword search:
```bash
# Check if Celery worker is processing tasks
docker compose logs celery_worker | grep -i "search_keyword"

# Check if articles are in database
docker compose exec postgres psql -U newsadmin -d news_intelligence -c "SELECT COUNT(*) FROM articles;"

# If count is 0, check Gemini API logs
docker compose logs backend | grep -i "gemini"
```

---

## 📊 Monitor the System

### View all service status:
```bash
docker compose ps
```

### View specific service logs:
```bash
docker compose logs backend
docker compose logs postgres
docker compose logs celery_worker
docker compose logs redis
```

### Check database:
```bash
docker compose exec postgres psql -U newsadmin -d news_intelligence

# Run SQL queries:
# SELECT COUNT(*) FROM keywords;
# SELECT COUNT(*) FROM articles;
# SELECT * FROM keywords LIMIT 5;
# \q to exit
```

---

## 🎯 What Should Happen

**Normal Flow:**

1. User suggests keyword → Stored in `keyword_suggestions` table
2. Admin approves → Triggers immediate search OR
3. Hourly cron job → Scrapes news from 12 European sources
4. Gemini API → Fetches recent articles about the keyword
5. Backend processes → Extracts sentiment, keywords, entities
6. Stores in database → `articles` and `keyword_articles` tables
7. Frontend queries → Displays results with sentiment analysis

**Timeline:**
- Immediate search (manual): 5-10 minutes
- Hourly auto-scraping: Next :00 hour (e.g., 14:00, 15:00)
- Keyword cooldown: 3 hours between searches for same keyword

---

## 📝 Summary Checklist

- [ ] Got Gemini API key from https://makersuite.google.com/app/apikey
- [ ] Updated `.env` file with real API key
- [ ] Installed Docker
- [ ] Ran `docker compose up -d`
- [ ] All services show "Up" in `docker compose ps`
- [ ] Frontend loads at http://localhost:3000
- [ ] Backend API responds at http://localhost:8000/health
- [ ] Validation script passes all checks
- [ ] Created test keyword
- [ ] Waited for processing
- [ ] Search returns results

---

## 🆘 Still Having Issues?

1. **Read the full report:**
   ```bash
   cat PROJECT_VALIDATION_REPORT.md
   ```

2. **Check service health:**
   ```bash
   docker compose exec backend curl http://localhost:8000/api/health/detailed
   ```

3. **Verify Gemini API key:**
   - Make sure no typos in `.env`
   - No spaces around the `=` sign
   - Key starts with `AIza`
   - Key is not wrapped in quotes

4. **Restart everything:**
   ```bash
   docker compose down
   docker compose up -d
   python3 validate_project.py
   ```

---

**Need more details?** See `PROJECT_VALIDATION_REPORT.md` for comprehensive troubleshooting.
