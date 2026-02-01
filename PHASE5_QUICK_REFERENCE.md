# PHASE 5: QUICK REFERENCE & TROUBLESHOOTING

## 🎯 Common Workflows

### Workflow 1: Patient Tracks Daily Metrics

**Scenario**: Patient wants to record daily weight and blood pressure

**Steps**:
1. Log into patient account
2. Navigate to `/health-tracking/metrics/add/`
3. Select "Weight" from metric type dropdown
4. Enter value (e.g., 75.5)
5. Optionally add notes: "After morning routine"
6. Click "Save Metric"
7. System automatically:
   - Checks if in alert range
   - Updates any related goal progress
   - Triggers health score recalculation

**Expected Outcome**: 
- Metric appears in dashboard
- Health score updates
- Any alerts appear immediately

---

### Workflow 2: Nutritionist Reviews Patient Progress

**Scenario**: Nutritionist needs to check patient's goal progress

**Steps**:
1. Log in with nutritionist account
2. Navigate to `/health-tracking/dashboard/nutritionist/`
3. View list of patients sharing data
4. Click patient to see:
   - Active health goals
   - Recent metrics
   - Meal effectiveness data
   - Pending alerts

**Admin Approach**:
1. Go to Admin Dashboard
2. Select "Patient Health Goals" 
3. Filter by "Status: Active" and "Is Public: True"
4. View progress percentages (visual progress bars)
5. Check "Days Remaining" for urgent goals

**Expected Outcome**:
- Clear visibility of patient health status
- Ability to identify at-risk goals
- Data for intervention recommendations

---

### Workflow 3: Create a Health Goal

**Scenario**: Patient wants to set a weight loss goal

**Steps**:
1. Go to Admin Dashboard
2. Navigate to "Patient Health Goals"
3. Click "Add Patient Health Goal"
4. Fill in:
   - Goal Name: "Lose 5kg"
   - Description: "Reach healthy BMI"
   - Goal Type: "Weight Loss"
   - Metric Type: "Weight"
   - Target Value: 70
   - Start Date: Today
   - Target Date: 3 months from now
   - Priority: 5 (highest)
   - Is Public: Check (share with nutritionist)
5. Click "Save"
6. Add milestones:
   - Milestone 1: Target 73kg by Month 1
   - Milestone 2: Target 71.5kg by Month 2
   - Milestone 3: Target 70kg by Month 3

**Expected Outcome**:
- Goal appears in patient dashboard
- Progress can be tracked via metrics
- Alerts trigger if goal at risk

---

### Workflow 4: Patient Reviews a Meal

**Scenario**: After eating a meal, patient wants to rate effectiveness

**Steps**:
1. Navigate to `/health-tracking/meal-review/create/`
2. Select meal from dropdown
3. Rate on 5 dimensions (1-5 scale):
   - Overall Rating: 4 (Very Good)
   - Satisfaction: 4 (Satisfied)
   - Digestibility: 3 (Okay, some bloating)
   - Energy Level: 4 (Felt energized)
   - Mood After: 4 (Happy)
4. Add conditions: "After lunch"
5. Add notes: "Slight bloating but otherwise good"
6. Click "Save Review"

**What Happens**:
- Review saved with timestamp
- Meal effectiveness score updated globally
- System generates insights if rating is low (< 2)
- Recommendations may appear in future reports

**Expected Outcome**:
- Review appears in meal history
- Meal effectiveness updated
- Aggregated score available for nutritionist insights

---

### Workflow 5: View Health Report

**Scenario**: Patient wants monthly health summary

**Steps**:
1. Navigate to `/health-tracking/reports/`
2. Click "Generate New Report"
3. Select report type: "Monthly Report"
4. System generates:
   - Metrics Summary (averages, min/max)
   - Goal Progress (% completion, days remaining)
   - Meal Analysis (most effective meals, average satisfaction)
   - Health Score trend
   - Personalized recommendations
5. View or download report

**Expected Outcome**:
- Comprehensive health summary
- Data-driven insights
- Actionable recommendations

---

## 🔧 Troubleshooting

### Problem: Health Score Not Updating
**Possible Causes**:
1. No active goals set - system defaults to 50%
2. Metrics not recorded - shows 50% for consistency
3. Signals not triggered

**Solution**:
```python
# Check if signals are loaded
from django.apps import apps
print(apps.get_app_config('health_tracking').ready())

# Manually trigger signal
from health_tracking.services import HealthService
HealthService.calculate_health_score(user)
```

---

### Problem: Alert Not Generated for Out-of-Range Metric
**Possible Causes**:
1. Alert thresholds not set on HealthMetricType
2. Metric value is within range
3. is_alert_generated already set to True

**Solution**:
1. Check HealthMetricType settings:
   ```python
   from health_tracking.models import HealthMetricType
   metric = HealthMetricType.objects.get(metric_name='Weight')
   print(f"Min: {metric.alert_threshold_min}, Max: {metric.alert_threshold_max}")
   ```

