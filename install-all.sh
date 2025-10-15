#!/bin/bash
# Complete Installation Script for European News Intelligence Hub
# Run with: sudo bash install-all.sh

set -e  # Exit on error

echo "================================================"
echo "European News Intelligence Hub"
echo "Complete Installation Script"
echo "================================================"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ ERROR: Please run as root (use: sudo bash install-all.sh)"
    exit 1
fi

# Get the actual user (not root) who ran sudo
ACTUAL_USER=${SUDO_USER:-$USER}
ACTUAL_HOME=$(eval echo ~$ACTUAL_USER)

echo "Installing for user: $ACTUAL_USER"
echo "Home directory: $ACTUAL_HOME"
echo ""

# ============================================================
# Step 1: Update System
# ============================================================
echo "Step 1: Updating package lists..."
apt-get update -qq

# ============================================================
# Step 2: Install Prerequisites
# ============================================================
echo ""
echo "Step 2: Installing prerequisites..."

PACKAGES_TO_INSTALL=""

# Check and install git
if ! command -v git &> /dev/null; then
    echo "  → Installing git..."
    PACKAGES_TO_INSTALL="$PACKAGES_TO_INSTALL git"
else
    echo "  ✅ git already installed ($(git --version | cut -d' ' -f3))"
fi

# Check and install curl
if ! command -v curl &> /dev/null; then
    echo "  → Installing curl..."
    PACKAGES_TO_INSTALL="$PACKAGES_TO_INSTALL curl"
else
    echo "  ✅ curl already installed"
fi

# Check and install wget
if ! command -v wget &> /dev/null; then
    echo "  → Installing wget..."
    PACKAGES_TO_INSTALL="$PACKAGES_TO_INSTALL wget"
else
    echo "  ✅ wget already installed"
fi

# Check and install ca-certificates
if ! dpkg -l | grep -q ca-certificates; then
    PACKAGES_TO_INSTALL="$PACKAGES_TO_INSTALL ca-certificates"
fi

# Check and install gnupg
if ! command -v gpg &> /dev/null; then
    PACKAGES_TO_INSTALL="$PACKAGES_TO_INSTALL gnupg"
fi

# Check and install lsb-release
if ! command -v lsb_release &> /dev/null; then
    PACKAGES_TO_INSTALL="$PACKAGES_TO_INSTALL lsb-release"
fi

# Additional useful packages
PACKAGES_TO_INSTALL="$PACKAGES_TO_INSTALL software-properties-common apt-transport-https"

if [ -n "$PACKAGES_TO_INSTALL" ]; then
    echo "  → Installing packages: $PACKAGES_TO_INSTALL"
    apt-get install -y $PACKAGES_TO_INSTALL
    echo "  ✅ Prerequisites installed"
else
    echo "  ✅ All prerequisites already installed"
fi

# ============================================================
# Step 3: Install Docker
# ============================================================
echo ""
echo "Step 3: Installing Docker..."

if command -v docker &> /dev/null; then
    echo "  ✅ Docker already installed ($(docker --version))"
else
    echo "  → Adding Docker's official GPG key..."
    mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    chmod a+r /etc/apt/keyrings/docker.gpg

    echo "  → Setting up Docker repository..."
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

    echo "  → Updating package lists..."
    apt-get update -qq

    echo "  → Installing Docker Engine..."
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

    echo "  ✅ Docker installed successfully"
fi

# ============================================================
# Step 4: Configure Docker
# ============================================================
echo ""
echo "Step 4: Configuring Docker..."

# Start Docker service
systemctl start docker
systemctl enable docker
echo "  ✅ Docker service started and enabled"

# Add user to docker group
if groups $ACTUAL_USER | grep -q docker; then
    echo "  ✅ User $ACTUAL_USER already in docker group"
else
    echo "  → Adding $ACTUAL_USER to docker group..."
    usermod -aG docker $ACTUAL_USER
    echo "  ✅ User added to docker group"
