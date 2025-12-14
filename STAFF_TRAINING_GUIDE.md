# NOURISH LINK - Staff Training Guide

## Overview
This guide provides training materials for different staff roles in the NOURISH LINK Hospital E-Commerce Restaurant system.

## Table of Contents

1. [Admin Staff Training](#admin-staff-training)
2. [Kitchen Staff Training](#kitchen-staff-training)
3. [Delivery Staff Training](#delivery-staff-training)
4. [Support Staff Training](#support-staff-training)
5. [Common Tasks](#common-tasks)
6. [Troubleshooting](#troubleshooting)

---

## Admin Staff Training

### Accessing the Admin Panel

1. Navigate to: `https://yourdomain.com/admin/`
2. Login with your admin credentials
3. You'll see the Django admin dashboard

### Main Admin Tasks

#### 1. Managing Menu Items

**Adding a New Menu Item:**
1. Go to **Menu** → **Menu items** → **Add menu item**
2. Fill in the form:
   - **Name**: Item name (e.g., "Grilled Chicken Breast")
   - **Description**: Detailed description
   - **Category**: Select from existing categories
   - **Price**: Enter price in UGX
   - **Image**: Upload item image
   - **Dietary Tags**: Select applicable tags (Diabetic-friendly, Low-sodium, etc.)
   - **Ingredients**: List ingredients
   - **Nutrition Info**: Add calories, protein, carbs, etc.
   - **Is Available**: Check if item is currently available
3. Click **Save**

**Editing a Menu Item:**
1. Go to **Menu** → **Menu items**
2. Click on the item you want to edit
3. Make changes
4. Click **Save**

**Deactivating a Menu Item:**
1. Edit the menu item
2. Uncheck **Is Available**
3. Click **Save**

#### 2. Managing Categories

**Adding a Category:**
1. Go to **Menu** → **Categories** → **Add category**
2. Enter name and description
3. Set display order (lower numbers appear first)
4. Click **Save**

#### 3. Managing Subscription Plans

**Viewing Subscription Plans:**
1. Go to **Subscriptions** → **Subscription plans**
2. View all available plans

**Creating a New Plan:**
1. Go to **Subscriptions** → **Subscription plans** → **Add subscription plan**
2. Fill in:
   - **Name**: Plan name
   - **Description**: Plan details
   - **Plan Type**: Daily, Weekly, or Monthly
   - **Price**: Plan price
   - **Meals per Cycle**: Number of meals
   - **Duration Days**: How long the plan lasts
   - **Discount Percentage**: Optional discount
   - **Is Active**: Check to make available
3. Click **Save**

#### 4. Managing Orders

**Viewing Orders:**
1. Go to **Orders** → **Orders**
2. Use filters to find specific orders:
   - Filter by status (Pending, Confirmed, etc.)
   - Filter by date range
   - Search by order number

**Updating Order Status:**
1. Click on an order
2. Change the **Status** field
3. Click **Save**

**Order Statuses:**
- **Pending**: Order placed, awaiting confirmation
- **Confirmed**: Order confirmed, ready for kitchen
- **Preparing**: Kitchen is preparing the order
- **Ready**: Order ready for pickup/delivery
- **Out for Delivery**: Order is being delivered
- **Delivered**: Order delivered to customer
- **Cancelled**: Order cancelled

#### 5. Managing Users

**Viewing Users:**
1. Go to **Accounts** → **Users**
2. View all registered users

**Creating Staff Account:**
1. Go to **Accounts** → **Users** → **Add user**
2. Fill in username, email, password
3. Check **Staff status** for admin access
4. Check **Superuser status** for full admin access
5. Click **Save**

**Viewing User Profiles:**
1. Go to **Accounts** → **Profiles**
2. View user information, addresses, dietary preferences

#### 6. Reports and Analytics

**Accessing Reports:**
1. Go to **Admin Dashboard** → **Reports & Analytics**
2. View:
   - Daily sales
   - Popular menu items
   - Order statistics
   - Revenue reports

### Admin Dashboard Features

**Main Dashboard:**
- Recent orders
- Order statistics
- Revenue overview
- Popular items

**Order Management:**
- View all orders
- Filter and search orders
- Update order status
- Assign deliveries

**Kitchen Dashboard:**
- Orders by status
- Kitchen queue
- Preparation time tracking

---

## Kitchen Staff Training

### Accessing Kitchen Dashboard

1. Navigate to: `https://yourdomain.com/admin-dashboard/kitchen/`
2. Login with your kitchen staff credentials

### Kitchen Workflow

#### 1. Viewing Orders

**Orders by Status:**
- **Pending**: New orders waiting to be confirmed
- **Confirmed**: Orders ready to start preparing
- **Preparing**: Orders currently being prepared
- **Ready**: Orders ready for pickup/delivery

#### 2. Starting Order Preparation

1. Find the order in **Confirmed** status
2. Click **Start Preparing**
3. Order status changes to **Preparing**
4. Begin preparing the items

#### 3. Completing Order Preparation

1. When order is ready, find it in **Preparing** status
2. Click **Mark as Ready**
3. Order status changes to **Ready**
4. Order is now available for pickup/delivery

#### 4. Viewing Order Details

Click on any order to see:
- Customer information
- Order items and quantities
- Special instructions
- Delivery address (if applicable)
- Order time

### Best Practices

1. **Check Orders Regularly**: Refresh the page to see new orders
2. **Update Status Promptly**: Keep order status updated
3. **Review Special Instructions**: Check for dietary requirements or special requests
4. **Prioritize Urgent Orders**: Check order time and delivery requirements

---

## Delivery Staff Training

### Accessing Delivery Dashboard

1. Navigate to: `https://yourdomain.com/admin-dashboard/`
2. Login with your delivery staff credentials

### Delivery Workflow

#### 1. Viewing Orders Ready for Delivery

1. Go to **Order Management**
2. Filter orders by status: **Ready** or **Out for Delivery**
3. View orders with delivery addresses

#### 2. Assigning Delivery

1. Find an order with status **Ready**
2. Click on the order
3. Click **Assign Delivery** (if available)
4. Order status changes to **Out for Delivery**

#### 3. Completing Delivery

1. After delivering the order, find it in **Out for Delivery** status
2. Click **Mark as Delivered**
3. Order status changes to **Delivered**

#### 4. Viewing Delivery Information

Each order shows:
- Customer name and phone
- Delivery address
- Delivery zone
- Delivery instructions
- Order items

### Delivery Zones

**Inside Hospital:**
- Lower delivery charge
- Faster delivery time
- Specific locations within hospital

**Outside Hospital:**
- Higher delivery charge
- Longer delivery time
- External addresses

### Best Practices

1. **Confirm Address**: Verify delivery address before leaving
2. **Check Contact Info**: Ensure you have customer phone number
3. **Update Status**: Mark as delivered immediately after completion
4. **Handle Issues**: Contact support if delivery cannot be completed

---

## Support Staff Training

### Accessing Support Features

1. Navigate to: `https://yourdomain.com/admin/`
2. Login with support staff credentials

### Support Tasks

#### 1. Viewing Customer Information

1. Go to **Accounts** → **Profiles**
2. Search for customer by username or email
3. View:
   - Contact information
   - Order history
   - Delivery addresses
   - Dietary preferences

#### 2. Viewing Orders

1. Go to **Orders** → **Orders**
2. Search by order number or customer
3. View order details and status

#### 3. Handling Customer Inquiries

**Common Issues:**
- **Order Status**: Check order status and update if needed
- **Payment Issues**: Verify payment status in Payments section
- **Delivery Issues**: Check delivery address and status
- **Subscription Issues**: View subscription details in Subscriptions section

#### 4. Cancelling Orders

1. Find the order
2. Change status to **Cancelled**
3. Add notes if needed
4. Save changes

### Customer Communication

- Use customer email or phone from profile
- Document any issues or resolutions
- Escalate complex issues to admin

---

## Common Tasks

### Daily Tasks

1. **Morning Check:**
   - Review overnight orders
   - Check subscription orders generated
   - Verify system status

2. **During Service:**
   - Monitor new orders
   - Update order statuses
   - Handle customer inquiries

3. **End of Day:**
   - Complete all pending orders
   - Review daily reports
   - Check for any issues

### Weekly Tasks

1. Review weekly sales reports
2. Check popular menu items
3. Review customer feedback
4. Update menu availability

### Monthly Tasks

1. Review monthly reports
2. Analyze subscription trends
3. Review and update menu items
4. Staff performance review

---

## Troubleshooting

### Common Issues

#### 1. Cannot Login
- **Solution**: Verify username and password
- **Solution**: Check if account is active
- **Solution**: Contact admin to reset password

#### 2. Orders Not Showing
- **Solution**: Check order filters
- **Solution**: Refresh the page
- **Solution**: Check if orders exist in admin panel

#### 3. Cannot Update Order Status
- **Solution**: Verify you have proper permissions
- **Solution**: Check if order is in correct status
- **Solution**: Refresh and try again

#### 4. Images Not Loading
- **Solution**: Check if static files are collected
- **Solution**: Verify image files exist
- **Solution**: Clear browser cache

#### 5. Payment Issues
- **Solution**: Check payment gateway configuration
- **Solution**: Verify payment status in admin
- **Solution**: Contact payment provider support

### Getting Help

1. **Documentation**: Check this guide and other documentation
2. **Admin Support**: Contact system administrator
3. **Technical Support**: Contact development team
4. **Emergency**: Use emergency contact procedures

---

## Security Best Practices

1. **Password Security:**
   - Use strong passwords
   - Don't share passwords
   - Change passwords regularly

2. **Access Control:**
   - Only access what you need
   - Don't share accounts
   - Log out when done

3. **Data Protection:**
   - Don't share customer information
   - Handle sensitive data carefully
   - Report security issues immediately

---

## Training Completion Checklist

- [ ] Understand admin panel navigation
- [ ] Can add/edit menu items
- [ ] Can manage orders and update status
- [ ] Can view reports and analytics
- [ ] Understand order workflow
- [ ] Know how to handle common issues
- [ ] Understand security best practices
- [ ] Know who to contact for help

---

## Additional Resources

- **Admin Panel**: `/admin/`
- **Admin Dashboard**: `/admin-dashboard/`
- **Kitchen Dashboard**: `/admin-dashboard/kitchen/`
- **Documentation**: Check project documentation files
- **Support**: Contact system administrator

---

## Notes

- This guide should be updated as new features are added
- Staff should receive hands-on training in addition to this guide
- Regular refresher training is recommended
- Document any issues or improvements needed