2. Verify metric value is actually out of range
3. Check if alert already exists:
   ```python
   from health_tracking.models import HealthAlert
   alerts = HealthAlert.objects.filter(metric_id=metric.id)
   ```

---

### Problem: Meal Review Not Saving
**Possible Causes**:
1. MenuItem doesn't exist
2. Rating validation failed (not 1-5)
3. User not authenticated

**Solution**:
```python
# Verify menu item exists
from menu.models import MenuItem
MenuItem.objects.filter(id=meal_id).exists()

# Check validation
if not (1 <= rating <= 5):
    print("Invalid rating")
```

---

### Problem: Goal Progress Not Calculating
**Possible Causes**:
1. Metric type not set on goal
2. No recent metrics for that type
3. Metric type normal_range not configured

**Solution**:
```python
# Check goal setup
goal = PatientHealthGoal.objects.get(id=goal_id)
print(f"Metric: {goal.metric_type}")
print(f"Current: {goal.current_value}, Target: {goal.target_value}")

# Manually update
from health_tracking.services import HealthService
HealthService.update_goal_progress(goal)
```

---

## 🎨 Admin Interface Tips

### Quick Filters
- **By Status**: Active, Completed, Abandoned, On Hold
- **By Date**: Use date hierarchy for metrics/goals/alerts
- **By Severity**: Critical, Warning, Info for alerts
- **By Type**: Vital Signs, Wellness, Custom for metric types

### Bulk Actions
- Select multiple alerts → "Mark as acknowledged"
- Select multiple goals → Filter and export
- Select metrics → View trends

### Custom Displays
- Progress bars show goal completion percentage
- Star ratings show meal quality
- Color-coded severity (Red=Critical, Orange=Warning, Blue=Info)

### Search Tips
```
Search by:
- User username or email
- Metric name
- Alert title or message
- Meal name
- Goal name
```

---

## 📊 Data Insights

### Health Score Calculation
```
Total Score = (Goals: 40%) + (Metrics: 30%) + (Meals: 20%) + (Alerts: 10%)

Components:
- Goals: Average progress of active goals (0-100%)
- Metrics: % of recent metrics in normal range
- Meals: Average meal rating converted to percentage
- Alerts: Deduction for unacknowledged critical alerts
```

### Meal Effectiveness Formula
```
Effectiveness = (Overall: 40%) + (Digestibility: 25%) + (Energy: 20%) + (Mood: 15%)
Range: 0-100%
```

### Goal Progress
```
% Progress = ((Current - Normal Min) / (Target - Normal Min)) * 100
For Weight Loss: ((Start - Current) / (Start - Target)) * 100
```

---

## 🔐 Permissions & Access

| Feature | Patient | Nutritionist | Admin |
|---------|---------|--------------|-------|
| View own dashboard | ✅ | - | ✅ |
| View nutritionist dashboard | - | ✅ | ✅ |
| Add metrics | ✅ | - | ✅ |
| Create goals | ✅ | - | ✅ |
| Review meals | ✅ | - | ✅ |
| View reports | ✅ | ✅ | ✅ |
| Manage all users' data | - | - | ✅ |
| Configure metric types | - | - | ✅ |

---

## 🚨 Common Errors & Fixes

### Error: "HealthMetricType matching query does not exist"
```
Fix: Create metric type in admin first
from health_tracking.models import HealthMetricType
HealthMetricType.objects.create(
    metric_name='Weight',
    unit='kg',
    category='vital'
)
```

### Error: "One-to-one relationship violation"
```
Fix: MealEffectivenessScore is one-to-one with MenuItem
Check if score already exists for meal:
from health_tracking.models import MealEffectivenessScore
MealEffectivenessScore.objects.filter(meal_id=meal_id).exists()
```

### Error: "TimeZone aware/naive mismatch"
```
Fix: Use timezone.now() instead of datetime.now()
from django.utils import timezone
date = timezone.now().date()
```

---

## 📈 Performance Tips

1. **For High Traffic**:
   - Index frequently filtered fields (user, recorded_date, status)
   - Use select_related for foreign keys
   - Cache health scores (recalculate every 24 hours)

2. **For Large Datasets**:
   - Paginate metric lists
   - Use bulk_create for batch metrics
   - Archive old alerts periodically

3. **Query Optimization**:
   ```python
   # Good
   metrics = DailyHealthMetric.objects.select_related('metric_type').filter(user=user)
   
   # Bad
   for metric in DailyHealthMetric.objects.filter(user=user):
       print(metric.metric_type.name)  # N+1 query
   ```

---

## 📞 Support & Questions

For issues:
1. Check admin interface for data integrity
2. Review system check: `python manage.py check`
3. Check migration status: `python manage.py showmigrations`
4. Review signal handlers in `health_tracking/signals.py`
5. Verify app is in INSTALLED_APPS in settings.py
