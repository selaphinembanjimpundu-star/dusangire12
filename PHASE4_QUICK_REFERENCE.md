# Phase 4: Analytics System - Quick Reference Guide

## 🚀 Quick Start

### Access the Analytics Dashboard
```
URL: http://localhost:8000/analytics/dashboard/
Required: Staff login
```

### Available Analytics Views
1. **Dashboard** → `/analytics/dashboard/` - Main KPI view
2. **Revenue Analysis** → `/analytics/revenue-streams/` - Revenue by channel
3. **Customer Analytics** → `/analytics/customers/` - Segmentation & insights
4. **Campaign Manager** → `/analytics/campaigns/` - Campaign management

---

## 📊 What Each Dashboard Shows

### Analytics Dashboard
**Main KPI Metrics:**
- Today's orders, revenue, customers, discounts
- 30-day totals and averages
- Customer segments breakdown
- Payment method distribution
- Active campaigns counter

**Key Charts:**
- Revenue trend (last 30 days)
- Payment methods distribution

### Revenue Analysis
**Revenue by Channel:**
- Direct orders
- Subscriptions
- VIP upgrades
- Corporate contracts
- Catering services
- Referral programs
- Loyalty redemptions

**Data Shown:**
- Total revenue and percentage
- Transaction count
- Daily trends
- Configurable time periods (7/30/90 days)

### Customer Analytics
**Customer Segments:**
- VIP customers
- Subscribed users
- High-value customers (500k+ RWF)
- Churn risk customers
- Inactive customers (30+ days)
- New customers (7 days)

**Program Performance:**
- Loyalty points earned/redeemed
- Referral statistics
- Lifetime value analysis
- Top 10 customers
- At-risk customers list

### Campaign Manager
**Campaign Features:**
- View all campaigns with status
- Filter by status (active, draft, completed)
- See performance metrics:
  - Orders influenced
  - Customer conversions
  - Conversion rate %
  - ROI %
  - Revenue generated
- Create new campaigns
- View detailed campaign analysis

---

## 🗄️ Database Tables

### 7 Analytics Models Created

1. **DailyAnalyticsSnapshot**
   - Daily metrics aggregation
   - Order counts, revenue, discounts
   - Payment method breakdown

2. **RevenueStream**
   - Revenue tracking by channel
   - Transaction counts
   - Channel attribution

3. **CustomerMetrics**
   - Individual customer analytics
   - Lifetime value
   - Churn risk detection
   - VIP tier tracking
   - Loyalty metrics

4. **Campaign**
   - Campaign setup and management
   - Discount configuration
   - Budget tracking
   - Date scheduling

5. **CampaignPerformance**
   - Campaign effectiveness
   - ROI calculations
   - Conversion tracking
   - Performance history

6. **PageViewAnalytics**
   - Traffic tracking
   - Unique visitor counts

7. **ConversionEvent**
   - Conversion funnel tracking
   - User journey events
   - Session tracking

---

## 🔧 Management Commands

### Update Analytics
```bash
# Update today's metrics
python manage.py update_analytics

# Backfill last 30 days
python manage.py update_analytics --backfill

# Custom days (example: 7 days)
python manage.py update_analytics --days=7
```

**Output:**
- Processes daily snapshots
- Updates customer metrics
- Calculates revenue streams
- Shows progress and counts

### Schedule for Cron
```bash
# Daily at 2 AM
0 2 * * * cd /path/to/project && python manage.py update_analytics
```

---

## 📈 Key Metrics Explained

### Daily Metrics
- **Total Orders**: Number of completed orders
- **Unique Customers**: Count of customers who ordered
- **Total Revenue**: Sum of all order totals
- **Total Discount**: Sum of all discounts applied
- **Average Order Value**: Revenue / Orders

### Customer Metrics
- **Lifetime Value (LTV)**: Total spent by customer
- **Churn Risk**: No order in 60+ days
- **Days Since Last Order**: Days of inactivity
- **VIP Tier**: Bronze, Silver, Gold, Platinum
- **Loyalty Points**: Points earned and redeemed

### Campaign Metrics
- **Orders Influenced**: Orders attributed to campaign
- **Conversion Rate**: Customers converted / Reached %
- **ROI**: (Revenue - Budget) / Budget * 100
- **Revenue Generated**: Total revenue from campaign

---

## 🔗 Integration Points

### Automatic Tracking (via Signals)
1. **Order Completion** → Tracks revenue and updates metrics
2. **Payment Processing** → Records payment method and amount
3. **Subscription Changes** → Updates subscription revenue
4. **Loyalty Actions** → Tracks points and tier changes

### API Endpoints
```
GET /analytics/api/daily-revenue/?days=30
Response: {dates: [], revenue: [], orders: []}

GET /analytics/api/customer-segments/
Response: {vip_customers: 0, subscribed: 0, ...}
```

