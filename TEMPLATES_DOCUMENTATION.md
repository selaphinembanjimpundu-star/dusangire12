# RBAC Templates Documentation

## Overview

This document describes all templates created for the Role-Based Access Control (RBAC) system. Templates are organized by functionality and include reusable components for consistent UI/UX across the application.

## Template Structure

```
templates/
├── dashboard/
│   └── role_dashboard.html          # Master dashboard for all 10 roles
├── accounts/
│   ├── profile_view.html            # User profile display
│   ├── login.html                   # Login form (existing)
│   └── register.html                # Registration form (existing)
├── components/
│   ├── card.html                    # Reusable card component
│   ├── modal.html                   # Reusable modal dialog
│   └── table.html                   # Reusable data table
├── forms/
│   └── base_form.html               # Base form template
├── utils/
│   ├── pagination.html              # Pagination navigation
│   ├── alerts.html                  # Alert messages
│   ├── breadcrumbs.html             # Breadcrumb navigation
│   └── buttons.html                 # Reusable buttons
├── errors/
│   └── permission_denied.html       # 403 Access Denied page
├── layouts/
│   └── base_layout.html             # Main layout with navigation
└── navbar_rbac.html                 # Role-aware navigation bar
```

## Core Templates

### 1. role_dashboard.html
**Location:** `templates/dashboard/role_dashboard.html`
**Purpose:** Master dashboard displaying role-specific content for all 10 roles

**Features:**
- Conditionally renders content based on user role
- 10 role-specific dashboard sections
- Responsive grid layout
- Role badge display
- Status indicators
- Quick action buttons
- Statistics and metrics
- Activity feeds

**Roles Supported:**
1. Patient
2. Caregiver
3. Nutritionist
4. Medical Staff
5. Chef
6. Kitchen Staff
7. Delivery Person
8. Support Staff
9. Hospital Manager
10. Admin

**Usage:**
```django
{% extends 'base.html' %}
{% load static %}

<!-- Template automatically shows role-specific content -->
<!-- No custom context needed beyond user object -->
```

**Context Variables Required:**
- `user` - Django User object with profile
- `user_permissions` - List of user permissions (from rbac_context)
- `role_permissions` - Dictionary of role permissions (from rbac_context)

### 2. navbar_rbac.html
**Location:** `templates/navbar_rbac.html`
**Purpose:** Sticky navigation bar with role-aware menu items

**Features:**
- Sticky top navigation
- Role badge display
- Dropdown menus for each role
- Permission-based menu items
- User profile dropdown
- Mobile responsive hamburger menu
- Smooth animations
- Role-specific navigation items

**Roles with Custom Menus:**
- Patient: Meals, Orders, Subscriptions
- Nutritionist: Patients, Meal Plans, Consultations
- Medical Staff: Hospital, Patients, Health Profiles
- Chef: Kitchen, Orders, Menu, Staff
- Kitchen Staff: Preparations, Recipes, Orders
- Delivery Person: Deliveries, Route, Zones
- Support Staff: Support, Tickets, Complaints
- Hospital Manager: Management, Operations, Staff
- Admin: Administration, System, Settings

**Usage:**
```django
{% include 'navbar_rbac.html' %}
```

**Mobile Features:**
- Hamburger menu toggle
- Collapsible dropdowns
- Full-screen mobile menu
- Touch-friendly interaction

### 3. profile_view.html
**Location:** `templates/accounts/profile_view.html`
**Purpose:** Display user profile information with role-specific fields

**Features:**
- Basic user information
- Account status display
- Role-specific fields
- Health information (for patients/caregivers)
- Staff information (for staff roles)
- Healthcare provider info (for medical roles)
- Delivery information (for delivery persons)
- Notification preferences
- Permission display
- Account action buttons

**Usage:**
```django
{% extends 'base.html' %}

<!-- Display user profile -->
<!-- Uses profile_view.html template -->
```

**Sections:**
1. Basic Information (name, email, phone, role)
2. Account Status (status, active, member since, last login)
3. Role-Specific Fields (varies by role)
4. Health Information (dietary, medical alerts)
5. Notification Preferences (email, SMS, push)
6. Permissions List
7. Account Actions (edit, password change, logout)

## Component Templates

### 4. card.html
**Location:** `templates/components/card.html`
**Purpose:** Reusable card component for displaying content in card format

**Features:**
- Optional icon display
- Card header with title and subtitle
- Card body for main content
- Card footer
- Action buttons
- Hover effects
- Responsive design

