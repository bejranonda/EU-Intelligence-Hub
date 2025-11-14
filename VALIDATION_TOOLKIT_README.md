# EU Intelligence Hub - Validation Toolkit

**Complete diagnostic and troubleshooting suite for project validation**

---

## 🎯 Purpose

This toolkit helps you validate that the EU Intelligence Hub is properly configured and diagnose why keyword searches might return no results.

---

## 📦 Tools Included

### 1. **validate_project.py** - Complete Project Validation
Comprehensive validation of all project components.

**What it checks:**
- ✅ Environment configuration (.env file)
- ✅ Python 3.11+ installation
- ✅ Node.js 18+ installation
- ✅ Docker availability
- ✅ Port availability (5432, 6379, 8000, 3000, etc.)
- ✅ PostgreSQL connection
- ✅ Redis connection
- ✅ Backend API health
- ✅ Gemini API key validity
- ✅ File structure integrity

**Usage:**
```bash
python3 validate_project.py
```

**When to run:**
- Before starting the project for the first time
- After any configuration changes
- When troubleshooting issues

---

### 2. **test_gemini_api.py** - Gemini API Connection Test
Tests if the Gemini API key is properly configured and working.

**What it checks:**
- ✅ .env file exists
- ✅ GEMINI_API_KEY is set
- ✅ API key is not a placeholder
- ✅ google-generativeai package installed
- ✅ API key is valid (makes test request)
- ✅ News research capability works

**Usage:**
```bash
python3 test_gemini_api.py
```

**When to run:**
- After setting up Gemini API key
- When scraper returns no articles
- When seeing authentication errors in logs

**Interactive:** Optionally tests the actual scraper implementation

---

### 3. **check_system_health.py** - Post-Startup Health Check
Verifies all services are running and healthy after Docker startup.

**What it checks:**
- ✅ Docker services status (postgres, redis, backend, etc.)
- ✅ Backend API health endpoints
- ✅ Database connection and health
- ✅ Redis connection
- ✅ Database content (keywords and articles count)
- ✅ Celery workers status
- ✅ Frontend accessibility

**Usage:**
```bash
# After starting services
docker compose up -d

# Wait a minute, then check health
python3 check_system_health.py
```

**When to run:**
- After `docker compose up -d`
- When services seem unresponsive
- To verify database has data

---

## 📚 Documentation

### 4. **PROJECT_VALIDATION_REPORT.md**
Detailed validation report with root cause analysis and recovery plan.

**Contents:**
- Executive summary of validation results
- Critical issues breakdown
- Why keyword search returns no results (root cause)
- Step-by-step recovery plan
- Manual setup guide (without Docker)
- Troubleshooting common issues

**When to read:**
- First time setting up the project
- When validation scripts show errors
- For comprehensive understanding of requirements

---

### 5. **QUICK_FIX_GUIDE.md**
Condensed quick-start guide to get the project working fast.

**Contents:**
- Critical fix (Gemini API key)
- Docker installation
- Service startup
- Verification steps
- Quick troubleshooting

**When to read:**
- Want to get started quickly (5-10 minutes)
- Already familiar with Docker
- Just need the essentials

---

### 6. **DATA_FLOW_EXPLAINED.md**
Complete data flow documentation explaining how the system works.

**Contents:**
- Why keyword search returns no results (deep dive)
- Complete data flow diagrams
- How articles get into the database (3 methods)
- Critical dependencies chain
- Code path for search queries
- Debugging decision tree
- Expected timelines

**When to read:**
- Want to understand the system architecture
- Debugging complex issues
- Contributing to the codebase
- Understanding Celery tasks

---

### 7. **TROUBLESHOOTING_PLAYBOOK.md**
Quick reference guide for diagnosing and fixing common issues.

**Contents:**
- Quick diagnostic commands
- Issue-specific troubleshooting guides
- Database debugging
- Celery task debugging
- Emergency reset procedures
- Log message interpretations
- Pre-flight checklist

**When to read:**
- Something is broken
- Need quick fixes
- Understanding error messages
- Want command references

---

## 🚀 Quick Start Workflow

### First Time Setup

