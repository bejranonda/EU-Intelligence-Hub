#!/bin/bash

###############################################################################
# Database Restore Script
# Restores PostgreSQL database from backup
###############################################################################

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check argument
if [ -z "$1" ]; then
    log_error "Backup file not specified"
    echo "Usage: ./restore.sh <backup_file.sql.gz>"
    echo ""
    echo "Available backups:"
    ls -lh ./backups/euint_backup_*.sql.gz 2>/dev/null || echo "  No backups found"
    exit 1
fi

BACKUP_FILE=$1

# Check if backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    log_error "Backup file not found: $BACKUP_FILE"
    exit 1
fi

log_warning "This will overwrite the current database!"
read -p "Are you sure you want to continue? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    log_info "Restore cancelled"
    exit 0
fi

# Check if docker-compose.prod.yml exists
if [ -f "docker-compose.prod.yml" ]; then
    COMPOSE_FILE="docker-compose.prod.yml"
else
    COMPOSE_FILE="docker-compose.yml"
fi

# Load environment variables
if [ -f ".env.production" ]; then
    export $(cat .env.production | grep -v '^#' | xargs)
elif [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

log_info "Starting database restore from: $BACKUP_FILE"

# Decompress if needed
if [[ $BACKUP_FILE == *.gz ]]; then
    log_info "Decompressing backup..."
    TEMP_FILE="${BACKUP_FILE%.gz}"
    gunzip -c "$BACKUP_FILE" > "$TEMP_FILE"
    SQL_FILE="$TEMP_FILE"
else
    SQL_FILE="$BACKUP_FILE"
fi

# Restore database
log_info "Restoring database..."
cat "$SQL_FILE" | docker-compose -f $COMPOSE_FILE exec -T postgres psql -U $POSTGRES_USER $POSTGRES_DB

# Clean up temp file
if [ -f "$TEMP_FILE" ]; then
    rm "$TEMP_FILE"
fi

log_success "Database restore complete!"
log_info "Please restart the application to apply changes"
