#!/bin/bash
# Quick Start Script for Entrupy

echo "🚀 Entrupy - Price Monitoring System Setup"
echo "=========================================="
echo ""

# Backend Setup
echo "📦 Setting up backend..."
python -m venv venv
source venv/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Initializing database..."
python init_db.py

echo "✅ Backend ready!"
echo ""

# Frontend Setup
echo "⚛️  Setting up frontend..."
cd frontend
npm install
echo "✅ Frontend ready!"
echo ""

cd ../

echo "📝 Setup complete!"
echo ""
echo "🎯 To run the application:"
echo ""
echo "Terminal 1 (Backend):"
echo "  source venv/bin/activate"
echo "  uvicorn app.main:app --reload --port 8000"
echo ""
echo "Terminal 2 (Frontend):"
echo "  cd frontend"
echo "  npm run dev"
echo ""
echo "📖 API Docs: http://localhost:8000/docs"
echo "🌐 Frontend: http://localhost:3000"
echo ""
echo "🧪 Run tests: pytest tests/ -v"