---

## 👤 User Roles & Access

### Staff Members
- Can view all analytics dashboards
- Cannot create/edit campaigns (admin only)
- Cannot access detailed configurations

### Admins
- Full access to all analytics views
- Can create and manage campaigns
- Can configure campaigns in Django admin
- Can view complete customer data

### Login Required
All analytics pages require:
- Valid user login
- Staff status (is_staff = True)

---

## 📱 Dashboard Features

### Main Dashboard
✅ Real-time KPI cards  
✅ Revenue trend chart  
✅ Payment method breakdown  
✅ Customer segments  
✅ Quick action buttons  

### Revenue Analysis
✅ Channel comparison  
✅ Percentage distribution  
✅ Daily trends  
✅ Time period filtering  
✅ Progress visualization  

### Customer Analytics
✅ Segment totals  
✅ Loyalty metrics  
✅ Referral stats  
✅ Top customers list  
✅ At-risk identification  

### Campaign Manager
✅ Campaign list with status  
✅ Performance metrics  
✅ ROI tracking  
✅ Filter by status  
✅ Quick edit access  

---

## 🛠️ Configuration

### Settings.py
```python
INSTALLED_APPS = [
    ...
    'analytics',  # Added for Phase 4
]
```

### URLs.py
```python
path('analytics/', include('analytics.urls')),
```

### Database
- 7 new tables created
- 1 migration applied
- All relationships configured

---

## 📊 Sample Queries

### Django ORM Examples
```python
# Get today's snapshot
today = DailyAnalyticsSnapshot.objects.get(date=timezone.now().date())

# Get top customers
top_customers = CustomerMetrics.objects.order_by('-lifetime_value')[:10]

# Get at-risk customers
at_risk = CustomerMetrics.objects.filter(churn_risk=True)

# Get active campaigns
active = Campaign.objects.filter(status='active')

# Get revenue by channel
revenue = RevenueStream.objects.values('channel').annotate(Sum('amount'))
```

### Service Layer
```python
from analytics.services import AnalyticsService

# Calculate daily snapshot
snapshot = AnalyticsService.calculate_daily_snapshot()

# Update customer metrics
metrics = AnalyticsService.update_customer_metrics(user)

# Get customer segments
segments = AnalyticsService.get_customer_segments()

# Calculate campaign ROI
roi = AnalyticsService.get_campaign_roi(campaign)
```

---

## 📋 Admin Interface

### Access Django Admin
```
URL: http://localhost:8000/admin/
Navigate: Analytics section
```

### Available Models
1. Daily Analytics Snapshot
2. Revenue Stream
3. Customer Metrics
4. Campaign
5. Campaign Performance
6. Page View Analytics
7. Conversion Event

### Admin Features
- Full CRUD operations
- Advanced filtering
- Search functionality
- Bulk actions
- Custom displays
- Read-only fields
- Organized fieldsets

---

## 🚨 Common Issues & Solutions

### Analytics Not Showing Data
**Problem**: Dashboard shows 0 values  
**Solution**: Run `python manage.py update_analytics --backfill`

### Charts Not Displaying
**Problem**: Charts appear blank  
**Solution**: 
1. Check browser console for errors
2. Verify Chart.js library loads
3. Ensure data exists in database

### Permission Denied
**Problem**: "Not allowed" when accessing analytics  
**Solution**: 
1. Ensure user is staff (is_staff=True)
2. Login as admin or staff member
3. Check user permissions in admin

### Migration Issues
**Problem**: Migration errors  
**Solution**:
1. Run `python manage.py showmigrations analytics`
2. Ensure analytics in INSTALLED_APPS
3. Run `python manage.py migrate`

---

## 📞 Support & Documentation

### File Structure
```
analytics/
├── models.py          # 7 models, 400+ lines
├── views.py          # 5 views, 280+ lines
├── services.py       # Analytics logic, 350+ lines
├── urls.py          # URL routing
├── admin.py         # Admin configuration
├── apps.py          # App config with signals
├── signals.py       # Event handlers
├── migrations/
│   └── 0001_initial.py
├── management/commands/
│   └── update_analytics.py
└── templates/analytics/
    ├── dashboard.html
    ├── revenue_streams.html
    ├── customer_analytics.html
    └── campaigns.html
```

### Documentation Files
- `PHASE4_ANALYTICS_IMPLEMENTATION.md` - Complete guide
- `PROJECT_STATUS.md` - Project overview
- This file - Quick reference

---

## ✨ Phase 4 Status: COMPLETE & PRODUCTION READY

**Date Completed**: 2024  
**Status**: ✅ ALL SYSTEMS OPERATIONAL  
**System Check**: ✅ 0 ISSUES  
**Migrations**: ✅ APPLIED  

All components are functioning correctly and ready for production deployment.
