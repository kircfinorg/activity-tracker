#!/bin/bash

echo "=========================================="
echo "Gamified Activity Tracker - Setup Script"
echo "=========================================="
echo ""

# Check for Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    echo "   Visit: https://nodejs.org/"
    exit 1
fi

echo "✅ Node.js found: $(node --version)"

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11+ first."
    echo "   Visit: https://www.python.org/"
    exit 1
fi

echo "✅ Python found: $(python3 --version)"
echo ""

# Setup Frontend
echo "📦 Setting up Frontend..."
cd frontend

if [ ! -f ".env.local" ]; then
    echo "Creating .env.local from example..."
    cp .env.local.example .env.local
    echo "⚠️  Please update frontend/.env.local with your Firebase configuration"
fi

echo "Installing frontend dependencies..."
if command -v yarn &> /dev/null; then
    yarn install
else
    npm install
fi

cd ..
echo "✅ Frontend setup complete!"
echo ""

# Setup Backend
echo "📦 Setting up Backend..."
cd backend

if [ ! -f ".env" ]; then
    echo "Creating .env from example..."
    cp .env.example .env
    echo "⚠️  Please update backend/.env with your configuration"
fi

echo "Creating Python virtual environment..."
python3 -m venv venv

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing backend dependencies..."
pip install -r requirements.txt

cd ..
echo "✅ Backend setup complete!"
echo ""

echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Update frontend/.env.local with your Firebase configuration"
echo "2. Download Firebase service account key to backend/serviceAccountKey.json"
echo "3. Update backend/.env with your configuration"
echo ""
echo "To start the frontend:"
echo "  cd frontend"
echo "  npm run dev  (or yarn dev)"
echo ""
echo "To start the backend:"
echo "  cd backend"
echo "  source venv/bin/activate"
echo "  python main.py"
echo ""