```bash
# 1. Clone and enter project
cd EU-Intelligence-Hub

# 2. Run full validation
python3 validate_project.py

# 3. Fix critical issues (usually Gemini API key)
# Edit .env and add your Gemini API key

# 4. Test Gemini API
python3 test_gemini_api.py

# 5. Start services
docker compose up -d

# 6. Wait for services to start (1-2 minutes)
sleep 120

# 7. Check system health
python3 check_system_health.py

# 8. If all checks pass, access the app!
# Frontend: http://localhost:3000
# Backend: http://localhost:8000/docs
```

### When Things Go Wrong

```bash
# Run diagnostics
python3 validate_project.py > validation.txt
python3 check_system_health.py > health.txt

# Check what failed
cat validation.txt
cat health.txt

# Fix based on recommendations
# Then re-run diagnostics
```

---

## 🔍 Diagnostic Decision Tree

```
Start: Keyword search returns no results
│
├─> Run: python3 check_system_health.py
│
├─> Are services running?
│   ├─ NO → docker compose up -d
│   └─ YES → Continue
│
├─> Are articles in database?
│   ├─ NO → Continue to check why
│   └─ YES → Check search terms match content
│
├─> Run: python3 test_gemini_api.py
│
├─> Is Gemini API working?
│   ├─ NO → Fix API key in .env
│   └─ YES → Continue
│
├─> Check Celery logs:
│   docker compose logs celery_worker
│
├─> Are tasks processing?
│   ├─ NO → docker compose restart celery_worker
│   └─ YES → Wait for articles (5-15 min)
│
└─> Read: DATA_FLOW_EXPLAINED.md
    for complete understanding
```

---

## 📊 Tools Comparison

| Tool | Purpose | When to Use | Duration |
|------|---------|-------------|----------|
| `validate_project.py` | Complete validation | Initial setup, config changes | 1-2 min |
| `test_gemini_api.py` | Test Gemini API | API key setup, scraper issues | 30 sec |
| `check_system_health.py` | Post-startup check | After docker compose up | 30 sec |
| `PROJECT_VALIDATION_REPORT.md` | Detailed docs | Understanding issues | 10 min read |
| `QUICK_FIX_GUIDE.md` | Quick start | Fast setup | 2 min read |
| `DATA_FLOW_EXPLAINED.md` | Architecture | Understanding system | 15 min read |
| `TROUBLESHOOTING_PLAYBOOK.md` | Quick reference | Specific issues | 5 min read |

---

## 🎓 Understanding the Validation Results

### ✅ All Green (Success)

```
✓ All checks passed!
You can start the application with: docker compose up -d
```

**Meaning:** Everything is configured correctly, proceed with startup.

---

### ⚠️ Warnings (Non-Critical)

```
⚠ Warnings: 3
  • No virtual environment detected
  • Frontend dependencies not installed
  • Docker containers not running
```

**Meaning:** System can work but has minor issues. If using Docker, some warnings are expected.

---

### ❌ Critical Issues

```
✗ Critical Issues: 2
  • GEMINI_API_KEY not configured
  • Backend API not accessible
```

**Meaning:** Fix these before the system can work. Follow recommended actions.

---

## 🆘 Common Scenarios

### Scenario 1: Fresh Install

**Symptoms:** Never run the project before

**Solution:**
1. Run `python3 validate_project.py`
2. Fix Gemini API key
3. Run `python3 test_gemini_api.py`
4. Start Docker: `docker compose up -d`
5. Run `python3 check_system_health.py`
6. Access http://localhost:3000

**Time:** 10-15 minutes

---

### Scenario 2: Search Returns Nothing

**Symptoms:** Application works but search is empty

**Solution:**
1. Run `python3 check_system_health.py`
2. Check article count in output
3. If 0, read DATA_FLOW_EXPLAINED.md
4. Add/approve keywords
5. Wait 5-15 minutes
6. Try search again

**Time:** 15-20 minutes

---

### Scenario 3: Services Won't Start

**Symptoms:** `docker compose up` fails

**Solution:**
1. Check Docker is running
2. Check port conflicts: `sudo lsof -i :5432`
3. Read TROUBLESHOOTING_PLAYBOOK.md → "Docker services won't start"
4. Follow fixes for your specific error

