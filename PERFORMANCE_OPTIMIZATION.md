# Performance Optimization Guide

## Overview

This document outlines the performance optimizations implemented in the EU Intelligence Hub and best practices for maintaining optimal performance in production.

## 1. Database Performance

### Connection Pooling

**Implemented:** SQLAlchemy with QueuePool
- Pool size: 20 connections
- Max overflow: 40 additional connections
- Pool recycling: 1 hour
- Pre-ping: Enabled (validates connections before use)

**Benefits:**
- Reduced connection overhead
- Connection reuse across requests
- Automatic stale connection removal

**Monitoring:**
```python
from app.database import get_pool_status
status = get_pool_status()
print(f"Active connections: {status['total']}")
```

### Query Optimization

**Best Practices:**

1. **Use Pagination**
   ```python
   # ✓ Good
   results = db.query(Model).offset(skip).limit(limit).all()
   
   # ✗ Bad
   results = db.query(Model).all()  # Fetches all rows
   ```

2. **Index Strategy**
   - Create indexes on frequently queried fields
   - Use composite indexes for multi-column queries
   - Monitor slow query log

3. **Eager Loading**
   ```python
   # ✓ Good - uses single query with JOIN
   query = db.query(Keyword).options(
       joinedload(Keyword.relations)
   )
   
   # ✗ Bad - N+1 problem
   keywords = db.query(Keyword).all()
   for kw in keywords:
       relations = kw.relations  # Separate query per keyword
   ```

### Query Caching

**Implemented:** Redis-based caching layer

```python
from app.cache import cached

@cached(ttl=3600, key_prefix="keywords")
def get_frequently_accessed_keywords():
    # This result will be cached for 1 hour
    return db.query(Keyword).filter(...).all()
```

**Cache Invalidation:**
```python
from app.cache import CacheInvalidationManager

# Invalidate all keyword-related caches
CacheInvalidationManager.invalidate_related_caches('keyword')

# Invalidate specific keyword caches
CacheInvalidationManager.invalidate_related_caches('keyword', entity_id=123)
```

### Statement Timeout

- **Default:** 30 seconds per query
- **Configuration:** `connect_args["statement_timeout"]` in database.py
- **Purpose:** Prevents long-running queries from blocking connections

---

## 2. Application-Level Caching

### Cache Strategies

**1. Full-Page Cache (TTL: 1 hour)**
```python
# Cache frequently accessed API responses
@cached(ttl=3600)
async def get_trending_keywords():
    return await fetch_trending_data()
```

**2. Entity Cache (TTL: 30 minutes)**
```python
@cached(ttl=1800, key_prefix="entity")
def get_keyword_details(keyword_id: int):
    return db.query(Keyword).filter_by(id=keyword_id).first()
```

**3. Session Cache (TTL: 15 minutes)**
```python
# Cache user-specific data
@cached(ttl=900, key_prefix=f"user:{user_id}")
def get_user_preferences(user_id: int):
    return db.query(UserPreference).filter_by(user_id=user_id).all()
```

### Cache Monitoring

```python
from app.cache import get_cache

cache = get_cache()
stats = cache.get_stats()
print(f"Cache memory usage: {stats['used_memory_mb']}MB")
print(f"Total commands: {stats['total_commands']}")
```

---

## 3. API Response Optimization

### Response Compression

**Enabled in production:**
- gzip compression for responses > 1KB
- Configured in Nginx reverse proxy

### Pagination

**Standard pagination parameters:**
- `skip`: Items to skip (default: 0)
- `limit`: Items to return (default: 10, max: 100)

**Example:**
```python
GET /api/keywords?skip=0&limit=50
```

### Field Selection

**Only return necessary fields:**
```python
# ✓ Good - minimal response size
GET /api/keywords?fields=id,name,score

# ✗ Bad - returns all fields
GET /api/keywords
```

---

## 4. Background Task Optimization

### Task Scheduling

**Celery Beat schedule (in UTC):**
- 00:30 - Daily sentiment analysis aggregation
- 01:00 - Daily database backup
- 02:00 - Keyword suggestion processing
- 03:00 - Weekly keyword performance review
- 04:00 - Old backup cleanup

### Task Configuration

