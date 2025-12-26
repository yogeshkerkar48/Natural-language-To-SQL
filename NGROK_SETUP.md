# Ngrok Setup Guide for NLP to SQL Project

This guide will help you expose your local development environment to the internet using ngrok.

## What is Ngrok?

Ngrok creates secure tunnels to your localhost, allowing you to:
- Share your local development with others
- Test webhooks from external services
- Access your app from mobile devices
- Demo your application without deploying

## Installation

### Option 1: Download from Website

1. Go to https://ngrok.com/download
2. Download the Windows version
3. Extract `ngrok.exe` to a folder (e.g., `C:\ngrok`)
4. Add to PATH or use full path

### Option 2: Using Chocolatey

```powershell
choco install ngrok
```

### Option 3: Using Scoop

```powershell
scoop install ngrok
```

## Authentication (Required)

1. Sign up for a free account at https://ngrok.com
2. Get your authtoken from https://dashboard.ngrok.com/get-started/your-authtoken
3. Configure ngrok with your token:

```powershell
ngrok config add-authtoken YOUR_AUTH_TOKEN
```

## Usage Scenarios

### Scenario 1: Expose Frontend Only (Port 8080)

Expose your Vue.js frontend to the internet:

```powershell
ngrok http 8080
```

**Access**:
- Your ngrok URL will be displayed (e.g., `https://abc123.ngrok.io`)
- Share this URL with others to access your frontend

**Note**: The frontend will still try to connect to `localhost:8000` for the backend, which won't work for external users.

---

### Scenario 2: Expose Backend Only (Port 8000)

Expose your FastAPI backend:

```powershell
ngrok http 8000
```

**Access**:
- API Docs: `https://your-ngrok-url.ngrok.io/api/docs`

---

### Scenario 3: Expose Nginx (Recommended - Port 8081)

This is the **BEST option** as it exposes both frontend and backend through a single URL:

```powershell
ngrok http 8081
```

**Access**:
- Main App: `https://your-ngrok-url.ngrok.io`
- API Docs: `https://your-ngrok-url.ngrok.io/api/docs`

**Prerequisites**:
- Nginx must be installed and running (see NGINX_SETUP.md)
- Both frontend (8080) and backend (8000) must be running

---

### Scenario 4: Multiple Tunnels (Advanced)

Expose multiple ports simultaneously using ngrok config file.

1. Create `ngrok.yml` in your project root:

```yaml
version: "2"
authtoken: YOUR_AUTH_TOKEN

tunnels:
  frontend:
    proto: http
    addr: 8080
    inspect: true
  
  backend:
    proto: http
    addr: 8000
    inspect: true
  
  nginx:
    proto: http
    addr: 8081
    inspect: true
```

2. Start all tunnels:

```powershell
ngrok start --all --config ngrok.yml
```

---

## Step-by-Step: Complete Setup with Ngrok

### 1. Start All Services

```powershell
# Terminal 1: Backend
cd "d:\Yogesh YK\CDAC PREP\NLP_ON_SQL_PROJECT\NLP_SQL_2\backend"
uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend
cd "d:\Yogesh YK\CDAC PREP\NLP_ON_SQL_PROJECT\NLP_SQL_2\frontend"
npm run dev

# Terminal 3: Nginx (optional but recommended)
cd C:\nginx
.\nginx.exe
```

Or use the convenience script:
```powershell
.\start-services.ps1
```

### 2. Start Ngrok

**For Nginx (Recommended)**:
```powershell
ngrok http 8081
```

**For Frontend Only**:
```powershell
ngrok http 8080
```

### 3. Access Your Application

Ngrok will display output like this:

```
Session Status                online
Account                       your-email@example.com
Version                       3.x.x
Region                        United States (us)
Latency                       -
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://abc123.ngrok.io -> http://localhost:8081

Connections                   ttl     opn     rt1     rt5     p50     p90
                              0       0       0.00    0.00    0.00    0.00
```

**Your public URL**: `https://abc123.ngrok.io`

### 4. Monitor Traffic

Open the ngrok web interface to inspect requests:
```
http://127.0.0.1:4040
```

