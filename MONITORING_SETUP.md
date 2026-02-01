# Dusangire - Monitoring Setup Guide

## Overview
This guide explains how to set up monitoring and logging for the Dusangire application in production.

## Table of Contents

1. [Logging Configuration](#logging-configuration)
2. [Application Monitoring](#application-monitoring)
3. [Server Monitoring](#server-monitoring)
4. [Database Monitoring](#database-monitoring)
5. [Error Tracking](#error-tracking)
6. [Performance Monitoring](#performance-monitoring)
7. [Alerting](#alerting)

---

## Logging Configuration

### Django Logging Setup

The production settings (`settings_production.py`) already includes logging configuration. Logs are written to:

- **Application Logs**: `logs/django.log`
- **Error Logs**: `logs/error.log`
- **Console Output**: Standard output (captured by systemd/Gunicorn)

### Log Levels

- **DEBUG**: Detailed information (development only)
- **INFO**: General information
- **WARNING**: Warning messages
- **ERROR**: Error messages
- **CRITICAL**: Critical errors

### Log Rotation

Logs are automatically rotated:
- **Max Size**: 10 MB per file
- **Backup Count**: 5 backup files
- **Rotation**: When file reaches max size

### Viewing Logs

```bash
# View application logs
tail -f logs/django.log

# View error logs
tail -f logs/error.log

# View last 100 lines
tail -n 100 logs/django.log

# Search logs
grep "ERROR" logs/django.log
```

### Log Directory Setup

Ensure logs directory exists:
```bash
mkdir -p logs
chmod 755 logs
```

---

## Application Monitoring

### Health Check Endpoint

Create a simple health check endpoint (optional):

```python
# In your main urls.py
from django.http import JsonResponse

def health_check(request):
    return JsonResponse({'status': 'healthy', 'service': 'nourish-link'})
```

### Monitoring Key Metrics

**1. Error Rate**
- Monitor error logs for frequency
- Target: < 1% error rate
- Alert if error rate exceeds threshold

**2. Response Time**
- Monitor page load times
- Target: < 3 seconds for most pages
- Alert if response time exceeds threshold

**3. Request Volume**
- Monitor number of requests
- Track peak times
- Plan capacity accordingly

**4. Database Performance**
- Monitor query execution time
- Check for slow queries
- Monitor connection pool usage

### Manual Monitoring Commands

```bash
# Check application status
systemctl status gunicorn

# Check recent errors
grep "ERROR" logs/error.log | tail -20

# Check request patterns
grep "GET\|POST" logs/django.log | tail -50

# Monitor real-time
tail -f logs/django.log | grep -E "ERROR|WARNING"
```

---

## Server Monitoring

### System Resources

Monitor these server metrics:

**1. CPU Usage**
```bash
# Current CPU usage
top
# Or
htop

# CPU usage over time
iostat -c 1 5
```

**2. Memory Usage**
```bash
# Memory usage
free -h

# Detailed memory
cat /proc/meminfo
```

**3. Disk Usage**
```bash
# Disk space
df -h

# Disk I/O
iostat -d 1 5
```

**4. Network Traffic**
```bash
# Network statistics
netstat -i

# Network connections
netstat -an | grep ESTABLISHED
```

### Automated Monitoring Tools

**Option 1: Using systemd (Built-in)**
```bash
# View service status
systemctl status gunicorn
systemctl status nginx
systemctl status postgresql

# View service logs
journalctl -u gunicorn -f
journalctl -u nginx -f
```

**Option 2: Using htop/atop**
```bash
# Install monitoring tools
sudo apt install htop atop

# Run htop
htop

# Run atop (logs system stats)
atop
```

**Option 3: Using Prometheus + Grafana (Advanced)**
- Set up Prometheus for metrics collection
- Set up Grafana for visualization
- Configure exporters for Django, PostgreSQL, Nginx

---

## Database Monitoring

### PostgreSQL Monitoring

**1. Connection Monitoring**
```sql
-- Check active connections
SELECT count(*) FROM pg_stat_activity;

-- Check connection details
SELECT datname, usename, application_name, state 
FROM pg_stat_activity;
```

**2. Query Performance**
```sql
-- Enable query logging in postgresql.conf
log_min_duration_statement = 1000  -- Log queries > 1 second

-- View slow queries
SELECT query, calls, total_time, mean_time 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;
```

**3. Database Size**
```sql
-- Database size
SELECT pg_size_pretty(pg_database_size('dusangire'));

-- Table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

**4. Database Health**
```sql
-- Check for locks
SELECT * FROM pg_locks WHERE NOT granted;

-- Check for long-running queries
SELECT pid, now() - pg_stat_activity.query_start AS duration, query
FROM pg_stat_activity
WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes';
```

### Database Backup Monitoring

```bash
# Check backup script execution
ls -lh backups/

# Verify backup integrity
pg_restore --list backups/db_backup_*.sql | head -20
```

---

## Error Tracking

### Django Error Logging

Errors are automatically logged to `logs/error.log`. Monitor for:

1. **500 Errors**: Server errors
2. **404 Errors**: Not found errors
3. **403 Errors**: Permission denied
4. **Database Errors**: Connection or query errors
5. **Payment Errors**: Payment gateway issues

### Error Alerting

Set up email alerts for critical errors (configured in `settings_production.py`):

```python
# In settings_production.py
ADMINS = [
    ('Admin Name', 'admin@example.com'),
]
```

### Error Analysis

```bash
# Count errors by type
grep "ERROR" logs/error.log | awk '{print $5}' | sort | uniq -c | sort -rn

# Find most common errors
grep "ERROR" logs/error.log | tail -100 | sort | uniq -c | sort -rn | head -10

# Track error trends
grep "ERROR" logs/error.log | cut -d' ' -f1-3 | uniq -c
```

---

## Performance Monitoring

### Application Performance

**1. Response Time Monitoring**
- Use Django Debug Toolbar (development)
- Monitor slow endpoints
- Optimize database queries

**2. Database Query Monitoring**
```python
# Enable query logging in settings
LOGGING = {
    'loggers': {
        'django.db.backends': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
    },
}
```

**3. Static File Performance**
- Monitor static file serving
- Check CDN performance (if used)
- Verify file compression

### Performance Metrics to Track

- **Page Load Time**: Target < 3 seconds
- **Database Query Time**: Target < 100ms per query
- **API Response Time**: Target < 500ms
- **Static File Load Time**: Target < 1 second

---

## Alerting

### Email Alerts

Configured in `settings_production.py`:
- Critical errors sent to ADMINS
- Email backend configured
- SMTP settings required

### Manual Alert Checks

Create a monitoring script:

```bash
#!/bin/bash
# check_system.sh

# Check if services are running
if ! systemctl is-active --quiet gunicorn; then
    echo "ALERT: Gunicorn is not running!"
fi

if ! systemctl is-active --quiet nginx; then
    echo "ALERT: Nginx is not running!"
fi

# Check disk space
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "ALERT: Disk usage is ${DISK_USAGE}%"
fi

# Check error rate
ERROR_COUNT=$(grep -c "ERROR" logs/error.log)
if [ $ERROR_COUNT -gt 100 ]; then
    echo "ALERT: High error count: ${ERROR_COUNT}"
fi
```

### Cron Job for Monitoring

```bash
# Add to crontab (crontab -e)
# Check system every 5 minutes
*/5 * * * * /path/to/check_system.sh >> /var/log/system_check.log 2>&1

# Daily backup check
0 2 * * * /path/to/check_backups.sh
```

---

## Monitoring Checklist

### Daily Checks
- [ ] Review error logs
- [ ] Check application status
- [ ] Monitor server resources
- [ ] Check for critical errors

### Weekly Checks
- [ ] Review performance metrics
- [ ] Analyze error trends
- [ ] Check database performance
- [ ] Review backup status

### Monthly Checks
- [ ] Review log file sizes
- [ ] Analyze usage patterns
- [ ] Review and optimize queries
- [ ] Update monitoring procedures

---

## Third-Party Monitoring Services (Optional)

### Recommended Services

1. **Sentry** (Error Tracking)
   - Real-time error tracking
   - Stack traces
   - Release tracking
   - Setup: `pip install sentry-sdk`

2. **New Relic** (APM)
   - Application performance monitoring
   - Database monitoring
   - Real user monitoring

3. **Datadog** (Full Stack Monitoring)
   - Infrastructure monitoring
   - Application monitoring
   - Log management

4. **Uptime Robot** (Uptime Monitoring)
   - Website uptime monitoring
   - Alert notifications
   - Free tier available

---

## Best Practices

1. **Log Everything Important**: But not too much
2. **Monitor Key Metrics**: Focus on what matters
3. **Set Up Alerts**: For critical issues
4. **Regular Reviews**: Review logs and metrics regularly
5. **Document Issues**: Keep track of recurring issues
6. **Automate Monitoring**: Use scripts and tools
7. **Test Alerts**: Ensure alerts work correctly

---

## Troubleshooting

### Logs Not Being Created
- Check directory permissions
- Verify logging configuration
- Check disk space

### Too Many Logs
- Adjust log levels
- Implement log rotation
- Filter unnecessary logs

### Alerts Not Working
- Verify email configuration
- Check SMTP settings
- Test email delivery

---

## Summary

Monitoring is essential for:
- **Early Problem Detection**: Catch issues before they become critical
- **Performance Optimization**: Identify bottlenecks
- **Capacity Planning**: Plan for growth
- **Security**: Detect suspicious activity
- **Reliability**: Ensure system availability

Set up monitoring before launch and maintain it continuously.














