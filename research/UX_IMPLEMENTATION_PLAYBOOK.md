# 🛠️ UX IMPLEMENTATION PLAYBOOK 2025
## Practical Guide to Enhancing EU Intelligence Hub

**Date**: 2025-11-19
**Owner**: Product & Engineering Teams
**Timeline**: 12 months (4 quarters)
**Budget**: $55,000 (development + infrastructure + marketing)

---

## 📋 OVERVIEW

This playbook provides **step-by-step implementation guidance** for transforming EU Intelligence Hub from an MVP into a market-leading freemium SaaS product. Based on comprehensive UX research and competitive analysis, we've identified **28 actionable features** prioritized using RICE scoring.

**Goal**: Achieve **10,000+ users** and **$48,000 ARR** by end of Year 1.

**Success Metrics**:
- ✅ **Activation**: 40% of users save ≥1 keyword (within 3 days)
- ✅ **Retention**: 30% return within 7 days
- ✅ **Conversion**: 3% free → paid
- ✅ **NPS**: >70 (excellent)

---

## 🗓️ QUARTERLY IMPLEMENTATION ROADMAP

---

## **Q1 2025: FREEMIUM FOUNDATION** (Weeks 1-12)

**Goal**: Enable user retention and monetization

**Budget**: $12,000 (dev) + $1,000 (infrastructure) + $2,000 (marketing)

---

### **Sprint 1-2: User Authentication System** (Weeks 1-2)

#### **Features to Implement**:
1. Email + password signup/login (bcrypt hashing)
2. OAuth providers (Google, GitHub)
3. JWT token management
4. Password reset flow
5. Email verification

#### **Technical Stack**:
```typescript
// Backend: FastAPI-Users
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import JWTAuthentication

jwt_authentication = JWTAuthentication(secret=SECRET, lifetime_seconds=3600)

fastapi_users = FastAPIUsers(
    user_db,
    [jwt_authentication],
    User,
    UserCreate,
    UserUpdate,
    UserDB,
)

app.include_router(
    fastapi_users.get_auth_router(jwt_authentication),
    prefix="/auth/jwt",
    tags=["auth"],
)
```

```tsx
// Frontend: React Context + TanStack Query
const AuthContext = createContext<AuthState | null>(null);

export const AuthProvider = ({children}) => {
  const [user, setUser] = useState<User | null>(null);

  const login = useMutation({
    mutationFn: async (credentials) => {
      const response = await api.post('/auth/jwt/login', credentials);
      const {access_token} = response.data;
      localStorage.setItem('token', access_token);
      return api.get('/auth/me');
    },
    onSuccess: (userData) => setUser(userData)
  });

  return (
    <AuthContext.Provider value={{user, login, logout}}>
      {children}
    </AuthContext.Provider>
  );
};
```

