# Database Migration Guide

This guide explains how to handle database migrations in the Dusangire Restaurant application.

## Overview

Django migrations are used to manage database schema changes. This guide covers:
- Creating migrations
- Applying migrations
- Rolling back migrations
- Handling migration conflicts
- Production migration procedures

## Basic Migration Commands

### 1. Create Migrations

After modifying models, create migrations:

```bash
python manage.py makemigrations
```

Create migrations for a specific app:

```bash
python manage.py makemigrations accounts
python manage.py makemigrations menu
python manage.py makemigrations orders
```

### 2. View Migration Status

Check which migrations have been applied:

```bash
python manage.py showmigrations
```

### 3. Apply Migrations

Apply all pending migrations:

```bash
python manage.py migrate
```

Apply migrations for a specific app:

```bash
python manage.py migrate accounts
python manage.py migrate menu
```

### 4. Rollback Migrations

Rollback to a specific migration:

```bash
python manage.py migrate app_name migration_number
```

Example:
```bash
python manage.py migrate accounts 0001
```

## Migration Workflow

### Development

1. **Make Model Changes**
   ```python
   # In models.py
   class MenuItem(models.Model):
       # ... existing fields ...
       new_field = models.CharField(max_length=100)  # New field
   ```

2. **Create Migration**
   ```bash
   python manage.py makemigrations menu
   ```

3. **Review Migration File**
   - Check `menu/migrations/XXXX_add_new_field.py`
   - Verify the changes are correct

4. **Apply Migration**
   ```bash
   python manage.py migrate menu
   ```

5. **Test Changes**
   - Run tests: `python manage.py test`
   - Test manually in development

### Production

1. **Backup Database**
   ```bash
   pg_dump -U dusangire dusangire > backup_$(date +%Y%m%d).sql
   ```

2. **Review Migrations**
   ```bash
   python manage.py showmigrations
   ```

3. **Apply Migrations**
   ```bash
   python manage.py migrate
   ```

4. **Verify**
   - Check application is working
   - Verify data integrity
   - Check logs for errors

## Migration Files Structure

Each migration file contains:
- **Dependencies**: Other migrations this depends on
- **Operations**: Database operations to perform
- **Forward migration**: Changes to apply
- **Reverse migration**: How to undo changes

Example:
```python
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('menu', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='menuitem',
            name='ingredients',
            field=models.TextField(blank=True, help_text='List of ingredients'),
        ),
    ]
```

## Handling Migration Conflicts

### Scenario 1: Divergent Migrations

If two developers create migrations with the same number:

1. **Identify Conflict**
   ```bash
   python manage.py showmigrations
   ```

2. **Rename Migration**
   ```bash
   # Rename the migration file
   mv menu/migrations/0002_auto_20240101_1200.py menu/migrations/0002_auto_20240101_1300.py
   ```

3. **Update Dependencies**
   Edit the migration file to update dependencies if needed.

4. **Apply**
   ```bash
   python manage.py migrate
   ```

### Scenario 2: Merge Migrations

If you need to merge multiple migrations:

1. **Create Empty Migration**
   ```bash
   python manage.py makemigrations --empty menu
   ```

2. **Edit Migration File**
   Copy operations from conflicting migrations into the new one.

3. **Delete Conflicting Migrations**
   Remove the old migration files.

4. **Update Dependencies**
   Ensure dependencies are correct.

## Data Migrations

For complex data changes, create data migrations:

```bash
python manage.py makemigrations --empty menu
```

Edit the migration file:

```python
from django.db import migrations

def update_prices(apps, schema_editor):
    MenuItem = apps.get_model('menu', 'MenuItem')
    for item in MenuItem.objects.all():
        item.price = item.price * Decimal('1.1')  # 10% increase
        item.save()

def reverse_update_prices(apps, schema_editor):
    MenuItem = apps.get_model('menu', 'MenuItem')
    for item in MenuItem.objects.all():
        item.price = item.price / Decimal('1.1')
        item.save()

class Migration(migrations.Migration):
    dependencies = [
        ('menu', '0003_previous_migration'),
    ]

    operations = [
        migrations.RunPython(update_prices, reverse_update_prices),
    ]
```

