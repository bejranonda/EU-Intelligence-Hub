# 🚀 Installation Guide - European News Intelligence Hub

Complete guide to install and run your application in under 30 minutes.

---

## ⚡ Quick Start (4 Commands)

```bash
# 1. Install all software
cd /home/payas/euint
sudo bash install-all.sh

# 2. Log out and log back in (REQUIRED!)
exit

# 3. Update API key
nano .env  # Change GEMINI_API_KEY to your key

# 4. Start everything
./setup.sh

# Done! Open http://localhost:3000
```

---

## 📋 Prerequisites

- **OS**: Ubuntu 20.04+ or Debian 10+ (You have: Ubuntu 24.04 ✅)
- **RAM**: 4GB minimum (8GB recommended)
- **Disk**: 10GB free space
- **Internet**: Active connection
- **Access**: Sudo/admin privileges

Check your system:
```bash
df -h        # Check disk space (need 10GB+)
free -h      # Check RAM (need 4GB+)
```

---

## 📖 Step-by-Step Installation

### Step 1: Install All Software (5 minutes)

Run the automated installation script:

```bash
cd /home/payas/euint
sudo bash install-all.sh
```

**What it installs:**
- ✅ Docker Engine & Docker Compose
- ✅ Python 3 & pip (if not installed)
- ✅ Node.js & npm (if not installed)
- ✅ Git, curl, wget, and build tools
- ✅ Development tools (nano, vim, htop)

**Expected output:**
```
================================================
✅ Installation Complete!
================================================

Installed/Verified:
  ✅ Git
  ✅ Curl & Wget
  ✅ Python 3 & pip
  ✅ Node.js & npm
  ✅ Docker Engine
  ✅ Docker Compose
  ✅ Development tools

⚠️  IMPORTANT: Log out and log back in
```

### Step 2: Log Out and Log Back In (CRITICAL!)

After installation, you **MUST** log out and log back in for Docker permissions to work.

**Option A**: Log out and log back in
```bash
exit  # Close terminal, then open new one
```

**Option B**: Restart your computer
```bash
sudo reboot
```

**Option C**: Try this (may not always work)
```bash
newgrp docker
```

### Step 3: Verify Installation (30 seconds)

After logging back in, verify everything works:

```bash
# Check Docker
docker --version
# Should show: Docker version 24.0.x

# Check Docker Compose
docker compose version
# Should show: Docker Compose version v2.x.x

# Test Docker works WITHOUT sudo
docker ps
# Should show empty list (no error)
```

If you get "permission denied", you didn't log out/in. Do it now!

### Step 4: Get Gemini API Key (1 minute)

1. Visit: https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy the API key

**IMPORTANT**: The current key in .env appears to be exposed. Get a new one!

### Step 5: Update Environment File (1 minute)

```bash
cd /home/payas/euint
nano .env
```

Find this line:
```env
GEMINI_API_KEY=AIzaSyAvmSxCYB8LVJvYcumtzZogoU4aQEkWCAo
```

Replace with your new key:
```env
GEMINI_API_KEY=your_actual_api_key_here
```

**Save**: Press `Ctrl+X`, then `Y`, then `Enter`

### Step 6: Start the Application (10-15 minutes first time)

```bash
chmod +x setup.sh
./setup.sh
```

**What happens:**
1. Checks Docker is installed ✅
2. Stops any existing containers
3. Builds Docker images (5-10 minutes first time)
4. Starts 6 services:
   - PostgreSQL database
   - Redis cache
   - FastAPI backend (port 8000)
   - React frontend (port 3000)
   - Celery worker (background tasks)
   - Celery beat (scheduler)
5. Initializes database
6. Waits for all services to be healthy

**Expected output:**
```
✅ All services are running!
================================================

Access the application:
  Frontend:  http://localhost:3000
  Backend:   http://localhost:8000
  API Docs:  http://localhost:8000/docs
```

### Step 7: Verify Everything Works (2 minutes)

**Test Frontend:**
```bash
# Open in browser (or use curl)
curl http://localhost:3000
```

**Test Backend:**
```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy"}
```

**Run Tests:**
```bash
docker compose exec backend pytest tests/ -v
```

Expected: **49 tests pass** with >80% coverage ✅

**Check Services:**
```bash
docker compose ps
```

Should show 6 services as "running":
- euint-postgres-1
- euint-redis-1
- euint-backend-1
- euint-frontend-1
- euint-celery_worker-1
- euint-celery_beat-1

---

## 🎯 You're Done!

Open your browser:
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs

Try searching for "Thailand" to see the app in action!

---

## 🔧 Daily Usage

### Start Services
```bash
cd /home/payas/euint
docker compose up -d
```

### Stop Services
```bash
docker compose down
```

### View Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f frontend
```

### Check Status
```bash
docker compose ps
```

### Restart a Service
```bash
docker compose restart backend
```

### Run Tests
```bash
docker compose exec backend pytest tests/ -v
```

### Access Database
```bash
docker compose exec postgres psql -U euint_user -d euint_dev
```

---

## 🐛 Troubleshooting

### "docker: command not found"

**Problem**: Docker not installed or not in PATH

**Solution**:
```bash
sudo bash install-all.sh
# Then log out and back in
```

### "Permission denied" when running docker

**Problem**: User not in docker group

**Solution**:
```bash
# Add yourself to docker group
sudo usermod -aG docker $USER

