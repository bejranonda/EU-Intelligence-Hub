# Implementation Roadmap & Strategic Recommendations
## Actionable 12-Month Plan to Transform EU Intelligence Hub into Market-Ready SaaS

**Document Date:** November 18, 2025
**Scope:** Detailed feature development, resource allocation, timelines, success metrics

---

## 🎯 Strategic Summary

**Current State:** Production-ready technical platform with strong AI capabilities but lacking:
- User authentication & multi-user support
- Monetization (freemium/paid tiers)
- UX polish (onboarding, mobile, notifications)
- Enterprise features (API, exports, SSO)

**Target State (12 Months):** $3.82M ARR SaaS platform with:
- 150,000 free users
- 6,700 paying users ($19-$500/mo tiers)
- API marketplace generating $600K/year
- White-label partnerships adding $500K/year

---

## 📅 Phase 1: Foundation (Months 1-3)
### **Goal:** Launch freemium SaaS with basic monetization

### **Sprint 1-2: Security & Authentication (Weeks 1-4)**

#### **Priority 1.1: Remove Hardcoded Credentials** 🔴 CRITICAL
**Current Risk:** Admin credentials visible in frontend code → Security breach vulnerability

**Tasks:**
- [ ] Remove hardcoded credentials from `frontend/src/api/client.ts` lines 39-40
- [ ] Implement environment variables for admin credentials
- [ ] Audit codebase for other hardcoded secrets
- [ ] Update deployment documentation

**Acceptance Criteria:**
✅ No credentials in Git history (use BFG Repo-Cleaner if needed)
✅ Admin login uses JWT tokens (not HTTP Basic Auth)
✅ Security audit passes (no exposed secrets)

**Resources:** 1 backend developer × 3 days
**Risk:** Low (straightforward refactoring)

---

#### **Priority 1.2: JWT-Based Authentication** 🔴 CRITICAL
**User Story:** As a user, I want to create an account and log in securely.

**Tasks:**
- [ ] **Backend:**
  - [ ] Install `PyJWT` library
  - [ ] Create `/api/auth/register` endpoint (email, password, name)
  - [ ] Create `/api/auth/login` endpoint (return JWT token)
  - [ ] Create `/api/auth/refresh` endpoint (refresh tokens)
  - [ ] Add `verify_token()` dependency for protected routes
  - [ ] Create `users` table (id, email, password_hash, role, created_at)
  - [ ] Hash passwords with `bcrypt`
  - [ ] Send email verification (SendGrid or Mailgun)

- [ ] **Frontend:**
  - [ ] Create `/register` page (form: email, password, confirm password)
  - [ ] Create `/login` page (form: email, password)
  - [ ] Store JWT token in `localStorage` (or `httpOnly` cookie)
  - [ ] Add token to all API requests (`Authorization: Bearer <token>`)
  - [ ] Handle token expiration (auto-refresh or redirect to login)
  - [ ] Add "Forgot Password" flow (reset email)

**Acceptance Criteria:**
✅ User can register with email/password
✅ Email verification sent (click link to activate)
✅ User can log in (JWT token returned)
✅ Protected routes return 401 if no token
✅ Token auto-refreshes before expiration

**Resources:** 1 backend dev + 1 frontend dev × 2 weeks
**Dependencies:** Database migration for `users` table
**Risk:** Medium (email delivery can be flaky; test with multiple providers)

---

#### **Priority 1.3: Role-Based Access Control (RBAC)** 🟡 HIGH
**User Story:** As an admin, I want to manage users and approve keywords (not available to free users).

**Roles:**
| Role | Permissions | Use Case |
|------|-------------|----------|
| **Free** | 10 keywords, 7-day history, 100 searches/mo | Freemium users |
| **Starter** | 50 keywords, 30-day history, semantic search, unlimited searches | $19/mo individual users |
| **Pro** | Unlimited keywords, 1-year history, API access, alerts, exports | $49/mo power users |
| **Enterprise** | SSO, SLA, dedicated support, white-label | $500+/mo corporate clients |
| **Admin** | All features + user management, source config, keyword approval | Platform operators |

