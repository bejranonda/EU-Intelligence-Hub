# Error Logging & Monitoring Guide

## Overview

This guide explains where to find error logs, how to monitor the system, and how to troubleshoot issues in the European News Intelligence Hub.

---

## Quick Reference: Log Commands

```bash
# View all services logs
docker compose logs

# Follow logs in real-time (all services)
docker compose logs -f

# Backend API logs
docker compose logs backend -f

# Celery worker logs
docker compose logs celery_worker -f

# Celery beat scheduler logs
docker compose logs celery_beat -f

# Database logs
docker compose logs postgres

# Redis logs
docker compose logs redis

# Frontend logs
docker compose logs frontend
```

---

## 1. Backend API Logs

### View Backend Logs

```bash
# Last 100 lines
docker compose logs backend --tail 100

# Real-time monitoring
docker compose logs backend -f

# Search for errors
docker compose logs backend | grep -i error

# Search for specific keyword
docker compose logs backend | grep "Singapore"

# Last 24 hours with timestamps
docker compose logs backend --since 24h
```

### Log Levels

The backend uses Python's logging module with these levels:
- **DEBUG**: Detailed information for debugging
- **INFO**: General informational messages
- **WARNING**: Warning messages (non-critical issues)
- **ERROR**: Error messages (failures)
- **CRITICAL**: Critical errors (system failures)

### Common Backend Errors

#### API Request Errors
```bash
# View HTTP errors (404, 500, etc.)
docker compose logs backend | grep "HTTP/1.1" | grep -E "4[0-9]{2}|5[0-9]{2}"
```

#### Database Connection Errors
```bash
docker compose logs backend | grep -i "database\|postgres\|connection"
```

#### Gemini API Errors
```bash
docker compose logs backend | grep -i "gemini\|api"
```

### Backend Log File Locations

Inside the container:
```bash
# Access backend container
docker compose exec backend bash

# View logs
tail -f /var/log/*.log  # If configured
python -m pip list  # Check installed packages
```

---

## 2. Celery Worker Logs

### View Celery Worker Logs

```bash
# Real-time worker logs
docker compose logs celery_worker -f

# Search for task failures
docker compose logs celery_worker | grep -i "failed\|error\|exception"

# View specific task execution
docker compose logs celery_worker | grep "scrape_news"
docker compose logs celery_worker | grep "search_keyword_immediately"

# Check task success rate
docker compose logs celery_worker | grep -E "succeeded|failed"
```

### Celery Task States

- **PENDING**: Task waiting to be executed
- **STARTED**: Task execution started
- **SUCCESS**: Task completed successfully
- **FAILURE**: Task failed with error
- **RETRY**: Task being retried
- **REVOKED**: Task cancelled

### Monitor Specific Tasks

```bash
# News scraping task
docker compose logs celery_worker | grep "app.tasks.scraping.scrape_news"

# Immediate keyword search
docker compose logs celery_worker | grep "search_keyword_immediately"

# Sentiment aggregation
docker compose logs celery_worker | grep "aggregate_daily_sentiment"

# Keyword processing
docker compose logs celery_worker | grep "process_pending_suggestions"
```

### Celery Worker Errors

```bash
# View all errors
docker compose logs celery_worker | grep ERROR

# View task timeouts
docker compose logs celery_worker | grep -i "timeout\|time limit"

# View connection issues
docker compose logs celery_worker | grep -i "connection\|redis\|broker"
```

---

## 3. Celery Beat Scheduler Logs

### View Beat Logs

```bash
# Real-time beat scheduler logs
docker compose logs celery_beat -f

# Check scheduled tasks
docker compose logs celery_beat | grep -i "scheduler"

# View task dispatch
docker compose logs celery_beat | grep "Sending due task"
```

### Scheduled Task Monitoring

```bash
# See what tasks are scheduled
docker compose logs celery_beat | grep "beat: Starting"

# Check task execution times
docker compose logs celery_beat | grep -E "scrape-news|aggregate-sentiment|process-keyword"
```