## Production Migration Checklist

Before running migrations in production:

- [ ] **Backup Database**
  ```bash
  pg_dump -U dusangire dusangire > backup_$(date +%Y%m%d_%H%M%S).sql
  ```

- [ ] **Test Migrations Locally**
  - Use production database copy
  - Test rollback procedures

- [ ] **Schedule Maintenance Window**
  - Notify users if needed
  - Plan for downtime if required

- [ ] **Review Migration Files**
  - Check for data loss risks
  - Verify foreign key constraints
  - Check for index creation

- [ ] **Apply Migrations**
  ```bash
  python manage.py migrate
  ```

- [ ] **Verify Application**
  - Test critical features
  - Check admin panel
  - Verify data integrity

- [ ] **Monitor Logs**
  ```bash
  tail -f logs/django.log
  ```

## Common Migration Operations

### Adding a Field

```python
# models.py
class MenuItem(models.Model):
    # ... existing fields ...
    new_field = models.CharField(max_length=100, default='')
```

```bash
python manage.py makemigrations
python manage.py migrate
```

### Removing a Field

```python
# Remove field from models.py
# Then:
python manage.py makemigrations
python manage.py migrate
```

### Changing Field Type

```python
# models.py - Change field type
price = models.DecimalField(max_digits=12, decimal_places=2)  # Was max_digits=10
```

```bash
python manage.py makemigrations
# Review migration - may need data migration
python manage.py migrate
```

### Adding Index

```python
# models.py
class MenuItem(models.Model):
    name = models.CharField(max_length=200, db_index=True)
```

```bash
python manage.py makemigrations
python manage.py migrate
```

## Troubleshooting

### Migration Won't Apply

1. **Check Dependencies**
   ```bash
   python manage.py showmigrations
   ```

2. **Fake Migration** (if already applied manually)
   ```bash
   python manage.py migrate --fake app_name migration_number
   ```

3. **Reset App** (last resort, loses data)
   ```bash
   python manage.py migrate app_name zero
   python manage.py migrate app_name
   ```

### Migration Conflicts

1. **Identify Conflicting Migrations**
   ```bash
   python manage.py showmigrations
   ```

2. **Resolve Manually**
   - Edit migration files
   - Update dependencies
   - Merge operations if needed

### Data Loss Warnings

If Django warns about data loss:

1. **Review Migration**
   - Check what data will be lost
   - Create data migration to preserve data

2. **Backup First**
   ```bash
   pg_dump -U dusangire dusangire > backup.sql
   ```

3. **Proceed Carefully**
   - Test in development first
   - Have rollback plan ready

## Best Practices

1. **Always Backup Before Migrations**
   - Especially in production
   - Keep multiple backups

2. **Test Migrations Locally**
   - Use production data copy
   - Test rollback procedures

3. **Review Migration Files**
   - Check for errors
   - Verify operations

4. **Use Transactions**
   - Django migrations are transactional by default
   - PostgreSQL supports DDL transactions

5. **Version Control**
   - Commit migration files
   - Don't delete migration files
   - Tag releases with migrations

6. **Document Breaking Changes**
   - Note in migration comments
   - Update documentation

## Migration Files in This Project

Current migration files:
- `accounts/migrations/`: User and profile migrations
- `menu/migrations/`: Menu, category, dietary tag migrations
- `orders/migrations/`: Cart and order migrations
- `delivery/migrations/`: Delivery address and zone migrations
- `payments/migrations/`: Payment migrations
- `subscriptions/migrations/`: Subscription migrations
- `loyalty/migrations/`: Loyalty points migrations
- `notifications/migrations/`: Notification migrations
- `reviews/migrations/`: Review migrations
- `support/migrations/`: Support ticket migrations

## Additional Resources

- [Django Migrations Documentation](https://docs.djangoproject.com/en/stable/topics/migrations/)
- [PostgreSQL Backup and Restore](https://www.postgresql.org/docs/current/backup.html)
- [Django Migration Operations](https://docs.djangoproject.com/en/stable/ref/migration-operations/)

