# Demo Script

Step-by-step walkthrough for demonstrating the Financial Advisor application.

---

## Prerequisites

1. Backend running on `http://localhost:8000`
2. Frontend running on `http://localhost:5173`
3. Database seeded with sample data
4. `.env` files configured with API keys

---

## Demo Flow (15-20 minutes)

### **1. Introduction** (2 min)

**Say**:
> "I'm going to demonstrate a Financial Advisor application that helps users plan their financial future using AI. It covers profile creation, risk assessment, goal setting, investment planning, and includes an AI chatbot for financial questions."

**Show**: Frontend landing page

---

### **2. User Registration** (2 min)

**Action**: Click "Sign Up"

**Enter**:
- Name: "Demo User"
- Email: "demo@example.com"
- Password: "DemoPass123"

**Say**:
> "The application uses JWT authentication. Passwords are hashed with bcrypt for security. After registration, you're automatically logged in."

**Result**: Redirected to profile form

---

### **3. Create Profile** (3 min)

**Action**: Fill profile form

**Enter**:
- Name: "Demo User"
- Age: 35
- Occupation: "Software Engineer"
- Monthly Income: ₹150,000
- Monthly Expenses: ₹80,000
- Total Assets: ₹2,000,000
- Total Liabilities: ₹500,000

**Say**:
> "The system automatically calculates key financial metrics: net worth, monthly surplus, and debt-to-income ratio. This profile is linked to your user account."

**Result**: Profile created, move to risk assessment

---

### **4. Risk Assessment** (2 min)

**Action**: Answer risk questionnaire

**Say**:
> "Risk tolerance determines your investment strategy. Let's select moderate risk preferences."

**Select**: Moderate options for all questions

**Result**: Risk score calculated (e.g., 65 - Moderate)

---

### **5. Set Financial Goal** (2 min)

**Action**: Create retirement goal

**Enter**:
- Goal Type: Retirement
- Goal Name: "Retirement Fund"
- Target Amount: ₹50,000,000 (5 Crores)
- Current Savings: ₹1,000,000 (10 Lakhs)
- Time Horizon: 25 years
- Priority: High

**Say**:
> "The system calculates required monthly savings based on expected returns. With our ₹70,000 surplus, this goal is achievable."

**Result**: Goal created, show required savings

---

### **6. Generate Investment Plans** (3 min)

**Action**: Click "Generate Plans"

**Say**:
> "The system now generates three investment plans - Conservative, Moderate, and Aggressive - each with different asset allocations and return expectations."

**Show**: 3 plans displayed

**Highlight**:
- Conservative: 40% Equity, higher debt allocation
- Moderate: 60% Equity, balanced approach
- Aggressive: 80% Equity, maximum growth potential

**Say**:
> "Notice the trade-off: higher returns come with higher risk. The Moderate plan aligns with our risk profile."

---

### **7. Compare Plans** (2 min)

**Action**: Click "Compare Plans"

**Say**:
> "Our AI generates a detailed comparison, explaining the differences and recommending the best fit for your profile."

**Show**: AI-generated comparison summary

**Highlight**: Recommendation section

---

### **8. What-If Analysis** (3 min)

**Action**: Open What-If panel

**Say**:
> "Let's explore a what-if scenario: What happens if we increase monthly investment from ₹50,000 to ₹70,000?"

**Enter**: Monthly investment: ₹70,000

**Show**: Before/After comparison

**Say**:
> "The AI explains the impact: an extra ₹20,000 per month compounds to ₹1.8 Crores more at retirement. This transforms a shortfall into a surplus."

---

### **9. AI Chatbot** (4 min)

**Action**: Open Chatbot

**Demo Questions**:

1. **"What is the 50/30/20 budgeting rule?"**
   - Shows general financial advice

2. **"How should I allocate my investments for retirement?"**
   - Uses customer context (age, risk profile, goals)
   - Provides personalized advice

3. **"What if I reduce my expenses by ₹10,000?"**
   - Detects what-if intent
   - Runs scenario analysis
   - Narrates the impact

**Say**:
> "The chatbot is context-aware. It knows your profile, goals, and plan. It can answer general questions and run what-if scenarios conversationally."

---

### **10. Select Plan & Summary** (2 min)

**Action**: Select Moderate plan

**Say**:
> "Once satisfied, select your preferred plan. It's marked as active and becomes your primary investment strategy."

**Show**:
- Plan marked as "Active"
- Summary of selections
- Next steps (implementation)

---

## **Technical Highlights** (Optional - 3 min)

If audience is technical:

1. **Architecture**:
   - React frontend + FastAPI backend
   - JWT authentication
   - SQLite/PostgreSQL database
   - Groq LLM integration

2. **Security**:
   - Bcrypt password hashing
   - JWT tokens with expiration
   - User-based data isolation

3. **AI Features**:
   - Context-aware chatbot
   - Plan explanations & comparisons
   - What-if scenario analysis
   - All powered by Groq's LLM

4. **Calculations**:
   - Future value projections
   - Asset allocation optimization
   - Risk scoring algorithm

---

## **Q&A Preparation**

### Common Questions:

**Q: Is this production-ready?**
A: It's a fully functional MVP. For production, add: rate limiting, enhanced security, real-time data, compliance features.

**Q: How accurate are the projections?**
A: Projections use standard financial formulas with assumed return rates. Real returns vary. Always consult a professional advisor.

**Q: Can it integrate with real bank accounts?**
A: Not currently. Future enhancement would use bank APIs for automatic data import.

**Q: What LLM does it use?**
A: Groq API with openai/gpt-oss-120b model. Could be swapped for other providers (OpenAI, Anthropic, etc.).

**Q: How is data secured?**
A: Passwords hashed with bcrypt, JWT auth, user-based isolation. For production, add encryption at rest, audit logs, compliance certifications.

---

## **Closing** (1 min)

**Say**:
> "This demonstrates a complete financial planning workflow with AI assistance. The application handles authentication, data management, complex calculations, and natural language interactions. It's built with modern web technologies and can be extended with additional features like document upload, real-time data, mobile apps, and more."

**Show**: GitHub repo or architecture diagram

---

## **Demo Data Reset**

Between demos:

```bash
# Reset database
cd backend
rm financial_advisor.db
python -m app.db.seed_data

# Or use different email for each demo
```

---

## **Troubleshooting**

- **Frontend shows mock data**: Check `.env.local` has `VITE_USE_MOCK_DATA=false`
- **401 errors**: Token expired, re-login
- **Chat not working**: Check GROQ_API_KEY in backend/.env
- **Blank screens**: Check browser console for errors

---

**Total Demo Time**: 15-20 minutes + Q&A
