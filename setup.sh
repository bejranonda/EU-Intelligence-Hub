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
    echo "❌ Docker is not installed!"
    echo ""
    echo "Please install Docker by running:"
    echo "  sudo bash install-docker.sh"
    echo ""
    echo "Or follow the installation guide at:"
    echo "  https://docs.docker.com/engine/install/"
    exit 1
fi

echo "✅ Docker is installed"
echo ""

# Determine which docker compose command to use
DOCKER_COMPOSE_CMD=""
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker-compose"
    echo "✅ Docker Compose (standalone) is installed"
elif docker compose version &> /dev/null 2>&1; then
    DOCKER_COMPOSE_CMD="docker compose"
    echo "✅ Docker Compose (plugin) is installed"
else
    echo "❌ Docker Compose is not installed!"
    echo ""
    echo "Please install Docker Compose:"
    echo "  sudo bash install-docker.sh"
    exit 1
fi

echo ""

# Stop any running containers
echo "🛑 Stopping any existing containers..."
$DOCKER_COMPOSE_CMD down 2>/dev/null || true
echo ""

# Build and start services
echo "🔨 Building and starting services..."
echo "This may take a few minutes on first run..."
echo ""

$DOCKER_COMPOSE_CMD up -d --build

echo ""
echo "⏳ Waiting for services to be healthy..."
echo ""

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL..."
timeout=60
counter=0
until $DOCKER_COMPOSE_CMD exec -T postgres pg_isready -U euint_user &> /dev/null; do
    if [ $counter -ge $timeout ]; then
        echo "❌ PostgreSQL failed to start within ${timeout} seconds"
        $DOCKER_COMPOSE_CMD logs postgres
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
until $DOCKER_COMPOSE_CMD exec -T redis redis-cli ping &> /dev/null; do
    if [ $counter -ge $timeout ]; then
        echo "❌ Redis failed to start within ${timeout} seconds"
        $DOCKER_COMPOSE_CMD logs redis
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
        $DOCKER_COMPOSE_CMD logs backend
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
        $DOCKER_COMPOSE_CMD logs frontend
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
echo "  View logs:       $DOCKER_COMPOSE_CMD logs -f"
echo "  Stop services:   $DOCKER_COMPOSE_CMD down"
echo "  Restart:         $DOCKER_COMPOSE_CMD restart"
echo "  Run tests:       $DOCKER_COMPOSE_CMD exec backend pytest"
echo ""
echo "To stop all services, run: $DOCKER_COMPOSE_CMD down"
echo ""
