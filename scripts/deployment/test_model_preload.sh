#!/bin/bash

# Quick Model Pre-loading Test Script
set -e

echo "🧪 Testing AI Model Pre-loading Process"
echo "======================================="

cd "$(dirname "$0")"

# Check if requirements are available
if [ ! -f "backend/requirements.txt" ]; then
    echo "❌ requirements.txt not found in backend directory"
    exit 1
fi

# Create test environment
echo "📦 Setting up test environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate

echo "📥 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r backend/requirements.txt

echo "🤖 Testing model pre-loading script..."
cd backend
python preload_models.py

echo "✅ Verifying models..."
python verify_models.py

echo ""
echo "🎉 Model pre-loading test completed successfully!"
echo "💡 You can now build Docker images with confidence"
echo ""
echo "Next steps:"
echo "  1. Edit .env file with your GROQ_API_KEY"
echo "  2. Run: ./deploy.sh"
echo "  3. Wait for initial build (models will be cached)"
echo "  4. Enjoy instant startup times!"
