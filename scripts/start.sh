#!/bin/bash

# Socivio Startup Script

echo "🚀 Starting Socivio - AI Social Media Assistant"
echo "=============================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp env.example .env
    echo "📝 Please edit .env with your API keys and configuration:"
    echo "   - INSTAGRAM_CLIENT_ID"
    echo "   - INSTAGRAM_CLIENT_SECRET"  
    echo "   - OPENAI_API_KEY"
    echo ""
    echo "Then run this script again."
    exit 1
fi

# Start services
echo "🐳 Starting Docker services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check service health
echo "🔍 Checking service health..."

# Check backend
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend is ready"
else
    echo "❌ Backend is not responding"
fi

# Check frontend
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend is ready"
else
    echo "❌ Frontend is not responding"
fi

echo ""
echo "🎉 Socivio is starting up!"
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "📋 To view logs: docker-compose logs -f"
echo "🛑 To stop: docker-compose down"
