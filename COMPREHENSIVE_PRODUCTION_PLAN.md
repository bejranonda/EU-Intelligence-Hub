# Comprehensive Production Readiness & Debugging Plan
## EU Intelligence Hub - European News Intelligence Platform

**Date**: 2025-10-20
**Current Status**: Phase 5 Complete, Ready for Production Testing
**Target**: Full Production Deployment with Zero Downtime

---

## Executive Summary

Based on comprehensive analysis of the codebase, this project is **95% production-ready** with the following status:

- ✅ **Architecture**: Well-designed, enterprise-grade microservices architecture
- ✅ **Code Quality**: 42 Python files, 22 TypeScript files - all syntax valid
- ✅ **Security**: Comprehensive security measures implemented
- ✅ **Monitoring**: Prometheus + Grafana + Alertmanager configured
- ⚠️ **Testing**: Backend tests exist but need execution validation
- ⚠️ **Services**: Docker stack not currently running - needs startup
- ⚠️ **Database**: Migration files present but need validation

**Critical Path**: 7 phases from current state to production deployment

---

## Current State Analysis

### ✅ Strengths

1. **Comprehensive Documentation**
   - 20+ markdown documentation files covering all aspects
   - Clear installation, deployment, and troubleshooting guides
   - Security checklist and best practices documented

2. **Robust Architecture**
   - 10 Docker services with health checks
   - Proper service dependencies and orchestration
   - Separate dev/staging/production configurations

3. **AI/ML Integration**
   - Gemini API with rate limiting and fallback mechanisms
   - Sentence Transformers for embeddings
   - VADER + Gemini dual-layer sentiment analysis
   - spaCy for NER and keyword extraction

4. **Security Implementation**
   - Environment variable externalization
   - CORS configuration
   - Rate limiting (Nginx + application level)
   - Security headers middleware
   - SSL/TLS support with Let's Encrypt

5. **Monitoring & Observability**
   - Prometheus metrics collection
   - Grafana dashboards
   - Alertmanager for notifications
   - Structured logging with python-json-logger
   - Health check endpoints

### ⚠️ Areas Requiring Attention

1. **Services Not Running**
   - Docker containers are currently stopped
   - Need to start and validate all services

2. **Database Migrations**
   - 5 SQL migration files in `/backend/migrations/`
   - No Alembic configuration (directory empty)
   - Migrations need to be applied and validated

3. **Test Execution**
   - 49 tests documented but execution status unknown
   - Need to run full test suite and verify coverage
   - Frontend tests not validated

4. **Environment Configuration**
   - `.env` file has 32 configured variables
   - GEMINI_API_KEY needs validation
   - Production secrets need rotation

5. **Dependencies**
   - 18+ outdated Python packages identified
   - Need security audit and updates
   - `react-flow-renderer` deprecated (use `reactflow`)

6. **Data Initialization**
   - No seed data for keywords
   - Empty database needs initial content
   - News sources need to be configured

---

## Phase-by-Phase Production Readiness Plan

### 🔴 PHASE 1: Environment Setup & Validation (CRITICAL)
**Objective**: Get all services running and healthy
**Duration**: 2-3 hours
**Priority**: CRITICAL

#### Tasks:

1. **Verify System Prerequisites**
   ```bash
   # Check Docker installation
   docker --version
   docker compose version

   # Check system resources
   free -h  # Need 4GB+ RAM
   df -h    # Need 10GB+ disk space
   ```

2. **Configure Environment Variables**
   ```bash
   # Verify .env configuration
   cat .env | grep -E "GEMINI_API_KEY|POSTGRES_PASSWORD|SECRET_KEY"

   # Generate secure secrets if needed
   python3 -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

3. **Start Docker Services**
   ```bash
   # Start all services
   docker compose up -d

   # Verify all services are healthy
   docker compose ps

   # Expected: All services showing "healthy" or "running"
   ```

4. **Validate Service Health**
   ```bash
   # Test PostgreSQL
   docker compose exec postgres pg_isready -U ${POSTGRES_USER}

   # Test Redis
   docker compose exec redis redis-cli ping

   # Test Backend API
   curl http://localhost:8000/health

   # Test Frontend
   curl http://localhost:3000
   ```

5. **Check Logs for Errors**
   ```bash
   # Backend logs
   docker compose logs backend | grep -i error

   # Celery worker logs
   docker compose logs celery_worker | grep -i error

   # Database logs
   docker compose logs postgres | grep -i error
   ```

#### Success Criteria:
- ✅ All 10 Docker containers running
- ✅ All health checks passing
- ✅ No errors in service logs
- ✅ Backend API responding on port 8000
- ✅ Frontend accessible on port 3000
- ✅ Prometheus metrics available on port 9090
- ✅ Grafana accessible on port 3001

#### Debugging Steps if Services Fail:

**If PostgreSQL fails to start:**
```bash
# Check volume permissions
ls -la postgres_data/

