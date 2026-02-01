# CUSTOMER DASHBOARD - QUICK REFERENCE

## What's Fixed? ✅

### Bug #1: TypeError in update_health_profile()
```python
# BEFORE (❌ BROKEN)
health_profile, _ = HealthProfile.objects.get_or_create(...)
return render(..., {'title': _('Update Health Profile')})  # ERROR!

# AFTER (✅ FIXED)
health_profile, created = HealthProfile.objects.get_or_create(...)
return render(..., {'title': _('Update Health Profile')})  # Works!
```

### Bug #2: TypeError in emergency_contact()
```python
# Same pattern, same fix
# Changed: health_profile, _ → health_profile, created
```

---

## Sidebar Navigation (4 Sections)

```
ACCOUNT
├─ Dashboard
├─ My Orders
└─ Subscriptions

REWARDS
├─ Loyalty & Rewards
└─ Billing & Invoices

HEALTH
├─ Meal Plans
├─ Consultations
└─ Health Reports

SETTINGS
├─ My Profile
└─ Notifications
```

---

## Dashboard Components

### 1️⃣ Breadcrumb
Shows: Home > Dashboard

### 2️⃣ Header (Gradient Purple)
Title + Welcome message + Date

### 3️⃣ Stats Cards (4 items, responsive grid)
- Total Orders → View All
- Subscriptions → Manage/Browse
- Meal Plans → View Plans
- Loyalty Points → Redeem

### 4️⃣ Delivery Widget (GRADIENT)
Shows pending orders with:
- Order #
- Status
- Estimated delivery
- Track Order button

### 5️⃣ Recent Orders Table
Order #, Date, Total, Status, Delivery Est., View button

### 6️⃣ Quick Actions (4 cards)
- Book Consultation
- Health Reports
- My Profile
- Rewards

---

## Color System

```
Primary:    #667eea  (Purple-Blue)
Secondary:  #764ba2  (Purple)
Success:    #48bb78  (Green)
Danger:     #f56565  (Red)
Warning:    #ed8936  (Orange)
Info:       #4299e1  (Blue)
```

---

## Button Classes

```django
<!-- Gradient (Purple) -->
<a class="btn-custom btn-primary-custom">Action</a>

<!-- White with Border -->
<a class="btn-custom btn-secondary-custom">View</a>

<!-- Disabled State -->
<button class="btn-custom" disabled>Processing</button>
```

---

## Card Classes

```django
<!-- Dashboard Card (white background) -->
<div class="dashboard-card">
    <div class="card-header">
        <h2>Title</h2>
        <a href="#" class="btn-custom btn-primary-custom">Action</a>
    </div>
    Content...
</div>

<!-- Stat Card (metric display) -->
<div class="stat-card">
    <h3>Label</h3>
    <div class="value">123</div>
    <a href="#" class="btn-custom btn-secondary-custom">View</a>
</div>
```

---

## Badge Status Indicators

```django
<!-- Success (Green tint) -->
<span class="badge-custom badge-success">Delivered</span>

<!-- Warning (Orange tint) -->
<span class="badge-custom badge-warning">Pending</span>

<!-- Danger (Red tint) -->
<span class="badge-custom badge-danger">Cancelled</span>

<!-- Info (Blue tint) -->
<span class="badge-custom badge-info">Shipped</span>
```

---

## Responsive Breakpoints

| Device | Width | Columns | Sidebar |
|--------|-------|---------|---------|
| Mobile | < 768px | 1 | Hidden/Scroll |
| Tablet | 768px-992px | 2-3 | Horizontal |
| Desktop | > 992px | 3-4 | Sticky (280px) |

---

## Delivery Widget Template

```django
<div class="delivery-widget">
    <h3><i class="bi bi-box-seam"></i> Your Deliveries</h3>
    <div class="delivery-info-grid">
        {% for order in pending_orders|slice:":3" %}
        <div class="delivery-info-item">
            <div class="label">Order #{{ order.id }}</div>
            <div class="value">{{ order.get_status_display }}</div>
            <div class="label" style="margin-top: 0.8rem;">Estimated</div>
            <div class="value">{{ order.estimated_delivery|date:"M d, Y" }}</div>
            <a href="{% url 'customer_dashboard:my_orders' %}" style="...">
                Track Order <i class="bi bi-arrow-right ms-1"></i>
            </a>
        </div>
        {% endfor %}
    </div>
</div>
```

---

## Common Icons Used

```
Dashboard:        bi-speedometer2
Orders:           bi-bag-check
Subscriptions:    bi-calendar2-check
Loyalty:          bi-star
Profile:          bi-person-circle
Health:           bi-heart-pulse
Consultations:    bi-chat-dots
Reports:          bi-file-text
Settings:         bi-gear
Notifications:    bi-bell
Deliveries:       bi-box-seam
Email:            bi-envelope
Phone:            bi-telephone
Address:          bi-geo-alt
Calendar:         bi-calendar-event
Clock:            bi-clock
```

---

## Files Modified

