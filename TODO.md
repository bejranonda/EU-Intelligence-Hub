# European News Intelligence Hub - TODO

## Phase 1: Foundation (Current)
**Goal**: Working development environment with database and basic API

### Critical Tasks
- [ ] Create project directory structure
- [ ] Set up Docker Compose with PostgreSQL, Redis, FastAPI, React dev server
- [ ] Create database schema with sentiment tracking tables
- [ ] Build FastAPI skeleton with health check endpoint
- [ ] Create React app with TypeScript and Tailwind
- [ ] Write setup.sh to start all services
- [ ] Create initial tests for database connection and API health
- [ ] Update state files with progress

### Acceptance Criteria
- [ ] `docker-compose up` starts all services successfully
- [ ] Database schema matches specification exactly (including sentiment fields)
- [ ] `curl http://localhost:8000/health` returns 200 OK
- [ ] React app loads at http://localhost:3000
- [ ] All tests in tests.json pass

## Phase 2: AI Integration & Scraping (Next)
- [ ] Implement Gemini API client with error handling
- [ ] Create news scraper for European sources
- [ ] Build keyword extraction pipeline using spaCy
- [ ] Implement fact/opinion classifier
- [ ] Implement multi-layered sentiment analysis (VADER + Gemini)
- [ ] Set up Celery worker for hourly scraping
- [ ] Generate embeddings using Sentence Transformers
- [ ] Write integration tests

## Phase 3: API Endpoints & Search
- [ ] Implement keyword search endpoint with pagination
- [ ] Build semantic search using vector similarity
- [ ] Create endpoints for keyword relationships (mind map data)
- [ ] Implement sentiment-specific endpoints
- [ ] Add document upload endpoint
- [ ] Create keyword suggestion endpoint
- [ ] Write comprehensive API tests

## Phase 4: Frontend UI
- [ ] Implement homepage with keyword tiles
- [ ] Build interactive mind map using React Flow
- [ ] Create keyword detail page
- [ ] Implement sentiment visualization components
- [ ] Add language toggle (EN/TH)
- [ ] Build keyword suggestion form
- [ ] Write Playwright tests

## Phase 5: Deployment & Polish
- [ ] Create production Docker Compose
- [ ] Set up Nginx reverse proxy
- [ ] Implement SSL with Let's Encrypt
- [ ] Create deployment script for VPS
- [ ] Write monitoring scripts
- [ ] Create admin dashboard
- [ ] Write comprehensive documentation

## Known Issues
None yet

## Future Enhancements
- Email alerts for sentiment changes
- Browser extension for quick saves
- Mobile app (iOS/Android)
