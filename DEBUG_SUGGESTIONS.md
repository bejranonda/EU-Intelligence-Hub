# Debugging Suggestion Submission Error

**Issue**: "Failed to submit suggestion. Please try again." when submitting keywords

**Error Location**: POST /api/suggestions/

---

## Step 1: Verify Backend is Running

```bash
# Check if backend container is running
docker compose ps backend

# Expected output: Container should show "Up" status
# If not running, start it:
docker compose up -d backend
```

---

## Step 2: Check Backend Logs for Errors

```bash
# View backend logs for the last 50 lines
docker compose logs backend | tail -50

# Look for:
# - ImportError (missing dependencies)
# - AttributeError (missing model fields)
# - Database connection errors
# - Type validation errors
```

---

## Step 3: Test the API Endpoint Directly

```bash
# Test if the endpoint exists and is accessible
curl -X GET http://localhost:8000/api/suggestions/ -v

# Expected: Should return JSON with suggestions list
# If error: Check logs for details
```

---

## Step 4: Test Suggestion Submission

```bash
# Test POST endpoint with a sample suggestion
curl -X POST http://localhost:8000/api/suggestions/ \
  -H "Content-Type: application/json" \
  -d '{
    "keyword_en": "Test Keyword",
    "category": "test",
    "reason": "Testing the endpoint",
    "contact_email": "test@example.com"
  }' \
  -v

# Expected: HTTP 200 with success response
# If error: Response will show the error detail
```

---

## Step 5: Check Frontend Console

```
1. Open browser DevTools (F12)
2. Go to Console tab
3. Try submitting the form again
4. Look for error messages like:
   - "Failed to submit suggestion: ..."
   - "API Error: ..."
   - Network errors

5. Go to Network tab
6. Look for the POST request to /api/suggestions/
7. Check:
   - Status code (200 = OK, 4xx = client error, 5xx = server error)
   - Response body (should show error detail)
```

---

## Common Issues & Solutions

### Issue 1: Backend Container Not Running
**Symptoms**: Connection refused errors
**Solution**:
```bash
docker compose up -d backend
docker compose logs backend -f
```

### Issue 2: Database Not Initialized
**Symptoms**: "table keyword_suggestions does not exist"
**Solution**:
```bash
# Force database reinitialization
docker compose exec postgres psql -U euint_user -d euint_dev -f /docker-entrypoint-initdb.d/init_db.sql
# Or restart the entire stack
docker compose down
docker compose up -d
```

### Issue 3: CORS Error
**Symptoms**: "Access to XMLHttpRequest blocked by CORS policy"
**Solution**: Check `app/main.py` CORS configuration
```python
cors_origins = [
    "http://localhost:3000",
    "http://frontend:3000"
]
# Make sure localhost:3000 is included
```

### Issue 4: API Client Not Using Correct Base URL
**Symptoms**: 404 errors on /api/suggestions/
**Solution**: Check environment variable
```bash
# In frontend .env or check console
echo $VITE_API_URL
# Should be: http://localhost:8000
```

---

## Verification Steps

Run this checklist:

- [ ] Docker container `euint_backend` is running
- [ ] Docker container `euint_postgres` is running
- [ ] Docker container `euint_redis` is running
- [ ] Backend is accessible: `curl http://localhost:8000/health`
- [ ] API Docs work: Open http://localhost:8000/docs
- [ ] Database has keyword_suggestions table
- [ ] Frontend is accessible: http://localhost:3000
- [ ] Browser console shows no errors

---

## Test Script

If you want to automate debugging, create a test file:

```bash
#!/bin/bash

echo "=== EU Intelligence Hub - Suggestion API Debug ==="

echo -e "\n1. Checking containers..."
docker compose ps | grep -E "backend|postgres|redis"

echo -e "\n2. Testing backend health..."
curl -s http://localhost:8000/health | jq .

echo -e "\n3. Getting existing suggestions..."
curl -s http://localhost:8000/api/suggestions/ | jq '.total'

echo -e "\n4. Submitting test suggestion..."
curl -X POST http://localhost:8000/api/suggestions/ \
  -H "Content-Type: application/json" \
  -d '{
    "keyword_en": "Debug Test",
    "category": "test",
    "reason": "Debugging suggestion endpoint"
  }' | jq .

echo -e "\n=== Debug Complete ==="
```

Save this as `debug.sh` and run: `bash debug.sh`

---

## If Issue Persists

1. Check the actual error response:
   - Open DevTools Network tab
   - Resubmit form
   - Click on POST /api/suggestions/ request
   - Check "Response" tab for error details

2. Share the error response:
   ```json
   {
     "detail": "Error message here"
   }
   ```

3. Check backend logs:
   ```bash
   docker compose logs backend | grep ERROR
   ```

4. Look for these specific errors:
   - `KeyError`: Missing field in model
   - `IntegrityError`: Database constraint violation
   - `ValidationError`: Pydantic validation failed
   - `OperationalError`: Database connection issue

---

## Recovery

If you need to reset and start fresh:

```bash
# Stop everything
docker compose down

# Remove database volume (will lose data)
docker volume rm euint_postgres_data

# Rebuild and restart
docker compose up -d

# Check if it's working now
curl http://localhost:8000/api/suggestions/
```

---

For additional help, check:
- README.md - General setup
- ERROR_LOGGING.md - Log analysis guide
- TROUBLESHOOTING_KEYWORDS.md - Common issues
