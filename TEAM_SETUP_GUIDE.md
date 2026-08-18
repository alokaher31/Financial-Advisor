# Financial Advisor - Team Setup Guide

## 🔐 **API Key Security - READ THIS FIRST!**

### **⚠️ NEVER commit your `.env` file to Git!**

Each team member needs their own Groq API key. Follow these steps:

---

## 📝 **Step 1: Get Your Own Groq API Key**

1. Go to: https://console.groq.com/
2. Sign up for a FREE account (no credit card required)
3. Navigate to **API Keys** section
4. Click **Create API Key**
5. Copy your key (looks like: `gsk_...`)

**Note**: Groq provides FREE API access with generous limits - perfect for development!

---

## 🛠️ **Step 2: Set Up Your Local Environment**

### **Backend Setup**

```bash
# 1. Navigate to backend directory
cd backend

# 2. Copy the example environment file
cp .env.example .env

# 3. Open .env in your text editor
nano .env
# or
code .env

# 4. Replace placeholder values with your actual keys:
# - GROQ_API_KEY: Paste your Groq API key from Step 1
# - JWT_SECRET_KEY: Generate using: openssl rand -hex 32
# - SECRET_KEY: Use the same value as JWT_SECRET_KEY
```

### **Frontend Setup**

```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Copy the example environment file
cp .env.example .env.local

# 3. No changes needed if running locally!
# (Already set to use http://localhost:8000)
```

---

## 🚀 **Step 3: Run the Project**

### **Terminal 1 - Backend**

```bash
cd backend

# Install dependencies (first time only)
pip3 install -r requirements.txt

# Start the backend server
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### **Terminal 2 - Frontend**

```bash
cd frontend

# Install dependencies (first time only)
npm install

# Start the frontend development server
npm run dev
```

**Expected Output:**
```
VITE v5.x.x  ready in xxx ms
➜  Local:   http://localhost:5173/
```

---

## ✅ **Step 4: Verify Everything Works**

1. **Open browser**: http://localhost:5173
2. **Register a new account**
3. **Create a financial profile**
4. **Test the chatbot** - Ask: "What is my risk tolerance?"
5. **Generate financial plans**
6. **Run a What-If scenario**

If the chatbot responds properly, your Groq API key is working! ✅

---

## 🔒 **Security Best Practices**

### **DO:**
- ✅ Keep your `.env` file private
- ✅ Use your own API keys
- ✅ Never share API keys in chat/email
- ✅ Add `.env` to `.gitignore` (already done)

### **DON'T:**
- ❌ Commit `.env` files to Git
- ❌ Share API keys with team members
- ❌ Hardcode API keys in source code
- ❌ Push API keys to GitHub/GitLab

---

## 📁 **Project Structure**

```
finance-planner/
├── backend/
│   ├── .env.example          ← Template (safe to commit)
│   ├── .env                  ← Your keys (DO NOT COMMIT)
│   ├── app/                  ← Python FastAPI application
│   └── requirements.txt      ← Python dependencies
├── frontend/
│   ├── .env.example          ← Template (safe to commit)
│   ├── .env.local            ← Your config (DO NOT COMMIT)
│   ├── src/                  ← React application
│   └── package.json          ← Node dependencies
└── docs/                     ← Technical documentation
```

---

## 🐛 **Troubleshooting**

### **Problem: Backend won't start**

```bash
# Check if port 8000 is already in use
lsof -ti:8000 | xargs kill -9

# Verify Python dependencies are installed
pip3 install -r requirements.txt
```

### **Problem: Frontend won't start**

```bash
# Check if port 5173 is already in use
lsof -ti:5173 | xargs kill -9

# Reinstall dependencies
rm -rf node_modules
npm install
```

### **Problem: Chatbot returns errors**

1. Check your Groq API key in `backend/.env`
2. Verify the key is valid: https://console.groq.com/keys
3. Check backend logs for specific error messages

### **Problem: Authentication fails**

1. Make sure both backend and frontend are running
2. Clear browser cache and cookies
3. Check `JWT_SECRET_KEY` is set in `backend/.env`

---

## 📞 **Getting Help**

If you encounter issues:

1. Check the console logs (backend terminal)
2. Check browser DevTools (F12 → Console tab)
3. Review the technical docs in `/docs` folder
4. Ask the team on your communication channel

---

## 🎯 **What's Implemented**

- ✅ User authentication (JWT-based)
- ✅ Financial profile creation
- ✅ Risk assessment questionnaire
- ✅ Goal setting and tracking
- ✅ Financial plan generation (3 strategies)
- ✅ AI chatbot with context (Groq LLM)
- ✅ What-If scenario analysis
- ✅ Plan comparison tool
- ✅ Markdown rendering for AI responses

---

## 📚 **Additional Documentation**

- **API Specification**: `docs/api_spec.md`
- **System Architecture**: `docs/architecture.md`
- **Database Schema**: `docs/db_schema.md`
- **Demo Script**: `docs/demo_script.md`
- **Prompt Library**: `docs/prompt_library.md`

---

**Happy Coding! 🚀**
