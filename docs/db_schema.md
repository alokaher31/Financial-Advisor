# Database Schema

## Overview

The Financial Advisor application uses **SQLAlchemy ORM** with support for:
- **SQLite** (development)
- **PostgreSQL** (production)

All tables include timestamps and proper foreign key relationships with cascade deletes.

---

## Entity Relationship Diagram

```
┌─────────────┐
│    users    │
│─────────────│
│ id (PK)     │
│ name        │
│ email (UQ)  │
│ hashed_pwd  │
│ created_at  │
│ updated_at  │
└──────┬──────┘
       │
       │ 1:N
       │
┌──────▼──────────────────┐
│  customer_profiles      │
│─────────────────────────│
│ id (PK)                 │
│ user_id (FK) [nullable] │◄────┐
│ name                    │     │
│ age                     │     │
│ occupation              │     │
│ monthly_income          │     │
│ monthly_expenses        │     │
│ total_assets            │     │
│ total_liabilities       │     │
│ net_worth (calculated)  │     │
│ monthly_surplus (calc)  │     │
│ debt_to_income (calc)   │     │
│ created_at              │     │
│ updated_at              │     │
└──────┬──────────────────┘     │
       │                        │
       │ 1:N                    │
       ├────────────┬───────────┼──────────┐
       │            │           │          │
┌──────▼──────┐ ┌──▼────────┐ ┌▼─────────────┐ ┌▼────────────────┐
│    goals    │ │   plans   │ │ risk_assess  │ │ chat_messages   │
│─────────────│ │───────────│ │──────────────│ │─────────────────│
│ id (PK)     │ │ id (PK)   │ │ id (PK)      │ │ id (PK)         │
│ customer_id │ │customer_id│ │ customer_id  │ │ customer_id     │
│ goal_type   │ │ plan_name │ │ risk_score   │ │ role            │
│ goal_name   │ │ status    │ │ risk_category│ │ content         │
│ target_amt  │ │ asset_all │ │ answers(JSON)│ │ session_id      │
│ current_sav │ │ monthly_  │ │ created_at   │ │ created_at      │
│ time_horiz  │ │   target  │ │ updated_at   │ └─────────────────┘
│ priority    │ │ goal_alloc│ └──────────────┘
│ notes       │ │ monthly_  │
│ req_monthly │ │   breakdn │
│ achievable  │ │ assumptns │
│ created_at  │ │ notes     │
│ updated_at  │ │ created_at│
└─────────────┘ │ updated_at│
                └───────────┘
```

---

## Table Definitions

### 1. **users**

User authentication and account management.

| Column           | Type          | Constraints           | Description                      |
|------------------|---------------|-----------------------|----------------------------------|
| `id`             | INTEGER       | PRIMARY KEY, AUTO_INC | User ID                          |
| `name`           | VARCHAR(200)  | NOT NULL              | User's full name                 |
| `email`          | VARCHAR(255)  | UNIQUE, NOT NULL, IDX | Email address (login)            |
| `hashed_password`| VARCHAR(255)  | NOT NULL              | Bcrypt hashed password           |
| `created_at`     | TIMESTAMP     | NOT NULL, DEFAULT NOW | Account creation time            |
| `updated_at`     | TIMESTAMP     | NOT NULL, ON UPDATE   | Last update time                 |

**Indexes**:
- `idx_users_email` on `email` (unique)

**Relationships**:
- `customer_profiles`: One user can have multiple profiles (1:N)

---

### 2. **customer_profiles**

Financial profile information for each customer.

| Column                  | Type          | Constraints           | Description                      |
|-------------------------|---------------|-----------------------|----------------------------------|
| `id`                    | INTEGER       | PRIMARY KEY, AUTO_INC | Profile ID                       |
| `user_id`               | INTEGER       | FK→users.id, NULL, IDX| Owning user (nullable for legacy)|
| `name`                  | VARCHAR(200)  | NOT NULL, IDX         | Customer name                    |
| `age`                   | INTEGER       | NOT NULL              | Customer age                     |
| `occupation`            | VARCHAR(200)  | NOT NULL              | Occupation                       |
| `monthly_income`        | FLOAT         | NOT NULL              | Monthly income (₹)               |
| `monthly_expenses`      | FLOAT         | NOT NULL              | Monthly expenses (₹)             |
| `total_assets`          | FLOAT         | NOT NULL              | Total assets (₹)                 |
| `total_liabilities`     | FLOAT         | NOT NULL              | Total liabilities (₹)            |
| `net_worth`             | FLOAT         | NOT NULL              | Calculated: assets - liabilities |
| `monthly_surplus`       | FLOAT         | NOT NULL              | Calculated: income - expenses    |
| `debt_to_income_ratio`  | FLOAT         | NOT NULL              | Calculated: liabilities / income |
| `created_at`            | TIMESTAMP     | NOT NULL, DEFAULT NOW | Creation time                    |
| `updated_at`            | TIMESTAMP     | NOT NULL, ON UPDATE   | Last update time                 |