**Tasks:**
- [ ] Add `role` column to `users` table (ENUM: free, starter, pro, enterprise, admin)
- [ ] Add `plan_limits` column (JSONB: `{"keywords": 10, "history_days": 7, "searches_per_month": 100}`)
- [ ] Create middleware: `check_permission(required_role)` decorator
- [ ] Protect admin routes with `@check_permission("admin")`
- [ ] Frontend: Show/hide features based on user role
- [ ] Frontend: "Upgrade" CTA when hitting limits

**Acceptance Criteria:**
✅ Free users see "10 keyword limit" message
✅ Admin users see admin panel
✅ API returns 403 Forbidden for unauthorized actions
✅ Frontend hides Pro features for Free users (with upgrade CTA)

**Resources:** 1 backend dev × 1 week
**Risk:** Low (standard RBAC implementation)

---

### **Sprint 3-4: Freemium Monetization (Weeks 5-8)**

#### **Priority 2.1: Stripe Payment Integration** 🔴 CRITICAL
**User Story:** As a user, I want to upgrade to Pro and pay $49/month.

**Tasks:**
- [ ] **Stripe Setup:**
  - [ ] Create Stripe account
  - [ ] Create products/prices (Starter $19/mo, Pro $49/mo, Enterprise custom)
  - [ ] Get API keys (test & live)

- [ ] **Backend:**
  - [ ] Install `stripe` Python library
  - [ ] Create `/api/billing/create-checkout-session` endpoint
  - [ ] Create `/api/billing/webhook` endpoint (handle `checkout.session.completed`)
  - [ ] Update `users` table: Add `stripe_customer_id`, `subscription_id`, `plan`, `subscription_status`
  - [ ] Sync subscription status daily (Stripe cron job)
  - [ ] Handle subscription cancellations (downgrade to Free)

- [ ] **Frontend:**
  - [ ] Create `/pricing` page (pricing table with CTAs)
  - [ ] Create `/billing` page (current plan, payment method, invoices)
  - [ ] Add "Upgrade" button throughout app (contextual nudges)
  - [ ] Stripe Checkout redirect flow
  - [ ] Success page after payment (`/billing/success`)

**Acceptance Criteria:**
✅ User clicks "Upgrade to Pro" → Stripe Checkout → Payment successful → Role updated to "pro"
✅ Subscription renews monthly (auto-charge)
✅ User can cancel subscription (downgrades to Free next billing cycle)
✅ Webhooks handle edge cases (failed payment, refund)

**Resources:** 1 backend dev + 1 frontend dev × 2 weeks
**Dependencies:** Stripe account approval (1-2 days)
**Risk:** Medium (webhook reliability; test thoroughly with Stripe CLI)

---

#### **Priority 2.2: Usage Tracking & Limits** 🟡 HIGH
**User Story:** As a free user, I see "7 of 10 keywords used" and "82 searches left this month."

**Tasks:**
- [ ] Create `usage_tracking` table (user_id, resource_type, count, month)
- [ ] Middleware: Increment search count on `/api/search/*` endpoints
- [ ] Middleware: Check limits before allowing action (return 402 Payment Required if exceeded)
- [ ] Frontend: Display usage stats (progress bars, badges)
- [ ] Reset monthly counters (Celery cron job on 1st of month)

**Acceptance Criteria:**
✅ Free user adding 11th keyword → Blocked with "Upgrade to add more keywords"
✅ User sees "47 searches left this month" in dashboard
✅ Usage resets on 1st of each month

**Resources:** 1 backend dev × 1 week
**Risk:** Low

---

### **Sprint 5-6: UX Enhancements (Weeks 9-12)**

#### **Priority 3.1: Interactive Onboarding** 🟡 HIGH
**User Story:** As a new user, I complete onboarding in 3 minutes and see value immediately.

**Tasks:**
- [ ] Install **Intro.js** library
- [ ] Create 5-step onboarding flow (see UX Strategy doc)
- [ ] Pre-populate dashboard with 10 popular keywords on first login
- [ ] Add "Skip" and "Don't show again" options
- [ ] Track completion rate in Mixpanel

