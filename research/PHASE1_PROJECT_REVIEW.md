# PHASE 1 — PROJECT REVIEW & CURRENT STATE ANALYSIS

**Date**: 2025-11-18
**Analyst**: UX/UI Research Team
**Project**: EU Intelligence Hub - European News Intelligence Platform

---

## 1.1 PROJECT SUMMARY

### Concept
**EU Intelligence Hub** is an AI-powered geopolitical news aggregation and sentiment analysis platform that transforms how European media coverage is tracked, analyzed, and visualized.

### Core Value Proposition
The platform goes beyond traditional news aggregators by:
- Extracting **underlying narrative tone** from news articles
- Tracking **opinion evolution over time**
- Using **dual-layer AI** to detect nuanced sentiment (beyond keyword matching)
- Providing **semantic search** that understands meaning, not just words
- Visualizing **topic relationships** through interactive mind maps

### Purpose
To provide intelligence analysts, PR teams, policy researchers, and news organizations with:
1. **Real-time sentiment tracking** across European media sources
2. **Narrative shift detection** for specific topics
3. **Source-level bias analysis** (which outlets are positive/negative)
4. **Relationship discovery** between geopolitical topics
5. **Fact vs. opinion classification** for objective analysis

### Vision
Transform manual news analysis (hours of reading) into **automated intelligence generation** that processes articles every hour and delivers actionable insights through intuitive visualizations.

### Target Audience
1. **Intelligence Analysts** - Track media narrative shifts
2. **Public Relations Teams** - Monitor brand sentiment
3. **Policy Researchers** - Separate facts from opinions
4. **News Organizations** - Aggregate competitor coverage
5. **Government Agencies** - Monitor public perception

---

## 1.2 CURRENT STATE ASSESSMENT

### Development Status: **PHASE 5 COMPLETED (Production Ready)**

#### Backend Status (✅ Fully Implemented)
- **Framework**: FastAPI (Python 3.11)
- **API Endpoints**: 30+ REST endpoints across 8 routers
- **Database**: PostgreSQL 16 with pgvector extension
- **Tables**: 12 tables with complete sentiment tracking
- **AI/ML Integration**: 4 models (Gemini, VADER, spaCy, Sentence Transformers)
- **Automation**: 9 Celery scheduled tasks
- **Testing**: 49 tests with >80% coverage
- **Code**: ~5,100 lines of Python

**Key Backend Features**:
1. Multi-language keyword tracking (9 languages)
2. Dual-layer sentiment analysis (VADER + Gemini)
3. Vector embedding semantic search (384 dimensions)
4. AI-powered keyword management with auto-approval
5. News source management (12 European outlets)
6. Automated hourly scraping and daily aggregation
7. Admin panels with HTTP Basic Auth

#### Frontend Status (✅ Fully Implemented)
- **Framework**: React 18 + TypeScript
- **Styling**: Tailwind CSS + shadcn/ui components
- **State Management**: Zustand + TanStack Query
- **Visualizations**: React Flow (mind maps) + Recharts (timelines)
- **Pages**: 8 main pages (11 total routes)
- **Internationalization**: i18next (EN/TH initially, expandable)
- **Code**: ~1,800 lines of TypeScript/React

**Frontend Pages**:
1. **HomePage** (`/`) - Keyword discovery with search
2. **SearchPage** (`/search`) - Advanced filtering
3. **KeywordDetailPage** (`/keywords/:id`) - Sentiment timeline & mind map
4. **SuggestPage** (`/suggest`) - User keyword submissions
5. **UploadPage** (`/upload`) - Document processing
6. **AdminSourcesPage** (`/admin/sources`) - Source management
7. **AdminSuggestionsPage** (`/admin/suggestions`) - Keyword approval
8. **AdminSearchPage** (`/admin/search`) - Comprehensive search
9. **ComparisonPage** (`/comparison`) - Multi-keyword comparison
10. **AboutPage** (`/about`) - Project information
11. **MethodologyPage** (`/methodology`) - How it works

