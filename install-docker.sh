#!/bin/bash
# Docker Installation Script for Ubuntu/Debian
# Run this script with: sudo bash install-docker.sh

set -e

echo "================================================"
echo "European News Intelligence Hub - Docker Setup"
echo "================================================"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "ERROR: Please run as root (use: sudo bash install-docker.sh)"
    exit 1
fi

echo "Step 1: Updating package index..."
apt-get update

echo ""
echo "Step 2: Installing prerequisites..."
apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

echo ""
echo "Step 3: Adding Docker's official GPG key..."
mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg

echo ""
echo "Step 4: Setting up Docker repository..."
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

echo ""
echo "Step 5: Installing Docker Engine..."
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

echo ""
echo "Step 6: Adding current user to docker group..."
# Get the actual user (not root) who ran sudo
ACTUAL_USER=${SUDO_USER:-$USER}
usermod -aG docker $ACTUAL_USER

echo ""
echo "Step 7: Starting Docker service..."
systemctl start docker
systemctl enable docker

echo ""
echo "Step 8: Verifying installation..."
docker --version
docker compose version

echo ""
echo "================================================"
echo "✅ Docker installed successfully!"
echo "================================================"
echo ""
echo "IMPORTANT: Please log out and log back in (or run: newgrp docker)"
echo "           This is needed for group membership to take effect."
echo ""
echo "Then you can run: ./setup.sh"
echo ""