---

## 4. Database Logs

### PostgreSQL Logs

```bash
# View database logs
docker compose logs postgres

# Connection errors
docker compose logs postgres | grep -i "error\|fatal"

# Slow queries
docker compose logs postgres | grep -i "slow"

# Connection attempts
docker compose logs postgres | grep -i "connection"
```

### Database Error Messages

Common PostgreSQL errors:
- `FATAL: role does not exist` - User/role issue
- `FATAL: database does not exist` - Database not created
- `ERROR: relation does not exist` - Table missing
- `ERROR: column does not exist` - Schema mismatch

### Check Database Health

```bash
# Access database
docker compose exec postgres psql -U euint_user -d euint_dev

# Check connections
SELECT count(*) FROM pg_stat_activity;

# Check table sizes
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename))
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

# Check recent errors (if pg_stat_statements enabled)
SELECT * FROM pg_stat_statements WHERE calls > 0 ORDER BY mean_exec_time DESC LIMIT 10;
```

---

## 5. Redis Logs

### View Redis Logs

```bash
# Redis logs
docker compose logs redis

# Connection issues
docker compose logs redis | grep -i "error\|connection"

# Memory issues
docker compose logs redis | grep -i "memory\|oom"
```

### Redis Monitoring

```bash
# Access Redis CLI
docker compose exec redis redis-cli

# Check Redis status
INFO

# Check memory usage
INFO memory

# Check connected clients
CLIENT LIST

# Monitor commands in real-time
MONITOR
```

---

## 6. Frontend Logs

### View Frontend Logs

```bash
# Frontend server logs
docker compose logs frontend -f

# Build errors
docker compose logs frontend | grep -i "error\|failed"

# React errors
docker compose logs frontend | grep -i "warning\|error"
```

### Browser Console

For frontend runtime errors:
1. Open browser DevTools (F12)
2. Go to Console tab
3. Look for JavaScript errors

Common frontend errors:
- API connection errors: Check Network tab
- CORS errors: Check browser console
- React warnings: Check console during development

---

## 7. Application-Level Logging

### Python Application Logs

The application uses structured logging throughout:

```python
import logging
logger = logging.getLogger(__name__)

logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical message")
```

### Log Locations by Module

#### Scraping Service Logs
```bash
docker compose logs backend | grep "app.services.scraper"
docker compose logs celery_worker | grep "app.tasks.scraping"
```

#### Sentiment Analysis Logs
```bash
docker compose logs backend | grep "app.services.sentiment"
docker compose logs celery_worker | grep "sentiment"
```

#### Keyword Approval Logs
```bash
docker compose logs backend | grep "app.services.keyword_approval"
docker compose logs celery_worker | grep "keyword_management"
```

#### Gemini API Logs
```bash
docker compose logs backend | grep "app.services.gemini_client"
docker compose logs celery_worker | grep "gemini"
```

---

## 8. Production Logging (Docker Compose)

### Log Rotation

Configure log rotation in `docker-compose.yml`:

```yaml
services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### Centralized Logging

For production, consider centralized logging:

#### Using Loki + Grafana

```bash
# Add to docker-compose.prod.yml
loki:
  image: grafana/loki:latest
  ports:
    - "3100:3100"

grafana:
  image: grafana/grafana:latest
  ports:
    - "3001:3000"
```

#### Using ELK Stack

```bash
# Elasticsearch + Logstash + Kibana
elasticsearch:
  image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0

logstash:
  image: docker.elastic.co/logstash/logstash:8.11.0

kibana:
  image: docker.elastic.co/kibana/kibana:8.11.0
```

---

## 9. Error Monitoring Tools

### Health Check Endpoint

```bash
# Check system health
curl http://localhost:8000/health

# Expected response
{
  "status": "healthy",
  "database": "healthy",
  "environment": "development"
}
```

### API Documentation

View all endpoints and test them:
```bash
# Swagger UI
http://localhost:8000/docs

