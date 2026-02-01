from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.http import JsonResponse
from django.db.models import Avg, Count, Q
from django.utils import timezone
from datetime import timedelta

from .models import (
    DailyHealthMetric, PatientHealthGoal, MealReview, HealthAlert,
    HealthReport, HealthMetricType, GoalMilestone
)
from .services import HealthService


@login_required
def health_dashboard_patient(request):
    """Patient health dashboard showing personal health metrics and goals"""
    user = request.user
    
    # Health score
    health_score = HealthService.calculate_health_score(user)
    
    # Active goals
    active_goals = PatientHealthGoal.objects.filter(user=user, status='active')
    
    # Recent metrics
    recent_metrics = DailyHealthMetric.objects.filter(user=user).order_by('-recorded_date')[:10]
    
    # Recent meal reviews
    recent_meals = MealReview.objects.filter(user=user).order_by('-date_consumed')[:5]
    
    # Alerts
    alerts = HealthAlert.objects.filter(user=user, is_acknowledged=False).order_by('-created_at')[:5]
    
    # Health recommendations
    recommendations = HealthService.get_goal_recommendations(user)
    
    context = {
        'health_score': health_score,
        'active_goals': active_goals,
        'recent_metrics': recent_metrics,
        'recent_meals': recent_meals,
        'alerts': alerts,
        'recommendations': recommendations,
        'page_title': 'My Health Dashboard',
    }
    
    return render(request, 'health_tracking/health_dashboard_patient.html', context)


@login_required
def health_dashboard_nutritionist(request):
    """Nutritionist dashboard showing patient health overview"""
    # Check if user is nutritionist or admin
    if not (request.user.is_staff or request.user.groups.filter(name='Nutritionists').exists()):
        return redirect('health_dashboard_patient')
    
    # Get patients with shared goals
    patients = PatientHealthGoal.objects.filter(
        is_public=True
    ).values_list('user', flat=True).distinct()
    
    # Recent alerts from patients
    alerts = HealthAlert.objects.filter(
        is_acknowledged=False,
        severity__in=['warning', 'critical']
    ).order_by('-created_at')[:10]
    
    # Goals at risk
    today = timezone.now().date()
    at_risk_goals = PatientHealthGoal.objects.filter(
        status='active',
        is_public=True,
        target_date__lt=today + timedelta(days=14)
    ).select_related('user')
    
    context = {
        'total_patients': len(patients),
        'alerts': alerts,
        'at_risk_goals': at_risk_goals,
        'page_title': 'Nutritionist Dashboard',
    }
    
    return render(request, 'health_tracking/health_dashboard_nutritionist.html', context)


@login_required
def health_metrics_add(request):
    """Add new health metric"""
    if request.method == 'POST':
        metric_type_id = request.POST.get('metric_type')
        value = request.POST.get('value')
        notes = request.POST.get('notes', '')
        conditions = request.POST.get('conditions', '')
        
        metric_type = get_object_or_404(HealthMetricType, id=metric_type_id)
        
        # Create metric
        metric = DailyHealthMetric.objects.create(
            user=request.user,
            metric_type=metric_type,
            value=value,
            notes=notes,
            conditions=conditions,
            recorded_date=timezone.now().date(),
            recorded_time=timezone.now().time()
        )
        
        # Check for alerts
        if metric.is_in_alert_range:
            HealthService.detect_health_alerts(request.user)
        
        # Update goal progress if applicable
        goals = PatientHealthGoal.objects.filter(
            user=request.user,
            metric_type=metric_type,
            status='active'
        )
        for goal in goals:
            HealthService.update_goal_progress(goal)
        
        return redirect('health_dashboard_patient')
    
    metric_types = HealthMetricType.objects.filter(active=True)
    context = {
        'metric_types': metric_types,
        'page_title': 'Add Health Metric',
    }
    
    return render(request, 'health_tracking/health_metrics_form.html', context)


@login_required
def health_goals_manage(request):
    """Manage health goals"""
    if request.method == 'POST':
        action = request.POST.get('action')
        goal_id = request.POST.get('goal_id')
        goal = get_object_or_404(PatientHealthGoal, id=goal_id, user=request.user)
        
        if action == 'pause':
            goal.status = 'on_hold'
            goal.save()
        elif action == 'abandon':
            goal.status = 'abandoned'
            goal.save()
        elif action == 'resume':
            goal.status = 'active'
            goal.save()
        
        return redirect('health_dashboard_patient')
    
    user_goals = PatientHealthGoal.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'goals': user_goals,
        'page_title': 'My Health Goals',
    }
    
    return render(request, 'health_tracking/health_goals_modal.html', context)


@login_required
def meal_review_create(request):
    """Create meal review"""
    if request.method == 'POST':
        meal_id = request.POST.get('meal_id')
        overall_rating = request.POST.get('overall_rating')
        satisfaction = request.POST.get('satisfaction')
        digestibility = request.POST.get('digestibility')
        energy_level = request.POST.get('energy_level')
        mood_after = request.POST.get('mood_after')
        notes = request.POST.get('notes', '')
        allergies = request.POST.get('allergies_or_issues', '')
        conditions = request.POST.get('health_condition_at_time', '')
        
        from menu.models import MenuItem
        meal = get_object_or_404(MenuItem, id=meal_id)
        
        review = MealReview.objects.create(
            user=request.user,
            meal=meal,
            overall_rating=int(overall_rating),
            satisfaction=int(satisfaction),
            digestibility=int(digestibility),
            energy_level=int(energy_level),
            mood_after=int(mood_after),
            notes=notes,
            allergies_or_issues=allergies,
            health_condition_at_time=conditions,
            date_consumed=timezone.now().date(),
            time_consumed=timezone.now().time()
        )
        
        # Update meal effectiveness
        HealthService.analyze_meal_effectiveness(meal)
        
        return JsonResponse({'status': 'success', 'message': 'Review saved successfully'})
    
    from menu.models import MenuItem
    recent_meals = MenuItem.objects.all()[:20]
    
    context = {
        'meals': recent_meals,
        'page_title': 'Review Meal',
    }
    
    return render(request, 'health_tracking/meal_review_modal.html', context)


@login_required
def health_reports_view(request):
    """View health reports"""
    reports = HealthReport.objects.filter(user=request.user).order_by('-report_date')
    
    # Generate new report if requested
    if request.GET.get('generate'):
        report_type = request.GET.get('type', 'weekly')
        report = HealthService.generate_health_report(request.user, report_type)
        return redirect('health_reports_view')
    
    context = {
        'reports': reports,
        'page_title': 'My Health Reports',
    }
    
    return render(request, 'health_tracking/health_reports_view.html', context)


@login_required
def metric_trend_chart(request, metric_id):
    """Get metric trend data for chart"""
    metric_type = get_object_or_404(HealthMetricType, id=metric_id)
    days = request.GET.get('days', 30)
    
    trend_data = HealthService.get_metric_trends(request.user, metric_type, int(days))
    
    return JsonResponse(trend_data)


@login_required
def acknowledge_alert(request, alert_id):
    """Acknowledge a health alert"""
    alert = get_object_or_404(HealthAlert, id=alert_id, user=request.user)
    alert.is_acknowledged = True
    alert.acknowledged_date = timezone.now()
    alert.acknowledged_by = request.user
    alert.save()
    
    return JsonResponse({'status': 'success'})
