from django.db.models import Avg, Q, Count, F
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta
from .models import (
    DailyHealthMetric, PatientHealthGoal, MealReview, HealthAlert,
    HealthReport, HealthMetricType, MealEffectivenessScore, GoalMilestone
)


class HealthService:
    """Business logic for health tracking system"""
    
    @staticmethod
    def calculate_health_score(user):
        """
        Calculate overall health score for a user (0-100)
        Based on:
        - Active goals progress (40%)
        - Recent metrics consistency (30%)
        - Meal effectiveness (20%)
        - Alert status (10%)
        """
        score_components = {}
        
        # Goals progress (0-100)
        goals = PatientHealthGoal.objects.filter(user=user, status='active')
        if goals.exists():
            avg_progress = sum([g.progress_percentage for g in goals]) / goals.count()
            score_components['goals'] = min(100, avg_progress * 0.4)
        else:
            score_components['goals'] = 50  # Neutral if no active goals
        
        # Metrics consistency (past 7 days)
        week_ago = timezone.now().date() - timedelta(days=7)
        metrics = DailyHealthMetric.objects.filter(
            user=user,
            recorded_date__gte=week_ago
        )
        
        in_range = metrics.filter(is_alert_generated=False).count()
        if metrics.exists():
            consistency = (in_range / metrics.count()) * 100
            score_components['metrics'] = consistency * 0.3
        else:
            score_components['metrics'] = 50
        
        # Meal effectiveness
        meal_reviews = MealReview.objects.filter(user=user)
        if meal_reviews.exists():
            avg_meal_score = meal_reviews.aggregate(
                avg_score=Avg('overall_rating')
            )['avg_score'] or 0
            score_components['meals'] = (avg_meal_score / 5) * 100 * 0.2
        else:
            score_components['meals'] = 50
        
        # Alert status
        unacknowledged_alerts = HealthAlert.objects.filter(
            user=user,
            is_acknowledged=False,
            severity='critical'
        ).count()
        alert_deduction = min(10, unacknowledged_alerts * 3)
        score_components['alerts'] = 10 - alert_deduction
        
        total_score = sum(score_components.values())
        return min(100, max(0, total_score))
    
    @staticmethod
    def update_goal_progress(goal):
        """Update progress for a goal based on latest metric"""
        if not goal.metric_type:
            return
        
        # Get latest metric of this type for the user
        latest_metric = DailyHealthMetric.objects.filter(
            user=goal.user,
            metric_type=goal.metric_type
        ).latest('recorded_date')
        
        goal.current_value = latest_metric.value
        goal.save()
        
        # Check if goal is achieved
        if goal.goal_type == 'weight_loss' and goal.current_value <= goal.target_value:
            HealthService.complete_goal(goal)
        elif goal.goal_type == 'weight_gain' and goal.current_value >= goal.target_value:
            HealthService.complete_goal(goal)
        elif goal.goal_type == 'custom' and goal.current_value >= goal.target_value:
            HealthService.complete_goal(goal)
    
    @staticmethod
    def complete_goal(goal):
        """Mark a goal as completed"""
        goal.status = 'completed'
        goal.completed_date = timezone.now().date()
        goal.save()
        
        # Create alert for completion
        HealthAlert.objects.create(
            user=goal.user,
            alert_type='goal_achieved',
            severity='info',
            title=f'Goal Achieved: {goal.goal_name}',
            message=f'Congratulations! You have achieved your goal: {goal.goal_name}',
            goal=goal,
            notify_nutritionist=True
        )
    
    @staticmethod
    def detect_health_alerts(user):
        """
        Detect and generate alerts for health anomalies
        Checks for:
        - Metrics outside alert thresholds
        - Goals at risk of not being met
        - Unusual trends
        """
        alerts_created = []
        
        # Check recent metrics for alert thresholds
        recent_metrics = DailyHealthMetric.objects.filter(
            user=user,
            recorded_date__gte=timezone.now().date() - timedelta(days=1),
            is_alert_generated=False
        )
        
        for metric in recent_metrics:
            if metric.is_in_alert_range:
                alert = HealthAlert.objects.create(
                    user=user,
                    alert_type='unusual_metric',
                    severity='warning',
                    title=f'Alert: Unusual {metric.metric_type.metric_name}',
                    message=f'{metric.metric_type.metric_name} reading of {metric.value} {metric.metric_type.unit} is outside normal range',
                    metric=metric,
                    notify_nutritionist=True,
                    send_email=True
                )
                metric.is_alert_generated = True
                metric.save()
                alerts_created.append(alert)
        
        # Check goals at risk
        today = timezone.now().date()
        at_risk_goals = PatientHealthGoal.objects.filter(
            user=user,
            status='active',
            target_date__lt=today + timedelta(days=14)  # Goals due in 2 weeks
        )
        
        for goal in at_risk_goals:
            # Calculate if on track
            days_remaining = (goal.target_date - today).days
            if days_remaining > 0 and goal.current_value:
                progress_needed = abs(goal.target_value - goal.current_value)
                daily_progress_needed = progress_needed / days_remaining
                
                # Check if past progress supports achieving goal
                if goal.current_value and not HealthService._is_on_track(goal):
                    alert = HealthAlert.objects.create(
                        user=user,
                        alert_type='goal_at_risk',
                        severity='warning',
                        title=f'Goal at Risk: {goal.goal_name}',
                        message=f'Your goal "{goal.goal_name}" may not be achieved by {goal.target_date}. Consider adjusting your strategy.',
                        goal=goal,
                        notify_nutritionist=True
                    )
                    alerts_created.append(alert)
        
        return alerts_created
    
    @staticmethod
    def _is_on_track(goal):
        """Check if goal progress is on track for target date"""
        today = timezone.now().date()
        days_elapsed = (today - goal.start_date).days
        days_total = (goal.target_date - goal.start_date).days
        
        if days_total <= 0 or days_elapsed <= 0:
            return True
        
        progress_ratio = days_elapsed / days_total
        expected_progress_ratio = (goal.current_value - goal.metric_type.normal_range_min) / (goal.target_value - goal.metric_type.normal_range_min) if goal.metric_type else 0
        
        return expected_progress_ratio >= progress_ratio * 0.8  # Allow 20% margin
    
    @staticmethod
    def analyze_meal_effectiveness(meal):
        """
        Analyze and update effectiveness score for a meal
        Updates MealEffectivenessScore based on all reviews
        """
        reviews = MealReview.objects.filter(meal=meal)
        
        if not reviews.exists():
            return None
        
        total_reviews = reviews.count()
        unique_users = reviews.values('user').distinct().count()
        
        # Calculate averages
        avg_overall = reviews.aggregate(Avg('overall_rating'))['overall_rating__avg'] or 0
        avg_satisfaction = reviews.aggregate(Avg('satisfaction'))['satisfaction__avg'] or 0
        avg_digestibility = reviews.aggregate(Avg('digestibility'))['digestibility__avg'] or 0
        avg_energy = reviews.aggregate(Avg('energy_level'))['energy_level__avg'] or 0
        avg_mood = reviews.aggregate(Avg('mood_after'))['mood_after__avg'] or 0
        
        # Calculate weighted effectiveness score
        # Weight: Overall 40%, Digestibility 25%, Energy 20%, Mood 15%
        effectiveness = (
            (avg_overall / 5 * 40) +
            (avg_digestibility / 5 * 25) +
            (avg_energy / 5 * 20) +
            (avg_mood / 5 * 15)
        )
        
        # Get or create effectiveness score object
        score_obj, created = MealEffectivenessScore.objects.get_or_create(meal=meal)
        score_obj.total_reviews = total_reviews
        score_obj.unique_users = unique_users
        score_obj.avg_overall_rating = Decimal(str(avg_overall))
        score_obj.avg_satisfaction = Decimal(str(avg_satisfaction))
        score_obj.avg_digestibility = Decimal(str(avg_digestibility))
        score_obj.avg_energy = Decimal(str(avg_energy))
        score_obj.avg_mood = Decimal(str(avg_mood))
        score_obj.effectiveness_score = Decimal(str(effectiveness))
        score_obj.save()
        
        return score_obj
    
    @staticmethod
    def generate_health_report(user, report_type='weekly', custom_range=None):
        """
        Generate comprehensive health report for user
        Types: weekly, monthly, goal_progress, meal_analysis, custom
        """
        if report_type == 'weekly':
            start_date = timezone.now().date() - timedelta(days=7)
        elif report_type == 'monthly':
            start_date = timezone.now().date() - timedelta(days=30)
        else:
            start_date = custom_range[0] if custom_range else timezone.now().date() - timedelta(days=7)
        
        # Metrics summary
        metrics = DailyHealthMetric.objects.filter(
            user=user,
            recorded_date__gte=start_date
        )
        
        metrics_summary = {}
        for metric_type in HealthMetricType.objects.all():
            type_metrics = metrics.filter(metric_type=metric_type)
            if type_metrics.exists():
                metrics_summary[metric_type.metric_name] = {
                    'count': type_metrics.count(),
                    'avg': float(type_metrics.aggregate(Avg('value'))['value__avg'] or 0),
                    'min': float(type_metrics.aggregate(models.Min('value'))['value__min'] or 0),
                    'max': float(type_metrics.aggregate(models.Max('value'))['value__max'] or 0),
                }
        
        # Goals progress
        active_goals = PatientHealthGoal.objects.filter(user=user, status='active')
        goal_progress = {}
        for goal in active_goals:
            goal_progress[goal.goal_name] = {
                'progress': goal.progress_percentage,
                'days_remaining': goal.days_remaining,
                'target_date': goal.target_date.isoformat(),
            }
        
        # Meal analysis
        meal_reviews = MealReview.objects.filter(
            user=user,
            date_consumed__gte=start_date
        )
        
        meal_analysis = {}
        if meal_reviews.exists():
            best_meals = meal_reviews.values('meal__name').annotate(
                avg_rating=Avg('overall_rating')
            ).order_by('-avg_rating')[:5]
            
            meal_analysis = {
                'total_reviewed': meal_reviews.count(),
                'best_meals': list(best_meals),
                'avg_satisfaction': float(meal_reviews.aggregate(Avg('satisfaction'))['satisfaction__avg'] or 0),
            }
        
        # Generate report
        title = f"{report_type.title()} Health Report - {timezone.now().date()}"
        
        summary = f"""
        Health Summary for {user.get_full_name() or user.username}
        Period: {start_date} to {timezone.now().date()}
        
        Overall Health Score: {HealthService.calculate_health_score(user)}/100
        
        Metrics Tracked: {metrics.count()} readings
        Active Goals: {active_goals.count()}
        Meals Reviewed: {meal_reviews.count()}
        """
        
        report = HealthReport.objects.create(
            user=user,
            report_type=report_type,
            report_title=title,
            metrics_summary=metrics_summary,
            goal_progress=goal_progress,
            meal_analysis=meal_analysis,
            summary=summary.strip(),
            generated_by=None  # Can be set to staff user if needed
        )
        
        return report
    
    @staticmethod
    def get_metric_trends(user, metric_type, days=30):
        """Get trend data for a specific metric"""
        start_date = timezone.now().date() - timedelta(days=days)
        
        metrics = DailyHealthMetric.objects.filter(
            user=user,
            metric_type=metric_type,
            recorded_date__gte=start_date
        ).order_by('recorded_date')
        
        trend_data = {
            'dates': [m.recorded_date.isoformat() for m in metrics],
            'values': [float(m.value) for m in metrics],
            'metric_name': metric_type.metric_name,
            'unit': metric_type.unit,
            'avg': float(metrics.aggregate(Avg('value'))['value__avg'] or 0),
            'min': float(metrics.aggregate(models.Min('value'))['value__min'] or 0),
            'max': float(metrics.aggregate(models.Max('value'))['value__max'] or 0),
        }
        
        return trend_data
    
    @staticmethod
    def get_goal_recommendations(user):
        """Get personalized goal recommendations based on health data"""
        recommendations = []
        
        # Analyze recent metrics for potential areas
        recent_metrics = DailyHealthMetric.objects.filter(
            user=user,
            recorded_date__gte=timezone.now().date() - timedelta(days=30)
        )
        
        # Check for consistent high/low values
        for metric_type in HealthMetricType.objects.filter(active=True):
            type_metrics = recent_metrics.filter(metric_type=metric_type)
            if type_metrics.count() >= 5:
                avg_value = float(type_metrics.aggregate(Avg('value'))['value__avg'] or 0)
                
                # Generate recommendations based on anomalies
                if metric_type.alert_threshold_max and avg_value > metric_type.alert_threshold_max:
                    recommendations.append({
                        'metric': metric_type.metric_name,
                        'issue': f'Consistently elevated {metric_type.metric_name}',
                        'suggestion': f'Consider a goal to reduce {metric_type.metric_name}',
                        'priority': 'high'
                    })
                elif metric_type.alert_threshold_min and avg_value < metric_type.alert_threshold_min:
                    recommendations.append({
                        'metric': metric_type.metric_name,
                        'issue': f'Consistently low {metric_type.metric_name}',
                        'suggestion': f'Consider a goal to increase {metric_type.metric_name}',
                        'priority': 'high'
                    })
        
        # Analyze meal effectiveness
        meal_reviews = MealReview.objects.filter(
            user=user,
            date_consumed__gte=timezone.now().date() - timedelta(days=30)
        )
        
        if meal_reviews.exists():
            low_effectiveness_meals = MealReview.objects.filter(
                user=user,
                overall_rating__lt=3
            ).values('meal__name').annotate(count=Count('id')).filter(count__gte=2)
            
            if low_effectiveness_meals.exists():
                recommendations.append({
                    'type': 'meal',
                    'issue': 'Low-effectiveness meals identified',
                    'suggestion': 'Consider avoiding or modifying low-rated meals',
                    'priority': 'medium'
                })
        
        return sorted(recommendations, key=lambda x: {'high': 0, 'medium': 1, 'low': 2}.get(x.get('priority', 'low')))
    
    @staticmethod
    def calculate_health_improvement(user, start_date, end_date):
        """Calculate health improvement metrics over a period"""
        metrics_start = DailyHealthMetric.objects.filter(
            user=user,
            recorded_date__lte=start_date
        ).order_by('-recorded_date')[:1]
        
        metrics_end = DailyHealthMetric.objects.filter(
            user=user,
            recorded_date__lte=end_date
        ).order_by('-recorded_date')[:1]
        
        goals_completed = PatientHealthGoal.objects.filter(
            user=user,
            status='completed',
            completed_date__gte=start_date,
            completed_date__lte=end_date
        ).count()
        
        improvement_score = {
            'goals_completed': goals_completed,
            'period': f'{start_date} to {end_date}',
            'health_score_improvement': 0  # Can be calculated if historical scores exist
        }
        
        return improvement_score
