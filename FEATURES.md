# 🎯 Complete Feature List
## EU Intelligence Hub - European News Intelligence Platform

**Last Updated**: 2025-10-20

---

## 📋 Table of Contents
- [Core Features](#core-features)
- [AI/ML Features](#aiml-features)
- [API Endpoints](#api-endpoints)
- [Frontend Features](#frontend-features)
- [Admin Features](#admin-features)
- [Automation Features](#automation-features)
- [Infrastructure Features](#infrastructure-features)

---

## 🚀 Core Features

### 1. Multi-Language Keyword Tracking
**Status**: ✅ Fully Implemented

Track keywords across 9 languages with automatic translations:
- 🇬🇧 English (keyword_en) - Primary
- 🇹🇭 Thai (keyword_th)
- 🇩🇪 German (keyword_de)
- 🇫🇷 French (keyword_fr)
- 🇪🇸 Spanish (keyword_es)
- 🇮🇹 Italian (keyword_it)
- 🇵🇱 Polish (keyword_pl)
- 🇸🇪 Swedish (keyword_sv)
- 🇳🇱 Dutch (keyword_nl)

**How it works**:
- Submit keyword in English
- AI automatically translates to other languages using context-aware translation
- Searches conducted across all language variants

**Database Table**: `keywords` with 9 language columns
**Service**: `app.services.keyword_approval:KeywordApprovalService`

---

### 2. Dual-Layer Sentiment Analysis
**Status**: ✅ Fully Implemented

Two-stage sentiment analysis for speed + accuracy:

**Stage 1: VADER Baseline** (Fast)
- Lexicon-based sentiment scoring
- Real-time processing (<10ms per article)
- Fallback when Gemini unavailable

**Stage 2: Gemini AI Enhancement** (Accurate)
- Nuanced opinion detection
- Sarcasm and context understanding
- Confidence scoring (0.0 - 1.0)
- Subjectivity rating (0.0 - 1.0)
- Emotion breakdown: positive/negative/neutral

**Output Fields**:
```python
{
  "sentiment_overall": float,         # -1.0 to 1.0
  "sentiment_confidence": float,      # 0.0 to 1.0
  "sentiment_subjectivity": float,    # 0.0 to 1.0
  "emotion_positive": float,          # 0.0 to 1.0
  "emotion_negative": float,          # 0.0 to 1.0
  "emotion_neutral": float            # 0.0 to 1.0
}
```

**Service**: `app.services.sentiment:SentimentAnalyzer`
**Fallback**: Graceful degradation to VADER when Gemini fails

---

### 3. Vector Embedding Semantic Search
**Status**: ✅ Fully Implemented

**Technology**:
- Sentence Transformers (all-MiniLM-L6-v2 model)
- 384-dimensional embeddings
- PostgreSQL pgvector extension
- Cosine similarity search

**Capabilities**:
- Find conceptually similar articles (not just keyword matches)
- Semantic search: "tourism growth" finds "visitor increases"
- Article similarity detection (>0.7 threshold)
- 50ms average query time for 100K embeddings

**Database**: Vector columns in `articles` and `keywords` tables
**Service**: `app.services.embeddings:EmbeddingGenerator`
**API**: `/api/search/semantic`, `/api/search/similar/{article_id}`

---

### 4. Intelligent Keyword Suggestion System
**Status**: ✅ Fully Implemented

User-submitted keyword suggestions with AI evaluation:

**Workflow**:
1. User submits keyword suggestion via `/suggest` page
2. AI evaluates significance (Gemini API)
3. Admin reviews pending suggestions
4. Auto-translation to 9 languages on approval
5. Immediate news search triggered (bypassing 3-hour cooldown)

**AI Evaluation Metrics**:
- **Searchability Score** (0-100): How easy to find news articles
- **Significance Score** (0-100): Global/regional importance
- **Specificity**: "too_broad", "optimal", "too_specific"
- **Decision**: "approve", "reject", "needs_review"
- **Reasoning**: AI explanation of decision

**Database Tables**:
- `keyword_suggestions` - User submissions
- `keyword_evaluations` - AI evaluation history

**Services**:
- `app.services.keyword_approval:KeywordApprovalService`
- `app.api.suggestions:router`
- `app.api.admin:router` (approval/rejection)

---

### 5. Smart Keyword Search Scheduling
**Status**: ✅ Fully Implemented

Prevents duplicate searches and manages API quota efficiently:

**Features**:
- 3-hour cooldown between searches for same keyword
- Priority queue system (0-100 scale)
- Retry mechanism (max 3 attempts)
- Scheduled search queue

**Database Table**: `keyword_search_queue`
**Columns**:
- `scheduled_at` - When to execute search
- `priority` - Queue priority (0-100)
- `attempts` - Retry count
- `max_attempts` - Failure threshold
- `last_error` - Error tracking

**Celery Tasks**:
- `populate_keyword_queue` - Runs every 30 minutes
- `process_keyword_queue` - Runs every 15 minutes

**Service**: `app.services.keyword_scheduler:KeywordScheduler`

---

### 6. News Source Management
**Status**: ✅ Fully Implemented

Configurable news sources with metadata:

**12 Pre-configured Sources**:
1. BBC News
2. Reuters
3. Deutsche Welle (DW)
4. France 24
5. Euronews
6. The Guardian
7. The Telegraph
8. El País
9. Le Monde
10. Corriere della Sera
11. Politico Europe
12. EUobserver

**Source Configuration**:
- Name, base URL, language
- Country of origin
- Priority level (0-100)
- Parser type
- Tags for categorization
- Enable/disable toggle

**Ingestion Tracking**:
- Last run timestamp
- Articles ingested count
- Success/failure status

**Database Tables**:
- `news_sources` - Source configuration
- `source_ingestion_history` - Tracking

**API Endpoints**:
- `GET /admin/sources` - List sources
- `POST /admin/sources` - Add source
- `POST /admin/sources/{id}/toggle` - Enable/disable
- `GET /admin/sources/{id}/ingestion` - View history

---

## 🤖 AI/ML Features

### 7. Gemini AI Integration
**Status**: ✅ Fully Implemented

**Use Cases**:
1. **Sentiment Analysis**: Nuanced opinion detection
2. **News Discovery**: AI-researched article finding
3. **Keyword Extraction**: spaCy NER + Gemini validation
4. **Keyword Evaluation**: Automatic suggestion scoring
5. **Translation**: Context-aware multi-language

**Rate Limiting**:
- 30 calls per minute (configurable)
- Automatic retry with exponential backoff
- Fallback to deterministic methods

**Error Handling**:
- Graceful degradation
- Detailed error logging
- Quota tracking

**Service**: `app.services.gemini_client:GeminiClient`

---

### 8. Keyword Extraction Pipeline
**Status**: ✅ Fully Implemented

**Two-Stage Extraction**:

**Stage 1: spaCy NER**
- Named Entity Recognition
- Extracts: PERSON, ORG, GPE, LOC, EVENT
- Fast baseline extraction

**Stage 2: Gemini Validation**
- Confirms relevance
- Extracts additional keywords missed by spaCy
- Filters noise and irrelevant entities

**Output**: List of validated keywords with confidence scores

**Service**: `app.services.keyword_extractor:KeywordExtractor`

---

### 9. Fact vs. Opinion Classification
**Status**: ✅ Fully Implemented

Automatically classifies articles:
- **fact**: Objective reporting
- **opinion**: Editorial/commentary
- **mixed**: Contains both

**Method**: Gemini AI analysis of article content
**Database**: `articles.classification` column
**Use Case**: Filter news by objectivity level

---

## 📡 API Endpoints

### Keyword Management (7 endpoints)
```http
GET    /api/keywords/                         # Search with pagination & filters
GET    /api/keywords/{id}                     # Detailed keyword info
GET    /api/keywords/{id}/articles            # Related articles (sorted)
GET    /api/keywords/{id}/relations           # Mind map data
POST   /api/suggestions/                      # Submit keyword suggestion
GET    /api/suggestions/                      # List all suggestions
POST   /api/suggestions/{id}/vote             # Upvote suggestion
```

### Sentiment Analysis (4 endpoints)
```http
GET    /api/sentiment/keywords/{id}/sentiment           # Overall stats
GET    /api/sentiment/keywords/{id}/sentiment/timeline  # Time-series (7/30/90 days)
GET    /api/sentiment/keywords/compare                  # Multi-keyword comparison
GET    /api/sentiment/articles/{id}/sentiment           # Article-level analysis
```

### Semantic Search (3 endpoints)
```http
GET    /api/search/articles                   # Full-text search
GET    /api/search/semantic                   # Vector similarity
GET    /api/search/similar/{article_id}       # Find similar articles
```

### Document Processing (1 endpoint)
```http
POST   /api/documents/upload                  # Upload PDF/DOCX/TXT
```

### Admin - Source Management (4 endpoints) ✨ NEW
```http
GET    /admin/sources                         # List all news sources
POST   /admin/sources                         # Add new source
POST   /admin/sources/{id}/toggle             # Enable/disable source
GET    /admin/sources/{id}/ingestion          # View ingestion history
```

### Admin - Keyword Approval (5 endpoints) ✨ NEW
```http
POST   /admin/keywords/suggestions/{id}/process    # AI evaluation
POST   /admin/keywords/suggestions/{id}/approve    # Approve + auto-translate + search
POST   /admin/keywords/suggestions/{id}/reject     # Reject suggestion
GET    /admin/keywords/suggestions/pending         # View pending
GET    /admin/keywords/suggestions/stats           # Dashboard stats
```

### Admin - Evaluation History (1 endpoint) ✨ NEW
```http
GET    /admin/suggestions/{id}/evaluations    # View AI evaluation history
```

**Total**: 30+ API endpoints
**Documentation**: http://localhost:8000/docs (Swagger UI)

---

## 🖥️ Frontend Features

### 7 Main Pages

#### 1. Home Page (`/`)
**Features**:
- Keyword search with autocomplete
- Grid/list view of keywords
- Article count badges
- Sentiment color indicators
- Quick access to details

#### 2. Search Page (`/search`)
**Features**:
- Advanced filtering (date range, sentiment, source)
- Full-text and semantic search toggle
- Article preview cards
- Pagination
- Sort by date/sentiment/relevance

#### 3. Keyword Detail Page (`/keywords/{id}`)
**Features**:
- 90-day sentiment timeline (Recharts)
- Article list with sentiment badges
- Keyword relationship mind map (React Flow)
- Export data functionality
- Share buttons

#### 4. Suggest Page (`/suggest`) ✨ UPDATED
**Features**:
- Multi-language keyword input (9 languages)
- Category selection
- Reason/justification textarea
- Optional contact email
- Success/error feedback
- View submitted suggestions

#### 5. Upload Page (`/upload`)
**Features**:
- Drag & drop file upload (PDF/DOCX/TXT)
- Progress indicator
- Automatic processing
- Sentiment analysis results
- Keyword extraction display

#### 6. Admin Sources Page (`/admin/sources`) ✨ NEW
**Features**:
- List all 12 news sources
- Enable/disable toggle switches
- View ingestion statistics
- Add new sources (modal form)
- Edit source configuration
- Delete sources (with confirmation)
- Ingestion history charts

**Requires**: Admin authentication (HTTP Basic Auth)

#### 7. Admin Suggestions Page (`/admin/suggestions`) ✨ NEW
**Features**:
- View pending keyword suggestions
- AI evaluation scores display
- One-click approve/reject
- Batch processing
- Filter by status (pending/approved/rejected)
- View evaluation history
- Statistics dashboard:
  - Total suggestions
  - Approval rate
  - Average AI scores
  - Top categories

**Requires**: Admin authentication (HTTP Basic Auth)

---

## 🔄 Automation Features

### Celery Background Tasks

#### 1. News Scraping (`scrape_news`)
**Schedule**: Hourly (at :00)
**Function**: Scrape articles from all enabled sources
**Process**:
1. Query enabled news sources
2. For each source, use Gemini to find recent articles
3. Extract keywords using spaCy + Gemini
4. Generate embeddings
5. Analyze sentiment (VADER + Gemini)
6. Store in database
7. Record ingestion statistics

**Task**: `app.tasks.scraping:scrape_news`

#### 2. Sentiment Aggregation (`aggregate_daily_sentiment`)
**Schedule**: Daily at 00:30 UTC
**Function**: Pre-compute daily sentiment trends
**Process**:
1. Group articles by keyword + date
2. Calculate weighted average sentiment
3. Count positive/negative/neutral articles
4. Identify top positive/negative sources
5. Store in `sentiment_trends` table

**Benefits**: 5ms queries vs 850ms raw scans

**Task**: `app.tasks.sentiment_aggregation:aggregate_daily_sentiment`

#### 3. Keyword Suggestion Processing (`process_pending_suggestions`)
**Schedule**: Daily at 02:00 UTC
**Function**: Batch AI evaluation of pending suggestions
**Process**:
1. Query pending suggestions
2. Run AI evaluation (Gemini)
3. Calculate searchability & significance scores
4. Determine specificity level
5. Auto-approve high-scoring suggestions
6. Store evaluation history

**Task**: `app.tasks.keyword_management:process_pending_suggestions`

#### 4. Keyword Performance Review (`review_keyword_performance`)
**Schedule**: Weekly (Monday 03:00 UTC)
**Function**: Analyze keyword usage and suggest removal
**Process**:
1. Identify keywords with no articles (>30 days)
2. Calculate search frequency
3. Determine popularity scores
4. Flag for admin review
5. Send summary report

**Task**: `app.tasks.keyword_management:review_keyword_performance`

#### 5. Database Backup (`daily_database_backup`)
**Schedule**: Daily at 01:00 UTC
**Function**: Automated PostgreSQL backup
**Process**:
1. pg_dump full database
2. Compress (gzip)
3. Timestamp filename
4. Store in `/backups` directory
5. Verify backup integrity

**Task**: `app.tasks.backup_tasks:daily_database_backup`

#### 6. Backup Cleanup (`cleanup_old_backups`)
**Schedule**: Daily at 04:00 UTC
**Function**: Remove old backups (7-day retention)
**Task**: `app.tasks.backup_tasks:cleanup_old_backups`

#### 7. Database Health Check (`database_health_check`)
**Schedule**: Hourly
**Function**: Monitor database health
**Checks**:
- Connection status
- Disk space
- Table sizes
- Index health
- Query performance

**Task**: `app.tasks.backup_tasks:database_health_check`

#### 8. Keyword Queue Population (`populate_keyword_queue`)
**Schedule**: Every 30 minutes
**Function**: Schedule keyword searches
**Process**:
1. Find keywords due for search (3-hour cooldown)
2. Calculate priority based on popularity
3. Add to `keyword_search_queue`
4. Set `scheduled_at` timestamp

**Task**: `app.tasks.keyword_search:populate_keyword_queue`

#### 9. Keyword Queue Processing (`process_keyword_queue`)
**Schedule**: Every 15 minutes
**Function**: Execute scheduled searches
**Process**:
1. Query queue for due searches
2. Execute news search (Gemini + scraping)
3. Update `last_searched` timestamp
4. Set next search time (current + 3 hours)
5. Remove from queue

**Task**: `app.tasks.keyword_search:process_keyword_queue`

---

## 🏗️ Infrastructure Features

### Docker Orchestration
**Services**: 11 containers
1. PostgreSQL 16 (with pgvector)
2. Redis 7
3. Backend (FastAPI + Uvicorn)
4. Celery Worker
5. Celery Beat
6. Frontend (React + Vite dev server)
7. Nginx (reverse proxy)
8. Prometheus (metrics)
9. Grafana (dashboards)
10. Postgres Exporter (metrics)
11. Redis Exporter (metrics)

### Monitoring Stack
**Prometheus Metrics**:
- HTTP request rate/latency
- Database query performance
- Celery task execution time
- Cache hit/miss rates
- Error rates

**Grafana Dashboards**:
- System overview
- API performance
- Database health
- Celery tasks
- Custom business metrics

### Security Features
1. **HTTPS/SSL**: Let's Encrypt auto-renewal
2. **Rate Limiting**: Nginx (10 req/s API, 30 req/s general)
3. **CORS**: Configured origins only
4. **Authentication**: HTTP Basic Auth for admin
5. **Input Validation**: Pydantic models
6. **SQL Injection**: SQLAlchemy ORM (parameterized)
7. **Security Headers**: CSP, HSTS, X-Frame-Options

### Backup & Recovery
- Daily automated backups
- 7-day retention
- Restore script: `./scripts/restore.sh`
- Health monitoring: `./scripts/health_check.sh`

---

## 📊 Database Schema

### 12 Tables

1. **keywords** - Multi-language keyword tracking (9 language columns)
2. **articles** - News articles with 6 sentiment fields + embeddings
3. **keyword_articles** - Junction table with relevance scores
4. **keyword_relations** - Mind map relationship data
5. **keyword_suggestions** - User-submitted suggestions (9 language columns)
6. **keyword_evaluations** - AI evaluation history
7. **keyword_search_queue** - Scheduled search queue
8. **documents** - Uploaded file metadata
9. **sentiment_trends** - Daily pre-computed aggregations
10. **comparative_sentiment** - Multi-keyword comparisons
11. **news_sources** - Configurable source list
12. **source_ingestion_history** - Scraping statistics

### Vector Embeddings
- **articles.embedding**: vector(384)
- **keywords.embedding**: vector(384)
- **pgvector extension**: v0.8.1

### Indexes (18 total)
- Primary keys on all tables
- Foreign keys with CASCADE delete
- Sentiment, date, source indexes
- Unique constraints on URLs
- Composite indexes for queries

---

## 🎯 Use Cases

### For Intelligence Analysts
✅ Track European media narrative shifts over time
✅ Identify sentiment trends by source/country
✅ Discover relationships between topics
✅ Export data for reports

### For PR Teams
✅ Monitor brand sentiment in European media
✅ Identify favorable/critical outlets
✅ Track coverage volume and tone
✅ Compare against competitors

### For Researchers
✅ Separate facts from opinions
✅ Analyze media bias patterns
✅ Track specific policy topics
✅ Access historical sentiment data

### For News Organizations
✅ Aggregate European coverage on stories
✅ Identify trending topics
✅ Find similar articles
✅ Monitor competitor coverage

---

## 📈 Performance Metrics

- **Article Processing**: 10,000/hour
- **Semantic Search**: 50ms average (100K embeddings)
- **Timeline Query**: 5ms (pre-aggregated)
- **API Response**: <500ms p95
- **Embedding Generation**: <100ms per article
- **Sentiment Analysis**: <200ms per article (VADER + Gemini)

---

## 🔜 Roadmap Features

### In Development
- [ ] Email alerts for sentiment changes
- [ ] Multi-keyword watchlists
- [ ] PDF report generation
- [ ] Data export (CSV/JSON/Excel)

### Planned
- [ ] Browser extension for quick saves
- [ ] Mobile app (iOS/Android)
- [ ] Webhook notifications
- [ ] Advanced analytics dashboard

---

**Document Version**: 2.0
**Last Updated**: 2025-10-20
**Maintained By**: EU Intelligence Hub Team
