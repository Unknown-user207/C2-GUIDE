# Deployment Notes — ShadowC2 & Guide

## VPS Setup (Ubuntu 22.04)
1. Install Python, Git, Docker
2. Clone repo
3. Set up virtual environment
4. Install dependencies
5. Use Gunicorn for production

## Cloudflare Tunnel
- No port forwarding needed
- `cloudflared tunnel --url http://localhost:8000`
- Public URL generated automatically

## Docker Compose
- Backend on port 8000
- Frontend on port 3000
- Persistent volumes for database and file history

## Monitoring
- Use `htop` for system resources
- Use `journalctl` for service logs
- Set up cron for daily backups of memory and context