# Financial Advisor Backend - Setup & Usage Guide

## ✅ What's Completed (Member 1 - Backend Lead)

### Core Backend Infrastructure (100% Complete)

1. **Configuration Management** ✅
   - `app/config.py` - Pydantic settings with environment variables
   - `.env.example` - All required environment variables documented
   - Support for SQLite (dev) and PostgreSQL (prod)

2. **Database Layer** ✅
   - `app/db/db_models.py` - SQLAlchemy ORM models with relationships
   - `app/db/database.py` - Connection management, session factory
   - `app/db/crud.py` - Complete CRUD operations for all entities
   - `app/db/seed_data.py` - Sample data for testing (5 customers, 14 goals)

3. **API Models (Pydantic)** ✅
   - `app/models/customer_profile.py` - Profile request/response models
   - `app/models/goal.py` - Goal models with enums (types, priorities)
   - `app/models/plan.py` - Plan models with asset allocation
   - `app/models/risk_assessment.py` - Risk questionnaire models
   - `app/models/chat.py` - Chat message and session models

4. **API Routes** ✅
   - `app/api/profile_routes.py` - Customer profile CRUD + financial summary
   - `app/api/risk_routes.py` - Risk assessment + questionnaire + profile
   - `app/api/goal_routes.py` - Goal CRUD + calculation details
   - `app/api/plan_routes.py` - Plan generation (calls core logic) + CRUD
   - `app/api/chat_routes.py` - Chat interface (placeholder for GenAI)

5. **Main Application** ✅
   - `app/main.py` - FastAPI app with CORS, error handling, lifespan
   - Health endpoint `/health`
   - API info endpoint `/api`
   - Proper exception handlers

6. **Utilities** ✅
   - `app/utils/logger.py` - Logging configuration
   - `app/utils/exceptions.py` - Custom exceptions and handlers

7. **Docker Setup** ✅
   - `Dockerfile` - Backend container
   - `docker-compose.yml` - Backend + PostgreSQL orchestration

8. **Data Loader** ✅
   - `app/data/data_loader.py` - Historical asset return data

## 🚧 What Needs Member 4 (GenAI)

The backend is **ready to run** but has placeholders for GenAI modules:

- `app/genai/chatbot.py` - Chatbot with LLM integration (placeholder in chat_routes.py)
- `app/genai/explainer.py` - Plan explanation generator
- `app/genai/comparator.py` - Plan comparison
- `app/genai/retriever.py` - Knowledge retrieval (optional)
- `app/genai/prompts/` - Prompt templates (started, not complete)

**Current behavior**: Chat endpoint returns a simple placeholder response. Everything else works fully.

## 📋 API Endpoints Available

All endpoints are prefixed with `/api/v1`:

### Customer Profile
- `POST /api/v1/profile` - Create customer profile (auto-calculates net worth, surplus, DTI)
- `GET /api/v1/profile/{id}` - Get customer profile
- `GET /api/v1/profile` - List all profiles
- `PUT /api/v1/profile/{id}` - Update profile
- `DELETE /api/v1/profile/{id}` - Delete profile (cascades to related data)
- `GET /api/v1/profile/{id}/summary` - Get financial summary

### Risk Assessment
- `GET /api/v1/risk/questionnaire` - Get risk questionnaire
- `POST /api/v1/risk` - Submit risk assessment (auto-calculates score & category)
- `GET /api/v1/risk/{id}` - Get assessment by ID
- `GET /api/v1/risk/customer/{id}` - Get all assessments for customer
- `GET /api/v1/risk/customer/{id}/latest` - Get latest assessment
- `GET /api/v1/risk/customer/{id}/profile` - Get risk profile with recommendations

### Financial Goals
- `POST /api/v1/goal` - Create goal (auto-calculates required savings)
- `GET /api/v1/goal/{id}` - Get goal by ID
- `GET /api/v1/goal/customer/{id}` - Get all goals for customer
- `PUT /api/v1/goal/{id}` - Update goal
- `DELETE /api/v1/goal/{id}` - Delete goal
- `GET /api/v1/goal/{id}/calculation` - Get detailed calculation breakdown

