# 🚀 Simple Deployment Guide: Render + Vercel

Super simple deployment - no shell scripts, no complications!

## 📋 What You Need

- GitHub account 
- Render account (free)
- Vercel account (free)
- Groq API Key

---

## 🖥️ Backend on Render (5 minutes)

### 1. Push to GitHub
```bash
git add .
git commit -m "Deploy to Render + Vercel"
git push origin main
```

### 2. Create Render Service
1. Go to [render.com](https://render.com) → New → Web Service
2. Connect your GitHub repo
3. Set **Root Directory** to: `backend`
4. Render will automatically detect and use `render.yaml`

### 3. Set Environment Variables
In Render dashboard:
```
GROQ_API_KEY = your_groq_api_key_here
CORS_ORIGINS = https://your-app.vercel.app
```

**That's it! Backend deploys automatically.** ✅

---

## 🌐 Frontend on Vercel (3 minutes)

### 1. Create Vercel Project
1. Go to [vercel.com](https://vercel.com) → New Project
2. Import your GitHub repo
3. Set **Root Directory** to: `frontend`

### 2. Set Environment Variables
In Vercel dashboard:
```
REACT_APP_API_URL = https://your-backend.onrender.com
REACT_APP_WS_URL = wss://your-backend.onrender.com
```

**That's it! Frontend deploys automatically.** ✅

---

## � After Both Deploy

1. Get your actual URLs from both platforms
2. Update the environment variables with real URLs
3. Both will auto-redeploy

## ✅ Done!

Your app is live! Both platforms auto-deploy when you push to GitHub.

**No scripts, no complications, just works!** 🎉
