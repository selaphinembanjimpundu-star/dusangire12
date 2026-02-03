# Quick Fix for PythonAnywhere Foreign Key Error

## Error You're Getting
```
django.db.utils.IntegrityError: The row in table 'orders_order' with primary key '1' 
has an invalid foreign key: orders_order.delivery_address_id contains a value 'ward 3' 
that does not have a corresponding value in delivery_deliveryaddress.id.
```

## Quick Fix (3 Steps)

### Step 1: Go to PythonAnywhere Bash Console
- Open your PythonAnywhere dashboard
- Click **Bash** (under "Consoles" section)

### Step 2: Navigate to Project and Activate Venv
```bash
cd ~/dusangire12
source ../../virtualenvs/dusangire_env/bin/activate
```

### Step 3: Run the Fix Script
```bash
python pythonanywhere_fix_db.py
```

Expected output:
```
==================================================
PythonAnywhere Database Integrity Fix
==================================================

1️⃣  Checking existing delivery addresses...
   ✓ ID: [address_id], Name: [address_name]

2️⃣  Checking for problematic orders...
   ✓ Fixed! Updated from 'ward 3' → [correct_id]
```

### Step 4: Run Migrations
```bash
python manage.py migrate
```

### Step 5: Run Django Checks
```bash
python manage.py check
```

Should show: `System check identified no issues (0 silenced).`

### Step 6: Reload Web App
1. Go back to **Web** tab on PythonAnywhere
2. Click **Reload** button
3. Your app should now work!

## If Script Doesn't Work

Try manual SQL fix:
```bash
python manage.py dbshell
```

Then run (in SQLite shell):
```sql
SELECT * FROM delivery_deliveryaddress;
SELECT * FROM orders_order WHERE id = 1;

-- Delete the broken order
DELETE FROM orders_order WHERE id = 1;

.exit
```

Then try migrations again:
```bash
python manage.py migrate
```

## Alternative: Nuclear Option (Last Resort)
```bash
# Delete entire database and start fresh
rm -f db.sqlite3

# Create new database
python manage.py migrate

# Reload web app
```

**Warning:** This will delete ALL data! Only use if nothing else works.
