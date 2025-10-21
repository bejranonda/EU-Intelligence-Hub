# 🌐 Web Pages & Access Points Guide
## EU Intelligence Hub - Complete URL Reference

**Last Updated**: 2025-10-20

---

## 📱 Frontend Pages (Port 3000)

Access the frontend at: **http://localhost:3000** (or your server IP)

| Page | URL | Purpose | Authentication |
|------|-----|---------|----------------|
| **Home** | `/` | Main page - search keywords, view article counts | Public |
| **Search** | `/search` | Advanced search with filters (date, sentiment, source) | Public |
| **Keyword Detail** | `/keywords/{id}` | View sentiment timeline, articles, mind map | Public |
| **Suggest Keyword** | `/suggest` | Submit new keyword suggestions for tracking | Public |
| **Upload Document** | `/upload` | Upload PDF/DOCX/TXT for sentiment analysis | Public |
| **Admin - Sources** | `/admin/sources` | Manage 12 news sources (enable/disable/add) | **Admin Auth Required** |
| **Admin - Suggestions** | `/admin/suggestions` | Review & approve pending keyword suggestions | **Admin Auth Required** |

**Examples**:
```
http://localhost:3000/
http://localhost:3000/keywords/5
http://localhost:3000/suggest
http://localhost:3000/admin/sources
```

---

## 🔧 Backend API (Port 8000)

Access the backend at: **http://localhost:8000**

### API Documentation
| Page | URL | Purpose |
|------|-----|---------|
| **Swagger UI** | `/docs` | Interactive API documentation (try endpoints) |
| **ReDoc** | `/redoc` | Alternative API documentation (clean layout) |
| **OpenAPI JSON** | `/openapi.json` | API schema in JSON format |

**Examples**:
```
http://localhost:8000/docs
http://localhost:8000/redoc
```

### Health & Status Endpoints
| Endpoint | URL | Purpose | Response |
|----------|-----|---------|----------|
| **Health Check** | `/health` | System health status | `{"status": "healthy"}` |
| **API Root** | `/` | API welcome message | Version info |

**Examples**:
```bash
curl http://localhost:8000/health
curl http://localhost:8000/
```

---

## 🔐 Admin Panel

**Authentication**: HTTP Basic Auth
- Default username: `admin` (configure in `.env`)
- Default password: Set in `ADMIN_PASSWORD` environment variable

### Admin Pages

#### 1. News Source Management
**URL**: http://localhost:3000/admin/sources

**Features**:
- View all 12 European news sources
- Enable/disable sources with toggle switches
- Add new custom sources
- View ingestion statistics and history
- Edit source configuration

**Who needs this**: System administrators managing which news outlets to track

---

#### 2. Keyword Suggestion Management
**URL**: http://localhost:3000/admin/suggestions

**Features**:
- View pending keyword suggestions from users
- See AI evaluation scores (searchability, significance)
- Approve suggestions (auto-translates to 9 languages + immediate search)
- Reject suggestions with reason
- View approval statistics dashboard
- Check evaluation history

**Who needs this**: Content moderators deciding which keywords to track

---

## 📊 Monitoring Dashboards

### 1. Prometheus Metrics
**URL**: http://localhost:9090

**Purpose**: Raw metrics collection and queries

**Key Pages**:
- `/targets` - View all monitored services status
- `/graph` - Query metrics with PromQL
- `/alerts` - View active alerts

**Example Queries**:
```
http_requests_total
celery_task_duration_seconds
postgresql_connections_active
```

**Who needs this**: DevOps engineers monitoring system performance

---

### 2. Grafana Dashboards
**URL**: http://localhost:3001

**Default Credentials**:
- Username: `admin`
- Password: `admin` (change on first login)

**Pre-configured Dashboards**:
1. **System Overview** - CPU, memory, disk usage
2. **API Performance** - Request rates, latency, errors
3. **Database Health** - Connections, query performance, table sizes
4. **Celery Tasks** - Task execution times, success/failure rates
5. **Business Metrics** - Articles processed, sentiment trends

**Who needs this**: Team leads and analysts viewing system health