```python
# Celery configuration (in tasks/celery_app.py)
celery_app.conf.update(
    task_time_limit=3600,  # 1 hour max per task
    worker_prefetch_multiplier=1,  # Process one task at a time
)
```

### Monitoring Task Performance

**Via Celery Flower:**
- Access at `http://localhost:5555` (development)
- Monitor task execution times
- Track failed tasks
- Analyze worker performance

---

## 5. Database Indexing Strategy

### Current Indexes

```sql
-- Create primary indexes
CREATE INDEX idx_keyword_name ON keywords(name);
CREATE INDEX idx_sentiment_date ON sentiments(date);
CREATE INDEX idx_document_created_at ON documents(created_at DESC);

-- Create composite indexes for common queries
CREATE INDEX idx_sentiment_keyword_date 
    ON sentiments(keyword_id, date DESC);

-- Vector index for semantic search
CREATE INDEX idx_embedding_vector 
    ON keyword_embeddings 
    USING ivfflat (embedding vector_cosine_ops);
```

### Query Execution Plan

**Always review query plans:**
```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM keywords WHERE name LIKE 'covid%'
LIMIT 10;
```

---

## 6. Horizontal Scaling

### Load Balancing

**Nginx configuration:**
```nginx
upstream backend {
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}
```

### Database Replication

**High Availability setup (docker-compose.ha.yml):**
- Primary PostgreSQL (read/write)
- Replica PostgreSQL (read-only)
- PgPool-II for connection pooling and failover
- Redis Sentinel for automatic Redis failover

### Scaling Recommendations

**For 100+ concurrent users:**
1. Deploy multiple backend instances (3-5 recommended)
2. Enable database replication
3. Use PgPool-II for connection management
4. Implement Redis Sentinel for high availability

---

## 7. Monitoring and Alerts

### Key Metrics to Monitor

**Application Metrics:**
- Response time (p95, p99)
- Error rate
- Requests per second
- Cache hit ratio

**Database Metrics:**
- Active connections
- Query duration
- Slow query log
- Index usage

**System Metrics:**
- CPU usage
- Memory usage
- Disk I/O
- Network I/O

### Prometheus Metrics Endpoint

```
GET /metrics
```

Access Grafana dashboards at `http://localhost:3001`

---

## 8. Production Checklist

- [ ] Enable query caching for frequently accessed data
- [ ] Configure database connection pooling
- [ ] Set up slow query logging
- [ ] Implement monitoring and alerting
- [ ] Schedule regular backups
- [ ] Configure database replication
- [ ] Use Nginx for reverse proxying and compression
- [ ] Enable gzip compression
- [ ] Set up CDN for static assets
- [ ] Configure rate limiting
- [ ] Implement security headers
- [ ] Monitor application logs
- [ ] Set up uptime monitoring
- [ ] Regular performance testing

---

## 9. Performance Testing

### Load Testing with Locust

```python
# Run load test (see locustfile.py)
locust -f locustfile.py --host=http://localhost:8000
```

### Benchmark Results (Target)

- **API Response Time:** < 200ms (p95)
- **Semantic Search:** < 500ms
- **Concurrent Users:** 100+
- **Cache Hit Ratio:** > 70%
- **Error Rate:** < 0.1%

---

## 10. Quick Performance Wins

1. **Enable caching** on frequently accessed endpoints
2. **Add database indexes** on filtered columns
3. **Use pagination** on list endpoints
4. **Implement connection pooling** (already done)
5. **Enable gzip compression** in Nginx
6. **Use async tasks** for long-running operations
7. **Monitor slow queries** with PostgreSQL logs
8. **Regular backup maintenance** to prevent disk bloat

---

## Support and Troubleshooting

### High Memory Usage

```python
# Check cache stats
cache.get_stats()

# Clear old cache entries
cache.clear_pattern("old_*")
```

### Slow Queries

```sql
-- Enable slow query logging
SET log_min_duration_statement = 1000;  -- Log queries > 1 second

-- View slow queries
SELECT query, mean_time, calls FROM pg_stat_statements
ORDER BY mean_time DESC LIMIT 10;
```

### Connection Pool Issues

```python
# Monitor pool status
status = get_pool_status()
if status['total'] > 30:
    # Pool is under stress, consider scaling
    logger.warning(f"High connection usage: {status['total']}")
```

---

**Last Updated:** 2025-10-17  
**Status:** Production Ready
