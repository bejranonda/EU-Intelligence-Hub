# European News Intelligence Hub - TODO

## Phase 1: Foundation ✅ COMPLETED
**Goal**: Working development environment with database and basic API

### Critical Tasks
- ✅ Create project directory structure
- ✅ Set up Docker Compose with PostgreSQL, Redis, FastAPI, React dev server
- ✅ Create database schema with sentiment tracking tables
- ✅ Build FastAPI skeleton with health check endpoint
- ✅ Create React app with TypeScript and Tailwind
- ✅ Write setup.sh to start all services
- ✅ Create initial tests for database connection and API health
- ✅ Update state files with progress

## Phase 2: AI Integration & Scraping ✅ COMPLETED
- ✅ Implement Gemini API client with error handling
- ✅ Create news scraper for European sources
- ✅ Build keyword extraction pipeline using spaCy
- ✅ Implement fact/opinion classifier
- ✅ Implement multi-layered sentiment analysis (VADER + Gemini)
- ✅ Set up Celery worker for hourly scraping
- ✅ Generate embeddings using Sentence Transformers
- ✅ Write integration tests

## Phase 3: API Endpoints & Search ✅ COMPLETED
- ✅ Implement keyword search endpoint with pagination
- ✅ Build semantic search using vector similarity
- ✅ Create endpoints for keyword relationships (mind map data)
- ✅ Implement sentiment-specific endpoints
- ✅ Add document upload endpoint
- ✅ Create keyword suggestion endpoint
- ✅ Write comprehensive API tests

## Phase 4: Frontend UI (Current)
**Goal**: Interactive React frontend with visualizations

### Critical Tasks
- [ ] Set up React component library with shadcn/ui
- [ ] Implement homepage with keyword search and tiles
- [ ] Build interactive mind map visualization (React Flow)
- [ ] Create keyword detail page with article list
- [ ] Implement sentiment overview dashboard
- [ ] Build sentiment timeline graph (Recharts)
- [ ] Create comparative sentiment charts
- [ ] Add language toggle functionality (EN/TH)
- [ ] Build document upload interface
- [ ] Create keyword suggestion form
- [ ] Implement responsive design with Tailwind CSS
- [ ] Write Playwright E2E tests

### Acceptance Criteria
- [ ] Homepage displays keyword tiles with article counts
- [ ] Mind map shows interactive keyword relationships
- [ ] Sentiment timeline displays 30-day trend graph
- [ ] Comparative sentiment chart compares multiple keywords
- [ ] Document upload form processes PDF/DOCX/TXT files
- [ ] Language toggle switches all text between EN/TH
- [ ] All pages are responsive and mobile-friendly
- [ ] E2E tests cover critical user flows

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
