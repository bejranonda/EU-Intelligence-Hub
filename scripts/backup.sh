#!/bin/bash

###############################################################################
# Database Backup Script
# Creates timestamped backups of PostgreSQL database
###############################################################################

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
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

# Configuration
BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="euint_backup_${TIMESTAMP}.sql"
RETENTION_DAYS=30

# Create backup directory
mkdir -p $BACKUP_DIR

log_info "Starting database backup..."

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

# Perform backup
log_info "Creating backup: $BACKUP_FILE"
docker-compose -f $COMPOSE_FILE exec -T postgres pg_dump -U $POSTGRES_USER $POSTGRES_DB > "$BACKUP_DIR/$BACKUP_FILE"

# Compress backup
log_info "Compressing backup..."
gzip "$BACKUP_DIR/$BACKUP_FILE"
COMPRESSED_FILE="$BACKUP_FILE.gz"

log_success "Backup created: $BACKUP_DIR/$COMPRESSED_FILE"

# Calculate backup size
BACKUP_SIZE=$(du -h "$BACKUP_DIR/$COMPRESSED_FILE" | cut -f1)
log_info "Backup size: $BACKUP_SIZE"

# Clean up old backups
log_info "Cleaning up old backups (older than $RETENTION_DAYS days)..."
find $BACKUP_DIR -name "euint_backup_*.sql.gz" -type f -mtime +$RETENTION_DAYS -delete

# Count remaining backups
BACKUP_COUNT=$(ls -1 $BACKUP_DIR/euint_backup_*.sql.gz 2>/dev/null | wc -l)
log_info "Total backups: $BACKUP_COUNT"

log_success "Backup complete!"

# Optional: Upload to S3 (if configured)
if [ -n "$BACKUP_S3_BUCKET" ] && command -v aws &> /dev/null; then
    log_info "Uploading to S3..."
    aws s3 cp "$BACKUP_DIR/$COMPRESSED_FILE" "s3://$BACKUP_S3_BUCKET/backups/" && \
        log_success "Uploaded to S3" || \
        log_error "Failed to upload to S3"
fi
