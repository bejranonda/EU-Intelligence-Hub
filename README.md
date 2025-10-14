# 🌍 European News Intelligence Hub

A production-grade web application that aggregates and analyzes European media coverage about Thailand (our pilot keyword) and other topics using AI-powered sentiment analysis, keyword extraction, and interactive visualizations.

## ✨ Key Features

- **🤖 Automated News Scraping**: Hourly collection from major European sources (BBC, Reuters, DW, France24)
- **😊😟 Sentiment Analysis**: AI-powered evaluation of positive/negative media opinions (-1.0 to +1.0 scale)
- **🗺️ Interactive Mind Maps**: Visualize semantic relationships between keywords using React Flow
- **📊 Trend Tracking**: Monitor sentiment changes over time with interactive timeline graphs
- **🔍 Semantic Search**: Find articles using vector similarity and keyword relationships
- **🌐 Bilingual Support**: Full EN/TH language support with instant toggle
- **📤 Manual Uploads**: Extract keywords from PDF/DOCX/TXT documents
- **💡 Crowd Intelligence**: Visitors can suggest keywords for future research

## 🛠️ Technology Stack

**Frontend**: React 18 + TypeScript + Tailwind CSS + shadcn/ui + React Flow + Recharts  
**Backend**: Python FastAPI + PostgreSQL 16 (pgvector) + Redis + Celery  
**AI/ML**: Google Gemini API + Sentence Transformers + spaCy + VADER  
**Infrastructure**: Docker Compose + Nginx + Ubuntu 24 LTS

## 🚀 Quick Start

### Prerequisites

```bash
# Required credentials
export GEMINI_API_KEY="your_gemini_api_key_here"
export ADMIN_PASSWORD="your_secure_password"
```

### Installation

```bash
# Clone and start all services
git clone <repository-url>
cd european-news-intelligence-hub
./setup.sh

# Application will be available at:
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Development

```bash
# Start services
docker-compose up

# Run tests
python -m pytest tests/
npm test

# View logs
docker-compose logs -f
```

## 📊 Core Capabilities

### Sentiment Analysis
- **Multi-layered detection**: VADER baseline + Gemini AI for nuanced opinion analysis
- **Confidence scoring**: Know which sentiment scores are most reliable
- **Emotion breakdown**: Positive/negative/neutral emotional components
- **Source tracking**: Identify which publications are most favorable/critical
- **Comparative analysis**: Compare sentiment across countries (Thailand vs. Vietnam vs. Indonesia)

### Data Processing
- **Fact vs. Opinion classification**: AI distinguishes verifiable claims from subjective analysis
- **Keyword extraction**: Automatic identification of 3-5 key terms per article
- **Relationship mapping**: Discover causal and thematic connections between keywords
- **Named entity recognition**: Extract people, organizations, and locations
- **Vector embeddings**: Enable semantic search beyond exact keyword matches

## 📁 Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── api/              # FastAPI endpoints
│   │   ├── models/           # Database models
│   │   ├── services/         # Business logic
│   │   │   ├── scraper.py    # News collection
│   │   │   ├── sentiment.py  # Sentiment analysis
│   │   │   └── embeddings.py # Vector search
│   │   └── tasks/            # Celery background jobs
│   └── tests/
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   │   ├── SentimentOverview.tsx
│   │   │   ├── SentimentTimeline.tsx
│   │   │   └── MindMap.tsx
│   │   ├── pages/            # Route pages
│   │   └── services/         # API clients
│   └── public/
├── docker-compose.yml
├── PROGRESS.md               # Session state tracking
├── tests.json                # Test results
├── TODO.md                   # Task backlog
└── setup.sh                  # Initialization script
```

## 🎯 Use Cases

### Intelligence Analyst
> "Show me how European media sentiment about Thailand has changed over the past 3 months"

**Result**: Interactive timeline graph showing +12% improvement in positive coverage, with drill-down into specific articles and sources.

### Public Relations Manager
> "Which European publications are most favorable toward Thailand's tourism sector?"

**Result**: Ranked list showing BBC and DW lead with +0.78 and +0.72 sentiment scores respectively.