| File | Changes | Status |
|------|---------|--------|
| views.py | Fixed TypeError (2 functions) | ✅ DONE |
| base.html | Enhanced with professional styling | ✅ DONE |
| dashboard.html | Redesigned with delivery widget | ✅ DONE |

---

## Next Steps (19 Templates Remaining)

### Priority 1 (This Week)
- [ ] my_orders.html - Order list with tracking
- [ ] my_subscriptions.html - Subscription management
- [ ] my_profile.html - Profile settings

### Priority 2 (Next Week)
- [ ] notifications.html
- [ ] my_meal_plans.html
- [ ] my_consultations.html
- [ ] loyalty.html
- [ ] health_reports.html

### Priority 3 (After)
- Payment history
- Billing info
- Emergency contact
- And 6 more...

---

## Button Functionality Checklist

All buttons must:
- ✅ Navigate to correct URL
- ✅ Show hover effect (lift 2px, shadow)
- ✅ Show active/focused state
- ✅ Show disabled state (opacity 0.6)
- ✅ Have loading indicator (if async)
- ✅ Work on mobile (44px minimum height)
- ✅ Have icon (for visual clarity)
- ✅ Have tooltip/title (if space-constrained)

---

## Testing Template

Before deploying each template:

```django
{% extends 'customer_dashboard/base.html' %}
{% load static %}

{% block dashboard_content %}
<div>
    <!-- 1. Add breadcrumb -->
    <nav class="breadcrumb">
        <span class="breadcrumb-item active">
            <i class="bi bi-[icon]"></i> [Page Name]
        </span>
    </nav>

    <!-- 2. Add gradient header -->
    <div class="dashboard-header">
        <h1><i class="bi bi-[icon]"></i> [Title]</h1>
        <p>[Description]</p>
    </div>

    <!-- 3. Add content in dashboard-card -->
    <div class="dashboard-card">
        <div class="card-header">
            <h2>[Section Title]</h2>
            <a href="#" class="btn-custom btn-primary-custom">Action</a>
        </div>
        [Content]
    </div>
</div>
{% endblock %}
```

---

## Frequently Used Variables

```python
# User
{{ user.get_full_name }}
{{ user.username }}
{{ user.email }}

# Orders
{% for order in recent_orders %}
    {{ order.id }}
    {{ order.created_at|date:"M d, Y" }}
    {{ order.total_amount|floatformat:0 }}
    {{ order.get_status_display }}
    {{ order.estimated_delivery|date:"M d" }}
{% endfor %}

# Context Checks
{% if pending_orders %}...{% endif %}
{% if active_subscriptions %}...{% endif %}
{% if request.resolver_match.url_name == 'dashboard' %}active{% endif %}
```

---

## CSS Variables Reference

```css
:root {
    --primary-color: #667eea;
    --secondary-color: #764ba2;
    --success-color: #48bb78;
    --danger-color: #f56565;
    --warning-color: #ed8936;
    --info-color: #4299e1;
    --light-bg: #f7fafc;
    --border-color: #e2e8f0;
    --text-primary: #2d3748;
    --text-secondary: #718096;
}
```

Use in CSS:
```css
color: var(--primary-color);
background: var(--light-bg);
border: 1px solid var(--border-color);
```

---

## Common Patterns

### Empty State
```django
<div style="text-align: center; padding: 3rem; color: var(--text-secondary);">
    <i class="bi bi-inbox" style="font-size: 3rem; opacity: 0.5; display: block; margin-bottom: 1rem;"></i>
    <p>No items yet. <a href="#">Take action</a></p>
</div>
```

### Table with Status
```django
<table class="dashboard-table">
    <thead>
        <tr>
            <th>ID</th>
            <th>Status</th>
            <th>Action</th>
        </tr>
    </thead>
    <tbody>
        {% for item in items %}
        <tr>
            <td>#{{ item.id }}</td>
            <td><span class="badge-custom badge-{{ item.get_status_display|lower }}">{{ item.get_status_display }}</span></td>
            <td><a href="#" class="btn-custom btn-secondary-custom">View</a></td>
        </tr>
        {% endfor %}
    </tbody>
</table>
```

### Grid Layout
```django
<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem;">
    <!-- Cards -->
</div>
```

---

## Performance Notes

- All transitions: 0.3s ease
- Lazy load images if needed
- Minimize reflows (use CSS transforms)
- Use CSS variables (no duplication)
- Optimize images before upload
- Monitor page load time (target < 2s)

---

## Deployment Checklist

Before pushing to production:

- [ ] All 20 templates enhanced
- [ ] All buttons functional
- [ ] Tested on Chrome, Firefox, Safari
- [ ] Tested on mobile (iOS/Android)
- [ ] Tested on tablet
- [ ] No console errors
- [ ] No console warnings
- [ ] Page load time acceptable
- [ ] Images optimized
- [ ] CSS file size checked
- [ ] Forms tested
- [ ] Links tested
- [ ] Status displays correct

---

**Last Updated**: Today
**Status**: 2/21 components complete (dashboard + base)
**Next Focus**: my_orders.html (High Priority)
