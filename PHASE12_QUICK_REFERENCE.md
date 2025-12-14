# Phase 12: Launch - Quick Reference Guide

## Pre-Launch Checklist

### 1. Run Pre-Launch Check
```bash
python manage.py pre_launch_check
```

### 2. Seed Initial Data
```bash
# Seed everything
python manage.py seed_all

# Or seed individually
python manage.py seed_menu
python manage.py seed_initial_data
```

### 3. Create Superuser
```bash
python manage.py createsuperuser
```

### 4. Collect Static Files
```bash
python manage.py collectstatic --noinput
```

### 5. Run Migrations
```bash
python manage.py migrate
```

### 6. Run Tests
```bash
python manage.py test
```

### 7. Security Check
```bash
python manage.py check --deploy
```

---

## Launch Day Commands

### Before Launch
```bash
# Final backup
python manage.py backup_database

# Final pre-launch check
python manage.py pre_launch_check

# Verify services
systemctl status gunicorn
systemctl status nginx
systemctl status postgresql
```

### After Launch
```bash
# Monitor logs
tail -f logs/django.log
tail -f logs/error.log

# Check application
curl http://localhost:8000
```

---

## Daily Operations

### Morning Checklist
```bash
# Check services
systemctl status gunicorn nginx postgresql

# Check errors
tail -100 logs/error.log

# Check disk space
df -h
```

### Backup
```bash
# Daily backup
python manage.py backup_database
```

### Monitoring
```bash
# View logs
tail -f logs/django.log
tail -f logs/error.log

# Check system resources
htop
free -h
```

---

## Common Management Commands

### Database
```bash
# Backup
python manage.py backup_database

# Restore
python manage.py restore_database backups/db_backup_YYYYMMDD_HHMMSS.sql

# Migrations
python manage.py migrate
python manage.py showmigrations
```

### Data Seeding
```bash
# Seed all
python manage.py seed_all

# Seed menu only
python manage.py seed_menu

# Seed subscriptions only
python manage.py seed_initial_data
```

### Testing
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test accounts
python manage.py test menu
python manage.py test orders

# Pre-launch check
python manage.py pre_launch_check
```

### System Checks
```bash
# Django checks
python manage.py check

# Security check
python manage.py check --deploy
```

---

## Emergency Procedures

### Application Down
```bash
# Restart services
sudo systemctl restart gunicorn
sudo systemctl restart nginx

# Check logs
journalctl -u gunicorn -n 50
tail -100 logs/error.log
```

### Database Issues
```bash
# Check PostgreSQL
systemctl status postgresql
sudo systemctl restart postgresql

# Restore from backup
python manage.py restore_database backups/latest_backup.sql
```

### High Error Rate
```bash
# Check error logs
grep "ERROR" logs/error.log | tail -50

# Count errors
grep -c "ERROR" logs/error.log
```

---

## File Locations

### Important Files
- **Settings**: `dusangire/settings_production.py`
- **Environment**: `.env`
- **Logs**: `logs/django.log`, `logs/error.log`
- **Backups**: `backups/`
- **Static Files**: `staticfiles/`

### Documentation
- **Deployment**: `DEPLOYMENT_GUIDE.md`
- **Staff Training**: `STAFF_TRAINING_GUIDE.md`
- **Monitoring**: `MONITORING_SETUP.md`
- **Post-Launch**: `POST_LAUNCH_PROCEDURES.md`
- **Data Seeding**: `INITIAL_DATA_SEEDING.md`

---

## Service Management

### Gunicorn
```bash
# Start
sudo systemctl start gunicorn

# Stop
sudo systemctl stop gunicorn

# Restart
sudo systemctl restart gunicorn

# Status
systemctl status gunicorn

# Logs
journalctl -u gunicorn -f
```

### Nginx
```bash
# Start
sudo systemctl start nginx

# Stop
sudo systemctl stop nginx

# Restart
sudo systemctl restart nginx

# Status
systemctl status nginx

# Test config
sudo nginx -t

# Logs
tail -f /var/log/nginx/error.log
tail -f /var/log/nginx/access.log
```

### PostgreSQL
```bash
# Start
sudo systemctl start postgresql

# Stop
sudo systemctl stop postgresql

# Restart
sudo systemctl restart postgresql

# Status
systemctl status postgresql

# Access database
python manage.py dbshell
```

---

## Useful Commands

### View Logs
```bash
# Application logs
tail -f logs/django.log

# Error logs
tail -f logs/error.log

# Gunicorn logs
journalctl -u gunicorn -f

# Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### System Resources
```bash
# CPU and memory
top
htop

# Disk usage
df -h
du -sh *

# Network
netstat -tulpn
```

### Database
```bash
# Connect to database
python manage.py dbshell

# Database size
python manage.py dbshell
# Then: SELECT pg_size_pretty(pg_database_size('dusangire'));

# Active connections
python manage.py dbshell
# Then: SELECT count(*) FROM pg_stat_activity;
```

---

## Quick Troubleshooting

### Can't Access Application
1. Check services: `systemctl status gunicorn nginx`
2. Check logs: `tail -100 logs/error.log`
3. Check firewall: `sudo ufw status`
4. Check port: `netstat -tulpn | grep :80`

### Database Connection Error
1. Check PostgreSQL: `systemctl status postgresql`
2. Check credentials in `.env`
3. Test connection: `python manage.py dbshell`

### Static Files Not Loading
1. Collect static: `python manage.py collectstatic`
2. Check permissions: `ls -la staticfiles/`
3. Check Nginx config

### High Memory Usage
1. Check processes: `top`
2. Restart services: `sudo systemctl restart gunicorn`
3. Check for memory leaks in logs

---

## Contact Information

- **System Admin**: [Your Contact]
- **Database Admin**: [Your Contact]
- **Development Team**: [Your Contact]
- **Hosting Provider**: [Your Contact]

---

## Notes

- Always backup before major changes
- Test in staging before production
- Monitor closely after deployment
- Document all issues and solutions
- Keep this guide updated
