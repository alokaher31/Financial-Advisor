# API Specification

Base URL: `http://localhost:8000/api/v1`

All authenticated endpoints require: `Authorization: Bearer <JWT_TOKEN>`

---

## Authentication Endpoints

### POST /auth/register
Register new user account.

**Request**:
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "SecurePass123"
}
```

**Response** (201):
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

### POST /auth/login
Login with email/password (OAuth2 form).

**Request** (form-data):
- `username`: email
- `password`: password

**Response** (200):
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

### POST /auth/login/json
Login with JSON body.

**Request**:
```json
{
  "email": "john@example.com",
  "password": "SecurePass123"
}
```

### GET /auth/me
Get current user info. **Requires auth**.

**Response** (200):
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "created_at": "2026-08-17T10:00:00Z"
}
```

---

## Profile Endpoints

### POST /profile
Create customer profile. **Requires auth**.

**Request**:
```json
{
  "name": "John Doe",
  "age": 35,
  "occupation": "Software Engineer",
  "monthly_income": 150000,
  "monthly_expenses": 80000,
  "total_assets": 2000000,
  "total_liabilities": 500000
}
```

**Response** (201):
```json
{
  "id": 1,
  "user_id": 1,
  "name": "John Doe",
  "age": 35,
  "occupation": "Software Engineer",
  "monthly_income": 150000,
  "monthly_expenses": 80000,
  "total_assets": 2000000,
  "total_liabilities": 500000,
  "net_worth": 1500000,
  "monthly_surplus": 70000,
  "debt_to_income_ratio": 0.33,
  "created_at": "2026-08-17T10:00:00Z",
  "updated_at": "2026-08-17T10:00:00Z"
}
```

### GET /profile/{customer_id}
Get profile. **Requires auth & ownership**.

### GET /profile
List user's profiles. **Requires auth**.

### PUT /profile/{customer_id}
Update profile. **Requires auth & ownership**.

### DELETE /profile/{customer_id}
Delete profile. **Requires auth & ownership**.

---

## Risk Assessment Endpoints

### GET /risk/questionnaire
Get risk assessment questions.

**Response** (200):
```json
{
  "questions": [
    {
      "id": "Q1",
      "text": "What is your primary investment goal?",
      "options": ["Preserve capital", "Generate income", "Growth", "Aggressive growth"]
    }
  ]
}
```

### POST /risk/assess
Submit risk assessment.

**Request**:
```json
{
  "customer_id": 1,
  "answers": {
    "Q1": "Growth",
    "Q2": "Comfortable",
    "Q3": "Hold steady",
    "Q4": "7-10 years",
    "Q5": "Moderate"
  }
}
```

**Response** (201):
```json
{
  "id": 1,
  "customer_id": 1,
  "risk_score": 65,
  "risk_category": "Moderate",
  "answers": {...},
  "created_at": "2026-08-17T10:00:00Z"
}
```

### GET /risk/assessment/{assessment_id}
Get assessment by ID.

### GET /risk/customer/{customer_id}/latest
Get latest assessment for customer.

---

## Goal Endpoints

### POST /goals
Create financial goal.

**Request**:
```json
{
  "customer_id": 1,
  "goal_type": "retirement",
  "goal_name": "Retirement Fund",
  "target_amount": 50000000,
  "current_savings": 1000000,
  "time_horizon_years": 25,
  "priority": "high"
}
```

**Response** (201):
```json
{
  "id": 1,
  "customer_id": 1,
  "goal_type": "retirement",
  "goal_name": "Retirement Fund",
  "target_amount": 50000000,
  "current_savings": 1000000,
  "time_horizon_years": 25,
  "priority": "high",
  "required_monthly_saving": 45000,
  "is_achievable": true,
  "created_at": "2026-08-17T10:00:00Z"
}
```

### GET /goals/{goal_id}
Get goal by ID.

### GET /goals/customer/{customer_id}
List customer's goals.

### PUT /goals/{goal_id}
Update goal.

### DELETE /goals/{goal_id}
Delete goal.

---

## Plan Endpoints

### POST /plans/generate
Generate 3 investment plans.

**Request**:
```json
{
  "customer_id": 1,
  "goal_ids": [1, 2],
  "risk_assessment_id": 1
}
```

**Response** (200):
```json
{
  "plans": [
    {
      "id": 1,
      "plan_name": "Conservative",
      "risk_level": "Conservative",
      "allocation": {
        "Equity": 40,
        "Debt": 45,
        "Gold": 10,
        "Real_Estate": 5
      },
      "blended_expected_return": 8.5,
      "current_monthly_investment": 50000,
      "projected_corpus": 45000000,
      "gap_vs_target": -5000000,
      "required_monthly_investment": 55000
    }
  ],
  "count": 3
}
```

### POST /plans/compare
Compare multiple plans.

**Request**:
```json
{
  "customer_id": 1,
  "plan_ids": [1, 2, 3]
}
```

**Response** (200):
```json
{
  "summary": "The Conservative plan offers...",
  "plans": [...],
  "key_differences": {...}
}
```

### POST /whatif
What-if scenario analysis.

**Request**:
```json
{
  "customer_id": 1,
  "goal_id": 1,
  "plan_id": 1,
  "scenario": {
    "parameter": "current_monthly_investment",
    "value": 70000
  }
}
```

**Response** (200):
```json
{
  "before": {...},
  "after": {...},
  "change": {...},
  "explanation": "By increasing your monthly investment..."
}
```

### POST /plans
Save plan.

### GET /plans/{plan_id}
Get plan by ID.

### GET /plans/customer/{customer_id}
List customer's plans.

### GET /plans/customer/{customer_id}/active
Get active plan.

### POST /plans/{plan_id}/select
Select plan as active.

---

## Chat Endpoints

### POST /chat
Send chat message.

**Request**:
```json
{
  "customer_id": 1,
  "message": "How should I save for retirement?",
  "session_id": "uuid-session-123",
  "include_context": true,
  "max_history_messages": 10
}
```

**Response** (200):
```json
{
  "message": "Based on your profile...",
  "session_id": "uuid-session-123",
  "customer_id": 1,
  "timestamp": "2026-08-17T10:00:00Z",
  "context_used": true
}
```

### GET /chat/history
Get chat history.

**Query Params**:
- `customer_id`: int
- `session_id`: string (optional)
- `limit`: int (default: 50)
- `offset`: int (default: 0)

### GET /chat/sessions/{customer_id}
Get all session IDs for customer.

### DELETE /chat/sessions/{customer_id}/{session_id}
Delete chat session.

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Validation error: ..."
}
```

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 403 Forbidden
```json
{
  "detail": "You don't have permission to access this resource"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## Interactive Documentation

Visit `http://localhost:8000/docs` for Swagger UI with interactive API testing.
