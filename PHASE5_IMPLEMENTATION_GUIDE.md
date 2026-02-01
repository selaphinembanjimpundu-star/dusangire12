# PHASE 5: IMPLEMENTATION GUIDE

## 📋 Complete Technical Architecture

### System Overview
```
┌─────────────────────────────────────────────────────────┐
│                 Health Tracking System                  │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Patient    │  │ Nutritionist │  │    Admin     │  │
│  │  Dashboard   │  │  Dashboard   │  │ Dashboard    │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
│         │                 │                 │           │
│  ┌──────────────────────────────────────────────────┐   │
│  │            Views Layer (6 views)                  │   │
│  │ - health_dashboard_patient                        │   │
│  │ - health_dashboard_nutritionist                   │   │
│  │ - health_metrics_add                              │   │
│  │ - health_goals_manage                             │   │
│  │ - meal_review_create                              │   │
│  │ - health_reports_view                             │   │
│  └──────┬──────────────────────────────────────────┘   │
│         │                                               │
│  ┌──────────────────────────────────────────────────┐   │
│  │       Service Layer (HealthService)               │   │
│  │ - calculate_health_score()                        │   │
│  │ - update_goal_progress()                          │   │
│  │ - detect_health_alerts()                          │   │
│  │ - analyze_meal_effectiveness()                    │   │
│  │ - generate_health_report()                        │   │
│  │ - get_metric_trends()                             │   │
│  │ - get_goal_recommendations()                      │   │
│  │ - calculate_health_improvement()                  │   │
│  └──────┬──────────────────────────────────────────┘   │
│         │                                               │
│  ┌──────────────────────────────────────────────────┐   │
│  │       Models Layer (8 models)                     │   │
│  │ - HealthMetricType                                │   │
│  │ - DailyHealthMetric                               │   │
│  │ - PatientHealthGoal                               │   │
│  │ - GoalMilestone                                   │   │
│  │ - MealReview                                      │   │
│  │ - MealEffectivenessScore                          │   │
│  │ - HealthReport                                    │   │
│  │ - HealthAlert                                     │   │
│  └──────┬──────────────────────────────────────────┘   │
│         │                                               │
│  ┌──────────────────────────────────────────────────┐   │
│  │          Database (SQLite/PostgreSQL)             │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 🗂️ Models Architecture

### 1. HealthMetricType
**Purpose**: Define what metrics can be tracked

```python
class HealthMetricType(models.Model):
    metric_name: CharField  # e.g., "Weight", "Blood Pressure"
    unit: CharField         # e.g., "kg", "mmHg"
    category: CharField     # vital / wellness / custom
    normal_range_min: DecimalField
    normal_range_max: DecimalField
    alert_threshold_min: DecimalField
    alert_threshold_max: DecimalField
    description: TextField
    active: BooleanField
    timestamps: DateTimeField
```

**Key Features**:
- Configurable alert thresholds
- Normal ranges for context
- Active/inactive flag for management
- Multiple categories for organization

**Relationships**:
- Referenced by: DailyHealthMetric (FK), PatientHealthGoal (FK)

---

### 2. DailyHealthMetric
**Purpose**: Store individual health metric recordings

```python
class DailyHealthMetric(models.Model):
    user: ForeignKey(User)
    metric_type: ForeignKey(HealthMetricType)
    value: DecimalField
    recorded_date: DateField
    recorded_time: TimeField
    notes: TextField
    conditions: CharField  # e.g., "After exercise", "Fasting"
    image: ImageField
    is_alert_generated: BooleanField
    timestamps: DateTimeField
    
    # Computed property
    is_in_alert_range: bool
