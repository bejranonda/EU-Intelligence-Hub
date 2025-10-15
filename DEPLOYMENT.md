# European News Intelligence Hub - Deployment Guide

Complete guide for deploying the European News Intelligence Hub to production.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Production Deployment](#production-deployment)
- [SSL Configuration](#ssl-configuration)
- [Monitoring](#monitoring)
- [Backup & Restore](#backup--restore)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### Server Requirements

- **OS**: Ubuntu 24.04 LTS or later
- **RAM**: Minimum 4GB (8GB recommended)
- **Storage**: Minimum 20GB free space
- **CPU**: 2+ cores recommended

### Software Requirements

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose-plugin

# Verify installation
docker --version
docker compose version
```

## Quick Start

```bash
# Clone and deploy
git clone https://github.com/yourusername/euint.git
cd euint
cp .env.example .env
./deploy.sh dev
```

## Production Deployment

See full documentation in the file for detailed steps including:
- Environment configuration
- SSL setup
- Monitoring
- Backup procedures
- Troubleshooting guides

## Quick Commands

```bash
# Deploy
./deploy.sh production

# Health check
./scripts/health_check.sh

# Backup
./scripts/backup.sh

# SSL setup
./setup-ssl.sh yourdomain.com admin@yourdomain.com
```