**Acceptance Criteria:**
✅ New user sees onboarding tour on first login
✅ User completes all 5 steps → "You're all set!" message
✅ Activation rate increases from 25% → 55% (target)

**Resources:** 1 frontend dev × 1 week
**Risk:** Low

---

#### **Priority 3.2: Dashboard Redesign** 🟡 HIGH
**Goal:** Reduce time-to-value from 10 minutes → 3 minutes.

**Tasks:**
- [ ] Design mockups in Figma (hero search, trending topics, watchlist cards)
- [ ] Implement card-based layout (not tables)
- [ ] Add "Trending Topics" widget (top 10 keywords by sentiment change)
- [ ] Visual hierarchy improvements (typography scale, white space)

**Acceptance Criteria:**
✅ User understands dashboard purpose in 5 seconds (5-second test)
✅ Session duration increases from 3 min → 8 min

**Resources:** 1 designer × 3 days, 1 frontend dev × 1 week
**Risk:** Low

---

#### **Priority 3.3: Mobile Touch Optimization** 🟡 HIGH
**Goal:** Increase mobile conversion by 25%.

**Tasks:**
- [ ] Increase tap targets to 44px minimum (iOS HIG)
- [ ] Implement bottom navigation (Home, Search, Saved, Profile)
- [ ] Add swipe gestures (timeline navigation)
- [ ] Bottom sheets for filters (not dropdowns)
- [ ] Test on real devices (iPhone 13, Pixel 7, Samsung S22)

**Acceptance Criteria:**
✅ All buttons ≥ 44px
✅ Bottom navigation works on iOS + Android
✅ User can swipe timeline left/right
✅ Mobile bounce rate decreases from 60% → 40%

**Resources:** 1 frontend dev × 1 week
**Risk:** Low

---

#### **Priority 3.4: Real-Time Alerts & Notifications** 🔴 CRITICAL
**User Story:** As a corporate comms professional, I get emailed within 1 hour when sentiment drops below -0.5.

**Tasks:**
- [ ] **Backend:**
  - [ ] Create `alerts` table (user_id, keyword_id, threshold, email, enabled)
  - [ ] Create `/api/alerts` CRUD endpoints
  - [ ] Celery task: Check sentiment thresholds every 15 minutes
  - [ ] Send email via SendGrid/Mailgun when threshold breached
  - [ ] Email template (HTML): "Alert: 'Thailand' sentiment dropped to -0.6"

- [ ] **Frontend:**
  - [ ] Create `/alerts` page (list, create, edit, delete alerts)
  - [ ] Add "Set Alert" button on keyword detail page
  - [ ] Alert form: Threshold slider, email toggle, SMS toggle (future)

**Acceptance Criteria:**
✅ User creates alert: "Email me if 'Thailand' sentiment < -0.5"
✅ Sentiment drops to -0.6 → Email sent within 15 minutes
✅ User receives email with link to keyword detail page

**Resources:** 1 backend dev + 1 frontend dev × 2 weeks
**Dependencies:** SendGrid account ($15/mo for 50K emails)
**Risk:** Medium (email deliverability; test spam folder placement)

---

## 📅 Phase 2: Growth (Months 4-6)
### **Goal:** Reach 5,000 users and $100K MRR

### **Sprint 7-8: Advanced Features (Weeks 13-16)**

#### **Priority 4.1: Watchlists** 🟡 HIGH
**User Story:** As a user, I want to save custom keyword collections (e.g., "Asia Politics", "Competitors").

**Tasks:**
- [ ] Create `watchlists` table (id, user_id, name, keywords[])
- [ ] Create `/api/watchlists` CRUD endpoints
- [ ] Frontend: "My Watchlists" page (list, create, edit)
- [ ] Frontend: Star icon on keywords → "Add to Watchlist" dropdown

**Acceptance Criteria:**
✅ User creates "Asia Politics" watchlist with 5 keywords
✅ Dashboard shows watchlist cards (not individual keywords)
✅ Click watchlist → View aggregated sentiment across all keywords

**Resources:** 1 backend dev + 1 frontend dev × 1 week
**Risk:** Low

---

#### **Priority 4.2: CSV/PDF Export** 🟡 HIGH
**User Story:** As a corporate comms pro, I export sentiment charts for executive briefings.