# Remove and recreate volume if corrupted
docker compose down
docker volume rm euint_postgres_data
docker compose up -d postgres
```

**If Backend fails to start:**
```bash
# Check for Python errors
docker compose logs backend --tail 100

# Common issues:
# - Missing dependencies: Rebuild image
# - Database connection: Verify DATABASE_URL
# - Import errors: Check app/main.py
```

**If Celery fails:**
```bash
# Verify Redis connection
docker compose exec redis redis-cli ping

# Check Celery configuration
docker compose logs celery_worker --tail 50

# Verify task registration
docker compose exec celery_worker celery -A app.tasks.celery_app inspect registered
```

---

### 🟠 PHASE 2: Database Validation & Migration (HIGH)
**Objective**: Ensure database schema is correct and complete
**Duration**: 1-2 hours
**Priority**: HIGH

#### Tasks:

1. **Verify Database Schema**
   ```bash
   # Connect to PostgreSQL
   docker compose exec postgres psql -U ${POSTGRES_USER} -d ${POSTGRES_DB}

   # List all tables
   \dt

   # Expected tables:
   # - keywords
   # - articles
   # - keyword_articles
   # - keyword_relations
   # - keyword_suggestions
   # - documents
   # - sentiment_trends
   # - comparative_sentiment
   # - news_sources
   # - keyword_search_queue
   # - source_ingestion_history
   ```

2. **Check pgvector Extension**
   ```sql
   # In psql
   SELECT * FROM pg_extension WHERE extname = 'vector';

   # Should return one row with version info
   ```

3. **Apply Pending Migrations**
   ```bash
   # Check migration files
   ls -la backend/migrations/

   # Apply each migration manually (since no Alembic)
   for file in backend/migrations/*.sql; do
     echo "Applying $file"
     docker compose exec postgres psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} -f /app/migrations/$(basename $file)
   done
   ```

4. **Validate Table Structures**
   ```sql
   # Check keywords table
   \d keywords
   # Should have: embedding vector(384) column

   # Check articles table
   \d articles
   # Should have: 6 sentiment fields + embedding

   # Check indexes
   \di
   # Should have indexes on frequently queried columns
   ```

5. **Initialize Seed Data**
   ```bash
   # Run keyword initialization script
   docker compose exec backend python /app/scripts/init_keywords.py

   # Verify keywords were created
   docker compose exec postgres psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} -c "SELECT COUNT(*) FROM keywords;"
   ```

#### Success Criteria:
- ✅ All required tables exist
- ✅ pgvector extension installed
- ✅ All migrations applied successfully
- ✅ Indexes created for performance
- ✅ Seed data loaded
- ✅ No foreign key constraint violations

#### Debugging Steps:

**If tables are missing:**
```bash
# Rerun init_db.sql
docker compose exec postgres psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} -f /docker-entrypoint-initdb.d/init_db.sql
```

**If pgvector fails:**
```bash
# Check PostgreSQL logs
docker compose logs postgres | grep vector

# Rebuild postgres container with pgvector
docker compose down postgres
docker compose up -d postgres
```

**If migrations fail:**
```bash
# Check for duplicate entries
# Modify migration to use IF NOT EXISTS
# Or manually fix conflicts in database
```

---

### 🟡 PHASE 3: Comprehensive Testing (MEDIUM-HIGH)
**Objective**: Validate all functionality works correctly
**Duration**: 2-4 hours
**Priority**: MEDIUM-HIGH

#### Tasks:

1. **Run Backend Unit Tests**
   ```bash
   # Run all tests with coverage
   docker compose exec backend pytest app/tests/ -v --cov=app --cov-report=html

   # Expected: All 49 tests passing, >80% coverage
   ```

2. **Test API Endpoints**
   ```bash
   # Health check
   curl http://localhost:8000/health

   # API documentation
   curl http://localhost:8000/docs

   # Test keyword search
   curl "http://localhost:8000/api/keywords?limit=10"

   # Test sentiment endpoint
   curl "http://localhost:8000/api/sentiment/keywords/1/sentiment"
   ```

3. **Test Celery Tasks**
   ```bash
   # Check registered tasks
   docker compose exec celery_worker celery -A app.tasks.celery_app inspect registered

   # Manually trigger scraping task (test mode)
   docker compose exec backend python -c "from app.tasks.scraping import scrape_news; scrape_news.delay()"

   # Check task execution
   docker compose logs celery_worker -f
   ```

4. **Test AI Services**
   ```bash
   # Test Gemini API connection
   docker compose exec backend python -c "
   from app.services.gemini_client import get_gemini_client
   client = get_gemini_client()
   print('Gemini client initialized:', client is not None)
   "

   # Test sentiment analysis
   docker compose exec backend python -c "
   from app.services.sentiment import SentimentAnalyzer
   analyzer = SentimentAnalyzer()
   result = analyzer.analyze_article('Test', 'This is a positive article', 'BBC')
   print('Sentiment:', result)
   "
   ```

5. **Frontend Testing**
   ```bash
   # Access frontend
   open http://localhost:3000

   # Check browser console for errors
   # Test key workflows:
   # - Search keywords
   # - View keyword details
   # - View sentiment timeline
   # - Submit keyword suggestion
   # - Upload document
   ```

6. **Load Testing**
   ```bash
   # Run Locust load test
   docker compose exec backend locust -f /app/locustfile.py --host=http://backend:8000 --users 10 --spawn-rate 2 --run-time 60s --headless

   # Monitor performance
   docker compose exec prometheus curl http://prometheus:9090/api/v1/query?query=up
   ```

#### Success Criteria:
- ✅ All 49 backend tests pass
- ✅ All API endpoints respond correctly
- ✅ Celery tasks execute successfully
- ✅ AI services (Gemini, VADER, spaCy) working
- ✅ Frontend loads without errors
- ✅ All user workflows functional
- ✅ Load test shows acceptable performance (<500ms p95)

#### Debugging Steps:

**If tests fail:**
```bash
# Run specific test file with verbose output
docker compose exec backend pytest app/tests/test_api_endpoints.py -v -s

# Check test database connection
docker compose exec backend pytest app/tests/test_database.py -v

# Review test fixtures
cat backend/app/testing/fixtures.py
```

**If Gemini API fails:**
```bash
# Verify API key
echo $GEMINI_API_KEY

# Check rate limiting
docker compose logs backend | grep -i gemini

# Test with fallback (VADER only)
# Set ENABLE_GEMINI_SENTIMENT=false in .env temporarily
```

**If frontend errors occur:**
```bash
# Check frontend logs
docker compose logs frontend

# Verify API connection
curl http://localhost:8000/api/keywords

# Check CORS configuration
# View Network tab in browser DevTools
```

---

### 🟢 PHASE 4: Performance Optimization (MEDIUM)
**Objective**: Optimize for production load
**Duration**: 2-3 hours
**Priority**: MEDIUM

#### Tasks:

1. **Database Performance**
   ```sql
   -- Add missing indexes
   CREATE INDEX IF NOT EXISTS idx_articles_published_date ON articles(published_date);
   CREATE INDEX IF NOT EXISTS idx_articles_sentiment ON articles(sentiment_overall);
   CREATE INDEX IF NOT EXISTS idx_keywords_popularity ON keywords(popularity_score DESC);
   CREATE INDEX IF NOT EXISTS idx_keyword_articles_relevance ON keyword_articles(relevance_score DESC);

   -- Analyze query performance
   EXPLAIN ANALYZE SELECT * FROM articles WHERE sentiment_overall > 0.5 ORDER BY published_date DESC LIMIT 10;
   ```

2. **Redis Caching**
   ```python
   # Verify cache configuration in app/cache.py
   # Test cache functionality
   docker compose exec backend python -c "
   from app.cache import get_redis_client
   redis_client = get_redis_client()
   redis_client.setex('test_key', 60, 'test_value')
   print('Cache test:', redis_client.get('test_key'))
   "
   ```

3. **API Response Time**
   ```bash
   # Measure endpoint response times
   time curl -s http://localhost:8000/api/keywords?limit=100 > /dev/null

   # Should be < 200ms for simple queries
   # Should be < 1000ms for complex queries with embeddings
   ```

4. **Embedding Generation**
   ```bash
   # Test embedding performance
   docker compose exec backend python -c "
   import time
   from app.services.embeddings import EmbeddingGenerator
   gen = EmbeddingGenerator()
   start = time.time()
   embedding = gen.generate_embedding('Test text for embedding generation')
   print(f'Embedding generation took: {time.time() - start:.3f}s')
   # Should be < 0.1s per embedding
   "
   ```

5. **Celery Task Optimization**
   ```bash
   # Monitor task execution times
   docker compose exec celery_worker celery -A app.tasks.celery_app events

   # Check for slow tasks
   docker compose logs celery_worker | grep "Task.*succeeded" | awk '{print $NF}' | sort -n
   ```

#### Success Criteria:
- ✅ Database queries < 200ms (simple), < 1s (complex)
- ✅ Cache hit rate > 80% for frequent queries
- ✅ API p95 response time < 500ms
- ✅ Embedding generation < 100ms per text
- ✅ Celery tasks complete within expected time
- ✅ No memory leaks (stable memory usage over time)

#### Optimization Recommendations:

1. **Database**
   - Add indexes on frequently queried columns
   - Use EXPLAIN ANALYZE to identify slow queries
   - Consider connection pooling adjustments
   - Enable query caching for repeated queries

2. **Caching Strategy**
   ```python
   # Cache frequently accessed data:
   # - Keyword lists (5 min TTL)
   # - Sentiment aggregations (1 hour TTL)
   # - Article embeddings (indefinite)
   # - API responses (1 min TTL for public endpoints)
   ```

3. **API Optimization**
   - Implement pagination for all list endpoints
   - Use database-level aggregations instead of Python loops
   - Lazy load relationships in SQLAlchemy
   - Compress responses with gzip

4. **Background Tasks**
   - Batch process embeddings (10-50 at a time)
   - Use task priorities for time-sensitive operations
   - Implement task retries with exponential backoff

---

### 🔵 PHASE 5: Security Hardening (HIGH)
**Objective**: Ensure production-grade security
**Duration**: 2-3 hours
**Priority**: HIGH

#### Tasks:

1. **Environment Variable Security**
   ```bash
   # Verify no secrets in git
   git log --all --full-history --source -- .env .env.production
   # Should return nothing

   # Check file permissions
   ls -la .env* | grep -E "^-rw-------"
   # Should be 600 (owner read/write only)

   # Rotate all secrets
   # Generate new SECRET_KEY
   python3 -c "import secrets; print(secrets.token_urlsafe(64))"

   # Generate new passwords
   python3 -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **SSL/TLS Configuration**
   ```bash
   # Install certbot certificates (if deploying to production)
   ./setup-ssl.sh yourdomain.com

   # Verify SSL configuration
   curl -I https://yourdomain.com
   # Should return 200 with security headers

   # Test SSL strength
   # Use: https://www.ssllabs.com/ssltest/
   ```

3. **CORS Configuration**
   ```python
   # Review app/main.py CORS settings
   # Ensure only necessary origins are allowed
   # Remove wildcard (*) if present
   # Add production domain
   ```

4. **Rate Limiting**
   ```bash
   # Test rate limiting
   for i in {1..100}; do curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8000/api/keywords; done

   # Should see 429 (Too Many Requests) after limit exceeded
   ```

5. **Input Validation**
   ```bash
   # Test with malicious input
   curl -X POST http://localhost:8000/api/suggestions/ \
     -H "Content-Type: application/json" \
     -d '{"keyword_en":"<script>alert(1)</script>","category":"test"}'

   # Should reject or sanitize input
   ```

6. **SQL Injection Prevention**
   ```bash
   # Test with SQL injection attempts
   curl "http://localhost:8000/api/keywords?search='; DROP TABLE keywords; --"

   # Should be prevented by SQLAlchemy parameterized queries
   ```

7. **Dependency Security Audit**
   ```bash
   # Backend security audit
   docker compose exec backend pip-audit

   # Frontend security audit
   docker compose exec frontend npm audit

   # Fix high/critical vulnerabilities
   npm audit fix
   ```

#### Success Criteria:
- ✅ No secrets in git history
- ✅ SSL/TLS certificate valid and strong
- ✅ CORS configured with minimal necessary origins
- ✅ Rate limiting functional on all endpoints
- ✅ Input validation prevents XSS attacks
- ✅ SQL injection prevented
- ✅ No high/critical security vulnerabilities in dependencies
- ✅ Security headers present (X-Frame-Options, CSP, etc.)

#### Security Checklist:

- [ ] All secrets rotated and stored securely
- [ ] SSL certificate installed and auto-renewal configured
- [ ] CORS origins restricted to production domains
- [ ] Rate limiting tested and functional
- [ ] Input validation on all user inputs
- [ ] SQL injection prevention verified
- [ ] XSS prevention verified
- [ ] CSRF protection enabled (if using forms)
- [ ] Security headers configured in Nginx
- [ ] Firewall rules configured (ports 22, 80, 443 only)
- [ ] SSH key authentication enabled, password auth disabled
- [ ] Database backups encrypted
- [ ] Logs not exposing sensitive information
- [ ] Admin endpoints protected with authentication
- [ ] API documentation secured in production

---

### 🟣 PHASE 6: Monitoring & Alerting Setup (MEDIUM)
**Objective**: Ensure visibility into system health
**Duration**: 2-3 hours
**Priority**: MEDIUM

#### Tasks:

1. **Configure Prometheus Metrics**
   ```bash
   # Verify Prometheus is scraping targets
   curl http://localhost:9090/api/v1/targets

   # Should show all exporters as "up":
   # - backend (port 8000)
   # - postgres_exporter (port 9187)
   # - redis_exporter (port 9121)
   # - node_exporter (port 9100)
   ```

2. **Setup Grafana Dashboards**
   ```bash
   # Access Grafana
   open http://localhost:3001

   # Login with credentials from .env
   # Import dashboards from monitoring/grafana/provisioning/dashboards/

   # Verify data sources connected
   # Check: Prometheus data source showing metrics
   ```

3. **Configure Alert Rules**
   ```yaml
   # Edit monitoring/alert_rules.yml
   # Add critical alerts:
   # - Service down (any container unhealthy > 1 min)
   # - High error rate (>5% of requests failing)
   # - Database connection pool exhausted
   # - Celery queue backed up (>100 pending tasks)
   # - Disk space low (<10% free)
   # - Memory usage high (>90%)
   ```

4. **Setup Alertmanager Notifications**
   ```yaml
   # Edit monitoring/alertmanager.yml
   # Configure notification channels:
   # - Email
   # - Slack webhook
   # - PagerDuty (if using)

   # Test alert notification
   docker compose exec prometheus promtool check rules /etc/prometheus/rules/alert_rules.yml
   ```

5. **Configure Log Aggregation**
   ```bash
   # Verify structured logging
   docker compose logs backend --tail 100 | grep -E '^\{.*\}$'
   # Should show JSON-formatted logs

   # Setup log rotation
   # Edit docker-compose.yml logging configuration:
   logging:
     driver: "json-file"
     options:
       max-size: "10m"
       max-file: "3"
   ```

6. **Create Monitoring Dashboard**
   ```bash
   # Create custom Grafana dashboard showing:
   # - Request rate (rpm)
   # - Response time (p50, p95, p99)
   # - Error rate (%)
   # - Active users
   # - Database connections
   # - Celery task queue length
   # - Gemini API usage
   # - Cache hit rate
   ```

#### Success Criteria:
- ✅ Prometheus collecting metrics from all services
- ✅ Grafana dashboards showing real-time data
- ✅ Alert rules configured for critical conditions
- ✅ Alertmanager sending test notifications
- ✅ Structured logging enabled
- ✅ Log rotation configured
- ✅ Custom dashboards created for key metrics

#### Monitoring Metrics to Track:

**System Metrics:**
- CPU usage per container
- Memory usage per container
- Disk I/O and space
- Network traffic

**Application Metrics:**
- Request rate (requests/min)
- Response time (ms) - p50, p95, p99
- Error rate (%)
- Active connections
- Queue depth (Celery, Redis)

**Business Metrics:**
- Articles scraped per hour
- Keywords tracked
- Sentiment analyses performed
- API calls by endpoint
- User suggestions submitted

**AI/ML Metrics:**
- Gemini API calls (count, rate)
- Embedding generation time
- Sentiment analysis accuracy
- Keyword extraction rate

---

### 🟤 PHASE 7: Production Deployment (CRITICAL)
**Objective**: Deploy to production server
**Duration**: 2-4 hours
**Priority**: CRITICAL

#### Pre-Deployment Checklist:

- [ ] All previous phases completed successfully
- [ ] All tests passing (backend + frontend)
- [ ] Security audit complete
- [ ] Monitoring configured and tested
- [ ] Backup/restore procedures documented and tested
- [ ] Rollback plan prepared
- [ ] Production environment variables configured
- [ ] SSL certificates obtained
- [ ] Domain DNS configured
- [ ] Firewall rules configured

#### Deployment Steps:

1. **Prepare Production Server**
   ```bash
   # On production VPS (Ubuntu 24 LTS)
   # Update system
   sudo apt update && sudo apt upgrade -y

   # Install Docker
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   sudo usermod -aG docker $USER

   # Install Docker Compose
   sudo apt install docker-compose-plugin -y

   # Verify installation
   docker --version
   docker compose version
   ```

2. **Clone Repository**
   ```bash
   # On production server
   git clone https://github.com/bejranonda/EU-Intelligence-Hub.git
   cd EU-Intelligence-Hub

   # Checkout stable branch/tag
   git checkout main  # or specific release tag
   ```

3. **Configure Production Environment**
   ```bash
   # Copy example environment file
   cp .env.production.example .env.production

   # Edit with production values
   nano .env.production

   # Set secure credentials:
   # - POSTGRES_PASSWORD (32+ char random string)
   # - REDIS_PASSWORD (32+ char random string)
   # - SECRET_KEY (64+ char random string)
   # - ADMIN_PASSWORD (strong password)
   # - GEMINI_API_KEY (your actual key)
   # - ALLOWED_HOSTS (your domain)
   # - CORS_ORIGINS (your frontend URL)

   # Secure file permissions
   chmod 600 .env.production
   ```

4. **Build and Start Services**
   ```bash
   # Build production images
   docker compose -f docker-compose.prod.yml build

   # Start services
   docker compose -f docker-compose.prod.yml up -d

   # Verify all containers started
   docker compose -f docker-compose.prod.yml ps
   ```

5. **Initialize Database**
   ```bash
   # Apply schema
   docker compose -f docker-compose.prod.yml exec postgres \
     psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} -f /docker-entrypoint-initdb.d/init_db.sql

   # Apply migrations
   for file in backend/migrations/*.sql; do
     docker compose -f docker-compose.prod.yml exec postgres \
       psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} -f /app/migrations/$(basename $file)
   done

   # Initialize seed data
   docker compose -f docker-compose.prod.yml exec backend \
     python /app/scripts/init_keywords.py
   ```

6. **Setup SSL Certificate**
   ```bash
   # Run SSL setup script
   ./setup-ssl.sh yourdomain.com

   # Verify certificate
   sudo certbot certificates

   # Test auto-renewal
   sudo certbot renew --dry-run
   ```

7. **Configure Firewall**
   ```bash
   # Allow necessary ports
   sudo ufw allow 22/tcp   # SSH
   sudo ufw allow 80/tcp   # HTTP (redirect to HTTPS)
   sudo ufw allow 443/tcp  # HTTPS

   # Enable firewall
   sudo ufw enable

   # Verify status
   sudo ufw status
   ```

8. **Verify Deployment**
   ```bash
   # Test HTTPS endpoint
   curl -I https://yourdomain.com

   # Test API
   curl https://yourdomain.com/api/health

   # Test frontend
   curl -I https://yourdomain.com

   # Check all services
   docker compose -f docker-compose.prod.yml ps
   ```

9. **Setup Monitoring**
   ```bash
   # Access Grafana
   open https://yourdomain.com:3001

   # Verify Prometheus targets
   open https://yourdomain.com:9090/targets

   # Test alerting
   # Temporarily stop a service to trigger alert
   ```

10. **Create Initial Backup**
    ```bash
    # Run backup script
    docker compose -f docker-compose.prod.yml exec backend \
      python /app/scripts/backup.py

    # Verify backup created
    ls -lh backups/
    ```

#### Post-Deployment Verification:

```bash
# Run health check script
./scripts/health_check.sh

# Expected output:
# ✅ Backend API: healthy
# ✅ PostgreSQL: healthy
# ✅ Redis: healthy
# ✅ Celery Worker: healthy
# ✅ Celery Beat: healthy
# ✅ Frontend: accessible
# ✅ Nginx: healthy
# ✅ SSL Certificate: valid

# Monitor logs for 30 minutes
docker compose -f docker-compose.prod.yml logs -f

# Run smoke tests
curl https://yourdomain.com/api/keywords?limit=5
curl https://yourdomain.com/api/sentiment/keywords/1/sentiment

# Test user workflows in browser
# - Search keywords
# - View details
# - View sentiment timeline
# - Submit suggestion
```

#### Success Criteria:
- ✅ All services running on production server
- ✅ HTTPS working with valid SSL certificate
- ✅ Frontend accessible and functional
- ✅ API endpoints responding correctly
- ✅ Database initialized with seed data
- ✅ Celery tasks running on schedule
- ✅ Monitoring dashboards showing data
- ✅ Backups configured and tested
- ✅ No errors in logs
- ✅ All smoke tests passing

---

## Known Issues & Fixes

### Issue 1: Services Not Starting
**Symptom**: `docker compose ps` shows no containers running

**Root Cause**: Docker service not started or permissions issue

**Fix**:
```bash
# Start Docker service
sudo systemctl start docker

# Fix permissions
sudo usermod -aG docker $USER
newgrp docker

# Restart Docker
sudo systemctl restart docker

# Try starting services again
docker compose up -d
```

### Issue 2: Database Connection Errors
**Symptom**: Backend logs show "could not connect to server: Connection refused"

**Root Cause**: PostgreSQL not ready when backend starts

**Fix**:
```bash
# Wait for PostgreSQL to be fully ready
docker compose up -d postgres
sleep 30

# Then start backend
docker compose up -d backend

# Or use health check dependencies (already configured)
```

### Issue 3: Gemini API Rate Limit Exceeded
**Symptom**: "429 Too Many Requests" or "Quota exceeded" errors

**Root Cause**: Exceeding Gemini API free tier limits

**Fix**:
```bash
# Reduce API call frequency
# Edit .env
GEMINI_RATE_LIMIT_PER_MINUTE=10  # Default: 30

# Use VADER-only mode temporarily
ENABLE_GEMINI_SENTIMENT=false

# Restart services
docker compose restart backend celery_worker
```

### Issue 4: Out of Memory Errors
**Symptom**: Containers restarting, OOMKilled in logs

**Root Cause**: Insufficient system memory

**Fix**:
```bash
# Check memory usage
docker stats

# Add memory limits to docker-compose.yml
services:
  backend:
    mem_limit: 1g
    mem_reservation: 512m

# Reduce worker count
# In docker-compose.prod.yml
command: gunicorn app.main:app --workers 2  # Default: 4
```

### Issue 5: Celery Tasks Not Running
**Symptom**: Celery beat/worker not executing scheduled tasks

**Root Cause**: Celery not able to connect to Redis broker

**Fix**:
```bash
# Verify Redis connection
docker compose exec redis redis-cli ping

# Check Celery worker status
docker compose exec celery_worker celery -A app.tasks.celery_app inspect active

# Restart Celery services
docker compose restart celery_worker celery_beat

# Check logs
docker compose logs celery_worker celery_beat
```

### Issue 6: Frontend Build Fails
**Symptom**: `docker compose up frontend` fails during build

**Root Cause**: Missing package-lock.json or dependency conflicts

**Fix**:
```bash
# Clean install
cd frontend
rm -rf node_modules package-lock.json
npm install

# Rebuild Docker image
docker compose build frontend

# Start service
docker compose up -d frontend
```

### Issue 7: Missing pgvector Extension
**Symptom**: "type 'vector' does not exist" in database logs

**Root Cause**: pgvector extension not installed

**Fix**:
```bash
# Rebuild Postgres with pgvector
docker compose down postgres
docker volume rm euint_postgres_data  # WARNING: Destroys data

# Use custom Dockerfile with pgvector
# Already configured in docker/Dockerfile.postgres

# Restart
docker compose up -d postgres
```

---

## Testing Checklist

### Unit Tests
- [ ] Backend unit tests (49 tests)
- [ ] Frontend component tests
- [ ] AI service mocks tests
- [ ] Database model tests

### Integration Tests
- [ ] API endpoint tests
- [ ] Celery task execution tests
- [ ] Database migrations tests
- [ ] Service communication tests

### End-to-End Tests
- [ ] User registration/login flow
- [ ] Keyword search workflow
- [ ] Sentiment analysis workflow
- [ ] Document upload workflow
- [ ] Admin keyword approval workflow

### Performance Tests
- [ ] Load test with 100 concurrent users
- [ ] Database query performance
- [ ] API response time under load
- [ ] Celery task execution time
- [ ] Memory leak tests (24h run)

### Security Tests
- [ ] SQL injection prevention
- [ ] XSS prevention
- [ ] CSRF protection
- [ ] Rate limiting effectiveness
- [ ] Authentication/authorization
- [ ] SSL/TLS configuration

---

## Rollback Plan

If critical issues occur in production:

### Immediate Rollback (< 5 minutes)
```bash
# Stop all services
docker compose -f docker-compose.prod.yml down

# Restore from backup
./scripts/restore.sh /backups/latest_backup.sql

# Start services with previous configuration
git checkout <previous-commit>
docker compose -f docker-compose.prod.yml up -d

# Verify functionality
./scripts/health_check.sh
```

### Database Rollback
```bash
# Export current state (just in case)
docker compose -f docker-compose.prod.yml exec postgres \
  pg_dump -U ${POSTGRES_USER} ${POSTGRES_DB} > /backups/pre_rollback_$(date +%Y%m%d_%H%M%S).sql

# Restore from specific backup
./scripts/restore.sh /backups/backup_YYYYMMDD_HHMMSS.sql

# Verify integrity
docker compose -f docker-compose.prod.yml exec postgres \
  psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} -c "SELECT COUNT(*) FROM keywords;"
```

### Code Rollback
```bash
# Revert to previous stable version
git log --oneline -10
git checkout <stable-commit-hash>

# Rebuild images
docker compose -f docker-compose.prod.yml build

# Restart services
docker compose -f docker-compose.prod.yml up -d
```

---

## Maintenance Procedures

### Daily Tasks
- [ ] Check service health: `./scripts/health_check.sh`
- [ ] Review error logs: `docker compose logs | grep -i error`
- [ ] Monitor disk space: `df -h`
- [ ] Check backup status: `ls -lh backups/`

### Weekly Tasks
- [ ] Review Grafana dashboards for anomalies
- [ ] Check Celery task success rate
- [ ] Review API usage patterns
- [ ] Update dependencies (security patches)
- [ ] Test backup restoration

### Monthly Tasks
- [ ] Full security audit
- [ ] Performance optimization review
- [ ] Database vacuum and analyze
- [ ] Log cleanup and archival
- [ ] SSL certificate renewal check

### Quarterly Tasks
- [ ] Disaster recovery drill
- [ ] Load testing
- [ ] Dependency major version updates
- [ ] Security penetration testing
- [ ] Architecture review

---

## Success Metrics

### Technical Metrics
- **Uptime**: > 99.9% (< 43 minutes downtime/month)
- **API Response Time**: p95 < 500ms, p99 < 1000ms
- **Error Rate**: < 0.1% of requests
- **Database Query Time**: p95 < 200ms
- **Celery Task Success Rate**: > 99%
- **Cache Hit Rate**: > 80%

### Business Metrics
- **Articles Scraped**: > 100/day per keyword
- **Sentiment Analyses**: > 500/day
- **API Calls**: > 10,000/day
- **Active Keywords**: > 50
- **User Suggestions**: > 10/week

### Monitoring Alerts
- Service down > 1 minute
- Error rate > 5%
- Response time p95 > 1000ms
- Database connections > 90%
- Disk space < 10%
- Memory usage > 90%
- SSL certificate expires < 7 days

---

## Documentation References

- **[README.md](README.md)** - Project overview
- **[INSTALLATION.md](INSTALLATION.md)** - Setup guide
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Production deployment
- **[ERROR_LOGGING.md](ERROR_LOGGING.md)** - Error handling
- **[SECURITY.md](SECURITY.md)** - Security checklist
- **[PRODUCTION_READINESS_AUDIT.md](PRODUCTION_READINESS_AUDIT.md)** - Audit report
- **[TROUBLESHOOTING_KEYWORDS.md](TROUBLESHOOTING_KEYWORDS.md)** - Common issues

---

## Timeline Estimate

| Phase | Duration | Priority | Can Parallelize |
|-------|----------|----------|-----------------|
| Phase 1: Environment Setup | 2-3 hours | CRITICAL | No |
| Phase 2: Database Validation | 1-2 hours | HIGH | No (depends on Phase 1) |
| Phase 3: Testing | 2-4 hours | MEDIUM-HIGH | Partial |
| Phase 4: Performance | 2-3 hours | MEDIUM | Yes |
| Phase 5: Security | 2-3 hours | HIGH | Yes |
| Phase 6: Monitoring | 2-3 hours | MEDIUM | Yes |
| Phase 7: Production Deploy | 2-4 hours | CRITICAL | No (final step) |

**Total Time**: 13-22 hours (2-3 working days)

**Parallel Execution**: Phases 4, 5, and 6 can be done simultaneously after Phase 3 completes, reducing total time to 10-15 hours.

---

## Next Immediate Steps

1. **Start Docker Services** (30 minutes)
   ```bash
   docker compose up -d
   docker compose ps
   docker compose logs -f
   ```

2. **Validate Services** (30 minutes)
   ```bash
   curl http://localhost:8000/health
   curl http://localhost:3000
   ./scripts/health_check.sh
   ```

3. **Run Tests** (1 hour)
   ```bash
   docker compose exec backend pytest app/tests/ -v
   ```

4. **Fix Any Failures** (variable)
   - Review logs
   - Apply fixes from "Known Issues" section
   - Re-test

5. **Proceed to Next Phase** (per timeline above)

---

## Contact & Support

**Project Repository**: https://github.com/bejranonda/EU-Intelligence-Hub

**For Issues**:
- Check existing documentation
- Review logs: `docker compose logs [service]`
- Run health check: `./scripts/health_check.sh`
- Create GitHub issue with logs and error details

**Emergency Rollback**:
- See "Rollback Plan" section above
- Contact system administrator

---

**Document Version**: 1.0
**Last Updated**: 2025-10-20
**Status**: Ready for Execution
