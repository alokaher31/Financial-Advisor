# Financial Advisor - AI-Powered Personal Finance Planning

A comprehensive financial planning platform with AI-powered insights, built with FastAPI (backend) and React (frontend).

## 🚀 Quick Start

### Backend Setup

1. **Navigate to backend and install dependencies:**
```bash
cd backend
pip install -r requirements.txt
```

2. **Create `.env` file:**
```bash
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

3. **Initialize database with sample data:**
```bash
python -m app.db.seed_data
```

4. **Run the development server:**
```bash
uvicorn app.main:app --reload
```

5. **Access the API:**
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **API Endpoints**: http://localhost:8000/api

### Using Docker (Recommended)

1. **Set your Groq API key:**
```bash
export GROQ_API_KEY="your-groq-api-key-here"
```

2. **Start all services:**
```bash
docker-compose up --build
```

3. **Seed the database (in another terminal):**
```bash
docker-compose exec backend python -m app.db.seed_data
```

## 📚 Documentation

- **[Backend Setup Guide](./BACKEND_SETUP.md)** - Complete backend documentation
- **[API Documentation](http://localhost:8000/docs)** - Interactive API docs (when server is running)

## 🏗️ Architecture

```
finance-planner/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API route handlers
│   │   ├── core/           # Financial calculation logic
│   │   ├── db/             # Database models & CRUD
│   │   ├── genai/          # AI/LLM integration
│   │   ├── models/         # Pydantic schemas
│   │   └── main.py         # FastAPI application
│   ├── tests/              # Backend tests
│   └── requirements.txt
├── frontend/               # React frontend (TBD)
├── docs/                   # Documentation
└── docker-compose.yml      # Docker orchestration
```

## ✨ Features

### ✅ Implemented (Backend)
- **Customer Profile Management** - Create and manage customer financial profiles
- **Risk Assessment** - 10-question risk profiling with automatic scoring
- **Goal Tracking** - Multiple financial goals with achievability analysis
- **Plan Generation** - Generate 3 investment plans (Conservative/Balanced/Growth)
- **Financial Calculations** - Net worth, surplus, debt-to-income, required savings
- **Chat Interface** - AI financial advisor chatbot (placeholder)
- **Docker Deployment** - One-command deployment with PostgreSQL

### 🚧 In Progress
- GenAI modules (chatbot, plan explainer, comparator)
- Frontend React application
- Integration tests

## 🔑 Key API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/profile` | POST | Create customer profile |
| `/api/v1/risk` | POST | Submit risk assessment |
| `/api/v1/goal` | POST | Create financial goal |
| `/api/v1/plans/generate` | POST | Generate 3 investment plans |
| `/api/v1/chat` | POST | Chat with AI advisor |
| `/health` | GET | Health check |

See [BACKEND_SETUP.md](./BACKEND_SETUP.md) for complete API documentation.

## 🧪 Testing

### Test with Sample Data
The seed data includes 5 customers with various financial profiles:
- **Rajesh Kumar** - Software Engineer (ID: 1)
- **Priya Sharma** - Marketing Manager (ID: 2)
- **Amit Patel** - Business Owner (ID: 3)
- **Sneha Reddy** - Data Analyst (ID: 4)
- **Vikram Singh** - Senior Manager (ID: 5)

### Example API Call
```bash
# Get customer profile
curl http://localhost:8000/api/v1/profile/1

# Generate plans for a customer
curl -X POST http://localhost:8000/api/v1/plans/generate \
  -H "Content-Type: application/json" \
  -d '{"customer_id": 1, "goal_ids": [1]}'
```

## 🛠️ Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - ORM for database management
- **Pydantic** - Data validation
- **PostgreSQL** - Production database
- **SQLite** - Development database
- **Groq** - LLM API for AI features
- **Docker** - Containerization

### Frontend (Planned)
- **React** - UI framework
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Styling

## 📋 Environment Variables

Required environment variables (see `.env.example`):

```env
# API Key (Required)
GROQ_API_KEY=your-groq-api-key-here

# Database
DATABASE_URL=sqlite:///./financial_advisor.db

# Application
DEBUG=False
LOG_LEVEL=INFO
```

## 🤝 Contributing

This is a prototype project. For production use:
1. Add authentication and authorization
2. Implement comprehensive testing
3. Add rate limiting and security headers
4. Set up monitoring and logging
5. Review and enhance error handling

## 📄 License

This is a prototype project for educational purposes.

## 🆘 Troubleshooting

### Server won't start
- Check if port 8000 is available
- Verify Python version (3.11+)
- Ensure all dependencies are installed

### Database errors
- For SQLite: Check file permissions
- For PostgreSQL: Verify database is running
- Check DATABASE_URL in .env

### Import errors
- Run from project root
- Set PYTHONPATH: `export PYTHONPATH=$PWD`

For more help, see [BACKEND_SETUP.md](./BACKEND_SETUP.md)

## 📞 Support

For issues or questions:
- Check API docs: http://localhost:8000/docs
- View logs: `docker-compose logs backend`
- Check health: http://localhost:8000/health