---

## 🗄️ Database Management

### PostgreSQL Admin (via Docker)
Access PostgreSQL directly:

```bash
# Connect to PostgreSQL CLI
docker compose exec postgres psql -U euint_user -d euint_dev

# View tables
\dt

# View database size
\l+

# Exit
\q
```

**Database URL**: `postgresql://euint_user:euint_pass@localhost:5432/euint_dev`

**Who needs this**: Database administrators running queries

---

### Redis Cache (via Docker)
Access Redis directly:

```bash
# Connect to Redis CLI
docker compose exec redis redis-cli

# Check connection
PING

# View keys
KEYS *

# Exit
exit
```

**Redis URL**: `redis://localhost:6379/0`

**Who needs this**: Backend developers debugging cache

---

## 🔍 Quick Access Summary

### For End Users
```
Main App:        http://localhost:3000
Search:          http://localhost:3000/search
Suggest Keyword: http://localhost:3000/suggest
```

### For Administrators
```
Manage Sources:      http://localhost:3000/admin/sources
Approve Keywords:    http://localhost:3000/admin/suggestions
API Documentation:   http://localhost:8000/docs
```

### For Developers
```
API Docs (Swagger):  http://localhost:8000/docs
API Docs (ReDoc):    http://localhost:8000/redoc
Health Check:        http://localhost:8000/health
```

### For DevOps/Monitoring
```
Prometheus:          http://localhost:9090
Grafana:             http://localhost:3001
Prometheus Targets:  http://localhost:9090/targets
```

---

## 🌍 Remote Access

If accessing from another computer on your network:

Replace `localhost` with your server's IP address:

**Examples**:
```
http://192.168.178.50:3000          # Frontend
http://192.168.178.50:8000/docs     # API Docs
http://192.168.178.50:9090          # Prometheus
http://192.168.178.50:3001          # Grafana
```

**Note**: The frontend automatically detects your access method and uses the correct backend URL (no configuration needed).

---

## 🔒 Security Notes

### Public Access (No Authentication)
- Frontend pages: `/`, `/search`, `/keywords/*`, `/suggest`, `/upload`
- Health check: `/health`

### Protected Access (Authentication Required)
- Admin pages: `/admin/sources`, `/admin/suggestions`
- Prometheus: Port 9090 (should be firewalled in production)
- Grafana: Port 3001 (has login)
- Database: Port 5432 (should NOT be exposed publicly)
- Redis: Port 6379 (should NOT be exposed publicly)

### Production Recommendations
1. **Close ports 9090, 5432, 6379** to external traffic (use SSH tunneling)
2. **Enable HTTPS** for ports 80/443 using Let's Encrypt
3. **Set strong passwords** for admin, Grafana, and database
4. **Use Nginx rate limiting** (already configured)

---

## 📱 Mobile Access

All frontend pages are **responsive** and work on mobile devices:
- Home page optimized for touch
- Search filters collapsible on small screens
- Timeline graphs interactive on mobile
- Forms mobile-friendly

---

## 🆘 Troubleshooting

### Page Not Loading?

**Check if services are running**:
```bash
docker compose ps
```

**Expected output**: All services should show "Up" status

**Check specific service logs**:
```bash
docker compose logs frontend -f    # Frontend issues
docker compose logs backend -f     # API issues
docker compose logs nginx -f       # Proxy issues
```

### Can't Access Admin Pages?

**Check authentication**:
1. Username/password set in `.env` file
2. Using HTTP Basic Auth (browser popup should appear)
3. Credentials match `ADMIN_USERNAME` and `ADMIN_PASSWORD`

### Monitoring Not Working?

**Check Prometheus targets**:
```bash
curl http://localhost:9090/api/v1/targets
```

All targets should show `"health": "up"`

---

## 📞 Support

**Documentation**: See [README.md](README.md) and [FEATURES.md](FEATURES.md)

**Health Check Script**:
```bash
./scripts/health_check.sh
```

**View All Services**:
```bash
docker compose ps
```

---

**Document Version**: 1.0
**Maintained By**: EU Intelligence Hub Team