**Usage:**
```django
{% include 'components/card.html' with 
    title="Card Title" 
    subtitle="Optional subtitle" 
    icon="📊"
    content=card_content
    footer="Footer text"
    actions=action_list
%}
```

**Parameters:**
- `title` (required) - Card title
- `subtitle` (optional) - Card subtitle
- `icon` (optional) - Emoji or icon
- `content` (optional) - HTML content
- `footer` (optional) - Footer text
- `actions` (optional) - List of action buttons

**Action Format:**
```python
[
    {'label': 'View', 'url': '/path/'},
    {'label': 'Edit', 'url': '/path/edit/'},
]
```

### 5. modal.html
**Location:** `templates/components/modal.html`
**Purpose:** Reusable modal dialog component

**Features:**
- Modal header with close button
- Modal body content
- Modal footer with action buttons
- Smooth animations
- Responsive design
- JavaScript controls

**Usage:**
```django
{% include 'components/modal.html' with 
    modal_id="confirmModal" 
    title="Confirm Action"
    message="Are you sure?"
    actions=action_list
%}

<!-- Open modal -->
<button onclick="showModal('confirmModal')">Open</button>

<!-- In JavaScript -->
<script>
    showModal('confirmModal');   // Show modal
    hideModal('confirmModal');   // Hide modal
</script>
```

**Modal Controls:**
- `showModal(id)` - Show modal by ID
- `hideModal(id)` - Hide modal by ID
- Close button - Click X to close
- Auto-close on action

**Action Buttons:**
```python
actions=[
    {'label': 'Confirm', 'action': 'confirm', 'type': 'primary'},
    {'label': 'Delete', 'action': 'delete', 'type': 'danger'},
]
```

### 6. table.html
**Location:** `templates/components/table.html`
**Purpose:** Reusable data table component with sorting and filtering

**Features:**
- Header with title and actions
- Sortable columns
- Badge support for status cells
- Link support for cell values
- Row action buttons
- Pagination integration
- Empty state display
- Responsive table
- Hover effects

**Usage:**
```django
{% include 'components/table.html' with 
    title="Data Table"
    headers=header_list
    rows=row_list
    row_actions=row_action_list
    pagination=page_obj
%}
```

**Header Format:**
```python
headers=[
    {'label': 'ID', 'field': 'id', 'sortable': True},
    {'label': 'Name', 'field': 'name'},
    {'label': 'Status', 'field': 'status'},
]
```

**Row Format:**
```python
rows=[
    {
        'id': 1,
        'cells': [
            {'value': '001'},
            {'value': 'John Doe', 'link': '/path/'},
            {'value': 'Active', 'badge': 'active'},
        ]
    },
]
```

**Row Actions:**
```python
row_actions=[
    {'label': 'View', 'url': '/path/ID/', 'type': 'view'},
    {'label': 'Edit', 'url': '/path/ID/edit/', 'type': 'edit'},
    {'label': 'Delete', 'url': '/path/ID/delete/', 'type': 'delete', 'confirm': 'Are you sure?'},
]
```

## Form Templates

### 7. base_form.html
**Location:** `templates/forms/base_form.html`
**Purpose:** Base form template for creating/editing content

**Features:**
- Form header with title and subtitle
- Automatic field rendering
- Support for all Django field types
- Required field indicators
- Field help text display
- Error messages
- Styled form controls
- Submit and cancel buttons
- CSRF protection

**Usage:**
```django
{% extends 'base.html' %}

{% block content %}
{% include 'forms/base_form.html' with 
    form=form 
    title="Create Item"
    subtitle="Fill in the form below"
    submit_label="Create"
    cancel_url="/path/back/"
%}
{% endblock %}
```

**Form Parameters:**
- `form` (required) - Django form object
- `title` (required) - Form title
- `subtitle` (optional) - Form subtitle
- `submit_label` (optional, default: "Submit") - Submit button text
- `cancel_url` (optional) - Cancel button URL
- `method` (optional, default: "POST") - HTTP method
- `enctype` (optional) - Form encoding type

**Field Types Supported:**
- Text input
- Email input
- Password input
- Textarea
- Select dropdown
- Checkbox
- Radio buttons
- File upload
- Date/DateTime
- All standard Django fields

**Error Display:**
- Non-field errors at top
- Per-field errors below each field
- Styled error messages
- Field highlighting on error

## Utility Templates

### 8. pagination.html
**Location:** `templates/utils/pagination.html`
**Purpose:** Pagination navigation component

**Features:**
- First/Previous/Next/Last navigation
- Page number links
- Current page highlight
- Page info display
- Responsive design
- Touch-friendly buttons

