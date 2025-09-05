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
# git clone https://github.com/your-username/anomaly-detection.git .
# cd anomaly-detection/backend

# Create virtual environment
echo "🌐 Creating Python virtual environment..."
python3.9 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📚 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
echo "📂 Creating application directories..."
mkdir -p logs
mkdir -p uploads
mkdir -p models

# Copy configuration files
echo "⚙️ Setting up configuration..."
cp azure_config.env .env
# Edit .env file with your actual values
echo "⚠️  Please edit .env file with your actual configuration values"

# Create systemd service file
echo "🔧 Creating systemd service..."
sudo tee /etc/systemd/system/anomaly-detection.service > /dev/null <<EOF
[Unit]
Description=Anomaly Detection System
After=network.target

[Service]
User=$USER
WorkingDirectory=/opt/anomaly-detection/backend
Environment=PATH=/opt/anomaly-detection/backend/venv/bin
ExecStart=/opt/anomaly-detection/backend/venv/bin/python dashboard_app.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
echo "▶️ Starting anomaly detection service..."
sudo systemctl daemon-reload
sudo systemctl enable anomaly-detection
sudo systemctl start anomaly-detection

# Configure firewall (if using ufw)
echo "🔥 Configuring firewall..."
sudo ufw allow 8001
sudo ufw --force enable

# Setup SSL with Let's Encrypt (optional)
echo "🔒 Setting up SSL certificate..."
# sudo apt install certbot python3-certbot-nginx
# sudo certbot --nginx -d your-domain.com

echo "✅ Azure VM deployment completed!"
echo ""
echo "📋 Next steps:"
echo "1. Edit /opt/anomaly-detection/backend/.env with your configuration"
echo "2. Update CORS origins in the application for your domain"
echo "3. Configure SSL certificate if needed"
echo "4. Test the application at http://your-vm-ip:8001"
echo ""
echo "🔍 Check service status: sudo systemctl status anomaly-detection"
echo "📜 View logs: sudo journalctl -u anomaly-detection -f"
