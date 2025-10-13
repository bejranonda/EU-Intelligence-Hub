# European News Intelligence Hub - Deployment Guide

## Prerequisites

### System Requirements
- Ubuntu 24 LTS (or similar Linux distribution)
- 4GB RAM minimum (8GB recommended)
- 20GB free disk space
- Docker 24.0+ and Docker Compose 2.0+

### Installing Docker

```bash
# Update package index
sudo apt-get update

# Install required packages
sudo apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Add Docker's official GPG key
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Set up Docker repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Add your user to docker group (to run docker without sudo)
sudo usermod -aG docker $USER

# Log out and log back in for group changes to take effect
# Or run: newgrp docker

# Verify installation
docker --version
docker compose version
```

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd euint
```

### 2. Configure Environment Variables

The `.env` file is already created with the Gemini API key. Review and update if needed:

```bash
nano .env
```

Important variables to review:
- `ADMIN_PASSWORD` - Change in production!
- `POSTGRES_PASSWORD` - Change in production!
- `SECRET_KEY` - Change in production!

### 3. Start All Services

```bash
./setup.sh
```

This script will:
- Check for Docker installation
- Build all Docker images
- Start PostgreSQL, Redis, Backend API, Celery workers, and Frontend
- Wait for all services to be healthy
- Display access URLs

### 4. Access the Application

Once setup is complete:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Interactive API Explorer**: http://localhost:8000/redoc

## Service Management

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres
docker-compose logs -f celery_worker
```

### Stop Services

```bash
docker-compose down
```

### Restart Services

```bash
docker-compose restart
```

### Rebuild Services

```bash
docker-compose up -d --build
```

### View Running Containers

```bash
docker-compose ps
```

## Database Management

### Access PostgreSQL

```bash
docker-compose exec postgres psql -U newsadmin -d news_intelligence
```

### Common PostgreSQL Commands

```sql
-- List all tables
\dt

-- Describe table structure
\d articles

-- View keywords
SELECT * FROM keywords;

-- View articles with sentiment
SELECT title, source_name, sentiment_overall FROM articles LIMIT 10;

-- Exit
\q
```

### Backup Database

```bash
docker-compose exec postgres pg_dump -U newsadmin news_intelligence > backup.sql
```

### Restore Database

```bash
cat backup.sql | docker-compose exec -T postgres psql -U newsadmin news_intelligence
```

## Running Tests

### Backend Tests

```bash
# Run all tests
docker-compose exec backend pytest

# Run with coverage
docker-compose exec backend pytest --cov=app --cov-report=html

# Run specific test file
docker-compose exec backend pytest app/tests/test_health.py

# Run specific test
docker-compose exec backend pytest app/tests/test_health.py::test_health_endpoint
```

### View Coverage Report

After running tests with coverage:

```bash
# Coverage report is generated in backend/htmlcov/index.html
# Open in browser to view detailed coverage
```

## Troubleshooting

### Services Won't Start

1. Check Docker is running:
   ```bash
   sudo systemctl status docker
   ```

2. Check port availability:
   ```bash
   sudo lsof -i :8000  # Backend
   sudo lsof -i :3000  # Frontend
   sudo lsof -i :5432  # PostgreSQL
   sudo lsof -i :6379  # Redis
   ```

3. View service logs:
   ```bash
   docker-compose logs backend
   docker-compose logs postgres
   ```

### Database Connection Issues

1. Ensure PostgreSQL is healthy:
   ```bash
   docker-compose exec postgres pg_isready -U newsadmin
   ```

2. Check database logs:
   ```bash
   docker-compose logs postgres
   ```

3. Restart database:
   ```bash
   docker-compose restart postgres
   ```

### Backend API Not Responding

1. Check backend logs:
   ```bash
   docker-compose logs backend
   ```

2. Verify backend is running:
   ```bash
   curl http://localhost:8000/health
   ```

3. Restart backend:
   ```bash
   docker-compose restart backend
   ```

### Frontend Not Loading

1. Check frontend logs:
   ```bash
   docker-compose logs frontend
   ```

2. Frontend takes ~30-60 seconds to start on first run (npm install)
3. Check if frontend container is running:
   ```bash
   docker-compose ps frontend
   ```

### Reset Everything

If things are completely broken, reset everything:

```bash
# Stop and remove all containers, networks, volumes
docker-compose down -v

# Remove all images
docker-compose down --rmi all

# Start fresh
./setup.sh
```

## Production Deployment

### Security Checklist

- [ ] Change `ADMIN_PASSWORD` to a strong password
- [ ] Change `POSTGRES_PASSWORD` to a strong password
- [ ] Generate a new `SECRET_KEY` (32+ random characters)
- [ ] Set `ENVIRONMENT=production`
- [ ] Set `DEBUG=false`
- [ ] Set up HTTPS with valid SSL certificate
- [ ] Configure firewall to only allow necessary ports
- [ ] Set up automated backups
- [ ] Configure monitoring and alerting

### SSL/HTTPS Setup

1. Obtain SSL certificate (Let's Encrypt recommended)
2. Place certificates in `docker/ssl/` directory
3. Update Nginx configuration to use certificates
4. Restart services

### Automated Backups

Add to crontab:

```bash
# Daily database backup at 2 AM
0 2 * * * cd /path/to/euint && docker-compose exec postgres pg_dump -U newsadmin news_intelligence | gzip > backups/db_$(date +\%Y\%m\%d).sql.gz
```

## Monitoring

### Check Service Health

```bash
# Backend health
curl http://localhost:8000/health

# View all service statuses
docker-compose ps
```

### Resource Usage

```bash
# View resource usage of all containers
docker stats

# View disk usage
docker system df
```

## Updates and Maintenance

### Update Application Code

```bash
git pull origin main
docker-compose up -d --build
```

### Update Dependencies

Backend:
```bash
# Update requirements.txt, then:
docker-compose build backend
docker-compose up -d backend
```

Frontend:
```bash
# Update package.json, then:
docker-compose build frontend
docker-compose up -d frontend
```

### Database Migrations

```bash
# Create new migration (after model changes)
docker-compose exec backend alembic revision --autogenerate -m "Description"

# Apply migrations
docker-compose exec backend alembic upgrade head

# View migration history
docker-compose exec backend alembic history
```

## Support

For issues or questions:
1. Check the logs: `docker-compose logs`
2. Review PROGRESS.md for current project state
3. Check TODO.md for known issues
4. Submit an issue on GitHub