**Tasks:**
- [ ] **CSV Export:**
  - [ ] `/api/keywords/{id}/export/csv` endpoint
  - [ ] Include: date, source, headline, sentiment, confidence, URL
  - [ ] Streaming response for large datasets (>10K rows)

- [ ] **PDF Export:**
  - [ ] Install `reportlab` library
  - [ ] Generate PDF with sentiment chart (matplotlib → image → PDF)
  - [ ] Include: keyword, date range, summary stats, chart, top articles

- [ ] **Frontend:**
  - [ ] "Export" dropdown on keyword detail page (CSV, PDF, JSON)
  - [ ] Progress bar for large exports

**Acceptance Criteria:**
✅ User exports 90-day sentiment data → CSV downloads in <5 seconds
✅ PDF includes chart + top 10 articles
✅ Pro users get unlimited exports (Free users blocked with upgrade CTA)

**Resources:** 1 backend dev × 1 week
**Risk:** Low

---

#### **Priority 4.3: Browser Extension** 🟢 MEDIUM
**User Story:** As a journalist, I save articles to EU Intelligence Hub while browsing news sites.

**Tasks:**
- [ ] Create Chrome Extension (manifest v3)
- [ ] Popup UI: "Save to EU Intelligence Hub"
- [ ] Extract article metadata (title, URL, published date)
- [ ] POST to `/api/documents/upload` endpoint
- [ ] Firefox version (same codebase)

**Acceptance Criteria:**
✅ User reading BBC article → Clicks extension icon → Article saved
✅ Article appears in "Saved Articles" dashboard
✅ Extension works on Chrome + Firefox

**Resources:** 1 frontend dev × 2 weeks
**Risk:** Medium (extension store approval can take 1-3 weeks)

---

### **Sprint 9-10: Content Expansion (Weeks 17-20)**

#### **Priority 5.1: Add 30+ Global News Sources** 🟡 HIGH
**Goal:** Expand from 12 European sources → 42 global sources (2x addressable market).

**New Sources to Add:**
- **Asia (10):** Al Jazeera, South China Morning Post, The Straits Times, Japan Times, Korea Herald, India Today, Bangkok Post, Nikkei Asia, Channel NewsAsia, Philippine Daily Inquirer
- **Americas (10):** New York Times, Washington Post, CNN, NBC, CBC (Canada), O Globo (Brazil), Clarín (Argentina), La Nación (Chile), El Universal (Mexico), Toronto Star
- **Africa (5):** Daily Maverick (South Africa), The East African, Egypt Independent, Premium Times (Nigeria), Afrique Media
- **Middle East (5):** Haaretz (Israel), Gulf News (UAE), Daily Sabah (Turkey), Arab News (Saudi Arabia), Tehran Times (Iran)

**Tasks:**
- [ ] Add sources to `news_sources` table
- [ ] Test Gemini scraping for each source (verify quality)
- [ ] Update language detection (add AR, HE, JA, KO, ZH)
- [ ] Backfill last 30 days of articles (Celery task)

**Acceptance Criteria:**
✅ 42 total sources enabled
✅ Hourly scraping works for all sources
✅ Language detection accuracy >90%

**Resources:** 1 backend dev × 2 weeks
**Risk:** Medium (some sources may block Gemini; need fallback scraping)

---

#### **Priority 5.2: Social Media Integration (Twitter/X)** 🟢 MEDIUM
**User Story:** As a user, I want to see Twitter sentiment alongside news articles.

**Tasks:**
- [ ] **Twitter API Setup:**
  - [ ] Apply for Twitter API (Elevated access $100/mo)
  - [ ] Implement OAuth 2.0 authentication
  - [ ] Create `/api/social/twitter/search` endpoint

- [ ] **Data Model:**
  - [ ] Create `social_posts` table (platform, post_id, author, content, sentiment, timestamp)
  - [ ] Link to keywords via `keyword_social_posts` junction table

- [ ] **Frontend:**
  - [ ] Add "Social Media" tab on keyword detail page
  - [ ] Display tweets with sentiment badges
  - [ ] Link to original tweet

