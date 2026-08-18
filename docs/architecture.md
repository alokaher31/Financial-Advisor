# Architecture Overview

## System Architecture

The Financial Advisor application follows a **3-tier architecture** with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                         FRONTEND                             │
│  React + Vite (Port 5173)                                   │
│  - UI Components                                             │
│  - State Management (Context API)                            │
│  - API Client Layer                                          │
└───────────────┬─────────────────────────────────────────────┘
                │ HTTP/REST
                │ JWT Auth
┌───────────────▼─────────────────────────────────────────────┐
│                         BACKEND                              │
│  FastAPI + Python (Port 8000)                               │
│  - Authentication (JWT)                                      │
│  - API Routes (/api/v1/*)                                    │
│  - Business Logic                                            │
│  - GenAI Integration (Groq)                                  │
└───────────────┬─────────────────────────────────────────────┘
                │ SQLAlchemy ORM
┌───────────────▼─────────────────────────────────────────────┐
│                        DATABASE                              │
│  SQLite / PostgreSQL                                         │
│  - Users                                                     │
│  - Customer Profiles                                         │
│  - Goals, Plans, Risk Assessments                            │
│  - Chat History                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Request Flow

### 1. **Authentication Flow**

```
User → Frontend (AuthLanding)
  → POST /api/v1/auth/register or /api/v1/auth/login
    → Backend validates credentials
    → Hash password (bcrypt)
    → Create/verify user in database
    → Generate JWT token
    → Return token to frontend
  → Frontend stores token in localStorage
  → All subsequent requests include: Authorization: Bearer <token>
```

### 2. **Authenticated Request Flow**

```
Frontend API Call
  ↓
  Add JWT token to Authorization header
  ↓
Backend receives request
  ↓
OAuth2PasswordBearer extracts token
  ↓
security.get_current_user() decodes token
  ↓
Verify user exists in database
  ↓
Check user owns requested resource (customer_id)
  ↓
Execute business logic
  ↓
Return response
```

### 3. **Financial Planning Flow**

```
1. User creates profile
   POST /api/v1/profile
   → Linked to user_id
   → Calculates net worth, surplus, DTI ratio

2. User completes risk assessment
   POST /api/v1/risk/assess
   → Calculates risk score
   → Classifies risk category (Conservative/Moderate/Aggressive)

3. User sets financial goal
   POST /api/v1/goal
   → Calculates required monthly savings
   → Determines if achievable

4. System generates 3 investment plans
   POST /api/v1/plans/generate
   → Conservative, Moderate, Aggressive allocations
   → Projects future corpus
   → Calculates gap vs target
   → Persists all 3 plans to database

5. User compares plans
   POST /api/v1/plans/compare
   → LLM generates comparison summary

6. User selects a plan
   POST /api/v1/plans/{plan_id}/select
   → Marks plan as active

7. User explores what-if scenarios
   POST /api/v1/whatif
   → Recalculates with adjusted parameters
   → LLM narrates impact
```

### 4. **Chatbot Flow**

```
User asks question
  ↓
POST /api/v1/chat
  ↓
Retrieve customer context:
  - Profile (income, expenses, assets)
  - Risk assessment
  - Goals
  - Active plan
  - Historical market data
  ↓
Detect what-if intent?
  ├─ YES → Run what-if analyzer
  │         → Generate narration
  └─ NO  → Build augmented prompt
            → Call Groq LLM
            → Generate response
  ↓
Save chat messages to database
  ↓
Return response to frontend
```

---

## Technology Stack

### **Frontend**
- **Framework**: React 18
- **Build Tool**: Vite
- **Styling**: CSS Modules
- **State Management**: Context API (AppContext, AuthContext)
- **Routing**: React Router (implicit via AppContext)
- **HTTP Client**: Native Fetch API
- **Environment**: Node.js

### **Backend**
- **Framework**: FastAPI 0.104+
- **Language**: Python 3.10+
- **Authentication**: JWT (python-jose), OAuth2, bcrypt
- **Database ORM**: SQLAlchemy 2.0
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **LLM Integration**: Groq API (openai/gpt-oss-120b)
- **Data Processing**: Pandas
- **Testing**: pytest
- **Server**: Uvicorn

### **AI/ML**
- **LLM Provider**: Groq
- **Model**: openai/gpt-oss-120b
- **Use Cases**:
  - Plan explanations
  - Plan comparisons
  - What-if scenario narration
  - Financial advice chatbot

---

## Module Structure

### **Backend Modules**

```
backend/app/
├── api/                    # API route handlers
│   ├── auth_routes.py     # Authentication endpoints
│   ├── profile_routes.py  # Profile CRUD
│   ├── risk_routes.py     # Risk assessment
│   ├── goal_routes.py     # Goal management
│   ├── plan_routes.py     # Plan generation & comparison
│   └── chat_routes.py     # Chatbot
│
├── core/                   # Business logic
│   ├── net_worth_calculator.py
│   ├── goal_calculator.py
│   ├── risk_scoring.py
│   └── plan_generator.py
│
├── genai/                  # AI/LLM integration
│   ├── llm_client.py      # Groq API wrapper
│   ├── chatbot.py         # Conversational AI
│   ├── retriever.py       # Context retrieval
│   ├── explainer.py       # Plan explanation
│   ├── comparator.py      # Plan comparison
│   ├── whatif_analyzer.py # Scenario analysis
│   └── prompts/           # LLM prompt templates
│
├── db/                     # Database layer
│   ├── database.py        # DB connection & session
│   ├── db_models.py       # SQLAlchemy ORM models
│   ├── crud.py            # CRUD operations
│   └── seed_data.py       # Sample data
│
├── models/                 # Pydantic models
│   ├── auth.py            # Authentication schemas
│   ├── customer_profile.py
│   ├── goal.py
│   ├── plan.py
│   ├── risk_assessment.py
│   └── chat.py
│
├── utils/                  # Utilities
│   ├── security.py        # JWT, password hashing
│   ├── logger.py          # Logging
│   └── exceptions.py      # Custom exceptions
│
├── data/                   # Data loading
│   └── data_loader.py     # Load historical market data
│
├── config.py              # Configuration
└── main.py                # FastAPI app entry point
```

### **Frontend Modules**

```
frontend/src/
├── pages/                  # Page components
│   ├── AuthLanding.jsx    # Login/signup
│   ├── ProfileForm.jsx    # Profile creation
│   ├── RiskQuestionnaire.jsx
│   ├── GoalInput.jsx
│   ├── PlanComparison.jsx
│   ├── PlanDetail.jsx
│   └── Chatbot.jsx
│
├── components/             # Reusable components
│   ├── ProgressStepper.jsx
│   ├── MockDataBanner.jsx
│   └── ...
│
├── context/                # State management
│   ├── AppContext.jsx     # App state & flow
│   └── AuthContext.jsx    # Authentication state
│
├── api/                    # Backend integration
│   └── apiClient.js       # API calls & normalization
│
├── mock/                   # Mock data (dev)
│   └── mockData.js
│
└── styles/                 # Global styles
```

---

## Security Architecture

### **Authentication**
- **JWT tokens** with 24-hour expiration
- **Bcrypt** password hashing (cost factor 12)
- **OAuth2PasswordBearer** for token validation
- Tokens stored in `localStorage` (frontend)
- All protected routes require valid token

### **Authorization**
- Users can only access their own data
- `user_id` foreign key on `customer_profiles`
- Ownership verification on every request
- 403 Forbidden for unauthorized access

### **API Security**
- CORS configured for allowed origins
- Input validation with Pydantic models
- SQL injection protected by SQLAlchemy ORM
- Rate limiting (not implemented, TODO)

---

## Data Flow

### **Profile Creation**
```
Frontend                Backend                 Database
   │                       │                        │
   │ POST /profile         │                        │
   ├──────────────────────►│                        │
   │  {name, age, income}  │ Validate input         │
   │                       │ Get current user       │
   │                       │ Calculate metrics      │
   │                       ├───────────────────────►│
   │                       │  INSERT customer       │
   │                       │  SET user_id           │
   │                       │◄───────────────────────┤
   │                       │  Return profile        │
   │◄──────────────────────┤                        │
   │  {id, netWorth...}    │                        │
```

### **Plan Generation**
```
Frontend                Backend                 Database
   │                       │                        │
   │ POST /plans/generate  │                        │
   ├──────────────────────►│                        │
   │                       │ Load profile           │
   │                       │ Load goals             │
   │                       │ Load risk              │
   │                       ├───────────────────────►│
   │                       │◄───────────────────────┤
   │                       │ Generate 3 plans       │
   │                       │ (plan_generator.py)    │
   │                       │ Persist each plan      │
   │                       ├───────────────────────►│
   │                       │  INSERT plans (x3)     │
   │                       │◄───────────────────────┤
   │◄──────────────────────┤  Return plans with IDs │
   │  {plans: [{id...}]}   │                        │
```

### **Chatbot Interaction**
```
Frontend                Backend                 GenAI                Database
   │                       │                        │                    │
   │ POST /chat            │                        │                    │
   ├──────────────────────►│                        │                    │
   │  {message}            │ Get context            │                    │
   │                       ├───────────────────────────────────────────►│
   │                       │                        │  Load profile      │
   │                       │                        │  Load goals        │
   │                       │                        │  Load plans        │
   │                       │◄───────────────────────────────────────────┤
   │                       │ Detect what-if?        │                    │
   │                       │ Build prompt           │                    │
   │                       ├───────────────────────►│                    │
   │                       │  POST to Groq API      │                    │
   │                       │◄───────────────────────┤                    │
   │                       │  LLM response          │                    │
   │                       │ Save messages          │                    │
   │                       ├───────────────────────────────────────────►│
   │                       │                        │  INSERT chat msgs  │
   │◄──────────────────────┤                        │                    │
   │  {reply, session_id}  │                        │                    │
```

---

## Deployment Architecture

### **Development**
- Frontend: `npm run dev` (port 5173)
- Backend: `uvicorn app.main:app --reload` (port 8000)
- Database: SQLite file (`financial_advisor.db`)

### **Production (Recommended)**
```
┌─────────────────────────────────────────────────────┐
│  CDN / Static Hosting (Vercel/Netlify)             │
│  Frontend Build (React SPA)                         │
└────────────────┬────────────────────────────────────┘
                 │ HTTPS
┌────────────────▼────────────────────────────────────┐
│  Application Server (Railway/Render/AWS)            │
│  - FastAPI Backend                                  │
│  - Uvicorn workers                                  │
│  - Environment variables                            │
└────────────────┬────────────────────────────────────┘
                 │ SQL
┌────────────────▼────────────────────────────────────┐
│  Database Server (PostgreSQL)                       │
│  - Managed service (AWS RDS/Heroku Postgres)        │
└─────────────────────────────────────────────────────┘
```

---

## Scalability Considerations

### **Current Limitations**
- Single-threaded SQLite (dev only)
- No caching layer
- No rate limiting
- No load balancing

### **For Production**
1. **Database**: Migrate to PostgreSQL with connection pooling
2. **Caching**: Add Redis for session storage and frequent queries
3. **API Gateway**: Add rate limiting and request throttling
4. **Load Balancer**: Horizontal scaling with multiple backend instances
5. **CDN**: Serve static assets via CDN
6. **Monitoring**: Add APM (DataDog, New Relic)
7. **Logging**: Centralized logging (ELK stack)

---

## Future Enhancements

1. **Real-time Data**: WebSocket support for live updates
2. **Document Upload**: PDF parsing for financial statements
3. **Multi-currency**: Support for multiple currencies
4. **Mobile App**: React Native or Flutter
5. **Advanced AI**: Fine-tuned models for Indian financial context
6. **Social Features**: Share plans, community forum
7. **Notifications**: Email/SMS alerts for milestones
8. **Integration**: Link bank accounts via APIs
