## EU Intelligence Hub — Discovery Notes

### 1. Current Architecture Overview
- **Frontend**: React 18 + Vite client (`frontend/`) with React Query, Tailwind, Zustand. Communicates with backend via REST (e.g. `/api/keywords`).
- **Backend**: FastAPI app (`backend/app/main.py`) exposing keyword, search, sentiment, document, suggestion APIs. Uses SQLAlchemy ORM against PostgreSQL and Celery for background tasks.
- **Data Layer**: PostgreSQL with models in `backend/app/models/models.py` (keywords, articles, keyword relations, suggestions, sentiment trends, etc.). Redis used for caching/celery broker.
- **AI & Services**: Gemini-based services (`app/services`) for keyword evaluation, embeddings (SentenceTransformer), scraping (Gemini-assisted), sentiment analysis.
- **Infrastructure**: Docker Compose orchestrating backend, frontend, postgres, redis, prometheus, grafana, exporters; monitoring setup in `monitoring/`.
- **Testing**: Pytest-based backend tests (`backend/app/tests`), Playwright/Vitest setup for frontend.

### 2. Tech Stack Inventory
- **Languages**: Python 3.11+, TypeScript/JavaScript (ES2020).
- **Backend Frameworks & Libraries**: FastAPI, SQLAlchemy, Celery, Redis, Pydantic, SentenceTransformers, aiohttp, Prometheus client.
- **Frontend Libraries**: React, React Router, React Query, TailwindCSS, Radix UI, Recharts, Lucide icons, Zustand.
- **Datastores**: PostgreSQL (primary), Redis (cache/broker).
- **AI/ML**: Gemini API for keyword evaluation, embeddings; spaCy + SentenceTransformer for NLP.
- **DevOps/Monitoring**: Docker Compose, Prometheus, Grafana, Alertmanager, Node/Postgres/Redis exporters.

### 3. Identified Improvement Areas
| Area | Description | Severity |
| --- | --- | --- |
| Keyword approval workflow | Existing `keyword_approval_service` uses Gemini but lacks structured scoring, persistence of evaluations, and merge logic aligned with new requirements. | **Critical** |
| Search functionality | No unified article search endpoint or CLI; current API limited to keyword/article listing, preventing user-driven queries. | **Critical** |
| News source coverage | `NewsScraper` relies on Gemini research with limited hard-coded sources; no configurable source registry or granular error handling. | **High** |
| Search throttling | Keywords model has `last_searched` but execution flow lacks enforced cooldown or scheduler to avoid redundant scraping. | **High** |
| Multilingual support | Translation limited to Thai; no language detection or configurable set of target languages, risking coverage gaps. | **High** |
| Logging & observability | Monitoring exists but logging not consistently structured; missing dedicated log files for AI decisions/search activity and log rotation. | **Medium** |
| Configuration management | Source definitions, rate limits, AI settings hard-coded in code; no external JSON config or env-driven overrides. | **Medium** |
| Documentation currency | README and docs lack details on new features, API keys, architecture diagrams; no changelog present. | **Low** |

### 4. Notes
- Database already includes `last_searched` on keywords, easing throttling implementation.
- Existing Celery tasks (e.g., `keyword_search`) provide hooks for scheduler integration.
- Monitoring scaffolding (Prometheus/Grafana) is present but should be tied into new log outputs and `/health` metrics.