**Usage:**
```django
{% include 'utils/pagination.html' with page_obj=page_obj %}
```

**Parameters:**
- `page_obj` (required) - Django Paginator page object

**Display:**
- Current page highlighted
- Nearby pages shown (±2 pages)
- Navigation arrows
- Page count display

### 9. alerts.html
**Location:** `templates/utils/alerts.html`
**Purpose:** Display alert and message components

**Features:**
- Success alerts (green)
- Error alerts (red)
- Warning alerts (yellow)
- Info alerts (blue)
- Auto-dismiss (5 seconds)
- Manual dismiss button
- Smooth animations
- Icon display

**Usage:**
```django
{% include 'utils/alerts.html' %}

<!-- In Django views -->
from django.contrib import messages
messages.success(request, 'Operation successful!')
messages.error(request, 'An error occurred.')
messages.warning(request, 'Please be careful.')
messages.info(request, 'Information message.')
```

**Alert Types:**
- `success` - Green background (✓)
- `error` / `danger` - Red background (✕)
- `warning` - Yellow background (⚠)
- `info` - Blue background (ℹ)

**Auto-Dismiss:**
- Success/Info/Warning: 5 seconds
- Errors: Manual dismiss only

### 10. breadcrumbs.html
**Location:** `templates/utils/breadcrumbs.html`
**Purpose:** Breadcrumb navigation for page hierarchy

**Features:**
- Home link
- Current page hierarchy
- Navigation links
- Current page indicator
- Responsive design
- Icon support

**Usage:**
```django
{% include 'utils/breadcrumbs.html' with breadcrumbs=breadcrumb_list %}

<!-- Or alternative format -->
{% include 'utils/breadcrumbs.html' with breadcrumb_items=breadcrumb_items %}
```

**Breadcrumb List Format:**
```python
breadcrumbs=[
    {'label': 'Patients', 'url': '/patients/'},
    {'label': 'John Doe', 'url': '/patients/1/'},
    {'label': 'Edit', 'url': None},  # Current page - no URL
]
```

**Alternative Format:**
```python
breadcrumb_items=[
    {'name': 'Patients', 'url': '/patients/', 'is_current': False},
    {'name': 'John Doe', 'url': '/patients/1/', 'is_current': False},
    {'name': 'Edit', 'is_current': True},
]
```

## Layout Templates

### 11. base_layout.html
**Location:** `templates/layouts/base_layout.html`
**Purpose:** Main layout template with navigation, sidebar, and content areas

**Features:**
- Sticky navbar
- Sidebar with role-based menu
- Main content area
- Footer
- Responsive grid layout
- Alert display
- Page header with actions
- Mobile responsive

**Usage:**
```django
{% extends 'layouts/base_layout.html' %}

{% block page_content %}
<!-- Your page content here -->
{% endblock %}
```

**Template Blocks:**
- `extra_css` - Additional CSS
- `page_content` - Main page content

**Context Variables:**
- `page_title` (optional) - Page title display
- `page_actions` (optional) - Action buttons
- `show_sidebar` (optional, default: True) - Show/hide sidebar

**Sidebar Navigation:**
- Auto-generates based on user role
- Highlights current page
- Role-specific menu items
- Emoji icons for visual cues

## Error Templates

### 12. permission_denied.html
**Location:** `templates/errors/permission_denied.html`
**Purpose:** 403 Forbidden/Access Denied page

**Features:**
- User role and status display
- Current permissions display
- Required permissions display
- Required roles display
- FAQ section
- Helpful links
- Support contact

**Usage:**
```django
# In views.py
from django.shortcuts import render

def permission_denied_view(request, exception=None):
    context = {
        'required_permission': 'view_patients',
        'required_role': ['nutritionist', 'medical_staff'],
    }
    return render(request, 'errors/permission_denied.html', context, status=403)

# Or using RBAC decorator
@permission_required('view_patients')
def protected_view(request):
    pass
```

**Context Variables:**
- `required_permission` (optional) - Required permission
- `required_role` (optional) - Required role(s)
- `user_permissions` (optional) - User's permissions

**Display Sections:**
1. Error icon and title
2. User's current access level
3. Required access information
4. FAQ (why error, how to get access, is this a bug)
5. Helpful actions (dashboard, support, profile)

## Integration Examples

### Example 1: Patient Dashboard
```django
{% extends 'layouts/base_layout.html' %}

{% block page_content %}
<div class="dashboard-content">
    {% include 'dashboard/role_dashboard.html' %}
</div>
{% endblock %}
```

