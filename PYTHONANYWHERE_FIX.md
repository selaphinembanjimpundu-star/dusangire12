# PythonAnywhere Database Fix Instructions

## Problem
```
django.db.utils.IntegrityError: The row in table 'orders_order' with primary key '1' 
has an invalid foreign key: orders_order.delivery_address_id contains a value 'ward 3' 
that does not have a corresponding value in delivery_deliveryaddress.id.
```

## Root Cause
An order was created with a delivery_address_id that no longer exists in the database.

## Solution

### Quick Fix (Recommended)
Run this on PythonAnywhere bash console:

```bash
cd ~/dusangire12
source ../../../virtualenvs/dusangire_env/bin/activate
python pythonanywhere_fix_db.py
```

### What This Does
1. ✓ Identifies the problematic order (Order ID 1)
2. ✓ Assigns it a valid delivery address
3. ✓ Creates any pending migrations
4. ✓ Runs migrations
5. ✓ Performs system checks

### Manual Fix (Alternative)

If the script doesn't work, do this manually:

```bash
cd ~/dusangire12
source ../../../virtualenvs/dusangire_env/bin/activate

# Open Django shell
python manage.py shell

# Run these commands in the shell:
from orders.models import Order
from delivery.models import DeliveryAddress

# Get the first available delivery address
first_address = DeliveryAddress.objects.first()

# Fix the problematic order
order = Order.objects.get(id=1)
order.delivery_address = first_address
order.save()

# Exit shell
exit()
```

Then run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

### After Fixing

1. **Reload Web App** - Go to PythonAnywhere Dashboard:
   - Click your web app
   - Click "Reload" button
   
2. **Verify** - Visit your site and check it loads without errors

3. **Check Logs** - If still having issues:
   - Go to PythonAnywhere Dashboard
   - Click your web app
   - View "Error log" at the bottom

## Files Included
- `pythonanywhere_fix_db.py` - Main fix script (easy to run)
- `pythonanywhere_fix_db.sh` - Bash wrapper script
- `PYTHONANYWHERE_FIX.md` - This file

## Questions?
Check these locations for more info:
- PythonAnywhere Error Log: Dashboard > Web app > Error log
- Django Migrations: `hospital_wards/migrations/0004_notificationpreferences.py`
- Local fix reference: `fix_order_delivery.py`
