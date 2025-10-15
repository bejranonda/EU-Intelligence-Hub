#!/bin/bash
# Fix Docker Permissions
# This script adds the current user to the docker group

echo "🔧 Fixing Docker Permissions"
echo "================================"
echo ""

# Check if docker group exists
if ! getent group docker > /dev/null 2>&1; then
    echo "❌ Docker group doesn't exist. Is Docker installed?"
    echo "Run: sudo bash install-all.sh"
    exit 1
fi

# Check if user is already in docker group
if groups $USER | grep -q docker; then
    echo "✅ User $USER is already in docker group"
    echo ""
    echo "⚠️  But you may need to log out and back in for it to take effect!"
    echo ""
    echo "Try this command to apply the group without logging out:"
    echo "  newgrp docker"
    echo ""
    echo "Then run: ./setup.sh"
else
    echo "Adding user $USER to docker group..."
    sudo usermod -aG docker $USER

    if [ $? -eq 0 ]; then
        echo "✅ User added to docker group successfully!"
        echo ""
        echo "⚠️  CRITICAL: You MUST log out and log back in"
        echo ""
        echo "Options:"
        echo "  1. Log out and log back in (recommended)"
        echo "  2. Restart your computer"
        echo "  3. Try: newgrp docker (may not always work)"
        echo ""
        echo "After logging back in, run:"
        echo "  ./setup.sh"
    else
        echo "❌ Failed to add user to docker group"
        echo "You may need to run this script with sudo"
    fi
fi