```

**Key Features**:
- Temporal tracking (date + time)
- Contextual notes (conditions)
- Image attachments for visual records
- Automatic alert threshold checking
- Unique constraint: (user, metric_type, recorded_date)

**Signal Handlers**:
- `health_metric_saved`: Triggers alert detection on creation

---

### 3. PatientHealthGoal
**Purpose**: Track patient health objectives

```python
class PatientHealthGoal(models.Model):
    user: ForeignKey(User)
    goal_name: CharField
    description: TextField
    goal_type: CharField  # weight_loss/gain, energy, fitness, etc.
    metric_type: ForeignKey(HealthMetricType, null=True)
    target_value: DecimalField
    current_value: DecimalField
    start_date: DateField
    target_date: DateField
    status: CharField  # active / completed / abandoned / on_hold
    completed_date: DateField
    priority: IntegerField (1-5)
    is_public: BooleanField  # Share with nutritionist
    timestamps: DateTimeField
    
    # Computed properties
    progress_percentage: float
    days_remaining: int
```

**Key Features**:
- Multiple goal types (weight, fitness, wellness)
- Progress calculation
- Timeline tracking
- Milestone support (via GoalMilestone)
- Public/private sharing
- Priority levels

**Signal Handlers**:
- `goal_status_changed`: Creates alert on completion

---

### 4. GoalMilestone
**Purpose**: Break goals into measurable checkpoints

```python
class GoalMilestone(models.Model):
    health_goal: ForeignKey(PatientHealthGoal)
    milestone_name: CharField
    target_value: DecimalField
    target_date: DateField
    achievement_order: IntegerField
    achieved_date: DateField
    created_at: DateTimeField
    
    # Computed property
    is_achieved: bool
```

**Key Features**:
- Ordered milestones
- Target tracking
- Achievement date recording
- Parent goal relationship

---

### 5. MealReview
**Purpose**: Track meal effectiveness from patient perspective

```python
class MealReview(models.Model):
    user: ForeignKey(User)
    meal: ForeignKey(MenuItem)
    overall_rating: IntegerField (1-5)
    satisfaction: IntegerField (1-5)
    digestibility: IntegerField (1-5)
    energy_level: IntegerField (1-5)
    mood_after: IntegerField (1-5)
    notes: TextField
    allergies_or_issues: CharField
    date_consumed: DateField
    time_consumed: TimeField
    health_condition_at_time: CharField
    timestamps: DateTimeField
    
    # Computed property
    average_score: float
```

**Key Features**:
- Multi-dimensional ratings
- Temporal tracking
- Allergy/issue documentation
- Context capture (health condition)
- Unique constraint: (user, meal, date_consumed)

**Signal Handlers**:
- `meal_review_saved`: Updates meal effectiveness score

---

### 6. MealEffectivenessScore
**Purpose**: Aggregate meal effectiveness across all users

```python
class MealEffectivenessScore(models.Model):
    meal: OneToOneField(MenuItem)
    total_reviews: IntegerField
    unique_users: IntegerField
    avg_overall_rating: DecimalField
    avg_satisfaction: DecimalField
    avg_digestibility: DecimalField
    avg_energy: DecimalField
    avg_mood: DecimalField
    effectiveness_score: DecimalField (0-100%)
    last_updated: DateTimeField
```

**Key Features**:
- One-to-one with MenuItem
- Weighted effectiveness calculation
- Comprehensive metrics
- Auto-updated via signal handler

**Calculation**:
```
Effectiveness = (Overall: 40%) + (Digestibility: 25%) 
              + (Energy: 20%) + (Mood: 15%)
```

---

### 7. HealthReport
**Purpose**: Generate comprehensive health summaries

```python
class HealthReport(models.Model):
    user: ForeignKey(User)
    report_type: CharField  # weekly / monthly / goal_progress / meal_analysis
    report_title: CharField
    report_date: DateField
    metrics_summary: JSONField
    goal_progress: JSONField
    meal_analysis: JSONField
    summary: TextField
    recommendations: TextField
    key_findings: TextField
    generated_by: ForeignKey(User, to_field=is_staff)
    is_shared_with_nutritionist: BooleanField
    timestamps: DateTimeField
