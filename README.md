# NLP to SQL Project - Quick Start Guide

## Current Configuration

- **Frontend**: Port 8080 (Vite dev server)
- **Backend**: Port 8000 (FastAPI/Uvicorn)
- **Nginx**: Port 8081 (Reverse proxy)
- **Ngrok**: Expose to internet (optional)

## Quick Start

### Option 1: Access via Nginx (Recommended)

This setup routes all requests through nginx on port 8081.

1. **Start Backend**:
   ```powershell
   cd "d:\Yogesh YK\CDAC PREP\NLP_ON_SQL_PROJECT\NLP_SQL_2\backend"
   uvicorn app.main:app --reload --port 8000
   ```

2. **Start Frontend**:
   ```powershell
   cd "d:\Yogesh YK\CDAC PREP\NLP_ON_SQL_PROJECT\NLP_SQL_2\frontend"
   npm run dev
   ```

3. **Start Nginx** (see NGINX_SETUP.md for installation):
   ```powershell
   cd C:\nginx
   .\nginx.exe
   ```

4. **Access Application**:
   - Main App: http://localhost:8081
   - API Docs: http://localhost:8081/api/docs

### Option 2: Direct Access (Development)

Access frontend and backend directly without nginx.

1. **Start Backend**:
   ```powershell
   cd "d:\Yogesh YK\CDAC PREP\NLP_ON_SQL_PROJECT\NLP_SQL_2\backend"
   uvicorn app.main:app --reload --port 8000
   ```

2. **Start Frontend**:
   ```powershell
   cd "d:\Yogesh YK\CDAC PREP\NLP_ON_SQL_PROJECT\NLP_SQL_2\frontend"
   npm run dev
   ```

3. **Access Application**:
   - Frontend: http://localhost:8080
   - Backend API: http://localhost:8000/api/docs

### Option 3: Expose via Ngrok (Share Publicly)

Expose your local development to the internet using ngrok.

1. **Start all services** (use Option 1 or 2 above)

2. **Install ngrok** (see NGROK_SETUP.md for details):
   - Download from https://ngrok.com/download
   - Sign up and get your authtoken
   - Configure: `ngrok config add-authtoken YOUR_TOKEN`

3. **Start ngrok**:
   ```powershell
   # Expose nginx (recommended - exposes both frontend and backend)
   ngrok http 8081
   
   # OR expose frontend only
   ngrok http 8080
   ```

4. **Access Application**:
   - Your ngrok URL will be displayed (e.g., `https://abc123.ngrok.io`)
   - Share this URL with anyone to access your app

📖 **See [NGROK_SETUP.md](file:///d:/Yogesh%20YK/CDAC%20PREP/NLP_ON_SQL_PROJECT/NLP_SQL_2/NGROK_SETUP.md) for detailed ngrok configuration and troubleshooting**

## Restarting Frontend (to apply port changes)

Since your frontend is currently running, you need to restart it:

1. Stop the current frontend process (Ctrl+C in the terminal)
2. Restart with:
   ```powershell
   npm run dev
   ```

The frontend will now run on port 8080 with ngrok-compatible settings.

## Project Structure

```
NLP_SQL_2/
├── backend/              # FastAPI backend (port 8000)
├── frontend/             # Vue.js frontend (port 8080)
├── nginx.conf            # Nginx configuration (port 8081)
├── ngrok.yml.template    # Ngrok configuration template
├── NGINX_SETUP.md        # Nginx installation guide
├── NGROK_SETUP.md        # Ngrok setup and usage guide
├── start-services.ps1    # Start all services script
├── stop-services.ps1     # Stop all services script
└── README.md             # This file
```

## API Configuration

The frontend is configured to call the backend at `http://localhost:8000/api`. When using nginx, requests to `http://localhost:8081/api/*` are automatically proxied to the backend.

## Troubleshooting

### Frontend not on port 8080?

Make sure you've restarted the frontend dev server after the `vite.config.js` changes.

### Nginx not working?

1. Check if nginx is installed (see NGINX_SETUP.md)
2. Verify the configuration: `nginx.exe -t`
3. Check error logs: `type C:\nginx\logs\error.log`

### Ngrok not working?

1. Check if you've authenticated: `ngrok config check`
2. Make sure the service is running on the port you're exposing
3. See NGROK_SETUP.md for detailed troubleshooting

### Port conflicts?

Check what's using a port:
```powershell
netstat -ano | findstr :8080
netstat -ano | findstr :8081
```

## Documentation

- **[NGINX_SETUP.md](file:///d:/Yogesh%20YK/CDAC%20PREP/NLP_ON_SQL_PROJECT/NLP_SQL_2/NGINX_SETUP.md)** - Complete nginx installation and configuration guide
- **[NGROK_SETUP.md](file:///d:/Yogesh%20YK/CDAC%20PREP/NLP_ON_SQL_PROJECT/NLP_SQL_2/NGROK_SETUP.md)** - Ngrok setup, usage, and troubleshooting

## Next Steps

1. ✅ Frontend configured for port 8080 with ngrok support
2. ✅ Nginx configuration created
3. ✅ Ngrok configuration template created
4. ⏳ Restart frontend dev server
5. ⏳ Install nginx (optional, see NGINX_SETUP.md)
6. ⏳ Install ngrok (optional, see NGROK_SETUP.md)
7. ⏳ Access application locally or via ngrok