**Indexes**:
- `idx_customer_user` on `user_id`
- `idx_customer_name` on `name`

**Relationships**:
- `user`: Belongs to one user (N:1)
- `goals`: Has many goals (1:N, cascade delete)
- `plans`: Has many plans (1:N, cascade delete)
- `risk_assessments`: Has many assessments (1:N, cascade delete)
- `chat_messages`: Has many messages (1:N, cascade delete)

**Calculated Fields**:
- `net_worth` = `total_assets` - `total_liabilities`
- `monthly_surplus` = `monthly_income` - `monthly_expenses`
- `debt_to_income_ratio` = `total_liabilities` / `monthly_income`

---

### 3. **goals**

Financial goals (retirement, home purchase, education, etc.).

| Column                   | Type          | Constraints           | Description                      |
|--------------------------|---------------|-----------------------|----------------------------------|
| `id`                     | INTEGER       | PRIMARY KEY, AUTO_INC | Goal ID                          |
| `customer_id`            | INTEGER       | FK→profiles.id, IDX   | Owner profile                    |
| `goal_type`              | VARCHAR(50)   | NOT NULL, IDX         | Type: retirement, education, etc.|
| `goal_name`              | VARCHAR(200)  | NOT NULL              | Display name                     |
| `target_amount`          | FLOAT         | NOT NULL              | Target corpus (₹)                |
| `current_savings`        | FLOAT         | NOT NULL, DEFAULT 0   | Current savings toward goal (₹)  |
| `time_horizon_years`     | INTEGER       | NOT NULL              | Years to achieve goal            |
| `priority`               | VARCHAR(20)   | NOT NULL, DEFAULT med | Priority: high, medium, low      |
| `notes`                  | TEXT          | NULL                  | Additional notes                 |
| `required_monthly_saving`| FLOAT         | NOT NULL              | Calculated: monthly savings needed|
| `is_achievable`          | BOOLEAN       | NOT NULL, DEFAULT 0   | Calculated: can afford?          |
| `created_at`             | TIMESTAMP     | NOT NULL, DEFAULT NOW | Creation time                    |
| `updated_at`             | TIMESTAMP     | NOT NULL, ON UPDATE   | Last update time                 |

**Indexes**:
- `idx_goals_customer_priority` on (`customer_id`, `priority`)
- `idx_goals_customer_type` on (`customer_id`, `goal_type`)

**Relationships**:
- `customer`: Belongs to one customer (N:1)

**Calculated Fields**:
- `required_monthly_saving`: Based on target, time horizon, expected return
- `is_achievable`: Whether monthly surplus can cover required savings

**Valid Values**:
- `goal_type`: retirement, home_purchase, education, emergency_fund, investment, other
- `priority`: high, medium, low

---

### 4. **plans**

Generated investment plans with asset allocations.

| Column               | Type          | Constraints           | Description                      |
|----------------------|---------------|-----------------------|----------------------------------|
| `id`                 | INTEGER       | PRIMARY KEY, AUTO_INC | Plan ID                          |
| `customer_id`        | INTEGER       | FK→profiles.id, IDX   | Owner profile                    |
| `plan_name`          | VARCHAR(200)  | NOT NULL              | Plan name (e.g., "Conservative") |
| `status`             | VARCHAR(20)   | NOT NULL, DEFAULT draft, IDX | Plan status            |
| `asset_allocation`   | JSON          | NOT NULL              | Asset mix (Equity, Debt, etc.)   |
| `monthly_savings_target` | FLOAT     | NOT NULL              | Target monthly investment (₹)    |
| `goal_allocations`   | JSON          | NOT NULL              | How much to each goal            |
| `monthly_breakdown`  | JSON          | NOT NULL              | Detailed monthly breakdown       |
| `assumptions`        | JSON          | NOT NULL              | Return rates, inflation, etc.    |
| `notes`              | TEXT          | NULL                  | Additional notes                 |
| `created_at`         | TIMESTAMP     | NOT NULL, DEFAULT NOW | Creation time                    |
| `updated_at`         | TIMESTAMP     | NOT NULL, ON UPDATE   | Last update time                 |

**Indexes**:
- `idx_plans_customer_status` on (`customer_id`, `status`)

**Relationships**:
- `customer`: Belongs to one customer (N:1)

**Valid Values**:
- `status`: draft, active, archived, completed

**JSON Structure Examples**:

```json
// asset_allocation
{
  "Equity": 70,
  "Debt": 20,
  "Gold": 5,
  "Real_Estate": 5
}

// goal_allocations
[
  {
    "goal_id": 1,
    "goal_name": "Retirement",
    "monthly_investment": 25000,
    "allocation_percentage": 60
  }
]

// monthly_breakdown
{
  "total_monthly_investment": 40000,
  "SIP_equity": 28000,
  "SIP_debt": 8000,
  "Gold_accumulation": 2000,
  "Real_estate_fund": 2000
}

// assumptions
{
  "equity_return": 12.0,
  "debt_return": 7.5,
  "inflation": 6.0,
  "time_horizon_years": 20
}
```

---

### 5. **risk_assessments**