```

**Key Features**:
- Flexible JSON storage for complex data
- Multiple report types
- Narrative summaries
- Shareable with nutritionists
- Auto-generated or manual

**Report Contents**:
```json
{
  "metrics_summary": {
    "Weight": {
      "count": 30,
      "avg": 75.2,
      "min": 74.5,
      "max": 76.0
    }
  },
  "goal_progress": {
    "Weight Loss": {
      "progress": 65,
      "days_remaining": 45,
      "target_date": "2025-06-30"
    }
  },
  "meal_analysis": {
    "total_reviewed": 25,
    "best_meals": [...],
    "avg_satisfaction": 4.2
  }
}
```

---

### 8. HealthAlert
**Purpose**: Intelligent alerts for health anomalies

```python
class HealthAlert(models.Model):
    user: ForeignKey(User)
    alert_type: CharField  # unusual_metric / goal_achieved / goal_at_risk / etc.
    severity: CharField    # info / warning / critical
    title: CharField
    message: TextField
    metric: ForeignKey(DailyHealthMetric, null=True)
    goal: ForeignKey(PatientHealthGoal, null=True)
    is_acknowledged: BooleanField
    acknowledged_date: DateTimeField
    acknowledged_by: ForeignKey(User, to_field=is_staff)
    send_email: BooleanField
    send_sms: BooleanField
    notify_nutritionist: BooleanField
    timestamps: DateTimeField
```

**Key Features**:
- Multiple alert types
- Severity levels
- Linked to source data
- Acknowledgment tracking
- Flexible notification settings

**Alert Types**:
- `unusual_metric`: Out-of-range reading
- `goal_achieved`: Goal completed
- `goal_at_risk`: Won't meet deadline
- `milestone_reached`: Milestone achieved
- `health_trend`: Trend alert
- `medication_reminder`: Medication time
- `custom`: Custom alert

---

## 🔧 Service Layer: HealthService

### Core Methods

#### 1. `calculate_health_score(user) -> float`
**Purpose**: Compute overall health score (0-100)

```python
def calculate_health_score(user):
    """
    Score Composition:
    - Goals Progress: 40% (average % completion)
    - Metrics Consistency: 30% (% in normal range, past 7 days)
    - Meal Effectiveness: 20% (average rating / 5 * 100)
    - Alert Status: 10% (deduction for critical unacknowledged)
    
    Returns: float (0-100)
    """
    # 1. Calculate goals contribution (40%)
    goals = PatientHealthGoal.objects.filter(user=user, status='active')
    goal_score = avg(goals.progress_percentage) * 0.4 if goals else 50 * 0.4
    
    # 2. Calculate metrics consistency (30%)
    week_metrics = DailyHealthMetric.objects.filter(
        user=user,
        recorded_date__gte=now - 7 days
    )
    consistency = (in_range_count / total_count) * 100 * 0.3 if week_metrics else 50 * 0.3
    
    # 3. Calculate meal score (20%)
    meal_reviews = MealReview.objects.filter(user=user)
    meal_score = (avg_rating / 5) * 100 * 0.2 if meal_reviews else 50 * 0.2
    
    # 4. Calculate alert penalty (10%)
    critical_alerts = HealthAlert.objects.filter(
        user=user,
        severity='critical',
        is_acknowledged=False
    )
    alert_score = max(0, 10 - (critical_count * 3))
    
    return min(100, max(0, goal_score + consistency + meal_score + alert_score))
```

**Usage**:
```python
from health_tracking.services import HealthService
score = HealthService.calculate_health_score(request.user)
print(f"Health Score: {score}/100")
```

---

#### 2. `update_goal_progress(goal) -> None`
**Purpose**: Update goal progress based on latest metric

```python
def update_goal_progress(goal):
    """
    Updates goal's current_value from latest metric
    Checks if goal is achieved and completes if necessary
    """
    if not goal.metric_type:
        return
    
    # Get latest metric
    latest = DailyHealthMetric.objects.filter(
        user=goal.user,
        metric_type=goal.metric_type
    ).latest('recorded_date')
    
    goal.current_value = latest.value
    goal.save()
    
    # Check achievement conditions
    if goal.goal_type == 'weight_loss' and goal.current_value <= goal.target_value:
        complete_goal(goal)
    # ... other goal types
