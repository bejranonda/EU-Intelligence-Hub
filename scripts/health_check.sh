#!/bin/bash

###############################################################################
# Health Check Script
# Checks the health of all services
###############################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
}

echo "========================================"
echo "  European News Intelligence Hub"
echo "  Health Check"
echo "========================================"
echo ""

# Check if docker-compose.prod.yml exists
if [ -f "docker-compose.prod.yml" ]; then
    COMPOSE_FILE="docker-compose.prod.yml"
    ENVIRONMENT="Production"
else
    COMPOSE_FILE="docker-compose.yml"
    ENVIRONMENT="Development"
fi

log_info "Environment: $ENVIRONMENT"
echo ""

# Check Docker
log_info "Checking Docker..."
if command -v docker &> /dev/null; then
    log_success "Docker is installed"
else
    log_error "Docker is not installed"
    exit 1
fi

# Check running containers
log_info "Checking containers..."
CONTAINERS=$(docker-compose -f $COMPOSE_FILE ps -q)

if [ -z "$CONTAINERS" ]; then
    log_error "No containers are running"
    exit 1
else
    log_success "Containers are running"
fi

# Check PostgreSQL
log_info "Checking PostgreSQL..."
if docker-compose -f $COMPOSE_FILE exec -T postgres pg_isready > /dev/null 2>&1; then
    log_success "PostgreSQL is healthy"
else
    log_error "PostgreSQL is not healthy"
fi

# Check Redis
log_info "Checking Redis..."
if docker-compose -f $COMPOSE_FILE exec -T redis redis-cli ping | grep -q "PONG"; then
    log_success "Redis is healthy"
else
    log_error "Redis is not healthy"
fi

# Check Backend API
log_info "Checking Backend API..."
if [ "$COMPOSE_FILE" == "docker-compose.prod.yml" ]; then
    API_URL="http://localhost/health"
else
    API_URL="http://localhost:8000/health"
fi

if curl -f -s $API_URL > /dev/null 2>&1; then
    log_success "Backend API is healthy"

    # Get detailed health info
    HEALTH_DATA=$(curl -s $API_URL)
    echo "  Response: $HEALTH_DATA"
else
    log_error "Backend API is not healthy"
fi

# Check Frontend
log_info "Checking Frontend..."
if [ "$COMPOSE_FILE" == "docker-compose.prod.yml" ]; then
    FRONTEND_URL="http://localhost/"
else
    FRONTEND_URL="http://localhost:3000/"
fi

if curl -f -s -o /dev/null $FRONTEND_URL; then
    log_success "Frontend is accessible"
else
    log_error "Frontend is not accessible"
fi

# Check Celery Worker
log_info "Checking Celery Worker..."
if docker-compose -f $COMPOSE_FILE ps | grep -q "celery_worker.*Up"; then
    log_success "Celery Worker is running"
else
    log_warning "Celery Worker is not running"
fi

# Check Celery Beat
log_info "Checking Celery Beat..."
if docker-compose -f $COMPOSE_FILE ps | grep -q "celery_beat.*Up"; then
    log_success "Celery Beat is running"
else
    log_warning "Celery Beat is not running"
fi

# Check disk space
log_info "Checking disk space..."
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -lt 80 ]; then
    log_success "Disk space is healthy ($DISK_USAGE% used)"
elif [ "$DISK_USAGE" -lt 90 ]; then
    log_warning "Disk space is getting low ($DISK_USAGE% used)"
else
    log_error "Disk space is critically low ($DISK_USAGE% used)"
fi

# Check memory
log_info "Checking memory..."
MEMORY_USAGE=$(free | awk 'NR==2 {printf "%.0f", $3/$2 * 100}')
if [ "$MEMORY_USAGE" -lt 80 ]; then
    log_success "Memory usage is healthy ($MEMORY_USAGE% used)"
elif [ "$MEMORY_USAGE" -lt 90 ]; then
    log_warning "Memory usage is high ($MEMORY_USAGE% used)"
else
    log_error "Memory usage is critically high ($MEMORY_USAGE% used)"
fi

echo ""
echo "========================================"
echo "  Health Check Complete"
echo "========================================"
