# ShadowC2 Architecture

## Backend (FastAPI)
- SQLite with SQLAlchemy ORM
- RESTful endpoints for device registration, command polling, and result exfiltration
- CORS enabled for frontend access

## Frontend (Next.js 14)
- App Router
- Tailwind CSS for dark theme
- Real-time device list updates via polling

## Android Client (Kotlin)
- Foreground service for persistent background operation
- OkHttp for HTTP requests
- Auto-registers device on first run
- Polls for commands every 10 seconds

## Deployment
- Docker Compose for local development
- Gunicorn for production (VPS)
- Cloudflare Tunnel for public exposure without port forwarding