### Financial Plans
- `POST /api/v1/plans/generate` - Generate 3 plans (Conservative/Balanced/Growth)
- `POST /api/v1/plans` - Save a generated plan
- `GET /api/v1/plans/{id}` - Get plan by ID
- `GET /api/v1/plans/customer/{id}` - Get all plans for customer
- `GET /api/v1/plans/customer/{id}/active` - Get active plan
- `PUT /api/v1/plans/{id}` - Update plan
- `POST /api/v1/plans/{id}/select` - Mark plan as active
- `DELETE /api/v1/plans/{id}` - Delete plan

### Chat
- `POST /api/v1/chat` - Chat with financial advisor (placeholder for GenAI)
- `POST /api/v1/chat/history` - Get chat history
- `GET /api/v1/chat/sessions/{customer_id}` - Get all session IDs
- `DELETE /api/v1/chat/sessions/{customer_id}/{session_id}` - Delete session

### System
- `GET /` - Root endpoint
- `GET /health` - Health check (checks DB connection)
- `GET /api` - API information

## 🚀 Quick Start

### Option 1: Local Development (SQLite)

1. **Create environment file:**
```bash
cd backend
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Initialize database with sample data:**
```bash
python -m app.db.seed_data
```

4. **Run the server:**
```bash
uvicorn app.main:app --reload
```

5. **Access the API:**
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health
- API Info: http://localhost:8000/api

### Option 2: Docker (PostgreSQL)

1. **Set environment variable:**
```bash
export GROQ_API_KEY="your-groq-api-key-here"
```

2. **Start services:**
```bash
docker-compose up --build
```

3. **Seed database (in another terminal):**
```bash
docker-compose exec backend python -m app.db.seed_data
```

4. **Access the API:**
- API: http://localhost:8000
- Database: localhost:5432

## 🧪 Testing the API

### 1. Create a Customer Profile
```bash
curl -X POST http://localhost:8000/api/v1/profile \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "age": 30,
    "occupation": "Engineer",
    "monthly_income": 100000,
    "monthly_expenses": 60000,
    "total_assets": 1000000,
    "total_liabilities": 200000
  }'
```

### 2. Submit Risk Assessment
```bash
curl -X POST http://localhost:8000/api/v1/risk \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 1,
    "answers": {
      "age": "25-34",
      "investment_experience": "some",
      "time_horizon": "long",
      "market_reaction": "hold",
      "risk_comfort": "moderate",
      "goal_priority": "balanced",
      "income_stability": "stable",
      "emergency_fund": "yes",
      "debt_level": "low",
      "investment_knowledge": "moderate"
    }
  }'
```

### 3. Create a Goal
```bash
curl -X POST http://localhost:8000/api/v1/goal \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 1,
    "goal_type": "retirement",
    "goal_name": "Retirement Fund",
    "target_amount": 10000000,
    "current_savings": 500000,
    "time_horizon_years": 20,
    "priority": "high"
  }'
```

### 4. Generate Financial Plans
```bash
curl -X POST http://localhost:8000/api/v1/plans/generate \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 1,
    "goal_ids": [1]
  }'
```

### 5. Chat (placeholder response)
```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 1,
    "message": "How should I start investing?",
    "include_context": true
  }'
```

## 📊 Sample Data

After running seed_data.py, you'll have:
- 5 customer profiles (Rajesh, Priya, Amit, Sneha, Vikram)
- 14 financial goals across various types
- 5 risk assessments

Customer IDs: 1-5
Goal IDs: 1-14 (distributed across customers)

## 🔧 Configuration

Key environment variables (see `.env.example`):

```env
# Database
DATABASE_URL="sqlite:///./financial_advisor.db"  # or PostgreSQL URL

# Groq API (required)
GROQ_API_KEY="your-groq-api-key"

# Application
DEBUG=False
LOG_LEVEL="INFO"