# ReDoc
http://localhost:8000/redoc
```

### Monitoring Scripts

Use the provided health check script:

```bash
# Run health check
./scripts/health_check.sh

# Output shows:
# ✅ Docker running
# ✅ PostgreSQL healthy
# ✅ Redis healthy
# ✅ Backend API responding
# ✅ Frontend responding
```

---

## 10. Common Error Scenarios

### Scenario 1: Backend Won't Start

**Symptoms:**
```bash
docker compose ps
# Shows backend as "unhealthy" or "restarting"
```

**Diagnosis:**
```bash
# Check logs
docker compose logs backend --tail 50

# Common issues:
# - Import errors
# - Database connection failed
# - Missing environment variables
```

**Solution:**
```bash
# Restart services
docker compose restart backend

# Rebuild if code changed
docker compose up -d --build backend
```

---

### Scenario 2: Celery Tasks Not Running

**Symptoms:**
- Scheduled tasks not executing
- No news articles being scraped

**Diagnosis:**
```bash
# Check Celery worker status
docker compose logs celery_worker | grep -i "ready"

# Check Celery beat
docker compose logs celery_beat | grep "beat: Starting"

# Check Redis connection
docker compose exec celery_worker celery -A app.tasks.celery_app inspect active
```

**Solution:**
```bash
# Restart Celery services
docker compose restart celery_worker celery_beat

# Clear Redis cache if needed
docker compose exec redis redis-cli FLUSHALL
```

---

### Scenario 3: Database Connection Errors

**Symptoms:**
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Diagnosis:**
```bash
# Check database status
docker compose ps postgres

# Check connection
docker compose exec backend python -c "from app.database import engine; engine.connect()"
```

**Solution:**
```bash
# Restart database
docker compose restart postgres

# Wait for database to be ready
docker compose exec postgres pg_isready -U euint_user
```

---

### Scenario 4: Gemini API Errors

**Symptoms:**
```
ERROR: Error calling Gemini API: 429 Too Many Requests
ERROR: Gemini API key invalid
```

**Diagnosis:**
```bash
# Check API key
docker compose exec backend env | grep GEMINI_API_KEY

# Check rate limiting
docker compose logs backend | grep "Rate limit"
```

**Solution:**
```bash
# Update .env file with valid API key
# Restart backend
docker compose restart backend celery_worker
```

---

## 11. Log Analysis Commands

### Find Errors in Last Hour

```bash
docker compose logs backend --since 1h | grep ERROR
```

### Count Errors by Service

```bash
docker compose logs | grep ERROR | awk '{print $1}' | sort | uniq -c
```

### Search for Specific Error

```bash
docker compose logs | grep -C 5 "KeyError\|AttributeError\|ImportError"
```

### Export Logs to File

```bash
# All logs
docker compose logs > logs_$(date +%Y%m%d_%H%M%S).txt

# Specific service
docker compose logs backend > backend_logs_$(date +%Y%m%d_%H%M%S).txt

# Errors only
docker compose logs | grep ERROR > errors_$(date +%Y%m%d_%H%M%S).txt
```

### Monitor Multiple Services

```bash
# Watch multiple services
watch -n 5 'docker compose ps && docker compose logs --tail 5 backend celery_worker'
```

---

## 12. Production Monitoring Setup

### Using Prometheus + Grafana

**Install Prometheus exporter:**

```python
# requirements.txt
prometheus-client==0.19.0

# main.py
from prometheus_client import Counter, Histogram, generate_latest

api_requests = Counter('api_requests_total', 'Total API requests')
api_latency = Histogram('api_latency_seconds', 'API latency')

@app.get("/metrics")
def metrics():
    return generate_latest()
```

### Using Sentry for Error Tracking

```python
# requirements.txt
sentry-sdk==1.40.0