fi

# ============================================================
# Step 5: Install Python packages (if needed)
# ============================================================
echo ""
echo "Step 5: Checking Python environment..."

if ! command -v python3 &> /dev/null; then
    echo "  → Installing Python 3..."
    apt-get install -y python3 python3-pip python3-venv
    echo "  ✅ Python 3 installed"
else
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo "  ✅ Python 3 already installed (version $PYTHON_VERSION)"
fi

# Install pip if not present
if ! command -v pip3 &> /dev/null; then
    echo "  → Installing pip..."
    apt-get install -y python3-pip
    echo "  ✅ pip installed"
else
    echo "  ✅ pip already installed"
fi

# ============================================================
# Step 6: Install Node.js and npm (if needed)
# ============================================================
echo ""
echo "Step 6: Checking Node.js environment..."

if ! command -v node &> /dev/null; then
    echo "  → Installing Node.js and npm..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt-get install -y nodejs
    echo "  ✅ Node.js and npm installed"
else
    NODE_VERSION=$(node --version)
    NPM_VERSION=$(npm --version)
    echo "  ✅ Node.js already installed (version $NODE_VERSION)"
    echo "  ✅ npm already installed (version $NPM_VERSION)"
fi

# ============================================================
# Step 7: Install useful development tools
# ============================================================
echo ""
echo "Step 7: Installing development tools..."

DEV_TOOLS="build-essential nano vim htop net-tools"
echo "  → Installing: $DEV_TOOLS"
apt-get install -y $DEV_TOOLS
echo "  ✅ Development tools installed"

# ============================================================
# Step 8: Verify Installations
# ============================================================
echo ""
echo "Step 8: Verifying installations..."
echo ""

echo "  Git:     $(git --version | cut -d' ' -f3)"
echo "  Curl:    $(curl --version | head -1 | cut -d' ' -f2)"
echo "  Python3: $(python3 --version | cut -d' ' -f2)"
echo "  pip3:    $(pip3 --version | cut -d' ' -f2)"
echo "  Node:    $(node --version)"
echo "  npm:     $(npm --version)"
echo "  Docker:  $(docker --version | cut -d' ' -f3 | tr -d ',')"

if docker compose version &> /dev/null; then
    echo "  Docker Compose: $(docker compose version | cut -d' ' -f4)"
fi

# ============================================================
# Step 9: Test Docker
# ============================================================
echo ""
echo "Step 9: Testing Docker installation..."
if docker ps &> /dev/null; then
    echo "  ✅ Docker is working correctly"
else
    echo "  ⚠️  Docker test skipped (needs user to be in docker group)"
fi

# ============================================================
# Step 10: Set proper permissions
# ============================================================
echo ""
echo "Step 10: Setting proper permissions..."

cd /home/payas/euint
chown -R $ACTUAL_USER:$ACTUAL_USER /home/payas/euint
chmod +x setup.sh install-docker.sh deploy.sh setup-ssl.sh scripts/*.sh 2>/dev/null || true

echo "  ✅ Permissions set"

# ============================================================
# Final Summary
# ============================================================
echo ""
echo "================================================"
echo "✅ Installation Complete!"
echo "================================================"
echo ""
echo "Installed/Verified:"
echo "  ✅ Git"
echo "  ✅ Curl & Wget"
echo "  ✅ Python 3 & pip"
echo "  ✅ Node.js & npm"
echo "  ✅ Docker Engine"
echo "  ✅ Docker Compose"
echo "  ✅ Development tools"
echo ""
echo "⚠️  IMPORTANT: Log out and log back in (or restart)"
echo "   This is required for Docker group membership to take effect."
echo ""
echo "After logging back in, verify Docker works:"
echo "  docker --version"
echo "  docker ps"
echo ""
echo "Then continue with setup:"
echo "  cd /home/payas/euint"
echo "  nano .env  # Update GEMINI_API_KEY"
echo "  ./setup.sh"
echo ""
