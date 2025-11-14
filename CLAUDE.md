# CLAUDE.md - AI Assistant Guide for EU Intelligence Hub

> **Purpose**: This document provides comprehensive guidance for AI assistants (like Claude) working on the European News Intelligence Hub codebase. It covers architecture, conventions, workflows, and best practices to ensure effective collaboration.

**Last Updated**: 2025-11-14
**Repository**: EU-Intelligence-Hub
**Primary Language**: Python 3.11 (Backend), TypeScript (Frontend)
**Architecture**: Microservices with Docker orchestration

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Architecture & Tech Stack](#2-architecture--tech-stack)
3. [Repository Structure](#3-repository-structure)
4. [Development Workflows](#4-development-workflows)
5. [Key Conventions & Patterns](#5-key-conventions--patterns)
6. [Database Schema](#6-database-schema)
7. [API Structure](#7-api-structure)
8. [Testing Guidelines](#8-testing-guidelines)
9. [Deployment Procedures](#9-deployment-procedures)
10. [Common Tasks](#10-common-tasks)
11. [Important Files Reference](#11-important-files-reference)
12. [Troubleshooting](#12-troubleshooting)

---

## 1. Project Overview

### What This Project Does

The **European News Intelligence Hub** is an AI-powered geopolitical news aggregation and sentiment analysis platform that:

- **Tracks sentiment** across 12 European news sources (BBC, Reuters, DW, France24, etc.)
- **Analyzes articles** using dual-layer sentiment analysis (VADER baseline + Google Gemini AI)
- **Performs semantic search** with 384-dimensional vector embeddings (Sentence Transformers)
- **Visualizes relationships** between topics using interactive mind maps (React Flow)
- **Automates collection** via hourly Celery tasks and scheduled searches
- **Supports 9 languages** (EN, TH, DE, FR, ES, IT, PL, SV, NL)

### Core Philosophy

1. **Speed + Accuracy**: Hybrid sentiment analysis balances VADER speed with Gemini nuance
2. **Automation First**: Celery tasks handle all scraping, aggregation, and evaluation
3. **Type Safety**: Pydantic (Python) and TypeScript ensure contract safety
4. **Separation of Concerns**: Clear boundaries between API, services, tasks, and models
5. **Production-Ready**: Docker orchestration, monitoring, backups, and security hardening

### Key Metrics

- **~9,800 lines of code** (5,100 Python, 1,800 TypeScript)
- **30+ API endpoints** across 8 routers
- **12 database tables** with pgvector support
- **49 tests** with >80% coverage
- **9 Celery scheduled tasks**
- **11 Docker services** in orchestration

---

## 2. Architecture & Tech Stack

### Backend Stack

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Framework** | FastAPI | 0.104.1 | REST API with async support |
| **Language** | Python | 3.11 | Core application language |
| **ORM** | SQLAlchemy | 2.0.23 | Database abstraction |
| **Validation** | Pydantic | 2.5.2 | Data validation & settings |
| **Task Queue** | Celery | 5.3.4 | Async task processing |
| **Task Broker** | Redis | 7-alpine | Message broker |
| **Database** | PostgreSQL | 16 | Primary data store |
| **Vector Extension** | pgvector | latest | Semantic search |
| **Web Server** | Uvicorn | 0.24.0 | ASGI server (dev) |
| **Web Server** | Gunicorn | 21.2.0 | WSGI server (prod) |

### Frontend Stack

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Framework** | React | 18.2 | UI library |
| **Language** | TypeScript | 5.3 | Type-safe JavaScript |
| **Build Tool** | Vite | 5.0 | Fast bundler |
| **Styling** | Tailwind CSS | 3.3 | Utility-first CSS |
| **UI Components** | shadcn/ui | latest | Accessible components |
| **State Management** | Zustand | 4.4.7 | Lightweight state |
| **Data Fetching** | TanStack Query | 5.12 | Server state management |
| **Visualizations** | Recharts | 2.10 | Charts (timelines) |
| **Mind Maps** | React Flow | 10.3 | Interactive graphs |
| **i18n** | i18next | 23.7 | Multi-language support |

### AI/ML Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **LLM** | Google Gemini API | AI reasoning, evaluation, translation |
| **Sentiment** | VADER | Fast baseline sentiment analysis |
| **NER** | spaCy (en_core_web_sm) | Named entity recognition |
| **Embeddings** | Sentence Transformers | 384-dim semantic vectors |

### Infrastructure Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Containerization** | Docker + Docker Compose | Service orchestration |
| **Reverse Proxy** | Nginx | Load balancing, SSL, rate limiting |
| **Monitoring** | Prometheus + Grafana | Metrics & dashboards |
| **Alerting** | AlertManager | Alert routing |
| **SSL** | Let's Encrypt | Production certificates |

---

## 3. Repository Structure

```
EU-Intelligence-Hub/
├── backend/                           # Python FastAPI backend (~5,100 lines)
│   ├── app/
│   │   ├── api/                      # API routers (8 routers, 30+ endpoints)
│   │   │   ├── keywords.py           # Keyword search, detail, relations
│   │   │   ├── sentiment.py          # Sentiment analysis & trends
│   │   │   ├── search.py             # Semantic & full-text search
│   │   │   ├── documents.py          # Document upload processing
│   │   │   ├── suggestions.py        # Keyword suggestions & voting
│   │   │   ├── admin.py              # Admin source/keyword management
│   │   │   └── admin_evaluations.py  # Admin evaluation history
│   │   ├── models/
│   │   │   └── models.py             # 12 SQLAlchemy ORM models (1,200+ lines)
│   │   ├── services/                 # Business logic & AI services
│   │   │   ├── gemini_client.py      # Rate-limited Gemini API wrapper
│   │   │   ├── sentiment.py          # VADER + Gemini hybrid analysis
│   │   │   ├── embeddings.py         # Sentence Transformers wrapper
│   │   │   ├── scraper.py            # News source scraping logic
│   │   │   ├── keyword_extractor.py  # spaCy + Gemini NER
│   │   │   ├── keyword_approval.py   # AI evaluation & translation
│   │   │   └── keyword_scheduler.py  # Search scheduling logic
│   │   ├── tasks/                    # Celery background jobs (9 tasks)
│   │   │   ├── scraping.py           # Hourly news collection
│   │   │   ├── sentiment_aggregation.py  # Daily trend precomputation
│   │   │   ├── keyword_management.py # AI suggestion processing
│   │   │   ├── keyword_search.py     # Queue-based search execution
│   │   │   ├── backup_tasks.py       # DB backups & health checks
│   │   │   └── celery_app.py         # Celery config & scheduler
│   │   ├── core/                     # Core utilities
│   │   │   ├── auth.py               # Admin authentication
│   │   │   ├── cache.py              # Redis caching layer
│   │   │   ├── config.py             # Pydantic settings (40+ env vars)
│   │   │   ├── database.py           # SQLAlchemy session management
│   │   │   └── validation.py         # Input validation utilities
│   │   ├── middleware/               # FastAPI middleware
│   │   │   ├── cors.py               # CORS configuration
│   │   │   ├── rate_limit.py         # Rate limiting
│   │   │   └── security.py           # Security headers
│   │   ├── monitoring/               # Observability
│   │   │   ├── prometheus.py         # Prometheus metrics
│   │   │   └── logging.py            # Structured logging
│   │   └── testing/
│   │       ├── fixtures.py           # Pytest fixtures
│   │       └── config.py             # Test environment overrides
│   ├── tests/                        # 49 test cases (~1,500 lines)
│   │   ├── test_database.py          # Database integrity tests
│   │   ├── test_ai_services.py       # AI service tests (mocked)
│   │   └── test_api_endpoints.py     # API endpoint tests
│   ├── Dockerfile                    # Development image
│   ├── Dockerfile.prod               # Production optimized image
│   ├── requirements.txt              # 30+ Python dependencies
│   ├── init_db.sql                   # Database schema initialization
│   └── pytest.ini                    # Pytest configuration
│
├── frontend/                          # React TypeScript frontend (~1,800 lines)
│   ├── src/
│   │   ├── components/               # React components (9 components)
│   │   │   ├── SentimentTimeline.tsx # Recharts timeline visualization
│   │   │   ├── MindMap.tsx           # React Flow relationship graph
│   │   │   ├── KeywordCard.tsx       # Keyword display card
│   │   │   ├── SentimentOverview.tsx # Sentiment statistics
│   │   │   ├── LanguageToggle.tsx    # EN/TH language switcher
│   │   │   └── ui/                   # shadcn/ui components
│   │   ├── pages/                    # Page components (7 pages)
│   │   │   ├── HomePage.tsx          # Keyword discovery
│   │   │   ├── KeywordDetailPage.tsx # Detail + timeline + mindmap
│   │   │   ├── SearchPage.tsx        # Semantic search interface
│   │   │   ├── UploadPage.tsx        # Document upload
│   │   │   ├── SuggestPage.tsx       # Keyword suggestion form
│   │   │   ├── AdminSuggestionsPage.tsx  # Admin approval interface
│   │   │   └── AdminSourcesPage.tsx  # Admin source management
│   │   ├── api/
│   │   │   └── client.ts             # Type-safe Axios API wrapper
│   │   ├── types/
│   │   │   └── index.ts              # TypeScript interfaces
│   │   ├── store/
│   │   │   └── languageStore.ts      # Zustand language state
│   │   ├── App.tsx                   # Main router & layout
│   │   └── main.tsx                  # React entry point
│   ├── Dockerfile.dev                # Development with hot reload
│   ├── Dockerfile.prod               # Production nginx serving
│   ├── package.json                  # 22 dependencies
│   └── tsconfig.json                 # TypeScript configuration
│
├── docker/                            # Custom Dockerfiles
│   ├── Dockerfile.postgres            # PostgreSQL with pgvector
│   └── Dockerfile.backup              # Backup utility image
│
├── nginx/                             # Reverse proxy configuration
│   ├── nginx.conf                     # Global config (rate limiting)
│   └── conf.d/app.conf                # App routing
│
├── monitoring/                        # Observability stack
│   ├── prometheus.yml                 # Prometheus scrape config
│   ├── alert_rules.yml                # Alert thresholds
│   ├── alertmanager.yml               # Notification routing
│   └── grafana/provisioning/          # Dashboards & data sources
│
├── scripts/                           # Utility scripts
│   ├── health_check.sh                # Health monitoring
│   ├── backup.sh & backup.py          # Database backup
│   ├── restore.sh                     # Backup restoration
│   └── init_keywords.py               # Seed initial keywords
│
├── .github/workflows/                 # CI/CD pipelines
│   ├── tests.yml                      # Tests + security scan
│   └── deploy.yml                     # Build & push to GHCR
│
├── docker-compose.yml                 # Development (11 services)
├── docker-compose.prod.yml            # Production with SSL
├── docker-compose.ha.yml              # High availability setup
├── deploy.sh                          # Deployment orchestration
├── setup.sh                           # One-command initialization
├── setup-ssl.sh                       # Let's Encrypt SSL setup
│
└── [Documentation Files]              # 40+ markdown files
    ├── README.md                      # Main documentation
    ├── INSTALLATION.md                # Detailed setup guide
    ├── DEPLOYMENT.md                  # Production deployment
    ├── FEATURES.md                    # Complete feature inventory
    ├── PROGRESS.md                    # Development progress
    ├── TODO.md                        # Prioritized backlog
    ├── WEBPAGES_GUIDE.md              # URL reference
    ├── ERROR_LOGGING.md               # Monitoring guide
    ├── KEYWORD_WORKFLOW.md            # AI keyword management
    └── SECURITY.md                    # Security best practices
```

---

## 4. Development Workflows

### 4.1 Initial Setup

```bash
# 1. Clone the repository
git clone https://github.com/ChildWerapol/EU-Intelligence-Hub.git
cd EU-Intelligence-Hub

# 2. Copy environment template
cp .env.example .env

# 3. Update environment variables (CRITICAL!)
nano .env  # Add your GEMINI_API_KEY

# 4. Start all services (11 Docker containers)
./setup.sh

# 5. Verify services are running
docker compose ps

# 6. Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
# Grafana: http://localhost:3001
# Prometheus: http://localhost:9090
```

### 4.2 Daily Development Workflow

```bash
# Start services
docker compose up -d

# View logs in real-time
docker compose logs -f backend

# Run tests
docker compose exec backend pytest tests/ -v

# Stop services
docker compose down
```

### 4.3 Making Changes

#### Backend Changes (Python)

1. **Edit Python files** in `backend/app/`
2. **Hot reload is automatic** (Uvicorn watches file changes)
3. **Run tests**: `docker compose exec backend pytest tests/ -v`
4. **Check linting**: `docker compose exec backend flake8 app/`
5. **Type checking**: `docker compose exec backend mypy app/`
6. **Format code**: `docker compose exec backend black app/`

#### Frontend Changes (TypeScript/React)

1. **Edit TypeScript files** in `frontend/src/`
2. **Hot reload is automatic** (Vite HMR)
3. **Run tests**: `docker compose exec frontend npm test`
4. **Lint**: `docker compose exec frontend npm run lint`
5. **Build**: `docker compose exec frontend npm run build`

#### Database Schema Changes

1. **Edit models** in `backend/app/models/models.py`
2. **Create migration**:
   ```bash
   docker compose exec backend alembic revision --autogenerate -m "Description"
   ```
3. **Apply migration**:
   ```bash
   docker compose exec backend alembic upgrade head
   ```

### 4.4 Git Workflow

**IMPORTANT**: This project uses feature branches starting with `claude/` prefix.

```bash
# Current branch (from git status)
git status
# Branch: claude/claude-md-mhz9wemfxx4kpu6z-01F5kZ9is7isp98fiPvk2vPa

# Stage changes
git add .

# Commit with descriptive message
git commit -m "feat: add comprehensive CLAUDE.md for AI assistants

- Document codebase structure and architecture
- Add development workflows and conventions
- Include API structure and database schema
- Provide troubleshooting guide"

# Push to remote (ALWAYS use -u for first push on new branch)
git push -u origin claude/claude-md-mhz9wemfxx4kpu6z-01F5kZ9is7isp98fiPvk2vPa

# If push fails due to network, retry up to 4 times with exponential backoff
# (2s, 4s, 8s, 16s)
```

**Commit Message Format**:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation only
- `refactor:` - Code refactoring
- `test:` - Adding tests
- `chore:` - Maintenance tasks

### 4.5 Testing Workflow

```bash
# Run all tests
docker compose exec backend pytest tests/ -v

# Run specific test file
docker compose exec backend pytest tests/test_api_endpoints.py -v

# Run with coverage report
docker compose exec backend pytest tests/ --cov=app --cov-report=html

# View coverage report
# Opens in browser: backend/htmlcov/index.html

# Run tests in parallel (faster)
docker compose exec backend pytest tests/ -n auto
```

---

## 5. Key Conventions & Patterns

### 5.1 Code Style Conventions

#### Python (Backend)

- **PEP 8 compliance**: Enforced by `flake8`
- **Black formatting**: 88 character line length
- **Type hints**: Required for all function signatures
- **Docstrings**: Google style for public functions

```python
async def get_keyword_sentiment(
    keyword_id: int,
    db: Session,
    days: int = 30
) -> SentimentStats:
    """
    Calculate sentiment statistics for a keyword.

    Args:
        keyword_id: The ID of the keyword
        db: Database session
        days: Number of days to analyze (default: 30)

    Returns:
        SentimentStats object with aggregated statistics

    Raises:
        ValueError: If keyword_id is invalid
        DatabaseError: If database query fails
    """
    # Implementation
```

#### TypeScript (Frontend)

- **ESLint compliance**: Enforced by `.eslintrc`
- **Prettier formatting**: Automatic on save
- **Strict type checking**: `tsconfig.json` with `strict: true`
- **Component naming**: PascalCase for components, camelCase for functions

```typescript
interface KeywordDetailProps {
  keywordId: number;
  language?: string;
}

const KeywordDetailPage: React.FC<KeywordDetailProps> = ({
  keywordId,
  language = 'en'
}) => {
  // Implementation
};
```

### 5.2 Architecture Patterns

#### 5.2.1 Multi-Layer Sentiment Analysis

**Pattern**: Hybrid approach combining speed and accuracy

```python
# Step 1: Fast VADER baseline
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
vader = SentimentIntensityAnalyzer()
vader_scores = vader.polarity_scores(text)

# Step 2: Gemini enhancement (cached)
gemini_analysis = await gemini_client.analyze_sentiment(text)

# Step 3: Confidence-weighted combination
final_sentiment = (
    vader_scores['compound'] * (1 - gemini_analysis['confidence']) +
    gemini_analysis['sentiment'] * gemini_analysis['confidence']
)
```

**Location**: `backend/app/services/sentiment.py`

#### 5.2.2 Service Layer Pattern

**Separation of Concerns**:
- **API Layer** (`api/`): Request/response handling, validation
- **Service Layer** (`services/`): Business logic, AI integration
- **Task Layer** (`tasks/`): Async background jobs
- **Model Layer** (`models/`): Database schema

**Example**:
```python
# api/keywords.py (API Layer)
@router.get("/{keyword_id}")
async def get_keyword_detail(keyword_id: int, db: Session = Depends(get_db)):
    keyword = await keyword_service.get_keyword_by_id(keyword_id, db)
    return keyword

# services/keyword_service.py (Service Layer)
async def get_keyword_by_id(keyword_id: int, db: Session) -> Keyword:
    # Business logic
    keyword = db.query(Keyword).filter(Keyword.id == keyword_id).first()
    if not keyword:
        raise ValueError("Keyword not found")
    return keyword
```

#### 5.2.3 Repository Pattern (Database Access)

**Convention**: All database queries go through service functions, not directly in API routes.

```python
# ❌ BAD: Direct database access in API route
@router.get("/keywords/{keyword_id}")
async def get_keyword(keyword_id: int, db: Session = Depends(get_db)):
    keyword = db.query(Keyword).filter(Keyword.id == keyword_id).first()
    return keyword

# ✅ GOOD: Service layer abstraction
@router.get("/keywords/{keyword_id}")
async def get_keyword(keyword_id: int, db: Session = Depends(get_db)):
    keyword = await keyword_service.get_keyword_by_id(keyword_id, db)
    return keyword
```

#### 5.2.4 Async Task Processing (Celery)

**Pattern**: Long-running tasks are delegated to Celery workers

```python
# tasks/scraping.py
@celery_app.task(bind=True, max_retries=3)
def scrape_news(self):
    """Scrape news from all enabled sources."""
    try:
        sources = get_enabled_sources()
        for source in sources:
            articles = scraper.scrape_source(source)
            save_articles(articles)
    except Exception as exc:
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))

# Schedule in celery_app.py
celery_app.conf.beat_schedule = {
    "scrape-news-hourly": {
        "task": "app.tasks.scraping.scrape_news",
        "schedule": crontab(minute=0),  # Every hour
    },
}
```

#### 5.2.5 Error Handling Pattern

**Convention**: Use structured logging with context

```python
from app.monitoring import get_logger

logger = get_logger(__name__)

async def process_keyword(keyword_id: int):
    try:
        # Business logic
        logger.info("Processing keyword", extra={"keyword_id": keyword_id})
        result = await perform_operation()
        logger.info("Keyword processed", extra={"keyword_id": keyword_id, "result": result})
        return result
    except ValueError as e:
        logger.warning("Invalid keyword", extra={"keyword_id": keyword_id, "error": str(e)})
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Unexpected error", extra={"keyword_id": keyword_id}, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
```

#### 5.2.6 Environment Configuration

**Pattern**: Pydantic Settings with validation

```python
# backend/app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    # Database
    database_url: str = Field(..., description="PostgreSQL connection string")

    # API Keys
    gemini_api_key: str = Field(..., description="Google Gemini API key")

    # Environment
    environment: str = Field("development", pattern="^(development|staging|production)$")
    debug: bool = Field(True)

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
    )

# Usage (singleton pattern)
from functools import lru_cache

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
```

#### 5.2.7 Type-Safe API Client (Frontend)

**Pattern**: Axios wrapper with TypeScript interfaces

```typescript
// frontend/src/api/client.ts
import axios, { AxiosInstance } from 'axios';

class APIClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
      timeout: 30000,
    });
  }

  async getKeyword(id: number, language: string = 'en'): Promise<Keyword> {
    const response = await this.client.get(`/api/keywords/${id}`, {
      params: { language },
    });
    return response.data as Keyword;
  }
}

export const apiClient = new APIClient();
```

---

## 6. Database Schema

### 6.1 Core Tables

#### `keywords` - Tracked keywords

```sql
CREATE TABLE keywords (
    id SERIAL PRIMARY KEY,
    keyword_en VARCHAR(255) UNIQUE NOT NULL,  -- English keyword
    keyword_th VARCHAR(255),                   -- Thai translation
    keyword_de VARCHAR(255),                   -- German translation
    keyword_fr VARCHAR(255),                   -- French translation
    keyword_es VARCHAR(255),                   -- Spanish translation
    keyword_it VARCHAR(255),                   -- Italian translation
    keyword_pl VARCHAR(255),                   -- Polish translation
    keyword_sv VARCHAR(255),                   -- Swedish translation
    keyword_nl VARCHAR(255),                   -- Dutch translation
    category VARCHAR(100),                     -- "geopolitics", "economy", etc.
    popularity_score FLOAT DEFAULT 0.0,        -- Trending metric
    search_count INTEGER DEFAULT 0,            -- User search count
    last_searched TIMESTAMP,                   -- Last search time
    next_search_after TIMESTAMP,               -- Cooldown expiry
    search_priority INTEGER DEFAULT 0,         -- Queue priority
    embedding vector(384),                     -- Semantic vector
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_keywords_en ON keywords(keyword_en);
CREATE INDEX idx_keywords_category ON keywords(category);
CREATE INDEX idx_keywords_priority ON keywords(search_priority DESC);
```

#### `articles` - News articles

```sql
CREATE TABLE articles (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    summary TEXT,                              -- AI-generated summary
    full_text TEXT,                            -- Complete article body
    source_url VARCHAR(2048) UNIQUE NOT NULL,  -- Article URL
    source VARCHAR(255) NOT NULL,              -- "BBC", "Reuters", etc.
    published_date TIMESTAMP,
    scraped_date TIMESTAMP DEFAULT NOW(),
    language VARCHAR(10) DEFAULT 'en',

    -- Content classification
    classification VARCHAR(50),                -- "fact", "opinion", "mixed"
    sentiment_classification VARCHAR(50),      -- "positive", "negative", "neutral"
    credibility_score FLOAT,                   -- 0.0-1.0

    -- Sentiment analysis (VADER + Gemini hybrid)
    sentiment_overall FLOAT,                   -- -1.0 to +1.0
    sentiment_confidence FLOAT,                -- 0.0 to 1.0
    sentiment_subjectivity FLOAT,              -- 0.0 to 1.0
    emotion_positive FLOAT,                    -- 0.0 to 1.0
    emotion_negative FLOAT,                    -- 0.0 to 1.0
    emotion_neutral FLOAT,                     -- 0.0 to 1.0

    -- Semantic search
    embedding vector(384),                     -- Sentence Transformers embedding

    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_articles_source ON articles(source);
CREATE INDEX idx_articles_published_date ON articles(published_date DESC);
CREATE INDEX idx_articles_sentiment ON articles(sentiment_overall);
CREATE INDEX idx_articles_url ON articles(source_url);
```

#### `keyword_articles` - Many-to-many junction

```sql
CREATE TABLE keyword_articles (
    keyword_id INTEGER REFERENCES keywords(id) ON DELETE CASCADE,
    article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE,
    relevance_score FLOAT DEFAULT 1.0,         -- Keyword relevance (0.0-1.0)
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (keyword_id, article_id)
);

-- Indexes
CREATE INDEX idx_keyword_articles_keyword ON keyword_articles(keyword_id);
CREATE INDEX idx_keyword_articles_article ON keyword_articles(article_id);
```

### 6.2 Analysis Tables

#### `sentiment_trends` - Daily precomputed aggregates

```sql
CREATE TABLE sentiment_trends (
    id SERIAL PRIMARY KEY,
    keyword_id INTEGER REFERENCES keywords(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    avg_sentiment FLOAT,                       -- Weighted by confidence
    article_count INTEGER,
    positive_count INTEGER,
    negative_count INTEGER,
    neutral_count INTEGER,
    top_sources JSONB,                         -- {"BBC": 0.82, "Reuters": 0.76}
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(keyword_id, date)
);

-- Indexes
CREATE INDEX idx_sentiment_trends_keyword_date ON sentiment_trends(keyword_id, date);
```

#### `keyword_relations` - Mind map relationships

```sql
CREATE TABLE keyword_relations (
    keyword1_id INTEGER REFERENCES keywords(id) ON DELETE CASCADE,
    keyword2_id INTEGER REFERENCES keywords(id) ON DELETE CASCADE,
    relation_type VARCHAR(50),                 -- "related", "parent", "child", "causal"
    strength_score FLOAT,                      -- 0.0-1.0
    evidence_count INTEGER DEFAULT 0,          -- Articles supporting relationship
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (keyword1_id, keyword2_id)
);
```

### 6.3 Management Tables

#### `keyword_suggestions` - User submissions

```sql
CREATE TABLE keyword_suggestions (
    id SERIAL PRIMARY KEY,
    keyword_en VARCHAR(255) NOT NULL,
    keyword_th VARCHAR(255),
    category VARCHAR(100) DEFAULT 'general',
    reason TEXT,                               -- Why suggest this
    contact_email VARCHAR(255),
    status VARCHAR(50) DEFAULT 'pending',      -- "pending", "approved", "rejected"
    votes INTEGER DEFAULT 1,                   -- Community voting
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### `news_sources` - Configurable scrapers

```sql
CREATE TABLE news_sources (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,         -- "BBC", "Reuters", etc.
    base_url TEXT NOT NULL,
    language VARCHAR(10) DEFAULT 'en',
    country VARCHAR(100),                      -- "UK", "Germany", etc.
    priority INTEGER DEFAULT 5,                -- 1-10 (higher = more frequent)
    parser VARCHAR(50),                        -- "generic", "xpath", etc.
    tags TEXT[],                               -- ["politics", "business"]
    enabled BOOLEAN DEFAULT TRUE,
    last_scraped TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 6.4 Important Relationships

```
Keyword
  ├── has many KeywordArticles (through junction)
  ├── has many SentimentTrends (daily aggregates)
  ├── has many KeywordEvaluations (AI decisions)
  ├── has many KeywordSearchQueues (scheduled searches)
  └── has many KeywordRelations (mind map connections)

Article
  ├── has many KeywordArticles (through junction)
  └── belongs to NewsSource (via source field)

KeywordSuggestion
  └── has many KeywordEvaluations (approval process)

NewsSource
  └── has many IngestionHistories (scraping log)
```

### 6.5 Vector Search (pgvector)

**Setup**:
```sql
-- Enable extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create vector indexes for fast similarity search
CREATE INDEX idx_keywords_embedding ON keywords
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

CREATE INDEX idx_articles_embedding ON articles
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

**Usage**:
```python
# Find similar keywords (cosine similarity > 0.7)
from sqlalchemy import text

similar_keywords = db.execute(
    text("""
        SELECT keyword_en, 1 - (embedding <=> :query_embedding) as similarity
        FROM keywords
        WHERE 1 - (embedding <=> :query_embedding) > 0.7
        ORDER BY embedding <=> :query_embedding
        LIMIT 10
    """),
    {"query_embedding": query_embedding}
).fetchall()
```

---

## 7. API Structure

### 7.1 API Organization

**Base URL**: `/api` (v1 implicit)
**Authentication**: Admin endpoints require HTTP Basic Auth
**Response Format**: JSON
**Error Format**: `{"detail": "Error message", "status_code": 400}`

### 7.2 Endpoint Summary

#### Keywords Router (`/api/keywords/`)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/` | Search keywords (paginated) | No |
| GET | `/{id}` | Get keyword detail | No |
| GET | `/{id}/articles` | Related articles | No |
| GET | `/{id}/relations` | Mind map data | No |

#### Sentiment Router (`/api/sentiment/`)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/keywords/{id}/sentiment` | Overall stats | No |
| GET | `/keywords/{id}/sentiment/timeline` | Time series | No |
| GET | `/keywords/compare` | Multi-keyword comparison | No |
| GET | `/articles/{id}/sentiment` | Article-level analysis | No |

#### Search Router (`/api/search/`)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/articles` | Full-text search | No |
| GET | `/semantic` | Vector similarity search | No |
| GET | `/similar/{article_id}` | Find similar articles | No |

#### Admin Router (`/admin/`)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/sources` | List news sources | Yes |
| POST | `/sources` | Add new source | Yes |
| POST | `/sources/{id}/toggle` | Enable/disable source | Yes |
| POST | `/keywords/suggestions/{id}/approve` | Approve suggestion | Yes |
| POST | `/keywords/suggestions/{id}/reject` | Reject suggestion | Yes |

### 7.3 Request/Response Examples

#### Get Keyword Detail

**Request**:
```http
GET /api/keywords/123?language=en
```

**Response**:
```json
{
  "id": 123,
  "keyword_en": "Thailand Tourism",
  "keyword_th": "การท่องเที่ยวไทย",
  "category": "economy",
  "popularity_score": 0.85,
  "search_count": 150,
  "article_count": 245,
  "average_sentiment": 0.35,
  "created_at": "2024-01-15T10:30:00Z"
}
```

#### Get Sentiment Timeline

**Request**:
```http
GET /api/sentiment/keywords/123/sentiment/timeline?days=30
```

**Response**:
```json
{
  "keyword_id": 123,
  "period": "30_days",
  "data_points": [
    {
      "date": "2024-01-01",
      "avg_sentiment": 0.25,
      "article_count": 8,
      "positive_count": 5,
      "negative_count": 2,
      "neutral_count": 1
    },
    {
      "date": "2024-01-02",
      "avg_sentiment": 0.32,
      "article_count": 12,
      "positive_count": 8,
      "negative_count": 3,
      "neutral_count": 1
    }
  ],
  "summary": {
    "total_articles": 245,
    "avg_sentiment": 0.35,
    "trend": "improving"
  }
}
```

### 7.4 Rate Limiting

- **Global**: 60 requests/minute per IP (FastAPI middleware)
- **API Endpoints**: 10 requests/second (Nginx)
- **Gemini API**: 30 calls/minute (client-side rate limiter)

---

## 8. Testing Guidelines

### 8.1 Test Structure

**Location**: `backend/app/tests/` and `backend/tests/`

**Test Categories**:
1. **Database Tests** (`test_database.py`) - Model integrity, relationships
2. **AI Services Tests** (`test_ai_services.py`) - Sentiment, embeddings, NER
3. **API Endpoint Tests** (`test_api_endpoints.py`) - All 30+ endpoints

### 8.2 Running Tests

```bash
# Run all tests
docker compose exec backend pytest tests/ -v

# Run specific category
docker compose exec backend pytest tests/test_api_endpoints.py -v

# Run with coverage
docker compose exec backend pytest tests/ --cov=app --cov-report=html

# Run specific test function
docker compose exec backend pytest tests/test_api_endpoints.py::test_get_keyword_detail -v

# Run tests matching pattern
docker compose exec backend pytest tests/ -k "sentiment" -v
```

### 8.3 Writing Tests

**Test Fixtures** (`backend/app/testing/fixtures.py`):

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

@pytest.fixture
def db_session():
    """Provide a clean database session for tests."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()

@pytest.fixture
def client(db_session):
    """Provide FastAPI test client."""
    from app.main import app
    from app.core.database import get_db

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)
```

**Example Test**:

```python
def test_get_keyword_detail(client, db_session):
    """Test GET /api/keywords/{id} endpoint."""
    # Arrange: Create test data
    keyword = Keyword(
        keyword_en="Test Keyword",
        category="test",
        popularity_score=0.5
    )
    db_session.add(keyword)
    db_session.commit()

    # Act: Make request
    response = client.get(f"/api/keywords/{keyword.id}")

    # Assert: Check response
    assert response.status_code == 200
    data = response.json()
    assert data["keyword_en"] == "Test Keyword"
    assert data["category"] == "test"
```

### 8.4 Mocking External Services

**Mock Gemini API**:

```python
import pytest
from unittest.mock import patch, MagicMock

@pytest.fixture
def mock_gemini():
    """Mock Gemini API client."""
    with patch('app.services.gemini_client.GeminiClient') as mock:
        mock_instance = MagicMock()
        mock_instance.analyze_sentiment.return_value = {
            "sentiment": 0.75,
            "confidence": 0.85,
            "subjectivity": 0.65
        }
        mock.return_value = mock_instance
        yield mock_instance

def test_sentiment_analysis(mock_gemini):
    """Test sentiment analysis with mocked Gemini."""
    from app.services.sentiment import analyze_text_sentiment

    result = analyze_text_sentiment("This is great news!")

    assert result["sentiment"] > 0.5
    assert result["confidence"] > 0.8
    mock_gemini.analyze_sentiment.assert_called_once()
```

### 8.5 Test Coverage Goals

- **Overall**: >80% code coverage
- **Critical paths**: 100% (authentication, payment, data integrity)
- **API endpoints**: All endpoints tested
- **Error handling**: All error branches tested

---

## 9. Deployment Procedures

### 9.1 Development Deployment

```bash
# Start all services
./setup.sh

# Or manually
docker compose up -d

# Verify services
docker compose ps
```

### 9.2 Production Deployment

```bash
# 1. Clone repository on VPS
git clone https://github.com/ChildWerapol/EU-Intelligence-Hub.git
cd EU-Intelligence-Hub

# 2. Configure production environment
cp .env.production.example .env.production
nano .env.production  # Update all secrets

# 3. Run deployment script
./deploy.sh production

# 4. Setup SSL (Let's Encrypt)
./setup-ssl.sh yourdomain.com

# 5. Verify deployment
./scripts/health_check.sh
```

### 9.3 Docker Compose Profiles

**Development** (`docker-compose.yml`):
- Hot reload enabled
- Exposed ports for debugging
- Volume mounts for live code editing
- Debug logging enabled

**Production** (`docker-compose.prod.yml`):
- Optimized images (multi-stage builds)
- No hot reload
- Gunicorn with 4 workers
- SSL termination via Nginx
- Health checks on all services
- Non-root users
- Secrets via environment variables

### 9.4 Health Checks

```bash
# Quick health check
curl http://localhost:8000/health

# Comprehensive health check
./scripts/health_check.sh

# Expected output:
# ✅ Backend API: Healthy
# ✅ PostgreSQL: Healthy
# ✅ Redis: Healthy
# ✅ Celery Worker: Healthy
# ✅ Frontend: Healthy
```

### 9.5 Database Backups

**Automated Backups** (Celery task):
```python
# Runs daily at 01:00 UTC
@celery_app.task
def backup_database():
    """Backup PostgreSQL database."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"/backups/db_backup_{timestamp}.sql.gz"

    # pg_dump with compression
    subprocess.run([
        "pg_dump",
        "-h", "postgres",
        "-U", settings.postgres_user,
        "-d", settings.postgres_db,
        "-F", "c",  # Custom format
        "-Z", "9",  # Max compression
        "-f", backup_file
    ])

    logger.info("Database backup completed", extra={"file": backup_file})
```

**Manual Backup**:
```bash
# Create backup
docker compose exec backend python scripts/backup.py

# Restore backup
docker compose exec backend python scripts/restore.py backups/db_backup_20240115_010000.sql.gz
```

### 9.6 Monitoring Setup

**Access Monitoring Tools**:
- **Grafana**: http://localhost:3001 (admin/admin)
- **Prometheus**: http://localhost:9090
- **AlertManager**: http://localhost:9093

**Key Metrics**:
- Request latency (p50, p95, p99)
- Error rate (5xx responses)
- Database connection pool usage
- Redis cache hit rate
- Celery task queue length
- Celery task success/failure rate

---

## 10. Common Tasks

### 10.1 Adding a New API Endpoint

**Steps**:

1. **Define route in router** (`backend/app/api/your_router.py`):
```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db

router = APIRouter(prefix="/api/your_feature", tags=["YourFeature"])

@router.get("/items/{item_id}")
async def get_item(item_id: int, db: Session = Depends(get_db)):
    """Get item by ID."""
    # Implementation
    return {"item_id": item_id}
```

2. **Register router in main app** (`backend/app/main.py`):
```python
from app.api import your_router

app.include_router(your_router.router)
```

3. **Add tests** (`backend/app/tests/test_your_router.py`):
```python
def test_get_item(client):
    response = client.get("/api/your_feature/items/123")
    assert response.status_code == 200
    assert response.json()["item_id"] == 123
```

4. **Update API docs**: OpenAPI will auto-generate docs at `/docs`

### 10.2 Adding a New Database Model

**Steps**:

1. **Define model** (`backend/app/models/models.py`):
```python
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class NewModel(Base):
    __tablename__ = "new_models"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)

    # Relationships
    related_id = Column(Integer, ForeignKey("related_table.id"))
    related = relationship("RelatedModel", back_populates="new_models")
```

2. **Create migration**:
```bash
docker compose exec backend alembic revision --autogenerate -m "Add new_models table"
```

3. **Review migration** (`backend/migrations/versions/xxxxx_add_new_models_table.py`)

4. **Apply migration**:
```bash
docker compose exec backend alembic upgrade head
```

5. **Add tests** (`backend/app/tests/test_database.py`):
```python
def test_new_model_creation(db_session):
    new_model = NewModel(name="Test", description="Test description")
    db_session.add(new_model)
    db_session.commit()

    assert new_model.id is not None
    assert new_model.name == "Test"
```

### 10.3 Adding a New Celery Task

**Steps**:

1. **Define task** (`backend/app/tasks/your_tasks.py`):
```python
from app.tasks.celery_app import celery_app
from app.monitoring import get_logger

logger = get_logger(__name__)

@celery_app.task(bind=True, max_retries=3)
def your_background_task(self, param1: str, param2: int):
    """Description of what this task does."""
    try:
        logger.info("Task started", extra={"param1": param1})

        # Business logic here
        result = perform_operation(param1, param2)

        logger.info("Task completed", extra={"result": result})
        return result

    except Exception as exc:
        logger.error("Task failed", exc_info=True)
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
```

2. **Schedule task** (`backend/app/tasks/celery_app.py`):
```python
celery_app.conf.beat_schedule.update({
    "your-task-daily": {
        "task": "app.tasks.your_tasks.your_background_task",
        "schedule": crontab(hour=2, minute=0),  # Daily at 2 AM
        "args": ("param1_value", 123),
    },
})
```

3. **Test task**:
```bash
# Run task manually
docker compose exec backend python -c "from app.tasks.your_tasks import your_background_task; your_background_task.delay('test', 123)"

# Check Celery logs
docker compose logs celery_worker -f
```

### 10.4 Adding a New React Component

**Steps**:

1. **Create component** (`frontend/src/components/YourComponent.tsx`):
```typescript
import React from 'react';

interface YourComponentProps {
  title: string;
  data: any[];
}

const YourComponent: React.FC<YourComponentProps> = ({ title, data }) => {
  return (
    <div className="p-4">
      <h2 className="text-2xl font-bold">{title}</h2>
      <div className="mt-4">
        {data.map((item, index) => (
          <div key={index}>{item.name}</div>
        ))}
      </div>
    </div>
  );
};

export default YourComponent;
```

2. **Add types** (`frontend/src/types/index.ts`):
```typescript
export interface YourDataType {
  id: number;
  name: string;
  description: string;
}
```

3. **Use in page** (`frontend/src/pages/YourPage.tsx`):
```typescript
import YourComponent from '@/components/YourComponent';

const YourPage: React.FC = () => {
  const [data, setData] = useState<YourDataType[]>([]);

  return (
    <div>
      <YourComponent title="Your Title" data={data} />
    </div>
  );
};
```

### 10.5 Debugging Issues

**Backend Debugging**:
```bash
# View logs
docker compose logs backend -f

# Access container shell
docker compose exec backend bash

# Python interactive shell with app context
docker compose exec backend python
>>> from app.core.database import SessionLocal
>>> db = SessionLocal()
>>> from app.models.models import Keyword
>>> keywords = db.query(Keyword).all()
>>> print(keywords)

# Check database directly
docker compose exec postgres psql -U newsadmin -d news_intelligence
# \dt  -- List tables
# SELECT * FROM keywords LIMIT 5;
```

**Frontend Debugging**:
```bash
# View logs
docker compose logs frontend -f

# Access container shell
docker compose exec frontend sh

# Check build
docker compose exec frontend npm run build
```

**Celery Debugging**:
```bash
# View worker logs
docker compose logs celery_worker -f

# View beat scheduler logs
docker compose logs celery_beat -f

# Inspect active tasks
docker compose exec backend celery -A app.tasks.celery_app inspect active

# Check scheduled tasks
docker compose exec backend celery -A app.tasks.celery_app inspect scheduled
```

---

## 11. Important Files Reference

### 11.1 Configuration Files

| File | Purpose | When to Edit |
|------|---------|--------------|
| `.env` | Environment variables (dev) | Adding secrets, changing ports |
| `.env.production` | Production secrets | Deploying to production |
| `backend/app/core/config.py` | Pydantic settings | Adding new config options |
| `docker-compose.yml` | Development orchestration | Adding services, changing ports |
| `docker-compose.prod.yml` | Production orchestration | Production-specific changes |
| `nginx/nginx.conf` | Nginx global config | Rate limiting, security headers |
| `nginx/conf.d/app.conf` | App-specific routing | Adding routes, SSL config |

### 11.2 Documentation Files

| File | Purpose | Update When |
|------|---------|-------------|
| `README.md` | Main project documentation | Major feature additions |
| `PROGRESS.md` | Development progress tracker | Completing tasks/phases |
| `TODO.md` | Prioritized backlog | Adding/completing tasks |
| `FEATURES.md` | Complete feature inventory | Adding features |
| `INSTALLATION.md` | Setup guide | Changing setup process |
| `DEPLOYMENT.md` | Deployment guide | Changing deployment |
| `CLAUDE.md` | This file (AI assistant guide) | Architecture changes |

### 11.3 Critical Backend Files

| File | Purpose | Lines | Key Responsibility |
|------|---------|-------|---------------------|
| `backend/app/main.py` | FastAPI app initialization | ~150 | App entry point |
| `backend/app/models/models.py` | Database models | ~1,200 | Schema definitions |
| `backend/app/core/database.py` | DB connection | ~100 | Session management |
| `backend/app/core/config.py` | Settings | ~200 | Environment config |
| `backend/app/services/gemini_client.py` | Gemini API wrapper | ~300 | AI integration |
| `backend/app/services/sentiment.py` | Sentiment analysis | ~400 | VADER + Gemini hybrid |
| `backend/app/tasks/celery_app.py` | Celery configuration | ~150 | Task scheduling |

### 11.4 Critical Frontend Files

| File | Purpose | Lines | Key Responsibility |
|------|---------|-------|---------------------|
| `frontend/src/main.tsx` | React entry point | ~20 | App initialization |
| `frontend/src/App.tsx` | Main router | ~100 | Routing & layout |
| `frontend/src/api/client.ts` | API client | ~300 | Type-safe API calls |
| `frontend/src/types/index.ts` | TypeScript types | ~100 | Interface definitions |

---

## 12. Troubleshooting

### 12.1 Common Issues

#### Issue: Docker Permission Denied

**Symptoms**:
```bash
docker: permission denied while trying to connect to the Docker daemon socket
```

**Solution**:
```bash
# Run fix script
./fix-docker-permissions.sh

# Log out and log back in
exit

# Verify
docker ps
```

#### Issue: PostgreSQL Connection Failed

**Symptoms**:
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Solution**:
```bash
# Check if PostgreSQL is running
docker compose ps postgres

# Check logs
docker compose logs postgres

# Restart PostgreSQL
docker compose restart postgres

# Verify connection
docker compose exec postgres psql -U newsadmin -d news_intelligence
```

#### Issue: Gemini API Rate Limit

**Symptoms**:
```
google.api_core.exceptions.ResourceExhausted: 429 Resource has been exhausted
```

**Solution**:
- Rate limiter is built-in (30 calls/min)
- Check `backend/app/services/gemini_client.py` for rate limit settings
- Increase cooldown: `rate_limiter = AsyncRateLimiter(max_calls=20, period=60)`

#### Issue: Frontend Cannot Connect to Backend

**Symptoms**:
```
Network Error: Failed to fetch
```

**Solution**:
```bash
# Check backend is running
curl http://localhost:8000/health

# Check frontend environment
docker compose exec frontend cat /app/.env
# Should have: VITE_API_URL=http://localhost:8000

# Restart frontend
docker compose restart frontend
```

#### Issue: Celery Tasks Not Running

**Symptoms**:
- News not being scraped
- Sentiment trends not updating

**Solution**:
```bash
# Check Celery worker status
docker compose logs celery_worker

# Check Celery beat (scheduler)
docker compose logs celery_beat

# Verify Redis connection
docker compose exec backend redis-cli -h redis ping
# Should return: PONG

# Restart Celery services
docker compose restart celery_worker celery_beat
```

#### Issue: Tests Failing

**Symptoms**:
```
pytest: FAILED tests/test_something.py
```

**Solution**:
```bash
# Run tests with verbose output
docker compose exec backend pytest tests/ -vv

# Run specific test
docker compose exec backend pytest tests/test_api_endpoints.py::test_get_keyword -vv

# Check test database
docker compose exec backend pytest tests/ --pdb  # Drop into debugger on failure
```

### 12.2 Logging & Debugging

**View Logs**:
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs backend -f
docker compose logs postgres -f
docker compose logs redis -f

# Filter by error level
docker compose logs backend | grep ERROR
docker compose logs backend | grep -i "exception"

# Search for specific keyword
docker compose logs backend | grep "Singapore"
```

**Structured Logging**:
```python
# Backend logs are JSON formatted
# Example log entry:
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "INFO",
  "logger": "app.tasks.scraping",
  "message": "News scraping completed",
  "extra": {
    "source": "BBC",
    "article_count": 15,
    "duration_seconds": 12.5
  }
}
```

### 12.3 Performance Issues

**Slow API Responses**:
```bash
# Check database indexes
docker compose exec postgres psql -U newsadmin -d news_intelligence
# \di  -- List all indexes

# Check query performance
EXPLAIN ANALYZE SELECT * FROM articles WHERE sentiment_overall > 0.5;

# Check Redis cache hit rate
docker compose exec redis redis-cli INFO stats
# Look for: keyspace_hits / (keyspace_hits + keyspace_misses)
```

**High Memory Usage**:
```bash
# Check container resource usage
docker stats

# Check PostgreSQL connections
docker compose exec postgres psql -U newsadmin -d news_intelligence
SELECT count(*) FROM pg_stat_activity;

# Restart services
docker compose restart
```

### 12.4 Getting Help

**Internal Resources**:
1. **README.md** - Project overview and quick start
2. **INSTALLATION.md** - Detailed setup guide
3. **ERROR_LOGGING.md** - Monitoring and error analysis
4. **PROGRESS.md** - Development history and context
5. **API Docs** - http://localhost:8000/docs (when backend running)

**External Resources**:
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **SQLAlchemy Docs**: https://docs.sqlalchemy.org/
- **Celery Docs**: https://docs.celeryq.dev/
- **React Docs**: https://react.dev/
- **pgvector Docs**: https://github.com/pgvector/pgvector

---

## Summary for AI Assistants

When working on this codebase:

✅ **DO**:
- Read `PROGRESS.md` and `TODO.md` before starting work
- Use TodoWrite tool to track multi-step tasks
- Follow existing code patterns (service layer, type hints, structured logging)
- Write tests for new features (maintain >80% coverage)
- Update documentation when adding features
- Use descriptive commit messages with conventional format
- Push to the correct branch (`claude/claude-md-mhz9wemfxx4kpu6z-01F5kZ9is7isp98fiPvk2vPa`)

❌ **DON'T**:
- Make database queries directly in API routes (use service layer)
- Hardcode secrets or configuration (use environment variables)
- Skip writing tests for new features
- Push to main branch directly
- Use blocking I/O in async functions
- Ignore type hints (Python) or TypeScript errors
- Skip logging for important operations

**Key Files to Know**:
- `backend/app/models/models.py` - Database schema (1,200+ lines)
- `backend/app/services/` - All AI/ML logic
- `backend/app/tasks/` - Background job definitions
- `frontend/src/api/client.ts` - Type-safe API wrapper
- `docker-compose.yml` - Service orchestration

**Common Commands**:
```bash
# Start development
./setup.sh

# Run tests
docker compose exec backend pytest tests/ -v

# View logs
docker compose logs backend -f

# Restart service
docker compose restart backend

# Access database
docker compose exec postgres psql -U newsadmin -d news_intelligence
```

**When in Doubt**:
1. Check the documentation files listed in section 11.2
2. Look at existing similar code for patterns
3. Run tests to verify your changes
4. Check logs for error details

---

**Document Maintenance**: Update this file when:
- Architecture changes significantly
- New major patterns are introduced
- Common troubleshooting steps emerge
- New services are added to Docker orchestration

**Last Updated**: 2025-11-14
**Maintained By**: Development Team + AI Assistants