---

## Vite Configuration for Ngrok

The `vite.config.js` has been updated with ngrok-compatible settings:

```javascript
server: {
  port: 8080,
  host: '0.0.0.0',      // Allow external connections
  strictPort: false,
  hmr: {
    clientPort: 443,    // Use HTTPS port for ngrok
    protocol: 'wss'     // WebSocket Secure for ngrok
  }
}
```

**Important**: Restart your frontend after this change:
```powershell
# Stop current frontend (Ctrl+C)
npm run dev
```

---

## Updating Frontend API Calls (If Not Using Nginx)

If you're exposing the frontend and backend separately, you'll need to update the API base URL.

### Option A: Environment Variables (Recommended)

1. Create `.env` in frontend directory:

```env
VITE_API_URL=https://your-backend-ngrok-url.ngrok.io/api
```

2. Update `src/services/api.js`:

```javascript
import axios from 'axios';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

export default {
  generate(question, schema) {
    return apiClient.post('/generate', { question, schema });
  }
};
```

3. Restart frontend to apply changes.

### Option B: Use Nginx (No Code Changes Needed)

When using nginx on port 8081, all API calls are automatically proxied to the backend. Just expose nginx via ngrok and everything works!

---

## Ngrok Free Tier Limitations

- **Random URLs**: URL changes every time you restart ngrok
- **Session Timeout**: Sessions expire after 2 hours
- **1 Online Tunnel**: Only 1 tunnel at a time (use paid plan for multiple)

### Upgrade Options

For persistent URLs and more features:
- **Static Domain**: Get a permanent ngrok URL
- **Multiple Tunnels**: Run multiple tunnels simultaneously
- **Custom Domains**: Use your own domain

Visit: https://ngrok.com/pricing

---

## Troubleshooting

### HMR (Hot Module Replacement) Not Working

If you see WebSocket errors in the browser console:

1. Make sure you've updated `vite.config.js` with the ngrok settings
2. Restart the frontend dev server
3. Clear browser cache

### CORS Errors

If you get CORS errors when accessing the backend:

1. Update backend CORS settings in `backend/app/main.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (for development)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

2. Restart the backend

### Ngrok Tunnel Not Starting

1. Check if you've authenticated: `ngrok config check`
2. Verify the port is correct and service is running
3. Check firewall settings

### Connection Refused

Make sure the service is running on the port you're trying to expose:

```powershell
netstat -ano | findstr :8080
netstat -ano | findstr :8081
```

---

## Security Considerations

⚠️ **Warning**: Ngrok exposes your local server to the internet!

- Don't expose sensitive data
- Use authentication for production-like testing
- Don't commit ngrok URLs to version control
- Monitor the ngrok web interface (http://127.0.0.1:4040) for suspicious activity
- Stop ngrok when not in use

---

## Quick Reference

### Start Ngrok
```powershell
# Expose nginx (recommended)
ngrok http 8081

# Expose frontend only
ngrok http 8080

# Expose backend only
ngrok http 8000

# With custom subdomain (paid feature)
ngrok http 8081 --subdomain=my-nlp-app
```

### Stop Ngrok
Press `Ctrl+C` in the ngrok terminal

### View Ngrok Status
```powershell
ngrok status
```

### View Ngrok Configuration
```powershell
ngrok config check
```

---

## Recommended Workflow

1. ✅ Start all services (`.\start-services.ps1`)
2. ✅ Start ngrok for nginx (`ngrok http 8081`)
3. ✅ Share the ngrok URL
4. ✅ Monitor traffic at http://127.0.0.1:4040
5. ✅ Stop ngrok when done (Ctrl+C)
6. ✅ Stop services (`.\stop-services.ps1`)

---

## Alternative: Ngrok Config File Template

Save this as `ngrok.yml` in your project root:

```yaml
version: "2"
authtoken: YOUR_AUTH_TOKEN_HERE

tunnels:
  nlp-sql:
    proto: http
    addr: 8081
    inspect: true
    bind_tls: true
```

Then start with:
```powershell
ngrok start nlp-sql --config ngrok.yml
```
