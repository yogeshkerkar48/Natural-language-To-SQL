# Ngrok Network Error - Troubleshooting Guide

## Problem
When accessing the application through ngrok URL, you're getting network errors. This happens because the frontend is trying to connect to `localhost:8000` which doesn't exist when accessed remotely.

## Root Cause
The API client was hardcoded to use `http://localhost:8000/api`, which only works on your local machine. When someone accesses your app through ngrok, their browser tries to connect to *their* localhost, not yours.

## ✅ Solution Applied

### Changes Made:

1. **Updated `vite.config.js`**
   - Added `host: '0.0.0.0'` to allow external connections
   - This ensures Vite accepts connections from ngrok

2. **Updated `frontend/src/services/api.js`**
   - Changed from: `baseURL: 'http://localhost:8000/api'`
   - Changed to: `baseURL: import.meta.env.VITE_API_URL || '/api'`
   - Now uses relative URLs by default, which work with nginx proxy

## 🚀 How to Use

### Option 1: With Nginx (Recommended - Zero Config)

This is the **BEST** approach as it requires no additional configuration:

1. **Start all services:**
   ```powershell
   # Terminal 1: Backend
   cd "d:\Yogesh YK\CDAC PREP\NLP_ON_SQL_PROJECT\NLP_SQL_2\backend"
   uvicorn app.main:app --reload --port 8000

   # Terminal 2: Frontend (RESTART REQUIRED after changes)
   cd "d:\Yogesh YK\CDAC PREP\NLP_ON_SQL_PROJECT\NLP_SQL_2\frontend"
   npm run dev

   # Terminal 3: Nginx
   cd C:\nginx
   .\nginx.exe
   ```

2. **Expose nginx via ngrok:**
   ```powershell
   ngrok http 8081
   ```

3. **Access your app:**
   - Use the ngrok URL (e.g., `https://abc123.ngrok.io`)
   - All API calls will automatically work through the nginx proxy

**Why this works:**
- Nginx proxies `/api/*` requests to backend (port 8000)
- Frontend uses relative URL `/api`, which goes through nginx
- Everything works seamlessly through a single ngrok URL

---

### Option 2: Without Nginx (Direct Backend Access)

If you don't want to use nginx:

1. **Create `.env` file in frontend directory:**
   ```env
   VITE_API_URL=https://your-backend-ngrok-url.ngrok.io/api
   ```

2. **Start backend and expose via ngrok:**
   ```powershell
   # Terminal 1: Backend
   cd "d:\Yogesh YK\CDAC PREP\NLP_ON_SQL_PROJECT\NLP_SQL_2\backend"
   uvicorn app.main:app --reload --port 8000

   # Terminal 2: Expose backend
   ngrok http 8000
   ```
   Copy the ngrok URL (e.g., `https://xyz789.ngrok.io`)

3. **Update `.env` with your ngrok backend URL:**
   ```env
   VITE_API_URL=https://xyz789.ngrok.io/api
   ```

4. **Start frontend and expose via ngrok:**
   ```powershell
   # Terminal 3: Frontend (RESTART REQUIRED)
   cd "d:\Yogesh YK\CDAC PREP\NLP_ON_SQL_PROJECT\NLP_SQL_2\frontend"
   npm run dev

   # Terminal 4: Expose frontend
   ngrok http 8080
   ```

5. **Access your app:**
   - Use the frontend ngrok URL

**Note:** Free ngrok only allows 1 tunnel at a time, so you'll need a paid plan for this approach.

---

### Option 3: Frontend Only (No Backend Access)

If you only want to expose the frontend and keep backend local:

1. **Create `.env` file:**
   ```env
   VITE_API_URL=http://localhost:8000/api
   ```

2. **Start services:**
   ```powershell
   # Backend (local only)
   cd "d:\Yogesh YK\CDAC PREP\NLP_ON_SQL_PROJECT\NLP_SQL_2\backend"
   uvicorn app.main:app --reload --port 8000

   # Frontend
   cd "d:\Yogesh YK\CDAC PREP\NLP_ON_SQL_PROJECT\NLP_SQL_2\frontend"
   npm run dev

   # Expose frontend
   ngrok http 8080
   ```

**Note:** This only works for you locally, not for external users.

---

## ⚠️ Important: Restart Frontend

After making these changes, you **MUST** restart the frontend dev server:

```powershell
# In the frontend terminal, press Ctrl+C to stop
# Then restart:
npm run dev
```

Vite needs to be restarted to pick up:
- Changes to `vite.config.js`
- Changes to `.env` files

---

## 🧪 Testing

### Test Locally First:

1. **Without nginx:**
   ```
   http://localhost:8080
   ```
   Should work as before

2. **With nginx:**
   ```
   http://localhost:8081
   ```
   Should work with the new relative URL setup

### Test with Ngrok:

1. **Start ngrok:**
   ```powershell
   ngrok http 8081  # For nginx
   # OR
   ngrok http 8080  # For frontend only
   ```

2. **Open ngrok URL in browser**

3. **Open browser console (F12)**
   - Check Network tab for API calls
   - Should see requests to `/api/generate` (not `localhost:8000`)

4. **Test the app:**
   - Enter a question and schema
   - Click "Generate SQL"
   - Should work without network errors

---

## 🔍 Debugging

### Check API Endpoint:

Open browser console and check what URL is being used:

```javascript
// In browser console
console.log(import.meta.env.VITE_API_URL)
```

### Check Network Requests:

1. Open browser DevTools (F12)
2. Go to Network tab
3. Try generating SQL
4. Look for the `/api/generate` request
5. Check the request URL - should be relative or pointing to correct ngrok URL

### Common Issues:

**Issue:** Still getting localhost errors
- **Fix:** Make sure you restarted the frontend after changes

**Issue:** CORS errors
- **Fix:** Backend already has CORS enabled for all origins (`allow_origins=["*"]`)

**Issue:** 404 errors
- **Fix:** Make sure nginx is running and configured correctly

**Issue:** Connection refused
- **Fix:** Verify all services are running:
  ```powershell
  netstat -ano | findstr :8000  # Backend
  netstat -ano | findstr :8080  # Frontend
  netstat -ano | findstr :8081  # Nginx
  ```

---

## 📋 Quick Reference

### Current Configuration:

- **Frontend:** Port 8080, accessible externally via `0.0.0.0`
- **Backend:** Port 8000, CORS enabled for all origins
- **Nginx:** Port 8081, proxies `/api/*` to backend
- **API URL:** Relative `/api` (works with nginx) or configurable via `VITE_API_URL`

### Recommended Setup:

```
User → Ngrok → Nginx (8081) → Frontend (8080)
                            → Backend (8000) for /api/* requests
```

### Files Modified:

1. `frontend/vite.config.js` - Added `host: '0.0.0.0'`
2. `frontend/src/services/api.js` - Changed to relative URL with env variable support
3. `frontend/.env.example` - Created template for configuration

---

## 🎯 Next Steps

1. ✅ Restart your frontend dev server
2. ✅ Choose your preferred setup (Option 1 recommended)
3. ✅ Start ngrok
4. ✅ Test the application
5. ✅ Monitor ngrok web interface at `http://127.0.0.1:4040`

---

## 💡 Pro Tips

- **Use nginx approach** - It's the cleanest and requires no configuration
- **Monitor traffic** - Check `http://127.0.0.1:4040` to see all requests
- **Free tier limits** - Ngrok free tier only allows 1 tunnel, use nginx to expose everything through one tunnel
- **Security** - Don't expose sensitive data, stop ngrok when not in use
- **URL changes** - Free ngrok URLs change on restart, paid plans get static URLs