**Acceptance Criteria:**
✅ User searches "Thailand" → Sees top 20 tweets with sentiment
✅ Sentiment analysis runs on tweet text (VADER + Gemini)
✅ Daily refresh (fetch new tweets)

**Resources:** 1 backend dev × 2 weeks
**Dependencies:** Twitter API approval (2-4 weeks)
**Risk:** High (Twitter API costs $100/mo; may not be profitable for free users)
**Decision:** Limit to Pro tier only

---

### **Sprint 11-12: API Marketplace (Weeks 21-24)**

#### **Priority 6.1: Public API Launch** 🔴 CRITICAL
**Goal:** Generate $10-20K MRR from API revenue by Month 12.

**API Endpoints to Expose:**
- `GET /api/v1/keywords` - List all keywords
- `GET /api/v1/keywords/{id}` - Get keyword details + sentiment
- `GET /api/v1/keywords/{id}/timeline` - Sentiment time series
- `GET /api/v1/keywords/{id}/articles` - Related articles
- `GET /api/v1/search/semantic` - Semantic search
- `GET /api/v1/search/fulltext` - Full-text search

**Tasks:**
- [ ] **API Gateway:**
  - [ ] Install **FastAPI API Key** middleware
  - [ ] Create `api_keys` table (user_id, key_hash, rate_limit, enabled)
  - [ ] Create `/api/account/keys` endpoint (generate, revoke keys)
  - [ ] Rate limiting: 60 req/min (free), 600 req/min (pro), unlimited (enterprise)

