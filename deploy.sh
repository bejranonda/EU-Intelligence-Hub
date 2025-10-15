#!/bin/bash

###############################################################################
# European News Intelligence Hub - Deployment Script
#
# Usage:
#   ./deploy.sh [environment]
#
# Environments:
#   production - Deploy to production with SSL
#   staging    - Deploy to staging environment
#   dev        - Deploy development environment
###############################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if environment argument is provided
if [ -z "$1" ]; then
    log_error "Environment not specified"
    echo "Usage: ./deploy.sh [production|staging|dev]"
    exit 1
fi

ENVIRONMENT=$1

log_info "Starting deployment for environment: $ENVIRONMENT"

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(production|staging|dev)$ ]]; then
    log_error "Invalid environment: $ENVIRONMENT"
    echo "Valid environments: production, staging, dev"
    exit 1
fi

# Check if .env file exists
if [ "$ENVIRONMENT" == "production" ] && [ ! -f ".env.production" ]; then
    log_error ".env.production file not found"
    echo "Please create .env.production file with required environment variables"
    exit 1
fi

# Load environment variables
if [ "$ENVIRONMENT" == "production" ]; then
    log_info "Loading production environment variables"
    export $(cat .env.production | grep -v '^#' | xargs)
elif [ "$ENVIRONMENT" == "staging" ]; then
    log_info "Loading staging environment variables"
    export $(cat .env.staging | grep -v '^#' | xargs)
else
    log_info "Loading development environment variables"
    export $(cat .env | grep -v '^#' | xargs)
fi

# Check required environment variables
required_vars=("POSTGRES_PASSWORD" "REDIS_PASSWORD" "SECRET_KEY" "GEMINI_API_KEY")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        log_error "Required environment variable $var is not set"
        exit 1
    fi
done

log_success "Environment variables loaded"

# Stop existing containers
log_info "Stopping existing containers..."
if [ "$ENVIRONMENT" == "production" ]; then
    docker-compose -f docker-compose.prod.yml down
else
    docker-compose down
fi

log_success "Containers stopped"

# Pull latest code (if deploying from git)
if [ "$ENVIRONMENT" == "production" ] && [ -d ".git" ]; then
    log_info "Pulling latest code from git..."
    git pull origin main
    log_success "Code updated"
fi

# Build and start containers
log_info "Building Docker images..."
if [ "$ENVIRONMENT" == "production" ]; then
    docker-compose -f docker-compose.prod.yml build --no-cache
else
    docker-compose build
fi

log_success "Docker images built"

log_info "Starting containers..."
if [ "$ENVIRONMENT" == "production" ]; then
    docker-compose -f docker-compose.prod.yml up -d
else
    docker-compose up -d
fi

log_success "Containers started"

# Wait for services to be healthy
log_info "Waiting for services to be healthy..."
sleep 10

# Check backend health
log_info "Checking backend health..."
if [ "$ENVIRONMENT" == "production" ]; then
    max_attempts=30
    attempt=0
    while [ $attempt -lt $max_attempts ]; do
        if curl -f http://localhost/health > /dev/null 2>&1; then
            log_success "Backend is healthy"
            break
        fi
        attempt=$((attempt + 1))
        echo -n "."
        sleep 2
    done

    if [ $attempt -eq $max_attempts ]; then
        log_error "Backend health check failed"
        exit 1
    fi
else
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        log_success "Backend is healthy"
    else
        log_warning "Backend health check failed (this is expected for first deployment)"
    fi
fi

# Run database migrations (if needed)
log_info "Running database migrations..."
if [ "$ENVIRONMENT" == "production" ]; then
    docker-compose -f docker-compose.prod.yml exec -T backend alembic upgrade head || log_warning "Migration skipped"
else
    docker-compose exec -T backend alembic upgrade head || log_warning "Migration skipped"
fi

# Show running containers
log_info "Running containers:"
if [ "$ENVIRONMENT" == "production" ]; then
    docker-compose -f docker-compose.prod.yml ps
else
    docker-compose ps
fi

# Deployment complete
echo ""
log_success "========================================"
log_success "  Deployment completed successfully!   "
log_success "========================================"
echo ""

if [ "$ENVIRONMENT" == "production" ]; then
    log_info "Application URLs:"
    echo "  Frontend: https://yourdomain.com"
    echo "  Backend API: https://yourdomain.com/api"
    echo "  API Docs: https://yourdomain.com/docs"
    echo ""
    log_info "View logs:"
    echo "  docker-compose -f docker-compose.prod.yml logs -f"
else
    log_info "Application URLs:"
    echo "  Frontend: http://localhost:3000"
    echo "  Backend API: http://localhost:8000"
    echo "  API Docs: http://localhost:8000/docs"
    echo ""
    log_info "View logs:"
    echo "  docker-compose logs -f"
fi

echo ""
log_info "Useful commands:"
echo "  Stop all services:    docker-compose down"
echo "  View backend logs:    docker-compose logs -f backend"
echo "  View celery logs:     docker-compose logs -f celery_worker"
echo "  Database backup:      ./scripts/backup.sh"
echo "  Health check:         ./scripts/health_check.sh"
echo ""
