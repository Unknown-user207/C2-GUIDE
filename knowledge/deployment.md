# 🚀 Deployment & Infrastructure

## Deployment Options

### 1. Self-Hosted
```

Requirements:

· VPS/Cloud Server
· Domain Name
· SSL Certificate
· Python 3.9+
· Node.js 18+

Setup:

1. Clone repository
2. Configure environment
3. Install dependencies
4. Start server
5. Setup NGINX reverse proxy
6. Configure SSL

```

### 2. Docker Deployment
```yaml
# docker-compose.yml
version: '3.8'

services:
  server:
    build: .
    ports:
      - "443:443"
      - "8000:8000"
    environment:
      - C2_DOMAIN=c2.shadow.com
      - SECRET_KEY=your_secret
    volumes:
      - ./data:/app/data
      - ./certs:/app/certs
    restart: always

  redis:
    image: redis:alpine
    restart: always

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_PASSWORD=secure_password
    volumes:
      - ./postgres:/var/lib/postgresql/data
```

3. Cloud Native

```
AWS/Azure/GCP:
├── EC2/VM → C2 Server
├── RDS/Cloud SQL → Database
├── S3/Storage → APK Storage
├── CloudFront/CDN → Frontend
└── Route53/DNS → Domain
```

Infrastructure Components

Web Server

· NGINX as reverse proxy
· SSL termination
· Static file serving
· Rate limiting

Application Server

· Python Flask (backend)
· Gunicorn/WSGI
· WebSocket server
· API endpoints

Database

· PostgreSQL for production
· SQLite for development
· Redis for caching/real-time

File Storage

· Local storage for APKs
· Cloud storage for distribution

Security Considerations

1. Server Security

· Firewall rules (allow only 443, 80)
· Fail2ban for brute force
· Regular security updates
· Hardened SSH access
· HTTPS mandatory

2. C2 Communication

· Certificate pinning
· Encrypted payloads
· Domain rotation
· Multiple C2 endpoints

3. Operational Security

· Separate accounts
· VPN/Proxy for access
· Log rotation
· Audit trails

Monitoring & Maintenance

Health Checks

```bash
# Server health
curl https://c2.shadow.com/health

# Database status
python manage.py check_db

# Redis status
redis-cli ping

# Agent count monitoring
python manage.py agent_stats
```

Logging

· Access logs
· Error logs
· Agent activity logs
· Security audit logs

Backup Strategy

· Daily database backup
· Weekly configuration backup
· Monthly disaster recovery test
· Encrypted backups