# Then MUST log out and back in
exit
```

### "Port already in use" (3000 or 8000)

**Problem**: Another application using the port

**Solution**:
```bash
# Find what's using the port
sudo lsof -i :3000
sudo lsof -i :8000

# Kill the process
sudo kill -9 <PID>

# Or change ports in docker-compose.yml
```

### Services fail to start

**Problem**: Container startup errors

**Solution**:
```bash
# Check logs
docker compose logs backend
docker compose logs postgres

# Try full rebuild
docker compose down -v
docker compose up -d --build
```

### "Cannot connect to Docker daemon"

**Problem**: Docker service not running

**Solution**:
```bash
# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Check status
sudo systemctl status docker
```

### Tests fail

**Problem**: Services not ready or database issues

**Solution**:
```bash
# Check all services running
docker compose ps

# Check backend logs
docker compose logs backend

# Restart services
docker compose restart backend
```

### Out of disk space

**Problem**: Not enough space for Docker images

**Solution**:
```bash
# Check disk space
df -h

# Clean Docker
docker system prune -a

# Clean apt cache
sudo apt-get clean
```

### Not enough memory

**Problem**: System running out of RAM

**Solution**:
```bash
# Check memory
free -h

# Stop other applications
# Or increase system RAM
```

---

## ⏱️ Time Estimates

| Task | First Time | Subsequent |
|------|------------|------------|
| Install software | 5 min | - |
| Log out/in | 1 min | - |
| Update .env | 1 min | - |
| Run setup.sh | 10-15 min | 30 sec |
| Verify | 2 min | 10 sec |
| **TOTAL** | **19-24 min** | **40 sec** |

---

## 📊 What You're Running

### Architecture
```
Browser → Frontend (React) → Backend (FastAPI) → PostgreSQL
                           ↓
                         Redis ← Celery Workers
```

### Services
1. **Frontend** (port 3000): React 18 + TypeScript + Tailwind CSS
2. **Backend** (port 8000): Python FastAPI with 15+ REST APIs
3. **PostgreSQL** (port 5432): Database with pgvector extension
4. **Redis** (port 6379): Caching and task queue
5. **Celery Worker**: Background jobs (hourly news scraping)
6. **Celery Beat**: Task scheduler

### Technologies
- **Frontend**: React, TypeScript, Tailwind, shadcn/ui, React Flow, Recharts
- **Backend**: Python, FastAPI, SQLAlchemy, Pydantic
- **AI/ML**: Google Gemini, VADER, spaCy, Sentence Transformers
- **Infrastructure**: Docker, PostgreSQL, Redis, Nginx

---

## 🎓 Next Steps

### After Installation

1. **Explore the application**:
   - Search for keywords
   - View sentiment analysis
   - Check mind map visualizations
   - Upload a document

2. **Read the documentation**:
   - [README.md](README.md) - Project overview
   - [PROGRESS.md](PROGRESS.md) - What's been built
   - [TODO.md](TODO.md) - Future plans

3. **Start developing**:
   - Edit `backend/app/` for Python changes
   - Edit `frontend/src/` for React changes
   - Changes auto-reload!

4. **Complete your portfolio**:
   - Take 4 screenshots
   - Record demo GIF
   - Update README contact info
   - See [docs/CHECKLIST.md](docs/CHECKLIST.md)

---

## ✅ Installation Checklist

- [ ] System has 4GB+ RAM and 10GB+ disk
- [ ] Run `sudo bash install-all.sh`
- [ ] See "✅ Installation Complete!"
- [ ] Log out and log back in
- [ ] Verify `docker --version` works
- [ ] Verify `docker ps` works (no sudo)
- [ ] Get Gemini API key from https://makersuite.google.com/app/apikey
- [ ] Update GEMINI_API_KEY in .env
- [ ] Run `./setup.sh`
- [ ] See "✅ All services are running!"
- [ ] Open http://localhost:3000 (frontend loads)
- [ ] Open http://localhost:8000/docs (API docs load)
- [ ] Run `docker compose exec backend pytest tests/ -v`
- [ ] See 49 tests pass
- [ ] Search for "Thailand" in frontend
- [ ] All 6 services running: `docker compose ps`

**All done? 🎉 Congratulations!**

---

## 🆘 Getting Help

If something doesn't work:

1. **Check logs**: `docker compose logs -f`
2. **Check this guide**: See Troubleshooting section above
3. **Verify system**: `df -h` (disk) and `free -h` (memory)
4. **Full rebuild**: `docker compose down -v && docker compose up -d --build`

---

## 📚 Additional Documentation

- **[README.md](README.md)** - Project overview (portfolio-ready)
- **[PROGRESS.md](PROGRESS.md)** - Development history (5 phases completed)
- **[TODO.md](TODO.md)** - Current tasks and roadmap
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Production deployment guide
- **[SECURITY.md](SECURITY.md)** - Security best practices
- **[docs/CHECKLIST.md](docs/CHECKLIST.md)** - README completion tasks

---

**Last Updated**: 2025-10-15
**Estimated Install Time**: 19-24 minutes
**Support**: See Troubleshooting section above
