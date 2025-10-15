# 🔧 Fix Docker Permission Error

## The Error You're Seeing

```
permission denied while trying to connect to the Docker daemon socket
```

This means you're not in the docker group yet.

---

## ⚡ Quick Fix (3 Options)

### Option 1: Run the Fix Script (Easiest)

```bash
sudo bash fix-docker-permissions.sh
```

Then **log out and log back in** (or restart).

### Option 2: Manual Fix

```bash
# Add yourself to docker group
sudo usermod -aG docker $USER

# Log out and log back in
exit
```

### Option 3: Temporary Fix (For Testing Only)

```bash
# This applies the group for current shell only
newgrp docker

# Then run setup
./setup.sh
```

**Note**: Option 3 may not always work. Options 1 or 2 are more reliable.

---

## ✅ Verify It's Fixed

After logging back in:

```bash
# Check you're in docker group
groups | grep docker
# Should show: ... docker ...

# Test docker works WITHOUT sudo
docker ps
# Should show empty list (no error)

# Now run setup
./setup.sh
```

---

## 🎯 Complete Installation Steps

If you haven't run the installation yet:

```bash
# 1. Install Docker
sudo bash install-all.sh

# 2. Fix permissions (if needed)
sudo bash fix-docker-permissions.sh

# 3. LOG OUT AND LOG BACK IN (critical!)
exit

# 4. After logging back in, verify
docker ps

# 5. Update API key
nano .env  # Change GEMINI_API_KEY

# 6. Start everything
./setup.sh
```

---

## 🐛 Still Getting Errors?

### Error: "Cannot connect to Docker daemon"

**Solution**: Docker service not running
```bash
sudo systemctl start docker
sudo systemctl enable docker
```

### Error: "docker: command not found"

**Solution**: Docker not installed
```bash
sudo bash install-all.sh
```

### Error: Still permission denied after logging out/in

**Solution**: Check group membership
```bash
# Check groups
groups

# If docker not listed, add again
sudo usermod -aG docker $USER

# Then MUST restart computer (not just log out)
sudo reboot
```

---

## 📝 Why This Happens

Docker daemon runs as root, and the docker socket (`/var/run/docker.sock`) is owned by the `docker` group.

When you install Docker, you need to:
1. Be added to the `docker` group
2. **Log out and log back in** for the group membership to take effect

This is a security feature to prevent unauthorized access to Docker.

---

## ✅ Success Checklist

- [ ] Run `sudo bash install-all.sh` OR `sudo bash fix-docker-permissions.sh`
- [ ] See "User added to docker group"
- [ ] **Log out and log back in** (or restart)
- [ ] Run `groups | grep docker` - should show docker
- [ ] Run `docker ps` - should work (no error)
- [ ] Run `./setup.sh` - should start building

---

**Once docker ps works without sudo, you're ready to run ./setup.sh!**
