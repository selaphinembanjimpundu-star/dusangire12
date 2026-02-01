from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal
from menu.models import MenuItem

class HealthMetricType(models.Model):
    """Define types of health metrics that can be tracked"""
    CATEGORY_CHOICES = [
        ('vital', 'Vital Signs'),
        ('wellness', 'Wellness Indicators'),
        ('custom', 'Custom Metric'),
    ]
    
    metric_name = models.CharField(max_length=100, unique=True)
    unit = models.CharField(max_length=50)  # kg, mmHg, mg/dL, etc.
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    
    # Normal ranges (can be null for custom metrics)
    normal_range_min = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True
    )
    normal_range_max = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True
    )
    
    # Alert thresholds
    alert_threshold_min = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True,
        help_text="Value below this triggers alert"
    )
    alert_threshold_max = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True,
        help_text="Value above this triggers alert"
    )
    
    description = models.TextField(blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['category', 'metric_name']
        verbose_name = 'Health Metric Type'
        verbose_name_plural = 'Health Metric Types'
    
    def __str__(self):
        return f"{self.metric_name} ({self.unit})"


class DailyHealthMetric(models.Model):
    """Track daily health metrics for users"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='health_metrics')
    metric_type = models.ForeignKey(HealthMetricType, on_delete=models.PROTECT)
    
    value = models.DecimalField(max_digits=8, decimal_places=2)
    recorded_date = models.DateField(default=timezone.now, db_index=True)
    recorded_time = models.TimeField(default=timezone.now)
    
    # Notes and context
    notes = models.TextField(blank=True)
    conditions = models.CharField(
        max_length=255, blank=True,
        help_text="e.g., 'After exercise', 'Before meal', 'Fasting'"
    )
    
    # Image for reference (optional)
    image = models.ImageField(upload_to='health_metrics/', blank=True, null=True)
    
    is_alert_generated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-recorded_date', '-recorded_time']
        verbose_name = 'Daily Health Metric'
        verbose_name_plural = 'Daily Health Metrics'
        unique_together = ('user', 'metric_type', 'recorded_date')
    
    def __str__(self):
        return f"{self.user.username} - {self.metric_type.metric_name}: {self.value}"
    
    @property
    def is_in_alert_range(self):
        """Check if metric is outside alert thresholds"""
        if self.metric_type.alert_threshold_min and self.value < self.metric_type.alert_threshold_min:
            return True
        if self.metric_type.alert_threshold_max and self.value > self.metric_type.alert_threshold_max:
            return True
        return False


class PatientHealthGoal(models.Model):
    """Track patient health goals and progress"""
    GOAL_TYPE_CHOICES = [
        ('weight_loss', 'Weight Loss'),
        ('weight_gain', 'Weight Gain'),
        ('energy', 'Increase Energy'),
        ('fitness', 'Improve Fitness'),
        ('digestion', 'Better Digestion'),
        ('sleep', 'Improve Sleep'),
        ('custom', 'Custom Goal'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('abandoned', 'Abandoned'),
        ('on_hold', 'On Hold'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='health_goals')
    
    goal_name = models.CharField(max_length=200)
    description = models.TextField()
    goal_type = models.CharField(max_length=20, choices=GOAL_TYPE_CHOICES)
    
    # Metric tracking
    metric_type = models.ForeignKey(
        HealthMetricType, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='tracked_in_goals'
    )
    
    # Target and progress
    target_value = models.DecimalField(max_digits=8, decimal_places=2)
    current_value = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True
    )
    
    # Timeline
    start_date = models.DateField(default=timezone.now)
    target_date = models.DateField()
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    completed_date = models.DateField(null=True, blank=True)
    
    # Metadata
    priority = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(5)])
    is_public = models.BooleanField(default=False, help_text="Share with nutritionist")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Patient Health Goal'
        verbose_name_plural = 'Patient Health Goals'
    
    def __str__(self):
        return f"{self.user.username} - {self.goal_name}"
    
    @property
    def progress_percentage(self):
        """Calculate goal progress percentage"""
        if not self.metric_type or self.current_value is None:
            return 0
        
        if self.goal_type == 'weight_loss':
            # Starting value - current value / starting value - target value
            if self.metric_type.normal_range_max:
                start = self.metric_type.normal_range_max
                progress = (start - self.current_value) / (start - self.target_value)
                return min(100, max(0, progress * 100))
        
        return ((self.current_value - self.metric_type.normal_range_min) / 
                (self.target_value - self.metric_type.normal_range_min) * 100) if self.metric_type else 0
    
    @property
    def days_remaining(self):
        """Calculate days until target date"""
        return (self.target_date - timezone.now().date()).days


class GoalMilestone(models.Model):
    """Track milestones within a health goal"""
    health_goal = models.ForeignKey(PatientHealthGoal, on_delete=models.CASCADE, related_name='milestones')
    
    milestone_name = models.CharField(max_length=200)
    target_value = models.DecimalField(max_digits=8, decimal_places=2)
    target_date = models.DateField()
    
    achievement_order = models.IntegerField(default=1)
    achieved_date = models.DateField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['achievement_order']
        verbose_name = 'Goal Milestone'
        verbose_name_plural = 'Goal Milestones'
    
    def __str__(self):
        return f"{self.health_goal.goal_name} - {self.milestone_name}"
    
    @property
    def is_achieved(self):
        return self.achieved_date is not None


class MealReview(models.Model):
    """Track user reviews and effects of meals"""
    RATING_SCALE = [
        (1, '⭐ Poor'),
        (2, '⭐⭐ Fair'),
        (3, '⭐⭐⭐ Good'),
        (4, '⭐⭐⭐⭐ Very Good'),
        (5, '⭐⭐⭐⭐⭐ Excellent'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='meal_reviews')
    meal = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='health_reviews')
    
    # Ratings (1-5 scale)
    overall_rating = models.IntegerField(choices=RATING_SCALE, validators=[MinValueValidator(1), MaxValueValidator(5)])
    satisfaction = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    digestibility = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    energy_level = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    mood_after = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    
    # Comments and details
    notes = models.TextField(blank=True)
    allergies_or_issues = models.CharField(max_length=255, blank=True)
    
    # Consumption tracking
    date_consumed = models.DateField(default=timezone.now, db_index=True)
    time_consumed = models.TimeField(default=timezone.now)
    
    # Health context
    health_condition_at_time = models.CharField(
        max_length=255, blank=True,
        help_text="e.g., 'Tired', 'Stressed', 'Hungry', 'Full'"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date_consumed', '-time_consumed']
        verbose_name = 'Meal Review'
        verbose_name_plural = 'Meal Reviews'
        unique_together = ('user', 'meal', 'date_consumed')
    
    def __str__(self):
        return f"{self.user.username} - {self.meal.name}: {self.overall_rating}★"
    
    @property
    def average_score(self):
        """Calculate average effectiveness score"""
        scores = [self.satisfaction, self.digestibility, self.energy_level, self.mood_after]
        return sum(scores) / len(scores) if scores else 0


class MealEffectivenessScore(models.Model):
    """Aggregate effectiveness scores for meals across all users"""
    meal = models.OneToOneField(MenuItem, on_delete=models.CASCADE, related_name='health_effectiveness')
    
    total_reviews = models.IntegerField(default=0)
    unique_users = models.IntegerField(default=0)
    
    avg_overall_rating = models.DecimalField(max_digits=3, decimal_places=2, default=Decimal('0.00'))
    avg_satisfaction = models.DecimalField(max_digits=3, decimal_places=2, default=Decimal('0.00'))
    avg_digestibility = models.DecimalField(max_digits=3, decimal_places=2, default=Decimal('0.00'))
    avg_energy = models.DecimalField(max_digits=3, decimal_places=2, default=Decimal('0.00'))
    avg_mood = models.DecimalField(max_digits=3, decimal_places=2, default=Decimal('0.00'))
    
    effectiveness_score = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal('0.00'),
        help_text="Weighted effectiveness (0-100)"
    )
    
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Meal Effectiveness Score'
        verbose_name_plural = 'Meal Effectiveness Scores'
    
    def __str__(self):
        return f"{self.meal.name} - {self.effectiveness_score}% effective"


class HealthReport(models.Model):
    """Generated health reports for patients and nutritionists"""
    REPORT_TYPE_CHOICES = [
        ('weekly', 'Weekly Report'),
        ('monthly', 'Monthly Report'),
        ('goal_progress', 'Goal Progress Report'),
        ('meal_analysis', 'Meal Analysis Report'),
        ('custom', 'Custom Report'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='health_reports')
    
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES)
    report_title = models.CharField(max_length=255)
    report_date = models.DateField(default=timezone.now)
    
    # Report content (stored as JSON for flexibility)
    metrics_summary = models.JSONField(default=dict, blank=True)
    goal_progress = models.JSONField(default=dict, blank=True)
    meal_analysis = models.JSONField(default=dict, blank=True)
    
    # Narrative report
    summary = models.TextField()
    recommendations = models.TextField(blank=True)
    key_findings = models.TextField(blank=True)
    
    # Metadata
    generated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='generated_reports',
        limit_choices_to={'is_staff': True}
    )
    
    is_shared_with_nutritionist = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-report_date']
        verbose_name = 'Health Report'
        verbose_name_plural = 'Health Reports'
    
    def __str__(self):
        return f"{self.user.username} - {self.report_title} ({self.report_date})"


class HealthAlert(models.Model):
    """Alerts generated from health data anomalies"""
    ALERT_TYPE_CHOICES = [
        ('unusual_metric', 'Unusual Metric Reading'),
        ('goal_achieved', 'Goal Achieved'),
        ('goal_at_risk', 'Goal At Risk'),
        ('milestone_reached', 'Milestone Reached'),
        ('health_trend', 'Health Trend Alert'),
        ('medication_reminder', 'Medication Reminder'),
        ('custom', 'Custom Alert'),
    ]
    
    SEVERITY_CHOICES = [
        ('info', 'Information'),
        ('warning', 'Warning'),
        ('critical', 'Critical'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='health_alerts')
    
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPE_CHOICES)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default='info')
    
    title = models.CharField(max_length=255)
    message = models.TextField()
    
    # Link to triggering data
    metric = models.ForeignKey(
        DailyHealthMetric, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='triggered_alerts'
    )
    goal = models.ForeignKey(
        PatientHealthGoal, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='triggered_alerts'
    )
    
    # Alert status
    is_acknowledged = models.BooleanField(default=False)
    acknowledged_date = models.DateTimeField(null=True, blank=True)
    acknowledged_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='acknowledged_alerts',
        limit_choices_to={'is_staff': True}
    )
    
    # Notification settings
    send_email = models.BooleanField(default=True)
    send_sms = models.BooleanField(default=False)
    notify_nutritionist = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at', 'user']),
            models.Index(fields=['severity', 'is_acknowledged']),
        ]
        verbose_name = 'Health Alert'
        verbose_name_plural = 'Health Alerts'
    
    def __str__(self):
        return f"{self.user.username} - {self.title} ({self.severity})"
