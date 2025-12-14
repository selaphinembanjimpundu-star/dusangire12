# NOURISH LINK - Post-Launch Procedures

## Overview
This document outlines procedures for maintaining and operating the NOURISH LINK application after launch.

## Table of Contents

1. [Daily Procedures](#daily-procedures)
2. [Weekly Procedures](#weekly-procedures)
3. [Monthly Procedures](#monthly-procedures)
4. [Emergency Procedures](#emergency-procedures)
5. [Update Procedures](#update-procedures)
6. [Backup and Restore](#backup-and-restore)
7. [Performance Optimization](#performance-optimization)

---

## Daily Procedures

### Morning Checklist (Before Service Starts)

1. **System Status Check**
   ```bash
   # Check all services are running
   systemctl status gunicorn
   systemctl status nginx
   systemctl status postgresql
   ```

2. **Review Overnight Activity**
   - Check error logs: `tail -100 logs/error.log`
   - Review overnight orders
   - Check subscription orders generated
   - Verify payment processing

3. **Database Health**
   ```bash
   # Check database connections
   python manage.py dbshell
   # Then: SELECT count(*) FROM pg_stat_activity;
   ```

4. **Disk Space Check**
   ```bash
   df -h
   # Ensure at least 20% free space
   ```

5. **Application Health**
   ```bash
   # Run quick health check
   python manage.py pre_launch_check --skip-tests
   ```

### During Service Hours

1. **Monitor Orders**
   - Check for new orders regularly
   - Monitor order processing
   - Watch for any errors

2. **Monitor Error Logs**
   ```bash
   # Real-time error monitoring
   tail -f logs/error.log | grep ERROR
   ```

3. **Monitor Server Resources**
   - Check CPU usage: `top` or `htop`
   - Check memory: `free -h`
   - Monitor if resources are high

4. **Customer Support**
   - Respond to customer inquiries
   - Handle order issues
   - Process refunds if needed

### End of Day Checklist

1. **Complete All Orders**
   - Ensure all orders are processed
   - Update order statuses
   - Verify deliveries completed

2. **Review Daily Reports**
   - Check daily sales
   - Review popular items
   - Note any issues

3. **Backup Check**
   ```bash
   # Verify today's backup exists
   ls -lh backups/ | grep $(date +%Y%m%d)
   ```

4. **Error Review**
   - Review error logs for the day
   - Note any recurring issues
   - Document critical errors

5. **System Cleanup**
   - Clear temporary files if needed
   - Check log file sizes

---

## Weekly Procedures

### Weekly Maintenance (Recommended: Sunday Night)

1. **Comprehensive System Check**
   ```bash
   # Full system check
   python manage.py pre_launch_check
   ```

2. **Database Maintenance**
   ```bash
   # Analyze database
   python manage.py dbshell
   # Then: VACUUM ANALYZE;
   ```

3. **Log Review**
   - Review all logs for the week
   - Identify patterns or issues
   - Archive old logs if needed

4. **Performance Review**
   - Check response times
   - Review slow queries
   - Identify optimization opportunities

5. **Security Check**
   ```bash
   # Run security checks
   python manage.py check --deploy
   ```

6. **Backup Verification**
   - Verify backups are working
   - Test restore procedure (on test server)
   - Check backup file sizes

7. **Update Review**
   - Check for dependency updates
   - Review security patches
   - Plan updates if needed

### Weekly Reports

1. **Sales Report**
   - Total revenue
   - Order count
   - Average order value
   - Popular items

2. **User Activity**
   - New registrations
   - Active users
   - Subscription trends

3. **Performance Metrics**
   - Average response time
   - Error rate
   - Uptime percentage

---

## Monthly Procedures

### Monthly Maintenance

1. **Full System Audit**
   - Comprehensive system check
   - Security audit
   - Performance analysis
   - Capacity planning

2. **Database Optimization**
   ```bash
   # Full database maintenance
   python manage.py dbshell
   # Then:
   # VACUUM FULL;
   # REINDEX DATABASE dusangire;
   # ANALYZE;
   ```

3. **Log Archival**
   ```bash
   # Archive old logs
   tar -czf logs_archive_$(date +%Y%m).tar.gz logs/*.log
   # Move to archive location
   # Clear old logs (keep last month)
   ```

4. **Backup Audit**
   - Verify all backups
   - Test restore on staging
   - Review backup retention policy
   - Check backup storage

5. **Dependency Updates**
   ```bash
   # Check for updates
   pip list --outdated
   # Review and test updates
   # Update requirements.txt
   ```

6. **Menu Review**
   - Review menu performance
   - Update menu items
   - Add/remove items based on popularity
   - Update pricing if needed

7. **Subscription Review**
   - Review subscription performance
   - Analyze subscription trends
   - Update plans if needed

8. **Staff Training Review**
   - Review staff performance
   - Update training materials
   - Conduct refresher training

### Monthly Reports

1. **Financial Report**
   - Monthly revenue
   - Cost analysis
   - Profit margins

2. **Operational Report**
   - Order statistics
   - Delivery performance
   - Customer satisfaction

3. **Technical Report**
   - System uptime
   - Error analysis
   - Performance metrics
   - Security incidents

---

## Emergency Procedures

### Application Down

1. **Immediate Actions**
   ```bash
   # Check service status
   systemctl status gunicorn
   systemctl status nginx
   
   # Restart services
   sudo systemctl restart gunicorn
   sudo systemctl restart nginx
   ```

2. **Check Logs**
   ```bash
   # Check recent errors
   tail -100 logs/error.log
   journalctl -u gunicorn -n 50
   ```

3. **Database Check**
   ```bash
   # Verify database is accessible
   python manage.py dbshell
   ```

4. **If Still Down**
   - Check server resources (CPU, memory, disk)
   - Review recent changes
   - Contact technical support
   - Consider rollback if recent deployment

### Database Issues

1. **Connection Errors**
   ```bash
   # Check PostgreSQL status
   systemctl status postgresql
   
   # Restart if needed
   sudo systemctl restart postgresql
   ```

2. **Performance Issues**
   ```sql
   -- Check for locks
   SELECT * FROM pg_locks WHERE NOT granted;
   
   -- Check long-running queries
   SELECT pid, now() - query_start AS duration, query
   FROM pg_stat_activity
   WHERE state = 'active' AND now() - query_start > interval '1 minute';
   ```

3. **Corruption Issues**
   - Stop application
   - Restore from latest backup
   - Contact database administrator

### High Error Rate

1. **Identify Error Type**
   ```bash
   # Count errors by type
   grep "ERROR" logs/error.log | tail -100 | sort | uniq -c | sort -rn
   ```

2. **Temporary Fix**
   - Disable affected feature if possible
   - Add error handling
   - Increase logging

3. **Permanent Fix**
   - Investigate root cause
   - Fix in development
   - Test thoroughly
   - Deploy fix

### Security Incident

1. **Immediate Actions**
   - Isolate affected systems
   - Preserve logs
   - Document incident

2. **Assessment**
   - Determine scope
   - Identify affected data
   - Assess damage

3. **Response**
   - Fix vulnerability
   - Notify affected users if needed
   - Update security measures
   - Report if required

4. **Prevention**
   - Review security measures
   - Update procedures
   - Conduct security audit

---

## Update Procedures

### Pre-Update Checklist

1. **Backup Everything**
   ```bash
   # Backup database
   python manage.py backup_database
   
   # Backup code (if using version control)
   git tag pre-update-$(date +%Y%m%d)
   ```

2. **Test in Staging**
   - Deploy to staging first
   - Test all functionality
   - Verify no breaking changes

3. **Review Changes**
   - Review update notes
   - Check for breaking changes
   - Plan rollback if needed

### Update Process

1. **Stop Services** (if needed)
   ```bash
   sudo systemctl stop gunicorn
   ```

2. **Apply Updates**
   ```bash
   # Update code
   git pull origin main  # or your branch
   
   # Update dependencies
   pip install -r requirements.txt --upgrade
   ```

3. **Run Migrations**
   ```bash
   python manage.py migrate
   ```

4. **Collect Static Files**
   ```bash
   python manage.py collectstatic --noinput
   ```

5. **Restart Services**
   ```bash
   sudo systemctl start gunicorn
   sudo systemctl restart nginx
   ```

6. **Verify**
   - Check application is running
   - Test critical functionality
   - Monitor for errors

### Rollback Procedure

1. **Stop Services**
   ```bash
   sudo systemctl stop gunicorn
   ```

2. **Restore Code**
   ```bash
   git checkout <previous-version>
   # Or restore from backup
   ```

3. **Restore Database** (if needed)
   ```bash
   # Restore from backup
   # See backup and restore section
   ```

4. **Restart Services**
   ```bash
   sudo systemctl start gunicorn
   sudo systemctl restart nginx
   ```

---

## Backup and Restore

### Backup Procedures

**Daily Backups:**
```bash
# Automated via cron
# Add to crontab: 0 2 * * * python manage.py backup_database
```

**Manual Backup:**
```bash
python manage.py backup_database
```

**Backup Verification:**
```bash
# Check backup file exists and is recent
ls -lh backups/
```

### Restore Procedures

**SQLite Restore:**
```bash
# Stop application
sudo systemctl stop gunicorn

# Restore database
cp backups/db_backup_YYYYMMDD_HHMMSS.sqlite3 /path/to/db.sqlite3

# Set permissions
chmod 600 /path/to/db.sqlite3

# Start application
sudo systemctl start gunicorn
```

**PostgreSQL Restore:**
```bash
# Stop application
sudo systemctl stop gunicorn

# Restore database
pg_restore -h localhost -U postgres -d dusangire backups/db_backup_YYYYMMDD_HHMMSS.sql

# Start application
sudo systemctl start gunicorn
```

**Test Restore:**
- Always test restore on staging first
- Verify data integrity
- Check application functionality

---

## Performance Optimization

### Regular Optimization Tasks

1. **Database Optimization**
   - Analyze slow queries
   - Add indexes where needed
   - Remove unused data
   - Optimize queries

2. **Cache Optimization**
   - Review cache hit rates
   - Adjust cache settings
   - Clear cache if needed

3. **Static File Optimization**
   - Compress images
   - Minify CSS/JS
   - Use CDN if available

4. **Code Optimization**
   - Profile application
   - Optimize slow views
   - Reduce database queries

### Performance Monitoring

```bash
# Monitor response times
# Use application monitoring tools

# Database query analysis
python manage.py dbshell
# Then: Enable query logging
```

---

## Communication Procedures

### Customer Communication

1. **Scheduled Maintenance**
   - Notify customers in advance
   - Use email, website banner, or SMS
   - Provide estimated downtime

2. **Unexpected Downtime**
   - Notify immediately
   - Provide status updates
   - Apologize and explain

3. **Feature Updates**
   - Announce new features
   - Provide user guides
   - Gather feedback

### Internal Communication

1. **Daily Standup**
   - Review previous day
   - Plan current day
   - Address issues

2. **Weekly Meeting**
   - Review week performance
   - Plan improvements
   - Address concerns

3. **Incident Communication**
   - Notify team immediately
   - Provide status updates
   - Document resolution

---

## Documentation Updates

### Keep Updated

1. **Procedure Updates**
   - Update as processes change
   - Document new procedures
   - Remove outdated procedures

2. **Issue Documentation**
   - Document all issues
   - Record solutions
   - Update troubleshooting guides

3. **Change Log**
   - Maintain change log
   - Document all updates
   - Version procedures

---

## Summary

Post-launch procedures ensure:
- **Reliability**: System runs smoothly
- **Performance**: Optimal performance maintained
- **Security**: Security maintained and improved
- **Growth**: System scales with demand
- **Support**: Issues resolved quickly

Follow these procedures consistently and adapt as needed.
