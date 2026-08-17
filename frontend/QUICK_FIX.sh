#!/bin/bash

# Quick Fix Script for Frontend-Backend Integration
# This makes the ONE critical change needed to connect to backend

echo "🔧 Applying frontend-backend integration fix..."
echo ""

# Backup original file
cp src/api/apiClient.js src/api/apiClient.js.backup
echo "✅ Backed up apiClient.js"

# Apply the fix: /api → /api/v1
sed -i.tmp "s|\${API_BASE_URL}/api\${path}|\${API_BASE_URL}/api/v1\${path}|g" src/api/apiClient.js
rm -f src/api/apiClient.js.tmp

echo "✅ Fixed API path: /api → /api/v1"
echo ""
echo "📝 Changes made:"
echo "   Line 69: fetch path now uses /api/v1 instead of /api"
echo ""
echo "🎯 Next steps:"
echo "   1. Create .env.local: cp .env.example .env.local"
echo "   2. Edit .env.local: Set VITE_USE_MOCK_DATA=false"
echo "   3. Start backend: cd ../backend && uvicorn app.main:app --reload"
echo "   4. Start frontend: npm run dev"
echo ""
echo "✨ Ready to integrate!"