#### Infrastructure Status (✅ Production Ready)
- **Orchestration**: Docker Compose (11 services)
- **Services**: PostgreSQL, Redis, Backend, Celery Worker, Celery Beat, Frontend, Nginx
- **Monitoring**: Prometheus, Grafana, exporters
- **Security**: HTTPS/SSL (Let's Encrypt), rate limiting, CORS, input validation
- **Backup**: Automated daily backups (7-day retention)
- **Health Checks**: Comprehensive monitoring scripts
- **Deployment**: One-command deployment with `./deploy.sh`

### Existing Features (Complete Inventory)

#### Core Intelligence Features
1. **Multi-Language Keyword Tracking**
   - 9 European languages (EN, TH, DE, FR, ES, IT, PL, SV, NL)
   - Auto-translation on approval
   - Cross-language search

2. **Dual-Layer Sentiment Analysis**
   - VADER baseline (fast, <10ms)
   - Gemini AI enhancement (nuanced, contextual)
   - Output: -1.0 to +1.0 sentiment score
   - Confidence scoring (0.0 to 1.0)
   - Subjectivity rating
   - Emotion breakdown (positive/negative/neutral)

3. **Semantic Search (Vector Embeddings)**
   - 384-dimensional vectors (Sentence Transformers)
   - PostgreSQL pgvector extension
   - Cosine similarity search (>0.7 threshold)
   - 50ms average query time (100K embeddings)

4. **Interactive Relationship Mapping**
   - React Flow mind maps
   - Automatic relationship discovery
   - Causal and thematic connections
   - Visual node graphs

5. **Real-Time Trend Intelligence**
   - 30/60/90-day timelines
   - Recharts interactive visualizations
   - Drill-down to specific articles
   - Source-level sentiment breakdown

#### AI/ML Features
1. **Gemini AI Integration** (5 use cases)
   - Sentiment analysis
   - News discovery (bypasses scraper blocking)
   - Keyword extraction
   - Keyword evaluation (auto-approval)
   - Context-aware translation

2. **Keyword Extraction Pipeline**
   - Stage 1: spaCy NER
   - Stage 2: Gemini validation
   - Entity types: PERSON, ORG, GPE, LOC, EVENT

3. **Fact vs. Opinion Classification**
   - AI-powered article classification
   - Categories: fact, opinion, mixed
   - Gemini analysis

4. **AI-Powered Keyword Management**
   - Significance assessment (0-100 score)
   - Searchability analysis (easy/moderate/difficult)
   - Duplicate detection & merging (85% similarity threshold)
   - Alternative keyword suggestions
   - Auto-approval (confidence > 0.6)

#### Automation Features (9 Celery Tasks)
1. **News Scraping** - Hourly (at :00)
2. **Sentiment Aggregation** - Daily at 00:30 UTC
3. **Keyword Suggestion Processing** - Daily at 02:00 UTC
4. **Keyword Performance Review** - Weekly (Monday 03:00 UTC)
5. **Database Backup** - Daily at 01:00 UTC
6. **Backup Cleanup** - Daily at 04:00 UTC
7. **Database Health Check** - Hourly
8. **Keyword Queue Population** - Every 30 minutes
9. **Keyword Queue Processing** - Every 15 minutes

#### News Sources (12 European Outlets)
1. BBC News (UK)
2. Reuters (International)
3. Deutsche Welle (Germany)
4. France 24 (France)
5. Euronews (Pan-European)
6. The Guardian (UK)
7. The Telegraph (UK)
8. El País (Spain)
9. Le Monde (France)
10. Corriere della Sera (Italy)
11. Politico Europe (EU Politics)
12. EUobserver (EU Affairs)

#### Admin Features
1. **Source Management**
   - Enable/disable sources
   - Add custom sources
   - View ingestion statistics
   - Monitor scraping performance

2. **Keyword Approval System**
   - AI evaluation dashboard
   - One-click approve/reject
   - Batch processing
   - Evaluation history
   - Statistics dashboard

3. **Comprehensive Search**
   - Search across all content types
   - All 9 languages simultaneously
   - Filter by type
   - Results grouped by category

### Technical Constraints

#### Current Limitations
1. **Language Support**
   - Frontend i18n: Only EN/TH implemented (9 backend languages)
   - Full UI translation needed for DE, FR, ES, IT, PL, SV, NL

2. **Mobile Experience**
   - Responsive design exists
   - No native mobile apps
   - Mind map visualization not optimized for mobile
   - Touch interactions limited

3. **News Scraping**
   - Relies on Gemini API (not direct scraping)
   - Subject to API rate limits (30 calls/min)
   - Some sources may be missed
   - Real-time scraping not available (hourly only)

4. **Scalability**
   - Single PostgreSQL instance
   - No horizontal scaling
   - Vector search limited by single-server performance
   - No CDN for global delivery

5. **User Management**
   - Basic HTTP Auth for admin only
   - No user accounts or profiles
   - No personalization
   - No saved searches or watchlists

6. **Data Export**
   - Limited export options
   - No CSV/Excel download
   - No PDF report generation
   - No API webhook notifications

7. **Real-Time Features**
   - No push notifications
   - No email alerts
   - No WebSocket updates
   - Polling required for updates

### Business Assumptions

#### Current Model
- **Free public access** to all features
- **No monetization** implemented
- **Self-hosted** deployment model
- **Open source** (MIT License)

#### Implicit Assumptions
1. Users have technical knowledge to self-deploy
2. Users manage their own Gemini API key
3. European media coverage is the primary focus
4. English is the primary interface language
5. Web browser is the primary access method
6. Users are comfortable with data visualization
7. No customer support infrastructure needed

---

## 1.3 INITIAL USER & UX OBSERVATIONS

### Preliminary Personas (To be validated)

#### Persona 1: **Intelligence Analyst (Primary)**
**Name**: Sarah Chen
**Age**: 32
**Role**: Geopolitical Intelligence Analyst at think tank
**Goals**:
- Track sentiment shifts across European media
- Identify narrative trends for specific countries
- Produce weekly intelligence briefs
- Distinguish fact-based reporting from opinion

**Pain Points**:
- Manual news reading takes 4-5 hours daily
- Hard to quantify sentiment objectively
- Difficult to track changes over time
- Source bias not immediately visible
- No centralized dashboard

**JTBD (Jobs-to-Be-Done)**:
> "When I need to understand how European media sentiment about Thailand has changed over the past month, I want an automated system that tracks and visualizes sentiment trends, so that I can produce data-driven intelligence reports in minutes instead of hours."

#### Persona 2: **PR Professional (Secondary)**
**Name**: Marcus Weber
**Age**: 38
**Role**: Communications Director at National Tourism Board
**Goals**:
- Monitor brand reputation in European media
- Identify favorable/critical publications
- Respond quickly to negative coverage
- Track campaign effectiveness

**Pain Points**:
- Reactive rather than proactive
- Miss negative articles until too late
- Can't quantify media sentiment ROI
- Don't know which outlets to prioritize

**JTBD**:
> "When I need to monitor our country's media reputation in Europe, I want real-time sentiment alerts from major outlets, so that I can respond to negative coverage immediately and amplify positive stories."

#### Persona 3: **Policy Researcher (Secondary)**
**Name**: Dr. Elena Kowalski
**Age**: 45
**Role**: Senior Researcher at European Policy Institute
**Goals**:
- Analyze media bias on policy issues
- Separate factual reporting from opinion
- Track policy debate evolution
- Publish academic papers

**Pain Points**:
- Manual classification is time-consuming
- Subjective judgment affects results
- Hard to analyze large datasets
- Limited access to historical data

**JTBD**:
> "When I'm researching media bias on EU policy issues, I want automated fact vs. opinion classification across multiple sources, so that I can analyze thousands of articles objectively for my academic research."

#### Persona 4: **Newsroom Editor (Tertiary)**
**Name**: Jean-Pierre Dubois
**Age**: 41
**Role**: Digital Editor at French News Organization
**Goals**:
- Track competitor coverage
- Identify trending topics
- Find story angles
- Aggregate European perspectives

**Pain Points**:
- Too many sources to monitor
- Miss breaking stories
- Don't know what Europe is saying
- Need quick background research

**JTBD**:
> "When I'm planning our daily news coverage, I want to see what major European outlets are reporting on key topics, so that I can identify gaps in our coverage and find unique story angles."

### Journey Map Assumptions (To be validated)

#### User Journey: Intelligence Analyst Using Platform

**Phase 1: Discovery** (First-time use)
1. **Awareness**: Hears about platform from colleague
2. **Landing**: Visits homepage
3. **Confusion Point**: "What keywords are already tracked?"
4. **Exploration**: Searches for "Thailand" keyword
5. **Aha Moment**: Sees 90-day sentiment timeline
6. **Engagement**: Clicks into detailed view

**Phase 2: Regular Use** (Weekly routine)
1. **Entry**: Direct to homepage
2. **Search**: Types specific keyword
3. **Analysis**: Reviews sentiment timeline
4. **Drill-Down**: Checks specific articles
5. **Insight**: Identifies sentiment shift
6. **Export**: (Feature gap - cannot export data)
7. **Report**: Manually copies findings to report

**Phase 3: Advanced Use** (Power user)
1. **Comparison**: Compares multiple keywords
2. **Mind Map**: Explores keyword relationships
3. **Source Filter**: Identifies biased outlets
4. **Suggestion**: Submits new keyword for tracking
5. **Return**: Checks back weekly

**Pain Points Identified**:
- No onboarding or tutorial
- Unclear what keywords exist before searching
- Cannot save searches or create watchlists
- Export functionality missing
- No email alerts for changes
- Mobile experience suboptimal

### Early Journey Map Assumptions

#### Critical Touchpoints
1. **First Impression** (Homepage)
   - Need: Clear value proposition
   - Current: Keyword search box only
   - Gap: No examples, no visualization preview

2. **Keyword Discovery**
   - Need: Browse available keywords
   - Current: Must know what to search
   - Gap: No keyword directory or categories

3. **Sentiment Understanding**
   - Need: Interpret sentiment scores
   - Current: Shows -1.0 to +1.0
   - Gap: No legend, no interpretation guide

4. **Actionable Insights**
   - Need: Export for reports
   - Current: View-only interface
   - Gap: No export, no sharing, no alerts

5. **Return Visits**
   - Need: Track specific keywords over time
   - Current: Must re-search each time
   - Gap: No saved searches, no dashboards

#### Hypothetical User Flows (To be tested)

**Flow 1: First-Time User**
```
Homepage → Search "Thailand" → Keyword Detail Page →
View Timeline → Click Article → Read Full Text →
Return to Timeline → Compare Sources →
[Dead End - No clear next action]
```

**Flow 2: Intelligence Analyst (Weekly Brief)**
```
Homepage → Search Keyword → Export Data (Missing!) →
Manually Screenshot → Copy to Word →
Repeat for 5-10 keywords → Produce Report
```

**Flow 3: PR Professional (Crisis Monitoring)**
```
Search Brand Keyword → Check Sentiment →
See Negative Spike → Read Articles →
[Need Alert System - Not Available]
```

### UX Observations (Desktop Web)

#### Strengths
1. ✅ Clean, minimal interface
2. ✅ Fast search response
3. ✅ Interactive visualizations (timeline, mind map)
4. ✅ Clear sentiment indicators
5. ✅ Responsive design basics

#### Weaknesses
1. ❌ No onboarding or user guide
2. ❌ Keyword discovery requires prior knowledge
3. ❌ No user accounts or personalization
4. ❌ Limited mobile optimization
5. ❌ No data export functionality
6. ❌ No alerts or notifications
7. ❌ Sentiment score interpretation unclear
8. ❌ No saved searches or watchlists
9. ❌ Admin features hidden (no UI indication)
10. ❌ No feedback mechanism for users

### UX Observations (Mobile)

#### Critical Issues (Hypothetical - To be tested)
1. **Mind Map**: Likely too complex for mobile
2. **Timeline**: May require horizontal scrolling
3. **Tables**: Article lists may not fit
4. **Navigation**: Admin panel navigation unclear
5. **Touch Targets**: Button sizes for mobile?
6. **Loading States**: Slow on mobile networks?

### Technical UX Considerations

#### Performance
- Backend response: <500ms p95 (Good ✅)
- Semantic search: 50ms average (Excellent ✅)
- Timeline query: 5ms (Excellent ✅)
- Frontend bundle size: Unknown (To be measured)
- Time to interactive: Unknown (To be measured)

#### Accessibility
- No ARIA labels mentioned (Potential gap ❌)
- Keyboard navigation: Unknown (To be tested)
- Screen reader support: Unknown (To be tested)
- Color contrast: Tailwind defaults (Likely OK ✅)

#### Browser Compatibility
- Modern browsers only (React 18)
- No IE11 support
- Mobile browsers: Unknown (To be tested)

---

## NEXT STEPS

### Phase 2: Competitor Analysis
1. Identify direct competitors (news aggregators + sentiment analysis)
2. Identify indirect competitors (media monitoring tools)
3. Identify substitutes (manual research, Google Alerts)
4. Analyze 5-10 competitors across dimensions
5. Produce competitive positioning matrix

### Phase 3: Deep Research
1. Validate personas through user research
2. Conduct usability testing on current platform
3. Perform card sorting for information architecture
4. Test journey maps with real users
5. Analyze market trends (AI news tools)
6. Define UX/UI roadmap priorities

### Phase 4: Reporting
1. Create stakeholder-specific reports
2. Produce executive summary
3. Define feature prioritization (RICE, Impact-Effort)
4. Create UX/UI enhancement roadmap

---

**Document Status**: Phase 1 Complete ✅
**Next Phase**: Competitor Analysis (5 iterative loops)
**Date**: 2025-11-18