#### **Database Schema**:
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    tier VARCHAR(50) DEFAULT 'free', -- 'free', 'premium', 'enterprise'
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP
);
```

#### **Acceptance Criteria**:
- [ ] User can sign up with email/password
- [ ] User can sign up with Google OAuth
- [ ] User can log in and stay logged in (JWT valid for 7 days)
- [ ] User can reset password via email link
- [ ] User must verify email before accessing premium features

---

### **Sprint 3-4: Saved Keywords & Dashboard** (Weeks 3-4)

#### **Features to Implement**:
1. "Save keyword" button on keyword detail page
2. Dashboard page (`/dashboard`) showing saved keywords
3. Unsave/delete functionality
4. Freemium gate: 10 keywords free, unlimited paid
5. Dashboard filters (by sentiment, category, date)

#### **Technical Implementation**:
```typescript
// Database Schema
CREATE TABLE user_saved_keywords (
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    keyword_id INTEGER REFERENCES keywords(id) ON DELETE CASCADE,
    saved_at TIMESTAMP DEFAULT NOW(),
    alert_enabled BOOLEAN DEFAULT FALSE,
    alert_threshold FLOAT DEFAULT 0.3,
    PRIMARY KEY (user_id, keyword_id)
);
```

```tsx
// Save Keyword Component
const SaveKeywordButton = ({keywordId}) => {
  const {user} = useAuth();
  const {data: savedKeywords} = useQuery(['saved-keywords', user.id]);

  const saveMutation = useMutation({
    mutationFn: async () => {
      // Check freemium limit
      if (user.tier === 'free' && savedKeywords.length >= 10) {
        throw new Error('Free tier limit reached (10 keywords)');
      }
      return api.post(`/users/${user.id}/saved-keywords`, {keywordId});
    },
    onError: (error) => {
      if (error.message.includes('limit')) {
        showUpgradeModal();
      }
    }
  });

  const isSaved = savedKeywords?.some(k => k.id === keywordId);

  return (
    <Button
      variant={isSaved ? 'default' : 'outline'}
      onClick={() => isSaved ? unsave() : saveMutation.mutate()}
    >
      {isSaved ? <BookmarkCheck /> : <Bookmark />}
      {isSaved ? 'Saved' : 'Save Keyword'}
    </Button>
  );
};
```

```tsx
// Dashboard Page
const DashboardPage = () => {
  const {user} = useAuth();
  const {data: keywords} = useQuery(['saved-keywords', user.id]);

  return (
    <Page title="My Dashboard">
      <div className="mb-6">
        <h1>Saved Keywords</h1>
        <p className="text-gray-600">
          {keywords?.length} / {user.tier === 'free' ? '10' : '∞'} keywords
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {keywords?.map(keyword => (
          <KeywordCard
            key={keyword.id}
            keyword={keyword}
            showUnsaveButton
          />
        ))}
      </div>

      {user.tier === 'free' && keywords?.length >= 8 && (
        <UpgradePrompt
          message="You're using 8/10 free keywords. Upgrade for unlimited tracking."
          cta="Unlock Unlimited - $20/month"
        />
      )}
    </Page>
  );
};
```

#### **Acceptance Criteria**:
- [ ] User can save keywords from detail page
- [ ] Dashboard shows all saved keywords
- [ ] Free users limited to 10 keywords
- [ ] Upgrade prompt shown when approaching limit
- [ ] Saved keywords persist after logout/login

---

### **Sprint 5: Data Export Functionality** (Week 5)

#### **Features to Implement**:
1. PNG export (timeline chart as image) - **FREE**
2. CSV export (article data) - **PREMIUM ONLY**
3. PDF export (full report with charts) - **PREMIUM ONLY**
4. Excel export (bonus) - **PREMIUM ONLY**

#### **Technical Implementation**:
```tsx
// Export Modal Component
const ExportModal = ({keyword, data}) => {
  const {user} = useAuth();
  const [format, setFormat] = useState<'png' | 'csv' | 'pdf' | 'excel'>('png');

  const exportMutation = useMutation({
    mutationFn: async () => {
      if (format !== 'png' && user.tier === 'free') {
        throw new Error('Premium feature');
      }

      switch (format) {
        case 'png':
          return exportAsPNG(data);
        case 'csv':
          return api.post('/export/csv', {keywordId: keyword.id});
        case 'pdf':
          return api.post('/export/pdf', {keywordId: keyword.id});
        case 'excel':
          return api.post('/export/excel', {keywordId: keyword.id});
      }
    },
    onSuccess: (blob) => {
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${keyword.name}_${format}.${format}`;
      a.click();
    }
  });

  return (
    <Modal title="Export Data">
      <RadioGroup value={format} onValueChange={setFormat}>
        <RadioItem value="png">
          PNG Image (Free) ✅
        </RadioItem>
        <RadioItem value="csv" disabled={user.tier === 'free'}>
          CSV Data {user.tier === 'free' && '🔒 Premium'}
        </RadioItem>
        <RadioItem value="pdf" disabled={user.tier === 'free'}>
          PDF Report {user.tier === 'free' && '🔒 Premium'}
        </RadioItem>
        <RadioItem value="excel" disabled={user.tier === 'free'}>
          Excel Spreadsheet {user.tier === 'free' && '🔒 Premium'}
        </RadioItem>
      </RadioGroup>

      {user.tier === 'free' && format !== 'png' && (
        <Alert variant="info">
          <p>Upgrade to Premium to unlock CSV, PDF, and Excel exports.</p>
          <Button href="/pricing">Upgrade Now - $20/month</Button>
        </Alert>
      )}

      <Button
        onClick={() => exportMutation.mutate()}
        disabled={user.tier === 'free' && format !== 'png'}
      >
        Export as {format.toUpperCase()}
      </Button>
    </Modal>
  );
};
```

```python
# Backend: PDF Export Endpoint
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet

@router.post("/export/pdf")
async def export_pdf(keyword_id: int, user: User = Depends(get_current_user)):
    if user.tier == "free":
        raise HTTPException(403, "Premium feature")

    keyword = db.query(Keyword).filter(Keyword.id == keyword_id).first()
    articles = get_articles_for_keyword(keyword_id)

    # Generate PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    story = []

    # Title
    styles = getSampleStyleSheet()
    story.append(Paragraph(f"Sentiment Report: {keyword.keyword_en}", styles['Title']))
    story.append(Spacer(1, 12))

    # Summary
    story.append(Paragraph(f"Average Sentiment: {keyword.average_sentiment:.2f}", styles['Normal']))
    story.append(Paragraph(f"Article Count: {len(articles)}", styles['Normal']))
    story.append(Spacer(1, 12))

    # Timeline Chart (as image)
    chart_image = generate_timeline_chart(keyword_id)
    story.append(Image(chart_image, width=400, height=200))

    # Article List
    for article in articles:
        story.append(Paragraph(f"<b>{article.title}</b>", styles['Heading2']))
        story.append(Paragraph(article.summary, styles['Normal']))
        story.append(Spacer(1, 8))

    doc.build(story)
    buffer.seek(0)

    return StreamingResponse(buffer, media_type="application/pdf",
                            headers={"Content-Disposition": f"attachment; filename={keyword.keyword_en}_report.pdf"})
```

#### **Acceptance Criteria**:
- [ ] All users can export PNG charts
- [ ] Premium users can export CSV data
- [ ] Premium users can export PDF reports
- [ ] Upgrade prompt shown for free users on CSV/PDF/Excel
- [ ] Exported files have correct filename format

---

### **Sprint 6: Onboarding Checklist** (Week 6)

#### **Features to Implement**:
1. Welcome modal on first visit
2. 5-step checklist with progress tracking
3. Completion rewards (badge, confetti animation)
4. Tooltip hints (Shepherd.js)
5. Sample search suggestions

#### **Onboarding Steps**:
1. ✅ Search a keyword
2. ✅ View sentiment timeline
3. ✅ Save your first keyword
4. ✅ Set up email digest
5. ✅ Export your first report

#### **Technical Implementation**:
```tsx
// Onboarding Checklist Component
const OnboardingChecklist = () => {
  const {user} = useAuth();
  const [steps, setSteps] = useLocalStorage<Step[]>('onboarding', INITIAL_STEPS);

  const progress = steps.filter(s => s.completed).length / steps.length;

  useEffect(() => {
    // Sync with backend
    api.put(`/users/${user.id}/onboarding`, {steps});
  }, [steps]);

  return (
    <Card className="border-2 border-blue-500 shadow-lg">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Get Started</h3>
        <Badge variant="secondary">
          {Math.round(progress * 100)}% Complete
        </Badge>
      </div>

      <Progress value={progress * 100} className="mb-4" />

      <div className="space-y-2">
        {steps.map((step, index) => (
          <ChecklistItem
            key={step.id}
            step={step}
            number={index + 1}
            onComplete={() => {
              const updated = [...steps];
              updated[index].completed = true;
              setSteps(updated);

              if (updated.every(s => s.completed)) {
                showConfetti();
                showCompletionModal();
              }
            }}
          />
        ))}
      </div>

      {progress >= 0.8 && (
        <Alert className="mt-4" variant="success">
          <Trophy className="w-5 h-5" />
          <p>Almost there! Complete all steps to unlock a surprise 🎉</p>
        </Alert>
      )}
    </Card>
  );
};

// Checklist Item Component
const ChecklistItem = ({step, number, onComplete}) => (
  <div className="flex items-start gap-3 p-3 rounded-lg hover:bg-gray-50 transition">
    <div className={`flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center ${
      step.completed ? 'bg-green-500' : 'bg-gray-200'
    }`}>
      {step.completed ? (
        <Check className="w-4 h-4 text-white" />
      ) : (
        <span className="text-sm text-gray-600">{number}</span>
      )}
    </div>

    <div className="flex-1">
      <p className={`font-medium ${step.completed ? 'line-through text-gray-500' : ''}`}>
        {step.title}
      </p>
      {!step.completed && step.description && (
        <p className="text-sm text-gray-600 mt-1">{step.description}</p>
      )}
    </div>

    {!step.completed && step.action && (
      <Button size="sm" variant="ghost" onClick={step.action}>
        {step.actionLabel}
      </Button>
    )}
  </div>
);
```

```tsx
// Welcome Modal (First Visit)
const WelcomeModal = () => {
  const [show, setShow] = useLocalStorage('welcome-shown', false);

  if (show) return null;

  return (
    <Modal open onClose={() => setShow(true)}>
      <div className="text-center">
        <h2 className="text-2xl font-bold mb-4">
          Welcome to EU Intelligence Hub! 👋
        </h2>
        <p className="text-gray-600 mb-6">
          Track European news sentiment with AI-powered analysis.
          Let's get you started with a quick tour.
        </p>

        <div className="grid grid-cols-3 gap-4 mb-6">
          <FeatureCard
            icon={<TrendingUp />}
            title="Track Sentiment"
            description="Monitor how European media covers topics over time"
          />
          <FeatureCard
            icon={<Zap />}
            title="AI-Powered"
            description="Dual-layer sentiment analysis (VADER + Gemini)"
          />
          <FeatureCard
            icon={<Globe />}
            title="12 Sources"
            description="BBC, Reuters, DW, France24, and more"
          />
        </div>

        <Button onClick={startTour}>Start Tour</Button>
        <Button variant="ghost" onClick={() => setShow(true)}>
          Skip, I'll explore on my own
        </Button>
      </div>
    </Modal>
  );
};
```

#### **Acceptance Criteria**:
- [ ] Welcome modal shows on first visit
- [ ] Checklist visible on dashboard
- [ ] Steps auto-complete when user performs action
- [ ] Confetti animation plays on 100% completion
- [ ] Tooltip hints guide user through first keyword search

---

### **Sprint 7-8: Email System (Digest + Alerts)** (Weeks 7-8)

#### **Features to Implement**:
1. Daily/weekly email digest (new articles for saved keywords)
2. Sentiment change alerts (email when sentiment drops >0.3)
3. Email preferences page
4. Unsubscribe link
5. Email templates (HTML responsive)

#### **Technical Implementation**:
```python
# Backend: Email Service (SendGrid)
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

class EmailService:
    def __init__(self):
        self.client = SendGridAPIClient(settings.SENDGRID_API_KEY)

    async def send_digest(self, user: User, keywords: List[Keyword]):
        template_data = {
            "user_name": user.full_name,
            "keywords": [
                {
                    "name": k.keyword_en,
                    "sentiment": k.average_sentiment,
                    "article_count": len(k.articles),
                    "url": f"{settings.FRONTEND_URL}/keywords/{k.id}"
                }
                for k in keywords
            ],
            "unsubscribe_url": f"{settings.FRONTEND_URL}/settings?section=emails&token={user.unsubscribe_token}"
        }

        message = Mail(
            from_email=settings.FROM_EMAIL,
            to_emails=user.email,
            subject=f"Your Daily Sentiment Digest - {date.today()}",
            html_content=render_template("digest.html", template_data)
        )

        self.client.send(message)

    async def send_alert(self, user: User, keyword: Keyword, old_sentiment: float, new_sentiment: float):
        change = new_sentiment - old_sentiment
        direction = "dropped" if change < 0 else "improved"

        template_data = {
            "user_name": user.full_name,
            "keyword_name": keyword.keyword_en,
            "old_sentiment": old_sentiment,
            "new_sentiment": new_sentiment,
            "change": abs(change),
            "direction": direction,
            "url": f"{settings.FRONTEND_URL}/keywords/{keyword.id}",
            "unsubscribe_url": f"{settings.FRONTEND_URL}/settings?section=alerts&keyword_id={keyword.id}"
        }

        message = Mail(
            from_email=settings.FROM_EMAIL,
            to_emails=user.email,
            subject=f"🚨 Alert: {keyword.keyword_en} sentiment {direction} by {abs(change):.2f}",
            html_content=render_template("alert.html", template_data)
        )

        self.client.send(message)
```

```python
# Celery Task: Send Daily Digests
@celery_app.task
def send_daily_digests():
    users = db.query(User).filter(
        User.email_preferences.digest_enabled == True,
        User.email_preferences.digest_frequency == "daily"
    ).all()

    for user in users:
        keywords = get_saved_keywords(user.id)
        if keywords:
            email_service.send_digest(user, keywords)
```

```python
# Celery Task: Check Sentiment Alerts
@celery_app.task
def check_sentiment_alerts():
    users = db.query(User).filter(
        User.email_preferences.alerts_enabled == True
    ).all()

    for user in users:
        saved_keywords = get_saved_keywords_with_alerts(user.id)

        for keyword in saved_keywords:
            # Get yesterday's sentiment
            yesterday_sentiment = get_sentiment_for_date(keyword.id, date.today() - timedelta(days=1))
            today_sentiment = get_sentiment_for_date(keyword.id, date.today())

            change = abs(today_sentiment - yesterday_sentiment)

            # Trigger alert if change exceeds threshold
            if change >= keyword.alert_threshold:
                email_service.send_alert(user, keyword, yesterday_sentiment, today_sentiment)
```

```tsx
// Frontend: Email Preferences Page
const EmailPreferencesPage = () => {
  const {user} = useAuth();
  const [prefs, setPrefs] = useState(user.email_preferences);

  const updateMutation = useMutation({
    mutationFn: async (newPrefs) => {
      return api.put(`/users/${user.id}/email-preferences`, newPrefs);
    }
  });

  return (
    <Page title="Email Settings">
      <Card>
        <h2>Email Digest</h2>
        <Switch
          checked={prefs.digest_enabled}
          onCheckedChange={(checked) => {
            setPrefs({...prefs, digest_enabled: checked});
            updateMutation.mutate({...prefs, digest_enabled: checked});
          }}
        />
        <Label>Send me a digest of new articles</Label>

        <Select
          value={prefs.digest_frequency}
          onValueChange={(freq) => {
            setPrefs({...prefs, digest_frequency: freq});
            updateMutation.mutate({...prefs, digest_frequency: freq});
          }}
        >
          <SelectItem value="daily">Daily</SelectItem>
          <SelectItem value="weekly">Weekly</SelectItem>
        </Select>
      </Card>

      <Card>
        <h2>Sentiment Alerts</h2>
        <Switch
          checked={prefs.alerts_enabled}
          onCheckedChange={(checked) => {
            setPrefs({...prefs, alerts_enabled: checked});
            updateMutation.mutate({...prefs, alerts_enabled: checked});
          }}
        />
        <Label>Alert me when sentiment changes significantly</Label>

        <p className="text-sm text-gray-600">
          {user.tier === 'free' ? '3 alerts/month (Free tier)' : 'Unlimited alerts (Premium)'}
        </p>
      </Card>
    </Page>
  );
};
```

#### **Acceptance Criteria**:
- [ ] Users can enable/disable email digest
- [ ] Daily digest sent at 8 AM user's local time
- [ ] Sentiment alerts trigger when change >0.3
- [ ] Unsubscribe link works (one-click unsubscribe)
- [ ] Free users limited to 3 alerts/month, premium unlimited

---

### **Sprint 9: Pricing Page + Stripe Integration** (Week 9)

#### **Features to Implement**:
1. Pricing page (`/pricing`) with 3-tier layout
2. Feature comparison table
3. FAQs
4. Stripe Checkout integration
5. Subscription management (Stripe Customer Portal)
6. Webhook handling (payment success, failed, cancelled)

#### **Pricing Tiers**:

| **Feature** | **Free** | **Premium ($20/mo)** | **Enterprise (Custom)** |
|-------------|----------|----------------------|-------------------------|
| Tracked Keywords | 10 | **Unlimited** | **Unlimited** |
| Historical Data | 30 days | **365 days** | **Unlimited** |
| Sentiment Analysis | ✅ VADER + Gemini | ✅ VADER + Gemini | ✅ VADER + Gemini |
| Export | PNG only | **CSV + PDF + Excel** | **CSV + PDF + Excel** |
| Email Alerts | 3/month | **Unlimited** | **Unlimited** |
| AI Insights | ❌ | ✅ **Included** | ✅ **Included** |
| Team Members | 1 | 5 | **Unlimited** |
| Support | Community | Priority (48h) | **Dedicated + SLA** |
| API Access | ❌ | ❌ | ✅ **Included** |
| White-Label | ❌ | ❌ | ✅ **Included** |

#### **Technical Implementation**:
```tsx
// Pricing Page Component
const PricingPage = () => {
  const {user} = useAuth();

  const plans = [
    {
      id: 'free',
      name: 'Free',
      price: '$0',
      billing: 'forever',
      features: [
        '10 tracked keywords',
        '30-day historical data',
        'VADER + Gemini sentiment',
        'PNG export',
        '3 email alerts/month',
        'Community support'
      ],
      cta: 'Current Plan',
      current: user?.tier === 'free'
    },
    {
      id: 'premium',
      name: 'Premium',
      price: '$20',
      billing: 'per month',
      popular: true,
      features: [
        '**Unlimited** keywords',
        '**365-day** historical data',
        'All sentiment features',
        '**CSV + PDF + Excel** export',
        '**Unlimited** email alerts',
        '**AI-generated insights**',
        '5 team members',
        'Priority support (48h)'
      ],
      cta: 'Upgrade Now',
      current: user?.tier === 'premium'
    },
    {
      id: 'enterprise',
      name: 'Enterprise',
      price: 'Custom',
      billing: 'contact sales',
      features: [
        'Everything in Premium',
        '**White-label** branding',
        '**Custom news sources**',
        '**API access** (REST + webhooks)',
        '**Unlimited** team members',
        '**SSO** integration',
        'Dedicated support + SLA',
        '99.9% uptime guarantee'
      ],
      cta: 'Contact Sales'
    }
  ];

  return (
    <Page title="Pricing">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold mb-4">
          Simple, Transparent Pricing
        </h1>
        <p className="text-xl text-gray-600">
          Start free. Upgrade when you need more.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-7xl mx-auto">
        {plans.map(plan => (
          <PricingCard key={plan.id} plan={plan} />
        ))}
      </div>

      <FAQSection className="mt-16" />
    </Page>
  );
};

// Stripe Checkout Button
const UpgradeButton = ({plan}) => {
  const {user} = useAuth();

  const checkoutMutation = useMutation({
    mutationFn: async () => {
      const response = await api.post('/payments/create-checkout-session', {
        plan_id: plan.id,
        success_url: `${window.location.origin}/dashboard?payment=success`,
        cancel_url: `${window.location.origin}/pricing?payment=cancelled`
      });
      return response.data.url;
    },
    onSuccess: (url) => {
      window.location.href = url; // Redirect to Stripe Checkout
    }
  });

  return (
    <Button onClick={() => checkoutMutation.mutate()}>
      {plan.cta}
    </Button>
  );
};
```

```python
# Backend: Stripe Integration
import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

@router.post("/payments/create-checkout-session")
async def create_checkout_session(
    plan_id: str,
    success_url: str,
    cancel_url: str,
    user: User = Depends(get_current_user)
):
    # Create Stripe customer if doesn't exist
    if not user.stripe_customer_id:
        customer = stripe.Customer.create(
            email=user.email,
            metadata={"user_id": user.id}
        )
        user.stripe_customer_id = customer.id
        db.commit()

    # Get price ID for plan
    price_id = {
        "premium": settings.STRIPE_PREMIUM_PRICE_ID,
    }[plan_id]

    # Create checkout session
    session = stripe.checkout.Session.create(
        customer=user.stripe_customer_id,
        payment_method_types=["card"],
        line_items=[{"price": price_id, "quantity": 1}],
        mode="subscription",
        success_url=success_url,
        cancel_url=cancel_url,
    )

    return {"url": session.url}

# Webhook Handler
@router.post("/payments/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    event = stripe.Webhook.construct_event(
        payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
    )

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        user_id = db.query(User).filter(
            User.stripe_customer_id == session["customer"]
        ).first().id

        # Upgrade user to premium
        user = db.query(User).filter(User.id == user_id).first()
        user.tier = "premium"
        db.commit()

    elif event["type"] == "customer.subscription.deleted":
        # Downgrade user to free
        customer_id = event["data"]["object"]["customer"]
        user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
        user.tier = "free"
        db.commit()

    return {"status": "success"}
```

#### **Acceptance Criteria**:
- [ ] Pricing page displays 3 tiers clearly
- [ ] Users can click "Upgrade Now" and complete payment
- [ ] Stripe Checkout redirects back to dashboard on success
- [ ] User tier upgrades immediately after payment
- [ ] Webhooks handle subscription cancellations
- [ ] Users can access Stripe Customer Portal to manage subscription

---

### **Q1 Success Metrics**:
- ✅ **Activation**: 40% of users save ≥1 keyword (within 3 days)
- ✅ **Retention**: 30% return within 7 days
- ✅ **Conversion Setup**: Pricing page live, Stripe integrated
- ✅ **First Paid Users**: ≥10 paid subscriptions
- ✅ **MRR**: $200+ (10 users × $20/month)

---

## **Q2-Q4 OVERVIEW** (Weeks 13-52)

Due to space limitations, here's a condensed roadmap for Q2-Q4:

### **Q2: Mobile Experience** (Weeks 13-24)
- Progressive Web App (service worker, manifest, install prompt)
- Mobile bottom navigation
- Push notifications
- Swipe gestures
- Responsive visualizations (mind map → list view on mobile)

**Budget**: $15,000

### **Q3: AI Enhancement** (Weeks 25-36)
- Conversational AI chat interface (Gemini-powered)
- AI-generated insights ("Sentiment improved 15% due to...")
- Event detection (timeline annotations)
- Automated PDF reports

**Budget**: $15,000

### **Q4: Collaboration & Enterprise** (Weeks 37-52)
- Team workspaces
- Comments & annotations
- Slack integration
- Microsoft Teams integration
- White-label branding (enterprise)
- API access (REST + webhooks)

**Budget**: $18,000

---

## 📏 TECHNICAL STANDARDS

### **Code Quality**
- [ ] TypeScript strict mode enabled
- [ ] ESLint + Prettier configured
- [ ] >80% test coverage
- [ ] All PRs require code review
- [ ] Automated CI/CD (GitHub Actions)

### **Performance**
- [ ] Lighthouse score >90 (mobile + desktop)
- [ ] First Contentful Paint <1.5s
- [ ] Time to Interactive <3.5s
- [ ] Bundle size <200KB (gzipped)

### **Accessibility**
- [ ] WCAG 2.1 AA compliance
- [ ] Keyboard navigation works
- [ ] Screen reader tested
- [ ] Color contrast 4.5:1 minimum

---

## 🎯 SUCCESS METRICS DASHBOARD

Track these metrics weekly:

| **Metric** | **Target (Month 3)** | **Target (Month 12)** |
|------------|----------------------|-----------------------|
| Total Users | 500 | 10,000 |
| Active Users (WAU) | 200 | 4,000 |
| Activation Rate | 40% | 40% |
| Week-4 Retention | 20% | 30% |
| Free → Paid Conversion | 2% | 3% |
| MRR | $100 | $4,800 |
| NPS | 50 | 70 |

---

**Document Status**: ✅ **COMPLETE**
**Owner**: Product Team
**Review Cycle**: Bi-weekly sprint planning
**Version**: 1.0 Final
**Date**: 2025-11-19