### Example 2: Data List View
```django
{% extends 'layouts/base_layout.html' %}

{% block page_content %}
{% include 'utils/alerts.html' %}
{% include 'utils/breadcrumbs.html' with breadcrumb_items=breadcrumbs %}

{% include 'components/table.html' with 
    title="Patients List"
    headers=table_headers
    rows=patient_rows
    row_actions=row_actions
    pagination=page_obj
%}
{% endblock %}
```

### Example 3: Create Form
```django
{% extends 'layouts/base_layout.html' %}

{% block page_content %}
{% include 'utils/breadcrumbs.html' with breadcrumb_items=breadcrumbs %}
{% include 'forms/base_form.html' with 
    form=form 
    title="Create New Patient"
    submit_label="Create"
%}
{% endblock %}
```

### Example 4: Confirmation Modal
```django
<button onclick="showModal('deleteModal')">Delete</button>

{% include 'components/modal.html' with 
    modal_id="deleteModal"
    title="Confirm Delete"
    message="Are you sure you want to delete this item?"
    actions=delete_actions
%}
```

## Styling and Customization

### Color Scheme
- Primary: #667eea (Blue/Purple)
- Secondary: #764ba2 (Dark Purple)
- Success: #28a745 (Green)
- Danger: #dc3545 (Red)
- Warning: #ffc107 (Yellow)
- Info: #17a2b8 (Cyan)
- Background: #f5f5f5 (Light Gray)

### Responsive Breakpoints
- Desktop: 1024px+
- Tablet: 768px - 1024px
- Mobile: < 768px

### Font Sizes
- H1: 32px (24px mobile)
- H2: 28px (20px mobile)
- H3: 18px (16px mobile)
- Body: 14px (13px mobile)
- Small: 12px (11px mobile)

## Best Practices

### 1. Template Includes
Always include templates rather than extending when possible:
```django
<!-- Good -->
{% include 'components/card.html' with title="Title" %}

<!-- Less ideal for reusable components -->
{% extends 'components/card.html' %}
```

### 2. Context Data
Keep template context clean:
```python
# Good
context = {
    'page_title': 'Dashboard',
    'user_permissions': get_user_permissions(user),
}

# Avoid
context = {
    'long_variable_name_that_is_confusing': value,
}
```

### 3. Responsive Design
Always test on mobile:
```django
<!-- Good - uses responsive classes -->
<div class="container-responsive">
    {% include 'components/card.html' %}
</div>

<!-- Test with Django debug toolbar -->
<!-- Test with browser dev tools mobile mode -->
```

### 4. Accessibility
Use semantic HTML:
```django
<!-- Good -->
<nav aria-label="Main navigation">
    {% include 'navbar_rbac.html' %}
</nav>

<!-- Use semantic tags -->
<main class="content-area">
<aside class="sidebar">
<footer class="footer">
```

## Troubleshooting

### Template Not Found
```
TemplateDoesNotExist: 'components/card.html'
```
**Solution:** Check template path and ensure it's in the correct directory.

### CSS Not Loading
**Solution:** 
- Check `{% load static %}`
- Verify CSS is inline or linked correctly
- Clear browser cache

### JavaScript Not Working
**Solution:**
- Check console for errors
- Verify script tags are at end of file
- Check for jQuery/dependency conflicts

### Modal Not Opening
**Solution:**
- Verify modal ID matches in showModal() call
- Check for JavaScript errors
- Ensure modal template is included

### Form Validation Errors
**Solution:**
- Check form class inherits from forms.Form
- Verify required field attributes
- Check form.is_valid() in view
- Display form.errors in template

## Version History

### v1.0 - Initial Release
- Dashboard template (11 roles)
- Navigation template
- Profile template
- Component templates (card, modal, table)
- Form template
- Utility templates (pagination, alerts, breadcrumbs)
- Error templates
- Layout template

### Future Enhancements
- PDF export functionality
- Email templates
- Advanced search interface
- Analytics dashboard
- Real-time notifications
- Mobile app templates

## Support and Documentation

For more information:
- [RBAC Implementation Guide](RBAC_IMPLEMENTATION_GUIDE.md)
- [Quick Reference](RBAC_QUICK_REFERENCE.md)
- [System Documentation](RBAC_SYSTEM_DOCUMENTATION.md)
- [Business Model](BUSINESS_MODEL_CANVAS_SUMMARY.md)

---

**Last Updated:** 2024
**Maintained By:** Development Team
**Status:** Active and Production Ready
