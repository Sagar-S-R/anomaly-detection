# Azure Anomaly Detection Deployment Guide

This guide provides comprehensive instructions for managing your Azure-based anomaly detection system.

## 🚀 Quick Start

### Prerequisites
- Azure CLI installed and configured
- SSH key pair for VM access
- Git repository access

### Current Deployment
- **VM Name**: `anomaly-detection-vm`
- **Resource Group**: `RG-SAMRUDHPRAKASH3084-9928`
- **Location**: East US 2
- **Size**: Standard_B2s (2 vCPUs, 4GB RAM)
- **Public IP**: `172.200.121.141`

## 📋 Service Management

### Start Services
```bash
# Start the VM
az vm start --resource-group RG-SAMRUDHPRAKASH3084-9928 --name anomaly-detection-vm

# Check service status (after VM starts)
az vm run-command invoke --resource-group RG-SAMRUDHPRAKASH3084-9928 --name anomaly-detection-vm --command-id RunShellScript --scripts "sudo systemctl status anomaly-api.service anomaly-dashboard.service --no-pager"
```

### Stop Services
```bash
# Stop the VM (recommended to save costs)
az vm stop --resource-group RG-SAMRUDHPRAKASH3084-9928 --name anomaly-detection-vm

# OR deallocate (frees compute resources)
az vm deallocate --resource-group RG-SAMRUDHPRAKASH3084-9928 --name anomaly-detection-vm
```

### Restart Services
```bash
# Restart VM
az vm restart --resource-group RG-SAMRUDHPRAKASH3084-9928 --name anomaly-detection-vm

# Restart individual services
az vm run-command invoke --resource-group RG-SAMRUDHPRAKASH3084-9928 --name anomaly-detection-vm --command-id RunShellScript --scripts "sudo systemctl restart anomaly-api.service && sudo systemctl restart anomaly-dashboard.service"
```

## 🌐 Endpoints

### Production URLs (HTTPS)
- **Dashboard**: `https://172.200.121.141`
- **API Documentation**: `https://172.200.121.141/api/docs`
- **API Base**: `https://172.200.121.141/api/`
- **Health Check**: `https://172.200.121.141/api/health`

### Development URLs (HTTP)
- **Dashboard**: `http://172.200.121.141` (redirects to HTTPS)
- **API**: `http://172.200.121.141:8000`
- **Dashboard Direct**: `http://172.200.121.141:8001`

### WebSocket Endpoints
- **Dashboard WS**: `wss://172.200.121.141`
- **API WS**: `wss://172.200.121.141/api/ws`

## 🔍 Monitoring & Diagnostics

### Check VM Status
```bash
# VM power state
az vm show --resource-group RG-SAMRUDHPRAKASH3084-9928 --name anomaly-detection-vm --query "powerState" -o tsv

# VM details
az vm show --resource-group RG-SAMRUDHPRAKASH3084-9928 --name anomaly-detection-vm --query "{Name:name, Status:provisioningState, Size:hardwareProfile.vmSize, Location:location}" -o table
```

### Check Service Health
```bash
# Service status
az vm run-command invoke --resource-group RG-SAMRUDHPRAKASH3084-9928 --name anomaly-detection-vm --command-id RunShellScript --scripts "sudo systemctl status anomaly-api.service anomaly-dashboard.service --no-pager"

# Process status
az vm run-command invoke --resource-group RG-SAMRUDHPRAKASH3084-9928 --name anomaly-detection-vm --command-id RunShellScript --scripts "ps aux | grep python"

# Port status
az vm run-command invoke --resource-group RG-SAMRUDHPRAKASH3084-9928 --name anomaly-detection-vm --command-id RunShellScript --scripts "sudo netstat -tlnp | grep :800"
```

### Check Logs
```bash
# System logs
az vm run-command invoke --resource-group RG-SAMRUDHPRAKASH3084-9928 --name anomaly-detection-vm --command-id RunShellScript --scripts "sudo journalctl -u anomaly-api.service -u anomaly-dashboard.service --no-pager -n 50"

# Nginx logs
az vm run-command invoke --resource-group RG-SAMRUDHPRAKASH3084-9928 --name anomaly-detection-vm --command-id RunShellScript --scripts "sudo tail -20 /var/log/nginx/access.log && sudo tail -20 /var/log/nginx/error.log"
```

### Test Endpoints
```bash
# Test dashboard
curl -k https://172.200.121.141

# Test API
curl -k https://172.200.121.141/api/docs

# Test health
curl -k https://172.200.121.141/api/health
```

## 💰 Cost Management

### Budget-Based Auto-Shutdown
- **Budget Limit**: $30.00 USD per month
- **Monitoring Script**: `cost-monitor.sh`
- **Action Group**: `budget-shutdown-action`
- **Automation Account**: `budget-automation`

#### Run Cost Monitor
```bash
# Check current costs and shutdown if over $30
./cost-monitor.sh

# Or run manually
bash cost-monitor.sh
```

#### Cost Monitoring Features
- ✅ **Real-time cost estimation**
- ✅ **Automatic shutdown** when over budget
- ✅ **Email notifications**
- ✅ **VM status checking**
- ✅ **Detailed cost breakdown**