### Policy Researcher
> "Find all articles discussing Thailand's political stability and classify as fact vs. opinion"

**Result**: 23 articles found, 61% classified as opinion, 39% as fact-based reporting, with sentiment distribution.

## 📈 API Endpoints

### Core Endpoints
```
GET  /api/keywords                    # Search keywords
GET  /api/keywords/{id}/articles      # Get related articles
GET  /api/keywords/{id}/relations     # Mind map data
POST /api/documents                   # Upload document
POST /api/suggestions                 # Suggest keyword
```

### Sentiment Endpoints
```
GET  /api/keywords/{id}/sentiment              # Overall sentiment
GET  /api/keywords/{id}/sentiment/timeline     # Time-series data
GET  /api/keywords/compare/sentiment           # Compare countries
GET  /api/articles/{id}/sentiment/details      # Article sentiment
```

## 🔐 Security

- API keys stored in environment variables (never committed)
- SQL injection protection via parameterized queries
- Rate limiting on public endpoints
- HTTPS with Let's Encrypt SSL
- Input validation using Pydantic models

## 🧪 Testing

```bash
# Backend tests
pytest tests/ --cov=app --cov-report=html

# Frontend tests
npm run test

# E2E tests
npx playwright test

# Coverage requirement: >80%
```

## 📦 Deployment

### VPS Deployment

```bash
# On VPS (Ubuntu 24 LTS)
git clone <repository-url>
cd european-news-intelligence-hub
./deploy.sh production

# Services will run on:
# - Frontend: https://yourdomain.com
# - Backend: https://yourdomain.com/api
```

### Environment Variables

```bash
# Production .env
GEMINI_API_KEY=<your-key>
ADMIN_USERNAME=admin
ADMIN_PASSWORD=<secure-password>
POSTGRES_PASSWORD=<generated-password>
SECRET_KEY=<generated-secret>
ENVIRONMENT=production
```

## 🔄 Background Jobs

- **Hourly News Scraping**: Celery task runs every hour
- **Daily Sentiment Aggregation**: Summarizes trends at midnight UTC
- **Weekly Keyword Relationship Update**: Recalculates semantic connections
- **Monthly Cleanup**: Archives old articles and optimizes database

## 📊 Database Schema Highlights

```sql
-- Articles with full sentiment tracking
articles (
  id, title, summary, full_text, source_url,
  sentiment_overall,      # -1.0 to 1.0
  sentiment_confidence,   # 0.0 to 1.0
  emotion_positive,       # 0.0 to 1.0
  emotion_negative,       # 0.0 to 1.0
  classification          # fact/opinion/mixed
)

-- Daily sentiment trends
sentiment_trends (
  keyword_id, date, avg_sentiment,
  positive_count, negative_count, neutral_count,
  top_sources  # JSON: which sources most pos/neg
)

-- Comparative analysis
comparative_sentiment (
  primary_keyword, comparison_keyword,
  sentiment_gap, article_counts
)
```

## 🤝 Contributing

This project follows multi-session development methodology:

1. Read `PROGRESS.md` to understand current state
2. Check `TODO.md` for pending tasks
3. Run `./setup.sh` to start services
4. Verify tests pass: `pytest && npm test`
5. Make changes and update state files
6. Commit frequently with descriptive messages

## 📝 License

MIT License - See LICENSE file for details

## 🆘 Support

- **Issues**: Submit via GitHub Issues
- **Documentation**: See `/docs` directory
- **API Docs**: http://localhost:8000/docs (when running)

## 🎯 Roadmap

- [ ] Phase 1: Foundation & Database ✅
- [ ] Phase 2: AI Integration & Sentiment Analysis ✅
- [ ] Phase 3: API Endpoints ✅
- [ ] Phase 4: Frontend UI & Visualization ✅
- [ ] Phase 5: Production Deployment ✅
- [ ] Phase 6: Email alerts for sentiment changes
- [ ] Phase 7: Browser extension for quick saves
- [ ] Phase 8: Mobile app (iOS/Android)