- [ ] **Documentation:**
  - [ ] OpenAPI schema auto-generated by FastAPI
  - [ ] Create developer portal (https://developers.euintel.com)
  - [ ] Code examples (Python, JavaScript, cURL)
  - [ ] Postman collection

- [ ] **Pricing:**
  - [ ] Free tier: 1,000 API calls/month
  - [ ] Pay-as-you-go: $0.01/query (Stripe metered billing)
  - [ ] Pro subscription: 50,000 calls/month included
  - [ ] Enterprise: Unlimited (custom contract)

**Acceptance Criteria:**
✅ Developer generates API key from dashboard
✅ API call: `GET /api/v1/keywords/123` with `X-API-Key` header → Returns JSON
✅ Rate limit exceeded → Returns 429 Too Many Requests
✅ Developer portal live with docs + examples

**Resources:** 1 backend dev + 1 technical writer × 3 weeks
**Dependencies:** Subdomain setup (developers.euintel.com)
**Risk:** Medium (API versioning strategy needed for breaking changes)

---

## 📅 Phase 3: Enterprise (Months 7-12)
### **Goal:** Reach $500K ARR with enterprise contracts

### **Sprint 13-14: White-Label & Partnerships (Weeks 25-28)**

#### **Priority 7.1: White-Label Dashboard** 🟢 MEDIUM
**User Story:** As a media monitoring reseller, I want to rebrand EU Intelligence Hub with my logo.

**Tasks:**
- [ ] Create `white_label_configs` table (partner_id, logo_url, primary_color, domain)
- [ ] Middleware: Detect custom domain → Load partner config
- [ ] Frontend: Dynamic branding (logo, colors, footer text)
- [ ] Subdomain setup (partner1.euintel.com, partner2.euintel.com)
- [ ] Revenue sharing dashboard (partner sees their metrics)

**Acceptance Criteria:**
✅ Partner uploads logo → Dashboard shows their branding
✅ Partner gets 70% revenue share (EU Intelligence Hub keeps 30%)
✅ Partner dashboard shows: users, revenue, API calls

**Resources:** 1 backend dev + 1 frontend dev × 2 weeks
**Risk:** Low

---

#### **Priority 7.2: SSO (Single Sign-On)** 🟡 HIGH
**User Story:** As an enterprise client, I want employees to log in with company Google/Microsoft accounts.

**Tasks:**
- [ ] Install `python-social-auth` library
- [ ] Implement OAuth 2.0 for Google Workspace
- [ ] Implement OAuth 2.0 for Microsoft Azure AD
- [ ] Implement SAML 2.0 for enterprise IdPs (Okta, OneLogin)
- [ ] Map SSO roles to EU Intelligence Hub roles

**Acceptance Criteria:**
✅ User clicks "Sign in with Google" → Redirects to Google → Returns logged in
✅ Enterprise user signs in via Okta SAML → Auto-provisioned with "enterprise" role

**Resources:** 1 backend dev × 2 weeks
**Risk:** Medium (SAML configuration can be complex)

---

### **Sprint 15-16: Advanced AI Features (Weeks 29-32)**

#### **Priority 8.1: RAG (Retrieval-Augmented Generation)** 🟢 MEDIUM
**User Story:** As an analyst, I ask "What's driving Thailand's political risk?" → Get AI-generated summary with citations.

**Tasks:**
- [ ] Implement RAG pipeline:
  1. User query → Vector search (retrieve top 10 relevant articles)
  2. Send articles + query to Gemini → Generate summary with citations
  3. Return summary with article links
- [ ] Create `/api/chat/ask` endpoint
- [ ] Frontend: Chat interface on keyword detail page
- [ ] Stream response (SSE for progressive display)

**Acceptance Criteria:**
✅ User asks question → Receives AI summary in <5 seconds
✅ Summary includes inline citations (e.g., [1], [2])
✅ Click citation → Opens source article

**Resources:** 1 backend dev × 2 weeks
**Risk:** Medium (Gemini API costs increase; need to optimize prompts)

---

#### **Priority 8.2: Multimodal AI (Video/Audio Transcription)** 🟢 MEDIUM
**User Story:** As a journalist, I want sentiment analysis on YouTube videos and podcasts.

**Tasks:**
- [ ] Integrate **Whisper API** (OpenAI) for audio transcription
- [ ] Integrate **Twelve Labs API** for video analysis
- [ ] Create `/api/media/transcribe` endpoint (accepts YouTube URL)
- [ ] Run sentiment analysis on transcript
- [ ] Store in `media_transcripts` table

**Acceptance Criteria:**
✅ User submits YouTube URL → Video transcribed → Sentiment analyzed
✅ Transcript searchable via semantic search

**Resources:** 1 backend dev × 2 weeks
**Dependencies:** Whisper API ($0.006/minute), Twelve Labs (custom pricing)
**Risk:** High (costs can spiral with video volume)

---

#### **Priority 8.3: Knowledge Graph Visualization** 🟢 MEDIUM
**User Story:** As an analyst, I visualize entity relationships (people, organizations, events).

**Tasks:**
- [ ] Implement **spaCy NER** for entity extraction (PERSON, ORG, GPE, EVENT)
- [ ] Create `entities` table (name, type, keyword_id)
- [ ] Create `entity_relations` table (entity1_id, entity2_id, relation_type)
- [ ] Frontend: D3.js or Cytoscape.js graph visualization
- [ ] Click entity → See related articles

**Acceptance Criteria:**
✅ Keyword "Thailand Elections" → Graph shows: "Prayuth Chan-ocha" (PERSON) ← "Prime Minister" → "Thailand" (GPE)
✅ Click entity → Filter articles mentioning that entity

**Resources:** 1 backend dev + 1 frontend dev × 3 weeks
**Risk:** Medium (entity linking accuracy depends on spaCy model quality)

---

### **Sprint 17-18: Explainable AI (Weeks 33-36)**

#### **Priority 8.4: Sentiment Explanation (XAI)** 🟢 MEDIUM
**User Story:** As a user, I see why an article is classified as negative (which words drove the sentiment).

**Tasks:**
- [ ] Implement **SHAP** (SHapley Additive exPlanations) for VADER sentiment
- [ ] Highlight words in article text (green = positive, red = negative)
- [ ] Add "Why this sentiment?" tooltip on hover
- [ ] Store SHAP values in database for performance

**Acceptance Criteria:**
✅ Article sentiment: -0.6 → Hover "Why?" → Tooltip shows: "Negative words: crisis (−0.5), collapse (−0.4)"
✅ Words highlighted in article text

**Resources:** 1 ML engineer + 1 frontend dev × 2 weeks
**Risk:** Medium (SHAP computation can be slow; need caching)

---

#### **Priority 8.5: Fact-Checking Assistant** 🟢 MEDIUM
**User Story:** As a journalist, I check if a claim is supported by multiple sources.

**Tasks:**
- [ ] Create `/api/factcheck` endpoint (accepts claim text)
- [ ] Gemini prompt: "Find articles supporting or refuting this claim: [claim]"
- [ ] Return: Similarity score, supporting articles, refuting articles
- [ ] Frontend: Fact-check widget on article detail page

**Acceptance Criteria:**
✅ User inputs claim: "Thailand GDP grew 3.2% in Q4" → System finds 5 supporting articles, 0 refuting
✅ Fact-check confidence score: 85% (high agreement)

**Resources:** 1 backend dev × 1 week
**Risk:** Low (leverages existing semantic search)

---

## 📊 Resource Allocation Summary

### **Team Structure (Recommended)**

| Role | Headcount | Months 1-3 | Months 4-6 | Months 7-12 | Total Cost (12 Months) |
|------|-----------|------------|------------|-------------|-------------------------|
| **Backend Developer** | 2 | Full-time | Full-time | Full-time | $240K (2 × $120K/year) |
| **Frontend Developer** | 2 | Full-time | Full-time | Full-time | $220K (2 × $110K/year) |
| **Product Designer** | 1 | Part-time (50%) | Full-time | Part-time (50%) | $75K (avg $75K/year) |
| **ML Engineer** | 1 | - | Part-time (50%) | Full-time | $75K (avg $100K/year) |
| **Technical Writer** | 1 | - | - | Part-time (25%) | $15K (contract) |
| **DevOps Engineer** | 1 | Part-time (25%) | Part-time (25%) | Full-time | $60K (avg $80K/year) |
| **Product Manager** | 1 | Part-time (50%) | Full-time | Full-time | $105K (avg $120K/year) |
| **Total** | 9 FTE (avg) | - | - | - | **$790K/year** |

---

### **Technology Costs (12 Months)**

| Service | Purpose | Cost/Month | Annual Cost |
|---------|---------|------------|-------------|
| **Google Gemini API** | Sentiment analysis | $500 | $6,000 |
| **SendGrid** | Email alerts + transactional | $50 | $600 |
| **Stripe** | Payment processing (2.9% + $0.30) | Variable | $18K (assumes $600K GMV) |
| **AWS / DigitalOcean** | Hosting (upgraded from dev) | $500 | $6,000 |
| **Mixpanel** | Product analytics | $100 | $1,200 |
| **Hotjar** | Heatmaps + session recordings | $80 | $960 |
| **Twitter API** | Social media integration | $100 | $1,200 |
| **Whisper API** | Audio transcription | $200 | $2,400 |
| **Domain + SSL** | euintel.com + wildcard cert | $20 | $240 |
| **Error Monitoring (Sentry)** | Error tracking | $30 | $360 |
| **Total** | - | ~$1,580/mo | **$36,960/year** |

---

### **Marketing Budget (12 Months)**

| Channel | Strategy | Budget |
|---------|----------|--------|
| **Content Marketing** | SEO blog posts (50 articles) | $15,000 |
| **Paid Ads (Google)** | "Meltwater alternative" keywords | $30,000 |
| **Paid Ads (LinkedIn)** | Target corporate comms pros | $20,000 |
| **ProductHunt Launch** | Launch promotion | $2,000 |
| **Referral Program** | 10% off for referrals (credits) | $10,000 |
| **Conferences** | 2× industry conferences (booth + travel) | $15,000 |
| **Influencer Partnerships** | 5× analyst/journalist sponsorships | $8,000 |
| **Total** | - | **$100,000** |

---

### **Total Investment (Year 1)**

| Category | Cost |
|----------|------|
| **Personnel** | $790,000 |
| **Technology** | $37,000 |
| **Marketing** | $100,000 |
| **Miscellaneous** | $23,000 (legal, accounting, tools) |
| **Total** | **$950,000** |

**Break-Even Analysis:**
- Year 1 Revenue Target: $290,000
- Year 1 Costs: $950,000
- **Net Loss Year 1:** -$660,000 (expected for SaaS; break-even in Year 2)

**Funding Needed:**
- **Seed Round:** $1.5M (covers Year 1 + 6 months runway for Year 2)
- **Valuation:** $6M pre-money (targeting 20% dilution)

---

## 🎯 Success Metrics (KPI Dashboard)

### **North Star Metric: Monthly Recurring Revenue (MRR)**

| Month | Target MRR | Target Users (Paid) | Cumulative Investment | Notes |
|-------|------------|---------------------|----------------------|-------|
| **Month 3** | $2,000 | 50 | $237,500 | Freemium launch |
| **Month 6** | $10,000 | 250 | $475,000 | API launch |
| **Month 9** | $30,000 | 800 | $712,500 | Enterprise features |
| **Month 12** | $60,000 | 1,500 | $950,000 | White-label partnerships |

---

### **Leading Indicators (Track Weekly)**

| Metric | Week 4 | Month 3 | Month 6 | Month 12 |
|--------|--------|---------|---------|----------|
| **Website Visitors** | 500 | 2,000 | 10,000 | 50,000 |
| **Trial Signups** | 50 | 200 | 1,000 | 5,000 |
| **Activation Rate** | 30% | 55% | 60% | 70% |
| **Free → Paid Conversion** | 0% | 5% | 8% | 12% |
| **Churn Rate** | N/A | 10% | 5% | 3% |
| **NPS (Net Promoter Score)** | N/A | 20 | 40 | 60 |

---

## 🚨 Risk Mitigation Plan

| Risk | Probability | Impact | Mitigation Strategy |
|------|-------------|--------|---------------------|
| **Gemini API cost spiral** | High | Critical | Implement aggressive caching; add local VADER-only tier; negotiate volume discounts with Google |
| **Low user acquisition** | Medium | Critical | Double marketing budget if CAC > $100; pivot to developer-led growth (API-first) |
| **Competitor copycat** | High | High | Speed to market (launch in 3 months); build community moat (user-generated keywords) |
| **Churn before PMF** | High | Critical | Weekly user interviews (n=10); rapid iteration (2-week sprints); feature flags for A/B testing |
| **GDPR violations** | Low | Critical | Privacy-by-design; EU data residency; hire compliance consultant ($15K) |
| **AWS outage / downtime** | Medium | High | Multi-region deployment (EU + US); 99.9% SLA guarantee for enterprise |
| **Key team member leaves** | Medium | High | Document all code; pair programming; knowledge sharing sessions |

---

## 📚 Next Steps (30-Day Sprint)

### **Week 1: Planning & Setup**
- [ ] Assemble team (hire 2 backend + 2 frontend devs if needed)
- [ ] Finalize product roadmap (review this document with stakeholders)
- [ ] Set up project management (Linear, Jira, or Notion)
- [ ] Create Figma mockups for authentication + pricing pages
- [ ] Security audit (remove hardcoded credentials)

### **Week 2: Development Kickoff**
- [ ] Sprint 1 begins: Authentication implementation
- [ ] Database migrations for `users`, `alerts`, `usage_tracking` tables
- [ ] Stripe account setup + test mode integration
- [ ] SendGrid account setup + email templates

### **Week 3: Testing & Iteration**
- [ ] QA authentication flow (unit tests + integration tests)
- [ ] User testing with 10 beta users (record onboarding sessions)
- [ ] Fix critical bugs identified in testing
- [ ] Prepare pricing page copy + FAQ

### **Week 4: Pre-Launch**
- [ ] Deploy to staging environment
- [ ] Load testing (1,000 concurrent users)
- [ ] Security penetration testing (hire external firm)
- [ ] Finalize launch marketing plan (ProductHunt, blog posts, social media)
- [ ] Set up analytics (Mixpanel, Hotjar, GA4)

---

**Document Status:** ✅ Complete
**Last Updated:** November 18, 2025
**Next Actions:**
1. Review with stakeholders (business owner, investors, team leads)
2. Prioritize features based on feedback
3. Begin Sprint 1 implementation (Week 1)
4. Schedule weekly progress reviews

**Success Indicator:** If this roadmap is followed, EU Intelligence Hub will transform from a technical demo into a $3.82M ARR SaaS platform within 12 months.
