# Data Assumptions

## 1. Purpose

The datasets used by the Finance Planner prototype are synthetic,
illustrative datasets created specifically for development, testing,
and demonstration.

They are NOT sourced from real financial-market data and should not
be interpreted as actual investment or market predictions.

---

## 2. Historical Financial Data

### Raw dataset

File:

`backend/app/data/synthetic_historical_data.csv`

The raw historical dataset contains annual illustrative performance
information for five asset categories:

- Equity
- Debt
- Gold
- Real_Estate
- Cash

The dataset covers the years 2015 through 2024.

Each record contains:

- `year` — illustrative calendar year
- `asset_category` — asset class represented by the record
- `annual_return_pct` — illustrative annual return expressed as a
  percentage
- `volatility_pct` — illustrative annual volatility expressed as a
  percentage

There are 10 years and 5 asset categories, resulting in 50 historical
records.

---

## 3. Historical Summary Data

File:

`backend/app/data/historical_data_summary.csv`

The summary contains one row for each asset category.

Columns:

- `asset_category`
- `avg_annual_return`
- `volatility`

The summary is derived from the synthetic historical dataset and is
provided as a convenient input for financial-plan calculations.

The summary is not real historical market performance.

---

## 4. Synthetic Customer Data

File:

`backend/app/data/synthetic_customers.csv`

The customer dataset contains eight fictional customer profiles.

Each profile includes:

- personal information
- monthly income
- monthly expenses
- savings
- total assets
- total liabilities
- financial goal
- target amount
- current goal savings
- time horizon
- illustrative risk category

The profiles are intentionally diverse so that the prototype can
demonstrate different financial-planning scenarios.

Examples include different:

- ages
- income levels
- expense levels
- financial positions
- goals
- investment-risk categories
- goal time horizons

---

## 5. Financial Consistency

The synthetic customer records are designed to be internally
consistent for prototype demonstrations.

Examples of validation rules include:

- monthly income should be greater than or equal to monthly expenses
- target amount should be greater than or equal to current goal savings
- time horizon should be positive
- total liabilities should not be negative
- financial numeric fields should contain valid numeric values

These checks are intended to prevent obviously inconsistent demo
profiles.

---

## 6. Risk Categories

The `likely_risk_category` field represents an illustrative
risk-profile classification for the synthetic customer.

It is intended for demo and seed-data purposes.

The actual application risk assessment should be determined by the
application's risk-scoring logic and questionnaire rather than
treating this synthetic field as a real financial assessment.

---

## 7. Data Loader

`backend/app/data/data_loader.py` provides reusable functions for
loading the datasets.

The main interfaces are:

- `load_raw_historical_data()`
- `load_historical_data()`
- `load_demo_customers()`

This keeps CSV-reading logic separated from the financial calculation
and API layers.

---

## 8. Database Seeding

The synthetic customer profiles can be loaded into PostgreSQL through
`backend/app/db/seed_data.py`.

The seed process creates:

- Customer records
- Goal records

The seeding operation is designed to be idempotent so that running the
seed script multiple times does not create duplicate demo customers
or goals.

---

## 9. Prototype Limitation

This data is intentionally illustrative.

It must NOT be used as:

- real investment-performance history
- a prediction of future returns
- a source of real market statistics
- personalized financial advice
- a substitute for professional financial advice

All financial projections produced by the prototype should be
interpreted as demonstrations of the application's calculations and
workflow.

---

## 10. Disclaimer

**This prototype uses synthetic and illustrative financial data.
The information and projections are for demonstration and educational
purposes only and do not constitute financial, investment, tax, or
legal advice.**