#!/bin/bash

# European News Intelligence Hub - Setup Script
# This script initializes and starts all services for the application

set -e  # Exit on error

echo "🌍 European News Intelligence Hub - Setup Script"
echo "================================================"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "⚠️  Please update .env with your configuration before running again."
    exit 1
fi

echo "✅ Environment file found"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

echo "✅ Docker is installed"
echo ""

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker Compose is installed"
echo ""

# Stop any running containers
echo "🛑 Stopping any existing containers..."
docker-compose down 2>/dev/null || true
echo ""

# Build and start services
echo "🔨 Building and starting services..."
echo "This may take a few minutes on first run..."
echo ""

docker-compose up -d --build

echo ""
echo "⏳ Waiting for services to be healthy..."
echo ""

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL..."
timeout=60
counter=0
until docker-compose exec -T postgres pg_isready -U newsadmin &> /dev/null; do
    if [ $counter -ge $timeout ]; then
        echo "❌ PostgreSQL failed to start within ${timeout} seconds"
        docker-compose logs postgres
        exit 1
    fi
    counter=$((counter + 1))
    sleep 1
    echo -n "."
done
echo ""
echo "✅ PostgreSQL is ready"

# Wait for Redis to be ready
echo "Waiting for Redis..."
counter=0
until docker-compose exec -T redis redis-cli ping &> /dev/null; do
    if [ $counter -ge $timeout ]; then
        echo "❌ Redis failed to start within ${timeout} seconds"
        docker-compose logs redis
        exit 1
    fi
    counter=$((counter + 1))
    sleep 1
    echo -n "."
done
echo ""
echo "✅ Redis is ready"

# Wait for backend to be ready
echo "Waiting for backend API..."
counter=0
until curl -s http://localhost:8000/health &> /dev/null; do
    if [ $counter -ge $timeout ]; then
        echo "❌ Backend API failed to start within ${timeout} seconds"
        docker-compose logs backend
        exit 1
    fi
    counter=$((counter + 1))
    sleep 1
    echo -n "."
done
echo ""
echo "✅ Backend API is ready"

# Wait for frontend to be ready
echo "Waiting for frontend..."
counter=0
until curl -s http://localhost:3000 &> /dev/null; do
    if [ $counter -ge 90 ]; then  # Frontend takes longer to build
        echo "❌ Frontend failed to start within 90 seconds"
        docker-compose logs frontend
        exit 1
    fi
    counter=$((counter + 1))
    sleep 1
    echo -n "."
done
echo ""
echo "✅ Frontend is ready"

echo ""
echo "================================================"
echo "✅ All services are running!"
echo "================================================"
echo ""
echo "Access the application:"
echo "  Frontend:  http://localhost:3000"
echo "  Backend:   http://localhost:8000"
echo "  API Docs:  http://localhost:8000/docs"
echo ""
echo "Useful commands:"
echo "  View logs:       docker-compose logs -f"
echo "  Stop services:   docker-compose down"
echo "  Restart:         docker-compose restart"
echo "  Run tests:       docker-compose exec backend pytest"
echo ""
echo "To stop all services, run: docker-compose down"
echo ""