# main.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[FastApiIntegration()],
    traces_sample_rate=1.0,
)
```

### Email Alerts on Errors

Create a simple alerting script:

```bash
#!/bin/bash
# scripts/alert_on_errors.sh

ERROR_COUNT=$(docker compose logs backend --since 5m | grep ERROR | wc -l)

if [ $ERROR_COUNT -gt 10 ]; then
    echo "High error rate detected: $ERROR_COUNT errors in last 5 minutes" | \
    mail -s "Alert: High Error Rate" admin@example.com
fi
```

Run as cron job:
```bash
*/5 * * * * /path/to/alert_on_errors.sh
```

---

## 13. Debugging Tips

### Enable Debug Logging

**Temporary (current session):**
```bash
# In backend container
docker compose exec backend python
>>> import logging
>>> logging.getLogger().setLevel(logging.DEBUG)
```

**Permanent (environment variable):**
```bash
# .env file
LOG_LEVEL=DEBUG

# docker-compose.yml
environment:
  - LOG_LEVEL=${LOG_LEVEL:-INFO}
```

### Python Debugger (pdb)

```python
# Add to code where you want to debug
import pdb; pdb.set_trace()

# Then attach to container
docker compose exec backend python
```

### Interactive Shell

```bash
# Backend Python shell
docker compose exec backend python

# Import and test
>>> from app.services.scraper import scrape_news_sync
>>> articles = scrape_news_sync(max_articles=1)
>>> print(articles)

# Database shell
docker compose exec backend python
>>> from app.database import SessionLocal
>>> db = SessionLocal()
>>> from app.models.models import Keyword
>>> keywords = db.query(Keyword).all()
>>> print(len(keywords))
```

---

## 14. Log Dashboard (Quick Setup)

Create a simple log dashboard:

```bash
#!/bin/bash
# scripts/log_dashboard.sh

echo "=== European News Intelligence Hub - Log Dashboard ==="
echo ""
echo "📊 Container Status:"
docker compose ps
echo ""
echo "🔴 Recent Errors (last 5 minutes):"
docker compose logs --since 5m | grep ERROR | tail -10
echo ""
echo "✅ Recent Success (last 5 minutes):"
docker compose logs celery_worker --since 5m | grep "succeeded" | tail -5
echo ""
echo "📈 Task Queue:"
docker compose exec redis redis-cli LLEN celery
echo ""
echo "💾 Database Connections:"
docker compose exec postgres psql -U euint_user -d euint_dev -c "SELECT count(*) FROM pg_stat_activity;"
```

Run it:
```bash
chmod +x scripts/log_dashboard.sh
./scripts/log_dashboard.sh
```

---

## 15. Support & Troubleshooting

### Get Help

1. **Check logs first**: 90% of issues can be diagnosed from logs
2. **Check health endpoint**: Verify services are running
3. **Review documentation**: [README.md](README.md), [DEPLOYMENT.md](DEPLOYMENT.md)
4. **Check GitHub Issues**: https://github.com/your-repo/issues

### Common Log Locations Summary

| Service | Command | Location |
|---------|---------|----------|
| Backend API | `docker compose logs backend` | stdout/stderr |
| Celery Worker | `docker compose logs celery_worker` | stdout/stderr |
| Celery Beat | `docker compose logs celery_beat` | stdout/stderr |
| PostgreSQL | `docker compose logs postgres` | stdout/stderr |
| Redis | `docker compose logs redis` | stdout/stderr |
| Frontend | `docker compose logs frontend` | stdout/stderr |
| All Services | `docker compose logs` | stdout/stderr |

### Emergency Commands

```bash
# Stop everything
docker compose down

# Start fresh (removes volumes - BE CAREFUL)
docker compose down -v && docker compose up -d

# Restart specific service
docker compose restart [service_name]

# View container resource usage
docker stats

# Clean up old logs
docker system prune -a
```

---

**Last Updated**: 2025-10-16
**Version**: 1.0