```

---

#### 3. `detect_health_alerts(user) -> List[HealthAlert]`
**Purpose**: Generate alerts for anomalies

```python
def detect_health_alerts(user):
    """
    Detects and creates:
    1. Metrics outside alert thresholds
    2. Goals at risk of not being met
    3. Unusual trends
    
    Returns: List of created alerts
    """
    alerts = []
    
    # 1. Check recent metrics
    recent = DailyHealthMetric.objects.filter(
        user=user,
        recorded_date__gte=now - 1 day,
        is_alert_generated=False
    )
    
    for metric in recent:
        if metric.is_in_alert_range:
            alert = HealthAlert.objects.create(
                user=user,
                alert_type='unusual_metric',
                severity='warning',
                title=f'Alert: {metric.metric_type.metric_name}',
                message=f'Reading {metric.value} is outside normal range',
                metric=metric
            )
            alerts.append(alert)
    
    # 2. Check goals at risk
    at_risk = PatientHealthGoal.objects.filter(
        user=user,
        status='active',
        target_date__lt=now + 14 days
    )
    
    for goal in at_risk:
        if not _is_on_track(goal):
            alert = HealthAlert.objects.create(
                user=user,
                alert_type='goal_at_risk',
                severity='warning',
                title=f'Goal at Risk: {goal.goal_name}',
                goal=goal
            )
            alerts.append(alert)
    
    return alerts
```

---

#### 4. `analyze_meal_effectiveness(meal) -> MealEffectivenessScore`
**Purpose**: Calculate and update meal effectiveness

```python
def analyze_meal_effectiveness(meal):
    """
    Analyzes all reviews for a meal and computes effectiveness score
    
    Formula:
    Effectiveness = (Overall: 40%) + (Digestibility: 25%)
                  + (Energy: 20%) + (Mood: 15%)
    
    Returns: MealEffectivenessScore object
    """
    reviews = MealReview.objects.filter(meal=meal)
    
    if not reviews.exists():
        return None
    
    # Calculate averages
    avg_overall = reviews.aggregate(Avg('overall_rating'))['overall_rating__avg']
    avg_digestibility = reviews.aggregate(Avg('digestibility'))['digestibility__avg']
    avg_energy = reviews.aggregate(Avg('energy_level'))['energy_level__avg']
    avg_mood = reviews.aggregate(Avg('mood_after'))['mood_after__avg']
    
    # Calculate weighted effectiveness
    effectiveness = (
        (avg_overall / 5 * 40) +
        (avg_digestibility / 5 * 25) +
        (avg_energy / 5 * 20) +
        (avg_mood / 5 * 15)
    )
    
    # Save or update
    score_obj, created = MealEffectivenessScore.objects.get_or_create(meal=meal)
    score_obj.effectiveness_score = effectiveness
    score_obj.save()
    
    return score_obj
```

---

#### 5. `generate_health_report(user, report_type) -> HealthReport`
**Purpose**: Create comprehensive health report

```python
def generate_health_report(user, report_type='weekly'):
    """
    Generates report with:
    - Metrics summary (stats by metric type)
    - Goal progress (% completion, timeline)
    - Meal analysis (effectiveness, preferences)
    - Trends and recommendations
    
    Returns: HealthReport object
    """
    if report_type == 'weekly':
        start_date = now - 7 days
    elif report_type == 'monthly':
        start_date = now - 30 days
    
    # Gather data
    metrics = DailyHealthMetric.objects.filter(
        user=user,
        recorded_date__gte=start_date
    )
    
    metrics_summary = {
        metric_type: {
            'count': metrics.filter(metric_type=type).count(),
            'avg': avg(values),
            'min': min(values),
            'max': max(values)
        }
        for metric_type in HealthMetricType.objects.all()
    }
    
    # Similar for goal_progress and meal_analysis
    
    # Create report
    report = HealthReport.objects.create(
        user=user,
        report_type=report_type,
        report_title=f"{report_type.title()} Report",
        metrics_summary=metrics_summary,
        goal_progress=goal_data,
        meal_analysis=meal_data,
        summary="Narrative summary...",
        recommendations="Recommendations..."
    )
    
    return report