### Check Usage
```bash
# VM creation time
az vm show --resource-group RG-SAMRUDHPRAKASH3084-9928 --name anomaly-detection-vm --query "timeCreated" -o tsv

# Current pricing (approximate)
echo "Standard_B2s costs:"
echo "- Compute: $0.0084/hour"
echo "- Storage: $0.0005/hour"
echo "- Total: ~$0.0089/hour"
```

### Cost Optimization
```bash
# Stop VM when not in use
az vm stop --resource-group RG-SAMRUDHPRAKASH3084-9928 --name anomaly-detection-vm

# Check VM status before starting
az vm show --resource-group RG-SAMRUDHPRAKASH3084-9928 --name anomaly-detection-vm --query "powerState" -o tsv
```

## 🔧 Troubleshooting

### Common Issues

#### Services Not Starting
```bash
# Check service logs
az vm run-command invoke --resource-group RG-SAMRUDHPRAKASH3084-9928 --name anomaly-detection-vm --command-id RunShellScript --scripts "sudo journalctl -u anomaly-api.service -u anomaly-dashboard.service --no-pager -n 100"

# Restart services
az vm run-command invoke --resource-group RG-SAMRUDHPRAKASH3084-9928 --name anomaly-detection-vm --command-id RunShellScript --scripts "sudo systemctl restart anomaly-api.service && sudo systemctl restart anomaly-dashboard.service"
```

#### Port Issues
```bash
# Check firewall
az vm run-command invoke --resource-group RG-SAMRUDHPRAKASH3084-9928 --name anomaly-detection-vm --command-id RunShellScript --scripts "sudo ufw status"

# Check NSG rules
az network nsg rule list --resource-group RG-SAMRUDHPRAKASH3084-9928 --nsg-name anomaly-detection-vmNSG --output table
```

#### HTTPS Issues
```bash
# Check nginx configuration
az vm run-command invoke --resource-group RG-SAMRUDHPRAKASH3084-9928 --name anomaly-detection-vm --command-id RunShellScript --scripts "sudo nginx -t"

# Reload nginx
az vm run-command invoke --resource-group RG-SAMRUDHPRAKASH3084-9928 --name anomaly-detection-vm --command-id RunShellScript --scripts "sudo systemctl reload nginx"
```

## 🔐 Security

### SSH Access
```bash
# SSH into VM
ssh azureuser@172.200.121.141

# Copy files to VM
scp local-file.txt azureuser@172.200.121.141:~/remote-file.txt
```

### Firewall Management
```bash
# Check firewall status
az vm run-command invoke --resource-group RG-SAMRUDHPRAKASH3084-9928 --name anomaly-detection-vm --command-id RunShellScript --scripts "sudo ufw status"

# Allow additional ports (if needed)
az vm run-command invoke --resource-group RG-SAMRUDHPRAKASH3084-9928 --name anomaly-detection-vm --command-id RunShellScript --scripts "sudo ufw allow PORT/tcp && sudo ufw reload"
```

## 📊 Resource Information

### VM Specifications
- **OS**: Ubuntu 22.04 LTS
- **Size**: Standard_B2s
- **vCPUs**: 2
- **RAM**: 4 GB
- **Storage**: 30 GB OS disk

### Network Configuration
- **Public IP**: 172.200.121.141
- **Open Ports**: 22 (SSH), 80 (HTTP), 443 (HTTPS), 8000 (API), 8001 (Dashboard)
- **DNS**: Not configured (using IP address)

### Services
- **API Service**: FastAPI on port 8000
- **Dashboard Service**: FastAPI with WebSocket on port 8001
- **Reverse Proxy**: Nginx on ports 80/443
- **SSL**: Self-signed certificate

## 🆘 Emergency Commands

### Quick VM Reset
```bash
az vm restart --resource-group RG-SAMRUDHPRAKASH3084-9928 --name anomaly-detection-vm
```

### Full Service Restart
```bash
az vm run-command invoke --resource-group RG-SAMRUDHPRAKASH3084-9928 --name anomaly-detection-vm --command-id RunShellScript --scripts "sudo systemctl restart anomaly-api.service anomaly-dashboard.service nginx"
```

### Emergency Stop
```bash
az vm stop --resource-group RG-SAMRUDHPRAKASH3084-9928 --name anomaly-detection-vm
```

## 📝 Notes

- All commands use the resource group `RG-SAMRUDHPRAKASH3084-9928`
- VM name is `anomaly-detection-vm`
- HTTPS uses a self-signed certificate (browser will show security warning)
- Services auto-start on VM boot
- Monitor costs regularly to avoid unexpected charges

## 🎯 Quick Reference

| Action | Command |
|--------|---------|
| Start VM | `az vm start --resource-group RG-SAMRUDHPRAKASH3084-9928 --name anomaly-detection-vm` |
| Stop VM | `az vm stop --resource-group RG-SAMRUDHPRAKASH3084-9928 --name anomaly-detection-vm` |
| Check status | `az vm show --resource-group RG-SAMRUDHPRAKASH3084-9928 --name anomaly-detection-vm --query powerState -o tsv` |
| SSH access | `ssh azureuser@172.200.121.141` |
| Dashboard | `https://172.200.121.141` |
| API docs | `https://172.200.121.141/api/docs` |
