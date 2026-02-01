# Dusangire - Initial Data Seeding Guide

## Overview
This guide explains how to seed the database with initial data for production launch, including menu items, subscription plans, delivery zones, and other essential data.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Seeding Commands](#seeding-commands)
3. [Menu Data Seeding](#menu-data-seeding)
4. [Subscription Plans Seeding](#subscription-plans-seeding)
5. [Delivery Zones Seeding](#delivery-zones-seeding)
6. [Payment Methods](#payment-methods)
7. [Complete Seeding Process](#complete-seeding-process)
8. [Verification](#verification)
9. [Customization](#customization)

---

## Prerequisites

Before seeding data:

1. **Database Setup**
   ```bash
   # Ensure database is created and migrations are applied
   python manage.py migrate
   ```

2. **Superuser Account**
   ```bash
   # Create superuser for admin access
   python manage.py createsuperuser
   ```

3. **Static Files** (if using images)
   ```bash
   # Collect static files
   python manage.py collectstatic
   ```

---

## Seeding Commands

### Master Seeding Command

The easiest way to seed all initial data:

```bash
# Seed everything (menu + subscriptions + delivery zones)
python manage.py seed_all

# Clear existing data and reseed
python manage.py seed_all --clear

# Seed only menu data
python manage.py seed_all --menu-only

# Seed only subscription plans and delivery zones
python manage.py seed_all --subscriptions-only
```

### Individual Commands

```bash
# Seed menu items, categories, and dietary tags
python manage.py seed_menu

# Clear and reseed menu
python manage.py seed_menu --clear

# Seed subscription plans and delivery zones
python manage.py seed_initial_data

# Clear and reseed subscriptions
python manage.py seed_initial_data --clear
```

---

## Menu Data Seeding

### What Gets Created

1. **Categories**
   - Breakfast
   - Lunch
   - Dinner
   - Snacks
   - Beverages

2. **Dietary Tags**
   - Diabetic-friendly
   - Low-sodium
   - High-protein
   - Vegetarian
   - Vegan
   - Gluten-free
   - Post-surgery
   - Low-fat
   - High-fiber

3. **Menu Items**
   - Sample items in each category
   - With prices, descriptions, and dietary tags
   - Placeholder for images (add images via admin)

### Running Menu Seeding

```bash
# Seed menu data
python manage.py seed_menu

# Output example:
# Creating categories...
#   [OK] Created category: Breakfast
#   [OK] Created category: Lunch
# ...
# Creating dietary tags...
#   [OK] Created tag: Diabetic-friendly
# ...
# Creating menu items...
#   [OK] Created item: Grilled Chicken Breast
# ...
```

### Adding Menu Item Images

After seeding, add images via admin panel:

1. Go to `/admin/menu/menuitem/`
2. Click on a menu item
3. Upload image in the **Image** field
4. Save

Or use the image upload guide: `IMAGE_UPLOAD_GUIDE.md`

---

## Subscription Plans Seeding

### What Gets Created

1. **Daily Plans**
   - Basic Daily Plan
   - Premium Daily Plan
   - Post-Surgery Recovery Plan

2. **Weekly Plans**
   - Standard Weekly Plan
   - Premium Weekly Plan
   - Diabetic-Friendly Weekly Plan

3. **Monthly Plans**
   - Standard Monthly Plan
   - Premium Monthly Plan

### Plan Details

Each plan includes:
- Name and description
- Plan type (Daily/Weekly/Monthly)
- Price in UGX
- Meals per cycle
- Duration in days
- Discount percentage (if applicable)
- Active status

### Running Subscription Seeding

```bash
# Seed subscription plans
python manage.py seed_initial_data

# Output example:
# Creating subscription plans...
#   [OK] Created plan: Basic Daily Plan
#   [OK] Created plan: Premium Daily Plan
# ...
```

---

## Delivery Zones Seeding

### What Gets Created

1. **Inside Hospital Zone**
   - Lower delivery charge
   - Faster delivery time
   - For hospital locations

2. **Outside Hospital Zone**
   - Higher delivery charge
   - Standard delivery time
   - For external addresses

### Zone Details

Each zone includes:
- Name
- Description
- Base delivery charge
- Delivery time estimate
- Active status

### Running Delivery Zone Seeding

Delivery zones are created automatically when running:
```bash
python manage.py seed_initial_data
```

---

## Payment Methods

### Default Payment Methods

Payment methods are created automatically in the system. Available methods:

1. **Cash on Delivery**
   - No additional setup needed
   - Available by default

2. **Mobile Money** (MTN, Airtel)
   - Requires API credentials in settings
   - Configure in `.env` file

3. **Bank Transfer**
   - Requires payment gateway setup
   - Configure in `.env` file

### Configuring Payment Methods

Edit payment methods in admin panel:
1. Go to `/admin/payments/paymentmethod/`
2. Enable/disable methods
3. Configure settings

---

## Complete Seeding Process

### Step-by-Step Guide

1. **Ensure Database is Ready**
   ```bash
   python manage.py migrate
   ```

2. **Create Superuser** (if not exists)
   ```bash
   python manage.py createsuperuser
   ```

3. **Seed All Initial Data**
   ```bash
   python manage.py seed_all --clear
   ```
   This will:
   - Clear existing data (if `--clear` is used)
   - Create categories
   - Create dietary tags
   - Create menu items
   - Create subscription plans
   - Create delivery zones

4. **Verify Seeding**
   ```bash
   # Check what was created
   python manage.py shell
   ```
   ```python
   from menu.models import Category, MenuItem
   from subscriptions.models import SubscriptionPlan
   from delivery.models import DeliveryZone
   
   print(f"Categories: {Category.objects.count()}")
   print(f"Menu Items: {MenuItem.objects.count()}")
   print(f"Subscription Plans: {SubscriptionPlan.objects.count()}")
   print(f"Delivery Zones: {DeliveryZone.objects.count()}")
   ```

5. **Add Menu Item Images**
   - Use admin panel to upload images
   - Or use bulk upload if available

6. **Customize Data**
   - Edit prices, descriptions
   - Add/remove items
   - Customize plans

---

## Verification

### Verify Seeding Success

```bash
# Run pre-launch check
python manage.py pre_launch_check

# Check specific models
python manage.py shell
```

```python
# In Django shell
from menu.models import Category, MenuItem, DietaryTag
from subscriptions.models import SubscriptionPlan
from delivery.models import DeliveryZone

# Check counts
print("Categories:", Category.objects.count())
print("Menu Items:", MenuItem.objects.count())
print("Dietary Tags:", DietaryTag.objects.count())
print("Subscription Plans:", SubscriptionPlan.objects.count())
print("Delivery Zones:", DeliveryZone.objects.count())

# Check sample data
print("\nSample Categories:")
for cat in Category.objects.all()[:5]:
    print(f"  - {cat.name}")

print("\nSample Menu Items:")
for item in MenuItem.objects.all()[:5]:
    print(f"  - {item.name} ({item.category.name})")

print("\nSample Subscription Plans:")
for plan in SubscriptionPlan.objects.all()[:3]:
    print(f"  - {plan.name} ({plan.plan_type}) - {plan.price} UGX")
```

### Admin Panel Verification

1. **Access Admin Panel**
   - Go to `/admin/`
   - Login with superuser credentials

2. **Check Menu**
   - Go to **Menu** → **Categories**
   - Go to **Menu** → **Menu items**
   - Verify items are created

3. **Check Subscriptions**
   - Go to **Subscriptions** → **Subscription plans**
   - Verify plans are created

4. **Check Delivery**
   - Go to **Delivery** → **Delivery zones**
   - Verify zones are created

---

## Customization

### Customizing Menu Items

**Via Admin Panel:**
1. Go to `/admin/menu/menuitem/`
2. Edit existing items or add new ones
3. Update prices, descriptions, images

**Via Management Command:**
Edit `menu/management/commands/seed_menu.py` to customize:
- Categories
- Dietary tags
- Menu items and their details

### Customizing Subscription Plans

**Via Admin Panel:**
1. Go to `/admin/subscriptions/subscriptionplan/`
2. Edit existing plans or add new ones
3. Update prices, durations, discounts

**Via Management Command:**
Edit `subscriptions/management/commands/seed_initial_data.py` to customize:
- Plan names and descriptions
- Prices
- Durations
- Discounts

### Customizing Delivery Zones

**Via Admin Panel:**
1. Go to `/admin/delivery/deliveryzone/`
2. Edit existing zones or add new ones
3. Update charges and times

**Via Management Command:**
Edit `subscriptions/management/commands/seed_initial_data.py` to customize:
- Zone names
- Delivery charges
- Delivery times

---

## Adding Real Data

### Replacing Sample Data

1. **Prepare Your Data**
   - List of menu items with prices
   - Images for menu items
   - Subscription plan details
   - Delivery zone information

2. **Clear Sample Data** (optional)
   ```bash
   python manage.py seed_all --clear
   ```

3. **Add Your Data**
   - Use admin panel for manual entry
   - Or modify seeding commands with your data
   - Or use data import scripts

### Bulk Import

For large amounts of data, consider:
- CSV import scripts
- Excel import tools
- API-based imports
- Database direct imports

---

## Troubleshooting

### Common Issues

1. **"No such command: seed_all"**
   - Ensure you're in the project directory
   - Check that management commands are in correct location
   - Verify Django can find the commands

2. **"IntegrityError: duplicate key"**
   - Data already exists
   - Use `--clear` flag to clear first
   - Or skip existing items

3. **"Image not found"**
   - Images are optional
   - Add images via admin panel after seeding
   - Or update image paths in seeding command

4. **"Permission denied"**
   - Check file permissions
   - Ensure database user has proper permissions
   - Check Django settings

### Getting Help

- Check command output for error messages
- Review Django logs: `logs/django.log`
- Check database directly
- Consult deployment guide

---

## Best Practices

1. **Seed Before Launch**
   - Seed data before going live
   - Test with sample data first
   - Customize before production

2. **Backup Before Seeding**
   ```bash
   python manage.py backup_database
   ```

3. **Test Seeding**
   - Test on staging first
   - Verify all data is correct
   - Check relationships

4. **Document Customizations**
   - Document any changes to seeding
   - Keep notes on custom data
   - Update procedures

5. **Regular Updates**
   - Update menu items regularly
   - Refresh subscription plans
   - Keep data current

---

## Summary

Initial data seeding provides:
- **Menu Items**: Categories, items, dietary tags
- **Subscription Plans**: Daily, weekly, monthly plans
- **Delivery Zones**: Inside/outside hospital zones
- **Base Configuration**: Ready-to-use system

Use the seeding commands to quickly set up your production environment, then customize as needed through the admin panel.