```

---

#### 6. `get_metric_trends(user, metric_type, days=30) -> dict`
**Purpose**: Extract trend data for charting

```python
def get_metric_trends(user, metric_type, days=30):
    """
    Returns data suitable for chart.js visualization
    
    Returns:
    {
        'dates': [...],
        'values': [...],
        'metric_name': 'Weight',
        'unit': 'kg',
        'avg': 75.2,
        'min': 74.5,
        'max': 76.0
    }
    """
    start_date = now - days
    metrics = DailyHealthMetric.objects.filter(
        user=user,
        metric_type=metric_type,
        recorded_date__gte=start_date
    ).order_by('recorded_date')
    
    return {
        'dates': [m.recorded_date.isoformat() for m in metrics],
        'values': [float(m.value) for m in metrics],
        'metric_name': metric_type.metric_name,
        'unit': metric_type.unit,
        'avg': avg(values),
        'min': min(values),
        'max': max(values)
    }
```

---

#### 7. `get_goal_recommendations(user) -> List[dict]`
**Purpose**: AI-driven goal suggestions

```python
def get_goal_recommendations(user):
    """
    Analyzes health data and suggests new goals
    
    Returns: [
        {
            'metric': 'Weight',
            'issue': 'Consistently elevated',
            'suggestion': 'Consider weight loss goal',
            'priority': 'high'
        },
        ...
    ]
    """
    recommendations = []
    
    # Analyze recent metrics
    recent = DailyHealthMetric.objects.filter(
        user=user,
        recorded_date__gte=now - 30 days
    )
    
    for metric_type in HealthMetricType.objects.all():
        type_metrics = recent.filter(metric_type=metric_type)
        if type_metrics.count() >= 5:
            avg_value = avg(type_metrics.values_list('value'))
            
            # Check thresholds
            if avg_value > metric_type.alert_threshold_max:
                recommendations.append({
                    'metric': metric_type.metric_name,
                    'issue': 'Consistently elevated',
                    'suggestion': f'Consider lowering {metric_type.metric_name}',
                    'priority': 'high'
                })
    
    return sorted(recommendations, key=lambda x: priority_order[x['priority']])
```

---

## 🔌 Signal Handlers

### health_metric_saved
```python
@receiver(post_save, sender=DailyHealthMetric)
def health_metric_saved(sender, instance, created, **kwargs):
    if created:
        # Auto-detect alerts on metric creation
        if instance.is_in_alert_range:
            HealthService.detect_health_alerts(instance.user)
```

### meal_review_saved
```python
@receiver(post_save, sender=MealReview)
def meal_review_saved(sender, instance, created, **kwargs):
    if created:
        # Update meal effectiveness
        HealthService.analyze_meal_effectiveness(instance.meal)
        
        # Low rating alert
        if instance.overall_rating <= 2:
            HealthAlert.objects.create(...)
```

### goal_status_changed
```python
@receiver(post_save, sender=PatientHealthGoal)
def goal_status_changed(sender, instance, created, **kwargs):
    if not created and instance.status == 'completed':
        # Celebrate goal completion
        HealthAlert.objects.create(
            alert_type='goal_achieved',
            severity='info'
        )
