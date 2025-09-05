# 🚀 Quick Deployment Guide

## 📋 Deployment Checklist

### Step 1: Build Frontend
```bash
cd frontend
npm run build
# ✅ Should output: "Compiled successfully"
```

### Step 2: Deploy Backend to Azure
1. Deploy `backend/` folder to Azure Web Apps
2. Get your Azure URL: `https://your-app-name.azurewebsites.net`

### Step 3: Update Frontend URLs
**Update TWO files with your actual Azure URL:**

#### File 1: `frontend/.env`
```bash
REACT_APP_API_URL=https://your-actual-azure-url.azurewebsites.net
REACT_APP_WS_URL=wss://your-actual-azure-url.azurewebsites.net
```

#### File 2: `frontend/vercel.json`
```json
{
  "env": {
    "REACT_APP_API_URL": "https://your-actual-azure-url.azurewebsites.net",
    "REACT_APP_WS_URL": "wss://your-actual-azure-url.azurewebsites.net"
  }
}
```

### Step 4: Deploy Frontend to Vercel
```bash
cd frontend
vercel --prod
```

## ✅ Final Checklist
- [ ] Backend deployed to Azure ✓
- [ ] Azure URL obtained ✓
- [ ] `.env` updated ✓
- [ ] `vercel.json` updated ✓
- [ ] Frontend deployed to Vercel ✓
- [ ] Test login/video upload ✓

## 🎯 You're Done!
Your anomaly detection system is now live on:
- **Frontend**: Vercel URL
- **Backend**: Azure URL

---
*For detailed instructions, see the main README.md*
