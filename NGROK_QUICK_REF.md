# Ngrok Quick Reference

## Installation & Setup

```powershell
# Download from https://ngrok.com/download

# Add authtoken (get from https://dashboard.ngrok.com)
ngrok config add-authtoken YOUR_AUTH_TOKEN

# Verify configuration
ngrok config check
```

## Basic Usage

```powershell
# Expose nginx (recommended - both frontend & backend)
ngrok http 8081

# Expose frontend only
ngrok http 8080

# Expose backend only
ngrok http 8000

# With custom subdomain (paid plan)
ngrok http 8081 --subdomain=my-app

# With specific region
ngrok http 8081 --region=us
```

## Using Config File

```powershell
# Copy template and add your authtoken
Copy-Item ngrok.yml.template ngrok.yml
# Edit ngrok.yml and replace YOUR_AUTH_TOKEN_HERE

# Start specific tunnel
ngrok start nginx --config ngrok.yml

# Start all tunnels (requires paid plan)
ngrok start --all --config ngrok.yml

# Start multiple specific tunnels
ngrok start nginx frontend --config ngrok.yml
```

## Monitoring

```powershell
# Web interface (view requests/responses)
http://127.0.0.1:4040

# Check status
ngrok status

# View version
ngrok version
```

## Common Commands

```powershell
# Stop ngrok
Ctrl+C

# Test connection
ngrok http 8081 --log=stdout

# Update ngrok
ngrok update
```

## Typical Workflow

```powershell
# 1. Start services
.\start-services.ps1

# 2. Start ngrok
ngrok http 8081

# 3. Copy the URL (e.g., https://abc123.ngrok.io)

# 4. Share with others or test

# 5. Monitor traffic at http://127.0.0.1:4040

# 6. When done, stop ngrok (Ctrl+C)

# 7. Stop services
.\stop-services.ps1
```

## Regions

```powershell
--region=us   # United States
--region=eu   # Europe
--region=ap   # Asia/Pacific
--region=au   # Australia
--region=sa   # South America
--region=jp   # Japan
--region=in   # India
```

## Troubleshooting

```powershell
# Check if service is running
netstat -ano | findstr :8081

# View ngrok logs
ngrok http 8081 --log=stdout

# Test configuration
ngrok config check

# Clear cache (if issues)
Remove-Item -Recurse -Force "$env:USERPROFILE\.ngrok2"
ngrok config add-authtoken YOUR_AUTH_TOKEN
```

## Free vs Paid

### Free Tier
- ✅ 1 online tunnel
- ✅ Random URLs
- ✅ HTTPS support
- ❌ Custom domains
- ❌ Reserved subdomains
- ❌ Multiple simultaneous tunnels

### Paid Plans
- ✅ Multiple tunnels
- ✅ Custom domains
- ✅ Reserved subdomains
- ✅ IP whitelisting
- ✅ More regions

See: https://ngrok.com/pricing
