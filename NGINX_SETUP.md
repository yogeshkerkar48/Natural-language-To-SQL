# Nginx Setup Guide for Windows

This guide will help you set up nginx on Windows to run on port 8081, proxying requests to your frontend (port 8080) and backend (port 8000).

## Architecture

```
User Request → nginx (port 8081)
                  ├─→ /api/* → Backend (port 8000)
                  └─→ /* → Frontend (port 8080)
```

## Prerequisites

- Frontend running on port 8080 (configured in `vite.config.js`)
- Backend running on port 8000 (uvicorn)
- nginx installed on Windows

## Installation

### Option 1: Download nginx for Windows

1. Download nginx from: https://nginx.org/en/download.html
   - Choose the latest stable Windows version (e.g., `nginx/Windows-1.24.0`)

2. Extract the zip file to a location like `C:\nginx`

### Option 2: Using Chocolatey (if installed)

```powershell
choco install nginx
```

## Configuration

1. Copy the `nginx.conf` file from this project to your nginx installation directory:
   ```powershell
   Copy-Item "nginx.conf" "C:\nginx\conf\nginx.conf" -Force
   ```

   Or manually copy the file to replace the default `nginx.conf`

## Running nginx

### Start nginx

Navigate to your nginx directory and run:

```powershell
cd C:\nginx
.\nginx.exe
```

Or if using Chocolatey:

```powershell
nginx
```

### Check if nginx is running

Open your browser and navigate to:
- http://localhost:8081 - Should show your frontend
- http://localhost:8081/api/docs - Should show your FastAPI docs

### Stop nginx

```powershell
cd C:\nginx
.\nginx.exe -s stop
```

### Reload configuration (after changes)

```powershell
cd C:\nginx
.\nginx.exe -s reload
```

### Test configuration

```powershell
cd C:\nginx
.\nginx.exe -t
```

## Running the Complete Stack

1. **Start Backend** (in terminal 1):
   ```powershell
   cd "d:\Yogesh YK\CDAC PREP\NLP_ON_SQL_PROJECT\NLP_SQL_2\backend"
   uvicorn app.main:app --reload --port 8000
   ```

2. **Start Frontend** (in terminal 2):
   ```powershell
   cd "d:\Yogesh YK\CDAC PREP\NLP_ON_SQL_PROJECT\NLP_SQL_2\frontend"
   npm run dev
   ```

3. **Start nginx** (in terminal 3):
   ```powershell
   cd C:\nginx
   .\nginx.exe
   ```

4. **Access your application**:
   - Main application: http://localhost:8081
   - API documentation: http://localhost:8081/api/docs

## Troubleshooting

### Port already in use

If port 8081 is already in use, you can:

1. Find the process using the port:
   ```powershell
   netstat -ano | findstr :8081
   ```

2. Kill the process (replace PID with the actual process ID):
   ```powershell
   taskkill /PID <PID> /F
   ```

### nginx won't start

1. Check the error log:
   ```powershell
   type C:\nginx\logs\error.log
   ```

2. Make sure ports 8000 and 8080 are accessible:
   ```powershell
   netstat -ano | findstr :8000
   netstat -ano | findstr :8080
   ```

### Configuration errors

Test your configuration:
```powershell
cd C:\nginx
.\nginx.exe -t
```

## Alternative: Run nginx in Docker (Optional)

If you prefer using Docker:

1. Create a `Dockerfile.nginx`:
   ```dockerfile
   FROM nginx:alpine
   COPY nginx.conf /etc/nginx/nginx.conf
   EXPOSE 8081
   ```

2. Build and run:
   ```powershell
   docker build -f Dockerfile.nginx -t nlp-nginx .
   docker run -d -p 8081:8081 --name nlp-nginx nlp-nginx
   ```

## Notes

- The current configuration assumes your backend is at `localhost:8000` and frontend at `localhost:8080`
- All API requests should be prefixed with `/api/` when accessing through nginx
- WebSocket connections are supported for hot module replacement (HMR)
- You may need to update your frontend API calls to use `/api/` prefix if they don't already
