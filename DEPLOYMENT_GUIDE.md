# Dusangire Restaurant - Deployment Guide

This guide provides step-by-step instructions for deploying the Dusangire Restaurant application to production.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Server Setup](#server-setup)
3. [Application Deployment](#application-deployment)
4. [Database Setup](#database-setup)
5. [Static Files Configuration](#static-files-configuration)
6. [Web Server Configuration](#web-server-configuration)
7. [SSL Certificate Setup](#ssl-certificate-setup)
8. [Post-Deployment Tasks](#post-deployment-tasks)
9. [Monitoring and Maintenance](#monitoring-and-maintenance)

## Prerequisites

### Required Software

- Python 3.10 or higher
- PostgreSQL 12 or higher
- Nginx (or Apache)
- Gunicorn
- Git
- Virtual environment (venv)

### Required Accounts

- Domain name (optional but recommended)
- SSL certificate (Let's Encrypt recommended)
- Email service (for notifications)

## Server Setup

### 1. Update System Packages

```bash
sudo apt update
sudo apt upgrade -y
```

### 2. Install Python and Required Packages

```bash
sudo apt install python3 python3-pip python3-venv python3-dev -y
sudo apt install postgresql postgresql-contrib -y
sudo apt install nginx -y
sudo apt install git -y
```

### 3. Create Application User

```bash
sudo adduser dusangire
sudo usermod -aG sudo dusangire
su - dusangire
```

## Application Deployment

### 1. Clone Repository

```bash
cd /home/dusangire
git clone https://github.com/Rukundojeandedieu67/Dusangire.git
cd Dusangire
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Create Environment File

```bash
cp .env.example .env
nano .env
```

Update the following variables:
- `SECRET_KEY`: Generate a new secret key (use `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)
- `DEBUG=False`
- `ALLOWED_HOSTS`: Your domain name(s), e.g., `dusangire.com,www.dusangire.com`
- Database credentials
- Email configuration

### 5. Configure Production Settings

The application uses `settings_production.py` for production. Update `dusangire/wsgi.py`:

```python
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dusangire.settings_production')

application = get_wsgi_application()
```

## Database Setup

### 1. Create PostgreSQL Database

```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE dusangire;
CREATE USER dusangire WITH PASSWORD 'your-secure-password';
ALTER ROLE dusangire SET client_encoding TO 'utf8';
ALTER ROLE dusangire SET default_transaction_isolation TO 'read committed';
ALTER ROLE dusangire SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE dusangire TO dusangire;
\q
```

### 2. Run Migrations

```bash
cd /home/dusangire/Dusangire
source venv/bin/activate
python manage.py migrate
```

### 3. Create Superuser

```bash
python manage.py createsuperuser
```

### 4. Load Initial Data (Optional)

```bash
python manage.py loaddata initial_data.json  # If you have fixture files
```

## Static Files Configuration

### 1. Collect Static Files

```bash
python manage.py collectstatic --noinput
```

This will create a `staticfiles` directory with all static files.

### 2. Verify Static Files

```bash
ls -la staticfiles/
```

## Web Server Configuration

### 1. Create Gunicorn Service

Create `/etc/systemd/system/dusangire.service`:

```ini
[Unit]
Description=Dusangire Restaurant Gunicorn daemon
After=network.target

[Service]
User=dusangire
Group=www-data
WorkingDirectory=/home/dusangire/Dusangire
Environment="PATH=/home/dusangire/Dusangire/venv/bin"
ExecStart=/home/dusangire/Dusangire/venv/bin/gunicorn \
    --access-logfile - \
    --workers 3 \
    --bind unix:/home/dusangire/Dusangire/dusangire.sock \
    dusangire.wsgi:application

[Install]
WantedBy=multi-user.target
```

### 2. Start and Enable Service

```bash
sudo systemctl daemon-reload
sudo systemctl start dusangire
sudo systemctl enable dusangire
sudo systemctl status dusangire
```

### 3. Configure Nginx

Create `/etc/nginx/sites-available/dusangire`:

```nginx
server {
    listen 80;
    server_name dusangire.com www.dusangire.com;

    # Redirect HTTP to HTTPS (after SSL setup)
    # return 301 https://$server_name$request_uri;

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/dusangire/Dusangire/dusangire.sock;
    }

    location /static/ {
        alias /home/dusangire/Dusangire/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /home/dusangire/Dusangire/media/;
        expires 7d;
        add_header Cache-Control "public";
    }
}
```

### 4. Enable Nginx Site

```bash
sudo ln -s /etc/nginx/sites-available/dusangire /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## SSL Certificate Setup

### 1. Install Certbot

```bash
sudo apt install certbot python3-certbot-nginx -y
```

### 2. Obtain SSL Certificate

```bash
sudo certbot --nginx -d dusangire.com -d www.dusangire.com
```

### 3. Auto-Renewal

Certbot automatically sets up auto-renewal. Test it:

```bash
sudo certbot renew --dry-run
```

### 4. Update Nginx Configuration

After SSL setup, update Nginx config to redirect HTTP to HTTPS:

```nginx
server {
    listen 80;
    server_name dusangire.com www.dusangire.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name dusangire.com www.dusangire.com;

    ssl_certificate /etc/letsencrypt/live/dusangire.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/dusangire.com/privkey.pem;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/dusangire/Dusangire/dusangire.sock;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /home/dusangire/Dusangire/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /home/dusangire/Dusangire/media/;
        expires 7d;
        add_header Cache-Control "public";
    }
}
```

## Post-Deployment Tasks

### 1. Set Up Logging

```bash
mkdir -p /home/dusangire/Dusangire/logs
chmod 755 /home/dusangire/Dusangire/logs
```

### 2. Set Up Cron Jobs

For subscription order generation:

```bash
crontab -e
```

Add:
```
# Generate subscription orders daily at 2 AM
0 2 * * * cd /home/dusangire/Dusangire && /home/dusangire/Dusangire/venv/bin/python manage.py generate_subscription_orders
```

### 3. Set Up Backups

Create backup script `/home/dusangire/backup.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/home/dusangire/backups"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# Database backup
pg_dump -U dusangire dusangire > $BACKUP_DIR/db_$DATE.sql

# Media files backup
tar -czf $BACKUP_DIR/media_$DATE.tar.gz /home/dusangire/Dusangire/media/

# Keep only last 7 days of backups
find $BACKUP_DIR -type f -mtime +7 -delete
```

Make executable:
```bash
chmod +x /home/dusangire/backup.sh
```

Add to crontab (daily at 3 AM):
```
0 3 * * * /home/dusangire/backup.sh
```

### 4. Test Application

1. Visit your domain
2. Test user registration
3. Test menu browsing
4. Test order placement
5. Test admin panel

## Monitoring and Maintenance

### 1. Check Application Status

```bash
sudo systemctl status dusangire
sudo systemctl status nginx
```

### 2. View Logs

```bash
# Application logs
tail -f /home/dusangire/Dusangire/logs/django.log

# Gunicorn logs
sudo journalctl -u dusangire -f

# Nginx logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

### 3. Update Application

```bash
cd /home/dusangire/Dusangire
source venv/bin/activate
git pull
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart dusangire
```

### 4. Database Maintenance

```bash
# Connect to database
sudo -u postgres psql dusangire

# Vacuum database
VACUUM ANALYZE;
```

## Troubleshooting

### Application Not Starting

1. Check Gunicorn service: `sudo systemctl status dusangire`
2. Check logs: `sudo journalctl -u dusangire -n 50`
3. Verify environment variables in `.env`
4. Check database connection

### Static Files Not Loading

1. Verify `collectstatic` was run
2. Check Nginx configuration for `/static/` location
3. Verify file permissions: `chmod -R 755 staticfiles/`

### Database Connection Issues

1. Verify PostgreSQL is running: `sudo systemctl status postgresql`
2. Check database credentials in `.env`
3. Verify user permissions in PostgreSQL

## Security Checklist

- [ ] `DEBUG = False` in production settings
- [ ] `SECRET_KEY` is set via environment variable
- [ ] `ALLOWED_HOSTS` is configured correctly
- [ ] SSL certificate is installed and valid
- [ ] Database password is strong
- [ ] File permissions are set correctly
- [ ] Firewall is configured (UFW recommended)
- [ ] Regular backups are set up
- [ ] Security headers are enabled
- [ ] Admin panel is protected

## Additional Resources

- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)

## Support

For issues or questions, please contact the development team or create an issue on GitHub.

