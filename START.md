# 🚀 START HERE - Quick Guide

## ⚡ Three Steps to Get Running

### 1. Install (5 minutes)
```bash
sudo bash install-all.sh
```

### 2. Log Out & Back In (REQUIRED!)
```bash
exit  # Then log back in
```

### 3. Start Everything (10-15 minutes first time)
```bash
nano .env  # Update GEMINI_API_KEY
./setup.sh
```

**Done!** Open http://localhost:3000

---

## 📚 Full Documentation

Need detailed instructions? See **[INSTALLATION.md](INSTALLATION.md)**

---

## 🆘 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| "docker: command not found" | Run `sudo bash install-all.sh` |
| "Permission denied" with docker | Log out and back in |
| Services won't start | `docker compose logs backend` |

Full troubleshooting in [INSTALLATION.md](INSTALLATION.md)

---

## ✅ You'll Know It Worked When:

- ✅ http://localhost:3000 loads
- ✅ http://localhost:8000/docs shows API
- ✅ `docker compose ps` shows 6 services running
- ✅ Tests pass: `docker compose exec backend pytest tests/ -v`

---

**For complete instructions, read [INSTALLATION.md](INSTALLATION.md)** 📖
