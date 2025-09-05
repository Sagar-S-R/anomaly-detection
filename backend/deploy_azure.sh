#!/bin/bash
# Azure VM Deployment Script for Anomaly Detection System
# Run this script on your Azure VM after cloning the repository

set -e

echo "🚀 Starting Azure VM deployment for Anomaly Detection System..."

# Update system packages
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Python 3.9+ if not available
echo "🐍 Installing Python 3.9..."
sudo apt install -y python3.9 python3.9-venv python3-pip

# Install system dependencies for OpenCV and other libraries
echo "🔧 Installing system dependencies..."
sudo apt install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    ffmpeg \
    portaudio19-dev \
    python3-dev \
    build-essential

# Create application directory
echo "📁 Setting up application directory..."
sudo mkdir -p /opt/anomaly-detection
sudo chown $USER:$USER /opt/anomaly-detection
cd /opt/anomaly-detection

# Clone repository (assuming this script is run from the cloned repo)
echo "📥 Copying project files..."
# If running from local clone, copy files instead of cloning
if [ -d "/Users/samrudhp/Projects-git/anomaly-detection" ]; then
    cp -r /Users/samrudhp/Projects-git/anomaly-detection/* /opt/anomaly-detection/
else
    # git clone https://github.com/your-username/anomaly-detection.git .
    echo "❌ Please ensure repository is cloned locally first"
    exit 1
fi

cd /opt/anomaly-detection/backend

# Create virtual environment
echo "🌐 Creating Python virtual environment..."
python3.9 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📚 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Pre-load all AI models (IMPORTANT for performance)
echo "🤖 Pre-loading AI models for optimal performance..."
python preload_models.py

# Setup environment configuration
echo "⚙️ Setting up environment configuration..."
if [ ! -f .env ]; then
    cp .env.template .env 2>/dev/null || echo "⚠️ No .env.template found, creating basic .env"
    cat > .env << EOF
# Azure VM Environment Configuration
ENVIRONMENT=production
DEBUG=false

# Model Cache Configuration
TRANSFORMERS_CACHE=/home/$USER/model_cache
WHISPER_CACHE_DIR=/home/$USER/model_cache
HF_HOME=/home/$USER/model_cache

# CORS Configuration (update with your Vercel domain)
CORS_ORIGINS=https://your-vercel-app.vercel.app,http://localhost:3000

# Add other environment variables as needed
EOF
    echo "✅ Created .env file - please update CORS_ORIGINS with your Vercel domain"
fi

# Create systemd services for both applications
echo "� Creating systemd services..."

# Service for app.py (API server)
sudo tee /etc/systemd/system/anomaly-api.service > /dev/null <<EOF
[Unit]
Description=Anomaly Detection API Service
After=network.target

[Service]
User=$USER
WorkingDirectory=/opt/anomaly-detection/backend
Environment=PATH=/opt/anomaly-detection/backend/venv/bin
Environment=TRANSFORMERS_CACHE=/home/$USER/model_cache
Environment=WHISPER_CACHE_DIR=/home/$USER/model_cache
Environment=HF_HOME=/home/$USER/model_cache
ExecStart=/opt/anomaly-detection/backend/venv/bin/python app.py --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Service for dashboard_app.py (WebSocket dashboard)
sudo tee /etc/systemd/system/anomaly-dashboard.service > /dev/null <<EOF
[Unit]
Description=Anomaly Detection Dashboard Service
After=network.target

[Service]
User=$USER
WorkingDirectory=/opt/anomaly-detection/backend
Environment=PATH=/opt/anomaly-detection/backend/venv/bin
Environment=TRANSFORMERS_CACHE=/home/$USER/model_cache
Environment=WHISPER_CACHE_DIR=/home/$USER/model_cache
Environment=HF_HOME=/home/$USER/model_cache
ExecStart=/opt/anomaly-detection/backend/venv/bin/python dashboard_app.py --host 0.0.0.0 --port 8001
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Enable and start both services
echo "▶️ Starting anomaly detection services..."
sudo systemctl daemon-reload
sudo systemctl enable anomaly-api
sudo systemctl enable anomaly-dashboard
sudo systemctl start anomaly-api
sudo systemctl start anomaly-dashboard

# Configure firewall (if using ufw)
echo "🔥 Configuring firewall..."
sudo ufw allow 8000  # API port
sudo ufw allow 8001  # Dashboard port
sudo ufw --force enable

# Setup SSL with Let's Encrypt (optional)
echo "🔒 Setting up SSL certificate..."
# sudo apt install certbot python3-certbot-nginx
# sudo certbot --nginx -d your-domain.com

echo "✅ Azure VM deployment completed!"
echo ""
echo "🌐 Frontend Dashboard Access:"
echo "  📊 Main Dashboard: http://your-vm-ip:8001/dashboard"
echo "  � API Documentation: http://your-vm-ip:8000/docs"
echo ""
echo "�📋 Next steps:"
echo "1. Edit /opt/anomaly-detection/backend/.env with your Vercel domain for CORS"
echo "2. Update CORS origins in app.py and dashboard_app.py for your domain"
echo "3. Configure SSL certificate if needed"
echo "4. Test the dashboard at http://your-vm-ip:8001/dashboard"
echo "5. Test the API at http://your-vm-ip:8000/docs"
echo ""
echo "🔍 Check service status:"
echo "  sudo systemctl status anomaly-api"
echo "  sudo systemctl status anomaly-dashboard"
echo "📜 View logs:"
echo "  sudo journalctl -u anomaly-api -f"
echo "  sudo journalctl -u anomaly-dashboard -f"
echo ""
echo "💾 Model cache location: /home/$USER/model_cache"
echo "🚀 Services will auto-restart on failure"