Risk tolerance questionnaire results.

| Column          | Type          | Constraints           | Description                      |
|-----------------|---------------|-----------------------|----------------------------------|
| `id`            | INTEGER       | PRIMARY KEY, AUTO_INC | Assessment ID                    |
| `customer_id`   | INTEGER       | FK→profiles.id, IDX   | Owner profile                    |
| `risk_score`    | INTEGER       | NOT NULL              | Calculated risk score (0-100)    |
| `risk_category` | VARCHAR(50)   | NOT NULL, IDX         | Category: Conservative/Moderate/Aggressive |
| `answers`       | JSON          | NOT NULL              | Questionnaire responses          |
| `created_at`    | TIMESTAMP     | NOT NULL, DEFAULT NOW | Assessment time                  |
| `updated_at`    | TIMESTAMP     | NOT NULL, ON UPDATE   | Last update time                 |

**Indexes**:
- `idx_risk_customer` on `customer_id`
- `idx_risk_category` on `risk_category`

**Relationships**:
- `customer`: Belongs to one customer (N:1)

**Valid Values**:
- `risk_category`: Conservative, Moderate, Aggressive

**JSON Structure Example**:

```json
{
  "Q1": "Preserve capital",
  "Q2": "Very uncomfortable",
  "Q3": "Sell everything",
  "Q4": "0-3 years",
  "Q5": "Very risk-averse"
}
```

---

### 6. **chat_messages**

Conversation history with AI chatbot.

| Column        | Type          | Constraints           | Description                      |
|---------------|---------------|-----------------------|----------------------------------|
| `id`          | INTEGER       | PRIMARY KEY, AUTO_INC | Message ID                       |
| `customer_id` | INTEGER       | FK→profiles.id, IDX   | Owner profile                    |
| `role`        | VARCHAR(20)   | NOT NULL              | Role: user, assistant, system    |
| `content`     | TEXT          | NOT NULL              | Message text                     |
| `session_id`  | VARCHAR(100)  | NULL, IDX             | Conversation session UUID        |
| `created_at`  | TIMESTAMP     | NOT NULL, DEFAULT NOW | Message timestamp                |

**Indexes**:
- `idx_chat_customer_session` on (`customer_id`, `session_id`)
- `idx_chat_session_created` on (`session_id`, `created_at`)

**Relationships**:
- `customer`: Belongs to one customer (N:1)

**Valid Values**:
- `role`: user, assistant, system

---

## Composite Indexes

These indexes optimize common query patterns:

1. **`idx_customer_user`** on `customer_profiles(user_id)`
   - For finding all profiles of a user

2. **`idx_goals_customer_priority`** on `goals(customer_id, priority)`
   - For fetching high-priority goals first

3. **`idx_goals_customer_type`** on `goals(customer_id, goal_type)`
   - For filtering goals by type

4. **`idx_plans_customer_status`** on `plans(customer_id, status)`
   - For finding active plans quickly

5. **`idx_chat_customer_session`** on `chat_messages(customer_id, session_id)`
   - For retrieving conversation history

6. **`idx_chat_session_created`** on `chat_messages(session_id, created_at)`
   - For ordering messages chronologically

---

## Foreign Key Constraints

All foreign keys have **CASCADE DELETE** to maintain referential integrity:

- When a **user** is deleted → all their **customer_profiles** are deleted
- When a **customer_profile** is deleted → all related **goals, plans, risk_assessments, chat_messages** are deleted

---

## Sample Data Counts

After running `seed_data.py`:

| Table               | Count |
|---------------------|-------|
| users               | 0     |
| customer_profiles   | 5     |
| goals               | 14    |
| risk_assessments    | 5     |
| plans               | 0-15  |
| chat_messages       | 0+    |

---

## Database Migrations

Currently using SQLAlchemy's `Base.metadata.create_all()` for schema creation.

For production, consider using **Alembic** for versioned migrations:

```bash
# Initialize Alembic
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Add user_id to customer_profiles"

# Apply migration
alembic upgrade head
```

---

## Connection Configuration

### **SQLite (Development)**
```python
DATABASE_URL = "sqlite:///./financial_advisor.db"
```

### **PostgreSQL (Production)**
```python
DATABASE_URL = "postgresql+psycopg2://user:password@host:5432/financial_advisor"
```

---

## Query Examples

### Get all profiles for a user
```sql
SELECT * FROM customer_profiles
WHERE user_id = ?;
```

### Get active plan for customer
```sql
SELECT * FROM plans
WHERE customer_id = ? AND status = 'active'
LIMIT 1;
```

### Get recent chat history
```sql
SELECT * FROM chat_messages
WHERE customer_id = ? AND session_id = ?
ORDER BY created_at DESC
LIMIT 10;
```

### Get high-priority goals
```sql
SELECT * FROM goals
WHERE customer_id = ? AND priority = 'high'
ORDER BY created_at DESC;
```

### Get latest risk assessment
```sql
SELECT * FROM risk_assessments
WHERE customer_id = ?
ORDER BY created_at DESC
LIMIT 1;
```