**Time:** 5-10 minutes

---

### Scenario 4: After Changing Config

**Symptoms:** Modified .env or docker-compose.yml

**Solution:**
1. Run `python3 validate_project.py`
2. Restart services: `docker compose restart`
3. Run `python3 check_system_health.py`
4. Verify changes took effect

**Time:** 2-3 minutes

---

## 📝 Files Reference

| File | Purpose | Type | Size |
|------|---------|------|------|
| `validate_project.py` | Main validation script | Python | ~600 lines |
| `test_gemini_api.py` | Gemini API tester | Python | ~300 lines |
| `check_system_health.py` | Health checker | Python | ~500 lines |
| `PROJECT_VALIDATION_REPORT.md` | Detailed report | Docs | ~800 lines |
| `QUICK_FIX_GUIDE.md` | Quick start | Docs | ~200 lines |
| `DATA_FLOW_EXPLAINED.md` | Architecture docs | Docs | ~600 lines |
| `TROUBLESHOOTING_PLAYBOOK.md` | Reference guide | Docs | ~500 lines |

**Total:** ~3,500 lines of validation code and documentation

---

## 🔗 Navigation Guide

**Starting fresh?**
→ Start with QUICK_FIX_GUIDE.md

**Want full details?**
→ Read PROJECT_VALIDATION_REPORT.md

**Search returns nothing?**
→ Read DATA_FLOW_EXPLAINED.md

**Something broken?**
→ Use TROUBLESHOOTING_PLAYBOOK.md

**Need to check config?**
→ Run validate_project.py

**Need to test API key?**
→ Run test_gemini_api.py

**Services just started?**
→ Run check_system_health.py

---

## 🎯 Success Criteria

Your system is fully operational when:

1. ✅ `validate_project.py` shows all green
2. ✅ `test_gemini_api.py` passes all tests
3. ✅ `check_system_health.py` reports "ALL SYSTEMS OPERATIONAL"
4. ✅ Frontend loads at http://localhost:3000
5. ✅ Backend API docs at http://localhost:8000/docs
6. ✅ Can create and approve keywords
7. ✅ Articles appear in database
8. ✅ Search returns results

---

## 💡 Tips

**Save time:**
```bash
# Create alias for common checks
alias validate='python3 validate_project.py'
alias healthcheck='python3 check_system_health.py'
alias testapi='python3 test_gemini_api.py'
```

**Monitor continuously:**
```bash
# Watch Celery worker process articles
docker compose logs -f celery_worker

# Watch all services
docker compose logs -f
```

**Quick diagnostics:**
```bash
# One-liner to check everything
python3 validate_project.py && python3 check_system_health.py
```

---

## 📞 Support

If you've run all diagnostic tools and still have issues:

1. Collect diagnostic output:
   ```bash
   python3 validate_project.py > diagnostics.txt
   python3 check_system_health.py >> diagnostics.txt
   docker compose logs > docker_logs.txt
   ```

2. Check the documentation:
   - TROUBLESHOOTING_PLAYBOOK.md for specific issues
   - DATA_FLOW_EXPLAINED.md for architecture understanding
   - PROJECT_VALIDATION_REPORT.md for comprehensive fixes

3. Review logs for error patterns:
   ```bash
   docker compose logs backend | grep -i error
   docker compose logs celery_worker | grep -i error
   ```

---

## 🎊 Summary

This validation toolkit provides:

- ✅ **3 Python diagnostic scripts** for automated validation
- ✅ **4 comprehensive documentation files** covering all aspects
- ✅ **Complete coverage** of common issues and fixes
- ✅ **Step-by-step guides** for all scenarios
- ✅ **Quick reference** commands and troubleshooting

**Total Time Investment:**
- Setup + validation: 15-20 minutes
- Reading docs (optional): 30-45 minutes
- Understanding system: 1-2 hours (deep dive)

**Result:**
Fully validated, properly configured, and working EU Intelligence Hub instance with comprehensive understanding of how it works.

---

**Created:** 2025-11-14
**Version:** 1.0
**Author:** EU Intelligence Hub Validation Team
