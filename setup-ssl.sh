#!/bin/bash

###############################################################################
# SSL Setup Script using Let's Encrypt
#
# Usage:
#   ./setup-ssl.sh yourdomain.com admin@yourdomain.com
###############################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
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

# Check arguments
if [ -z "$1" ] || [ -z "$2" ]; then
    log_error "Domain and email not provided"
    echo "Usage: ./setup-ssl.sh <domain> <email>"
    echo "Example: ./setup-ssl.sh example.com admin@example.com"
    exit 1
fi

DOMAIN=$1
EMAIL=$2

log_info "Setting up SSL for domain: $DOMAIN"
log_info "Email: $EMAIL"

# Create directories
log_info "Creating directories..."
mkdir -p certbot/conf
mkdir -p certbot/www

# Update nginx configuration with domain
log_info "Updating nginx configuration..."
sed -i "s/yourdomain.com/$DOMAIN/g" nginx/conf.d/app.conf

# Start nginx for Let's Encrypt challenge
log_info "Starting nginx..."
docker-compose -f docker-compose.prod.yml up -d nginx

# Wait for nginx to be ready
sleep 5

# Obtain SSL certificate
log_info "Obtaining SSL certificate from Let's Encrypt..."
docker-compose -f docker-compose.prod.yml run --rm certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    -d $DOMAIN

if [ $? -eq 0 ]; then
    log_success "SSL certificate obtained successfully!"

    # Reload nginx
    log_info "Reloading nginx..."
    docker-compose -f docker-compose.prod.yml exec nginx nginx -s reload

    log_success "SSL setup complete!"
    echo ""
    log_info "Your site is now available at: https://$DOMAIN"
    echo ""
    log_info "Certificate will auto-renew. To manually renew:"
    echo "  docker-compose -f docker-compose.prod.yml run --rm certbot renew"
else
    log_error "Failed to obtain SSL certificate"
    log_error "Please check:"
    echo "  1. Domain DNS is pointing to this server"
    echo "  2. Port 80 is accessible from the internet"
    echo "  3. No firewall is blocking port 80"
    exit 1
fi