# Financial Defaults
DEFAULT_INFLATION_RATE=0.03
DEFAULT_SAVINGS_RATE=0.05
DEFAULT_EQUITY_RETURN=0.12
DEFAULT_DEBT_RETURN=0.08
```

## 🎯 Integration Points for GenAI (Member 4)

### 1. Chatbot Integration
File: `app/api/chat_routes.py` (line ~47)

Replace this:
```python
# TODO: Call chatbot module here (Member 4's work)
assistant_response = "placeholder..."
```

With:
```python
from app.genai.chatbot import get_chatbot_response
assistant_response = get_chatbot_response(
    customer=customer,
    user_message=request.message,
    conversation_history=context_messages
)
```

### 2. Plan Explanation
Add to `app/api/plan_routes.py`:
```python
from app.genai.explainer import explain_plan

@router.get("/plans/{plan_id}/explanation")
def get_plan_explanation(plan_id: int, db: Session = Depends(get_db)):
    plan = crud.get_plan(db, plan_id)
    explanation = explain_plan(plan)
    return explanation
```

### 3. Plan Comparison
Add to `app/api/plan_routes.py`:
```python
from app.genai.comparator import compare_plans

@router.post("/plans/compare")
def compare_two_plans(plan_a_id: int, plan_b_id: int, db: Session = Depends(get_db)):
    comparison = compare_plans(plan_a_id, plan_b_id, db)
    return comparison
```

## 📁 Project Structure

```
backend/
├── app/
│   ├── api/              # API routes (✅ Complete)
│   │   ├── profile_routes.py
│   │   ├── risk_routes.py
│   │   ├── goal_routes.py
│   │   ├── plan_routes.py
│   │   └── chat_routes.py
│   ├── core/             # Financial logic (✅ Already existed)
│   │   ├── goal_calculator.py
│   │   ├── net_worth_calculator.py
│   │   ├── plan_generator.py
│   │   └── risk_scoring.py
│   ├── db/               # Database layer (✅ Complete)
│   │   ├── database.py
│   │   ├── db_models.py
│   │   ├── crud.py
│   │   └── seed_data.py
│   ├── genai/            # AI modules (🚧 Needs Member 4)
│   │   ├── chatbot.py
│   │   ├── explainer.py
│   │   ├── comparator.py
│   │   ├── retriever.py
│   │   └── prompts/
│   ├── models/           # Pydantic models (✅ Complete)
│   ├── utils/            # Utilities (✅ Complete)
│   ├── data/             # Data loaders (✅ Complete)
│   ├── config.py         # Configuration (✅ Complete)
│   └── main.py           # FastAPI app (✅ Complete)
├── tests/                # Tests (⏳ Partial)
├── requirements.txt      # Dependencies (✅ Complete)
├── Dockerfile            # Container (✅ Complete)
└── .env.example          # Environment template (✅ Complete)
```

## 🐛 Troubleshooting

### Database connection error
- Check DATABASE_URL in .env
- For Docker: ensure db service is healthy
- For SQLite: check file permissions

### Import errors
- Ensure you're running from project root
- Check PYTHONPATH: `export PYTHONPATH=$PWD`

### CORS errors
- Update CORS_ORIGINS in .env or config.py
- Default allows localhost:3000 and localhost:5173

### Groq API errors
- Verify GROQ_API_KEY is set
- Check API key is valid
- GenAI features need this key

## 📝 Next Steps

1. **Member 4 (GenAI)**: Implement chatbot, explainer, comparator modules
2. **Testing**: Run existing tests, add integration tests
3. **Frontend**: Connect React frontend to these endpoints
4. **Documentation**: API documentation is auto-generated at /docs

## 🎉 What Works Now

✅ Full CRUD for customers, goals, plans, risk assessments
✅ Financial calculations (net worth, surplus, DTI, goal achievability)
✅ Risk scoring and categorization
✅ Plan generation (3 plans with proper allocations)
✅ Database persistence with relationships
✅ Proper error handling and logging
✅ Health checks and monitoring
✅ Docker deployment
✅ Sample data for testing
✅ API documentation (OpenAPI/Swagger)

## 📞 Support

For issues or questions about the backend:
- Check logs: `docker-compose logs backend`
- API docs: http://localhost:8000/docs
- Health status: http://localhost:8000/health
