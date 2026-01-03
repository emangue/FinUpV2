# 🚀 Deployment Guide - Financial Management System

**Version:** 3.0.1  
**Last Updated:** 02/01/2026  
**Deployment Status:** Production Ready ✅

---

## 📋 Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [VM Requirements](#vm-requirements)
3. [Initial Setup](#initial-setup)
4. [Deployment Process](#deployment-process)
5. [Post-Deployment](#post-deployment)
6. [Backup & Recovery](#backup--recovery)
7. [Security](#security)
8. [Troubleshooting](#troubleshooting)

---

## 🎯 Pre-Deployment Checklist

### 1. Local Environment

- [ ] All changes committed to git
- [ ] VERSION.md updated
- [ ] CHANGELOG.md updated  
- [ ] Tests passing locally

### 2. Run Pre-Deployment Scripts

```bash
# 1. Database health check
python scripts/database_health_check.py

# 2. Deployment tests
python tests/deployment_health_check.py

# 3. Generate diff report
python scripts/deployment_diff.py --save-manifest

# 4. Backup local database
python scripts/backup_database.py backup --tag pre-deploy
```

### 3. VM Information

Fill in [VM_INFO_CHECKLIST.md](VM_INFO_CHECKLIST.md) with your VM details.

---

## 🖥️ VM Requirements

### Minimum Specifications

- **OS:** Ubuntu 22.04 LTS / Debian 12
- **CPU:** 2 cores
- **RAM:** 2 GB
- **Disk:** 20 GB SSD
- **Network:** Public IP or domain name

### Recommended Specifications

- **OS:** Ubuntu 22.04 LTS
- **CPU:** 4 cores
- **RAM:** 4 GB
- **Disk:** 50 GB SSD
- **Backup:** Automated snapshots

### Software Requirements

```
Python 3.10+
Nginx 1.22+
Gunicorn 21.x
SQLite 3.x (or PostgreSQL 15+)
systemd
Certbot (for SSL)
```

---

## 🛠️ Initial Setup

### Step 1: Prepare VM

```bash
# Connect to VM
ssh user@your-vm-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3 python3-pip python3-venv nginx git sqlite3

# Install Certbot for SSL
sudo apt install -y certbot python3-certbot-nginx

# Create application user
sudo useradd -m -s /bin/bash financial-app
sudo usermod -aG www-data financial-app
```

### Step 2: Create Directory Structure

```bash
# Create app directory
sudo mkdir -p /opt/financial-app
sudo chown financial-app:www-data /opt/financial-app
cd /opt/financial-app

# Create subdirectories
sudo -u financial-app mkdir -p {instance,logs,backups,uploads_temp,flask_session}
```

### Step 3: Deploy Application Files

**Option A: Using rsync (recommended)**

```bash
# From your local machine
rsync -avz --exclude-from='.gitignore' \
  --exclude='venv/' \
  --exclude='*.db' \
  --exclude='flask_session/' \
  --exclude='_temp_scripts/' \
  --exclude='changes/' \
  /path/to/ProjetoFinancasV3/ \
  user@your-vm-ip:/opt/financial-app/
```

**Option B: Using git**

```bash
# On VM
cd /opt/financial-app
sudo -u financial-app git clone https://github.com/yourusername/financial-app.git .
```

### Step 4: Setup Python Environment

```bash
# On VM as financial-app user
cd /opt/financial-app
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install production server
pip install gunicorn
```

### Step 5: Configure Environment

```bash
# Copy environment template
cp .env.production.template .env.production

# Generate SECRET_KEY
python3 -c 'import secrets; print(secrets.token_hex(32))'

# Edit .env.production with generated key
nano .env.production

# Set permissions
chmod 600 .env.production
```

**Required changes in `.env.production`:**
- `SECRET_KEY` - Use generated value
- `DATABASE_URI` - Set to `/opt/financial-app/instance/financas.db`
- `LOG_FILE` - Set to `/opt/financial-app/logs/app.log`

### Step 6: Initialize Database

**Option A: Fresh Start (recommended for new deployments)**

```bash
cd /opt/financial-app
source venv/bin/activate

# Initialize database schema
python -c "from app.models import init_db; init_db('instance/financas.db')"

# Create admin user
python scripts/create_admin_user.py
```

**Option B: Migrate Existing Data**

```bash
# Transfer database from local
scp financas.db user@your-vm-ip:/opt/financial-app/instance/

# Run migrations if needed
python scripts/migrate_to_multiuser.py
```

### Step 7: Configure Gunicorn

Create `/opt/financial-app/gunicorn_config.py`:

```python
bind = "127.0.0.1:8000"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Logging
accesslog = "/opt/financial-app/logs/gunicorn_access.log"
errorlog = "/opt/financial-app/logs/gunicorn_error.log"
loglevel = "info"

# Process naming
proc_name = "financial-app"

# Security
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190
```

### Step 8: Configure systemd Service

Create `/etc/systemd/system/financial-app.service`:

```ini
[Unit]
Description=Financial Management Flask Application
After=network.target

[Service]
Type=notify
User=financial-app
Group=www-data
WorkingDirectory=/opt/financial-app
Environment="PATH=/opt/financial-app/venv/bin"
EnvironmentFile=/opt/financial-app/.env.production
ExecStart=/opt/financial-app/venv/bin/gunicorn \
  --config /opt/financial-app/gunicorn_config.py \
  --bind 127.0.0.1:8000 \
  "app:create_app()"

Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=financial-app

[Install]
WantedBy=multi-user.target
```

```bash
# Reload systemd and enable service
sudo systemctl daemon-reload
sudo systemctl enable financial-app
sudo systemctl start financial-app

# Check status
sudo systemctl status financial-app
```

### Step 9: Configure Nginx

Create `/etc/nginx/sites-available/financial-app`:

```nginx
# HTTP (will redirect to HTTPS after SSL setup)
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    # Let's Encrypt challenge
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    # Redirect to HTTPS (after SSL setup)
    # location / {
    #     return 301 https://$server_name$request_uri;
    # }

    # Temporary HTTP access (remove after SSL setup)
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Static files
    location /static {
        alias /opt/financial-app/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/financial-app /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

### Step 10: Setup SSL with Let's Encrypt

```bash
# Obtain certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Verify auto-renewal
sudo certbot renew --dry-run
```

After SSL setup, update Nginx config to enable HTTPS redirect.

### Step 11: Configure Firewall

```bash
# Allow SSH, HTTP, HTTPS
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

### Step 12: Setup Automated Backups

```bash
# Test backup
cd /opt/financial-app
source venv/bin/activate
python scripts/backup_database.py backup --tag initial

# Setup cron job (as financial-app user)
crontab -e

# Add line (daily backup at 2 AM):
0 2 * * * /opt/financial-app/venv/bin/python /opt/financial-app/scripts/backup_database.py auto
```

---

## 🚀 Deployment Process

### Complete Deployment Script

Use the master deployment script:

```bash
# On local machine
python scripts/deploy.py --target production --check-only

# If checks pass, deploy
python scripts/deploy.py --target production
```

### Manual Deployment Steps

1. **Backup on Server**
```bash
ssh user@your-vm ' cd /opt/financial-app && source venv/bin/activate && python scripts/backup_database.py backup --tag pre-deploy-$(date +%Y%m%d)'
```

2. **Sync Files**
```bash
rsync -avz --exclude-from='.gitignore' \
  --exclude='venv/' \
  --exclude='*.db' \
  --exclude='flask_session/' \
  /path/to/ProjetoFinancasV3/ \
  user@your-vm-ip:/opt/financial-app/
```

3. **Install Dependencies (if requirements.txt changed)**
```bash
ssh user@your-vm 'cd /opt/financial-app && source venv/bin/activate && pip install -r requirements.txt'
```

4. **Restart Application**
```bash
ssh user@your-vm 'sudo systemctl restart financial-app'
```

5. **Verify**
```bash
ssh user@your-vm 'sudo systemctl status financial-app'
curl https://your-domain.com
```

---

## ✅ Post-Deployment

### Smoke Tests

```bash
# On VM
cd /opt/financial-app
source venv/bin/activate

# Run health check
python tests/deployment_health_check.py

# Check application logs
tail -f logs/app.log
tail -f logs/gunicorn_error.log
```

### Manual Testing Checklist

- [ ] Homepage loads
- [ ] Login works
- [ ] Dashboard displays data
- [ ] Upload file works
- [ ] Classification works
- [ ] Multi-user isolation works
- [ ] Logout works

### Monitor First Hours

```bash
# Watch application logs
tail -f /opt/financial-app/logs/app.log

# Watch Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Watch system resources
htop
```

---

## 💾 Backup & Recovery

### Manual Backup

```bash
cd /opt/financial-app
source venv/bin/activate

# Create backup
python scripts/backup_database.py backup --tag manual-$(date +%Y%m%d)

# List backups
python scripts/backup_database.py list
```

### Automated Backup

Backups run daily at 2 AM via cron (configured in Step 12).

### Backup to Remote Server

Setup rsync backup to external server:

```bash
# On VM, create script /opt/financial-app/scripts/remote_backup.sh
#!/bin/bash
BACKUP_DIR="/opt/financial-app/backups"
REMOTE_HOST="backup-server.example.com"
REMOTE_USER="backup_user"
REMOTE_PATH="/backups/financial-app"

rsync -avz --delete \
  -e "ssh -i /home/financial-app/.ssh/backup_key" \
  $BACKUP_DIR/ \
  $REMOTE_USER@$REMOTE_HOST:$REMOTE_PATH/

# Add to cron (daily at 3 AM)
0 3 * * * /opt/financial-app/scripts/remote_backup.sh
```

### Recovery

```bash
cd /opt/financial-app
source venv/bin/activate

# List available backups
python scripts/backup_database.py list

# Restore specific backup
python scripts/backup_database.py restore backups/financas.db.backup_YYYYMMDD_HHMMSS.gz

# Restart application
sudo systemctl restart financial-app
```

---

## 🔒 Security

### Checklist

- [x] SECRET_KEY changed from default
- [x] DEBUG=False in production
- [x] HTTPS enabled (SSL certificate)
- [x] Firewall configured (UFW)
- [x] Database outside web root
- [x] .env.production has 600 permissions
- [x] Application runs as non-root user
- [x] Security headers configured in Nginx
- [x] File upload size limited (16MB)
- [x] Session cookies secure and httponly

### Additional Recommendations

1. **Fail2ban** - Protect against brute force

```bash
sudo apt install fail2ban
sudo systemctl enable fail2ban
```

2. **Regular Updates**

```bash
# Weekly system updates
sudo apt update && sudo apt upgrade -y
```

3. **Monitor Logs**

```bash
# Setup log rotation
sudo nano /etc/logrotate.d/financial-app
```

```
/opt/financial-app/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 financial-app www-data
    sharedscripts
    postrotate
        systemctl reload financial-app > /dev/null 2>&1 || true
    endscript
}
```

---

## 🔧 Troubleshooting

### Application Won't Start

```bash
# Check service status
sudo systemctl status financial-app

# View logs
sudo journalctl -u financial-app -n 50 --no-pager

# Check configuration
cat /opt/financial-app/.env.production

# Test gunicorn manually
cd /opt/financial-app
source venv/bin/activate
gunicorn --config gunicorn_config.py "app:create_app()"
```

### Database Connection Errors

```bash
# Check database file exists
ls -la /opt/financial-app/instance/financas.db

# Check permissions
sudo chown financial-app:www-data /opt/financial-app/instance/financas.db
sudo chmod 664 /opt/financial-app/instance/financas.db

# Test database integrity
sqlite3 /opt/financial-app/instance/financas.db "PRAGMA integrity_check;"
```

### 502 Bad Gateway (Nginx)

```bash
# Check Gunicorn is running
sudo systemctl status financial-app

# Check Gunicorn is listening on correct port
sudo netstat -tulpn | grep 8000

# Check Nginx configuration
sudo nginx -t

# View Nginx error log
sudo tail -f /var/log/nginx/error.log
```

### Out of Disk Space

```bash
# Check disk usage
df -h

# Find large files
sudo du -h /opt/financial-app | sort -rh | head -20

# Clean old backups
cd /opt/financial-app
source venv/bin/activate
python scripts/backup_database.py cleanup

# Clean old logs
sudo find /opt/financial-app/logs -name "*.log.*" -mtime +30 -delete
```

### Performance Issues

```bash
# Check resource usage
htop

# Increase Gunicorn workers (edit gunicorn_config.py)
# Rule of thumb: (2 x CPU cores) + 1

# Add caching (future enhancement)
# Consider Redis for session storage
```

---

## 📞 Support & Maintenance

### Regular Maintenance Tasks

**Daily:**
- Monitor application logs
- Check backup success

**Weekly:**
- Review error logs
- Check disk space
- Test backup restore

**Monthly:**
- Update system packages
- Review security headers
- Test disaster recovery plan
- Update SSL certificates (auto via certbot)

### Useful Commands

```bash
# Restart application
sudo systemctl restart financial-app

# View logs
tail -f /opt/financial-app/logs/app.log
sudo journalctl -u financial-app -f

# Database backup
cd /opt/financial-app && source venv/bin/activate && python scripts/backup_database.py backup

# Check application status
sudo systemctl status financial-app
curl -I https://your-domain.com

# Update application
cd /opt/financial-app
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart financial-app
```

---

## 📝 Quick Reference

### File Locations

| Type | Location |
|------|----------|
| Application Code | `/opt/financial-app/` |
| Database | `/opt/financial-app/instance/financas.db` |
| Logs | `/opt/financial-app/logs/` |
| Backups | `/opt/financial-app/backups/` |
| Environment Config | `/opt/financial-app/.env.production` |
| Nginx Config | `/etc/nginx/sites-available/financial-app` |
| systemd Service | `/etc/systemd/system/financial-app.service` |

### Ports

| Service | Port |
|---------|------|
| HTTP | 80 |
| HTTPS | 443 |
| Gunicorn (internal) | 8000 |
| SSH | 22 |

### Logs

| Log Type | Location |
|----------|----------|
| Application | `/opt/financial-app/logs/app.log` |
| Gunicorn Access | `/opt/financial-app/logs/gunicorn_access.log` |
| Gunicorn Error | `/opt/financial-app/logs/gunicorn_error.log` |
| Nginx Access | `/var/log/nginx/access.log` |
| Nginx Error | `/var/log/nginx/error.log` |
| System | `journalctl -u financial-app` |

---

**Last Updated:** 02/01/2026  
**Version:** 3.0.1  
**Maintained by:** Emanuel Guerra Leandro