```

---

## 📡 API Endpoints

### GET /health-tracking/dashboard/patient/
Patient personal health dashboard

### GET /health-tracking/dashboard/nutritionist/
Nutritionist professional dashboard

### POST /health-tracking/metrics/add/
Add new health metric

### GET /health-tracking/metrics/trend/<metric_id>/
Get metric trend data (JSON)

### GET/POST /health-tracking/goals/
Manage health goals

### POST /health-tracking/meal-review/create/
Create meal review

### GET /health-tracking/reports/
View health reports

### POST /health-tracking/alerts/<alert_id>/acknowledge/
Acknowledge alert

---

## 🗄️ Database Schema

### Key Indexes
- `DailyHealthMetric`: (user, recorded_date), (metric_type)
- `PatientHealthGoal`: (user, status), (target_date)
- `MealReview`: (user, date_consumed), (meal)
- `HealthAlert`: (user, created_at), (severity, is_acknowledged)

### Constraints
- `DailyHealthMetric`: Unique(user, metric_type, recorded_date)
- `MealReview`: Unique(user, meal, date_consumed)
- `MealEffectivenessScore`: OneToOne with MenuItem

---

## 🔐 Security & Permissions

### Authentication Required
All views require `@login_required` decorator

### Data Privacy
- Patients see only their own data
- Nutritionists see only shared data
- Admins can see all data

### Field Validation
- Rating fields: 1-5 integer validation
- Decimal fields: proper precision (8,2)
- Foreign key constraints enforced

---

## 🧪 Testing Strategy

### Unit Tests
```python
def test_health_score_calculation():
    user = create_test_user()
    goal = create_test_goal(user)
    score = HealthService.calculate_health_score(user)
    assert 0 <= score <= 100

def test_alert_detection():
    metric = create_out_of_range_metric()
    alerts = HealthService.detect_health_alerts(metric.user)
    assert len(alerts) > 0

def test_meal_effectiveness():
    meal = create_test_meal()
    review = create_test_review(meal)
    score = HealthService.analyze_meal_effectiveness(meal)
    assert score.effectiveness_score > 0
```

### Integration Tests
```python
def test_metric_workflow():
    # Add metric → detect alert → update goal → recalc score
    ...

def test_goal_completion():
    # Create goal → add metrics → complete goal → check alerts
    ...
```

---

## 📊 Performance Considerations

### Query Optimization
```python
# Use select_related for ForeignKey
metrics = DailyHealthMetric.objects.select_related('metric_type', 'user')

# Use prefetch_related for reverse relations
goals = PatientHealthGoal.objects.prefetch_related('milestones')

# Use only() to limit fields
alerts = HealthAlert.objects.only('title', 'severity')
```

### Caching Strategy
```python
# Cache health scores (24 hour TTL)
from django.core.cache import cache

score = cache.get(f'health_score_{user_id}')
if score is None:
    score = HealthService.calculate_health_score(user)
    cache.set(f'health_score_{user_id}', score, 86400)
```

### Batch Operations
```python
# Use bulk_create for multiple metrics
metrics = [
    DailyHealthMetric(user=user, value=75.2, ...),
    DailyHealthMetric(user=user, value=74.8, ...),
]
DailyHealthMetric.objects.bulk_create(metrics)
```

---

## 🔄 Data Migration Path

For existing systems:

```python
# 1. Create health metric types
from health_tracking.models import HealthMetricType
metric_types = [
    HealthMetricType(name='Weight', unit='kg'),
    HealthMetricType(name='Blood Pressure', unit='mmHg'),
]
HealthMetricType.objects.bulk_create(metric_types)

# 2. Link existing patient health data
# 3. Generate historical reports
# 4. Set up alert thresholds per metric type
```

---

## 📈 Extension Points

Future enhancements:

1. **Mobile App Integration**: REST API with JWT auth
2. **Wearable Device Sync**: Apple Health, Google Fit
3. **AI Predictions**: ML-based health trend prediction
4. **Advanced Analytics**: Cohort analysis, population health
5. **Compliance**: HIPAA audit logs, encryption
6. **Integration**: EHR systems, lab test results
