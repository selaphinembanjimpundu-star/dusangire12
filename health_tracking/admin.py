from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Avg
from .models import (
    HealthMetricType, DailyHealthMetric, PatientHealthGoal, GoalMilestone,
    MealReview, MealEffectivenessScore, HealthReport, HealthAlert
)


@admin.register(HealthMetricType)
class HealthMetricTypeAdmin(admin.ModelAdmin):
    list_display = ['metric_name', 'unit', 'category', 'active', 'created_at']
    list_filter = ['category', 'active', 'created_at']
    search_fields = ['metric_name', 'description']
    fields = ['metric_name', 'unit', 'category', 'description', 'normal_range_min', 'normal_range_max', 'alert_threshold_min', 'alert_threshold_max', 'active']
    ordering = ['category', 'metric_name']


@admin.register(DailyHealthMetric)
class DailyHealthMetricAdmin(admin.ModelAdmin):
    list_display = ['user', 'metric_type', 'value_display', 'recorded_date', 'alert_status', 'created_at']
    list_filter = ['metric_type', 'recorded_date', 'is_alert_generated']
    search_fields = ['user__username', 'user__email', 'metric_type__metric_name']
    readonly_fields = ['created_at', 'updated_at', 'is_in_alert_range']
    fields = ['user', 'metric_type', 'value', 'recorded_date', 'recorded_time', 'notes', 'conditions', 'image', 'is_alert_generated', 'is_in_alert_range', 'created_at', 'updated_at']
    date_hierarchy = 'recorded_date'
    
    def value_display(self, obj):
        """Display value with unit"""
        return f"{obj.value} {obj.metric_type.unit}"
    value_display.short_description = 'Value'
    
    def alert_status(self, obj):
        """Display alert status with color"""
        if obj.is_in_alert_range:
            return format_html('<span style="color: red;">⚠ Alert Range</span>')
        return format_html('<span style="color: green;">✓ Normal</span>')
    alert_status.short_description = 'Status'


class GoalMilestoneInline(admin.TabularInline):
    model = GoalMilestone
    extra = 1
    fields = ['milestone_name', 'target_value', 'target_date', 'achieved_date']


@admin.register(PatientHealthGoal)
class PatientHealthGoalAdmin(admin.ModelAdmin):
    list_display = ['user', 'goal_name', 'goal_type', 'progress_display', 'status', 'target_date']
    list_filter = ['status', 'goal_type', 'start_date', 'target_date', 'is_public']
    search_fields = ['user__username', 'user__email', 'goal_name']
    readonly_fields = ['created_at', 'updated_at', 'progress_percentage', 'days_remaining']
    fields = ['user', 'goal_name', 'description', 'goal_type', 'metric_type', 'target_value', 'current_value', 'start_date', 'target_date', 'status', 'completed_date', 'priority', 'is_public', 'progress_percentage', 'days_remaining', 'created_at', 'updated_at']
    inlines = [GoalMilestoneInline]
    date_hierarchy = 'target_date'
    
    def progress_display(self, obj):
        """Display progress bar"""
        progress = obj.progress_percentage
        color = 'green' if progress >= 80 else 'orange' if progress >= 50 else 'red'
        return format_html(
            '<div style="width: 100px; background-color: #ddd; border-radius: 5px;">'
            '<div style="width: {}%; background-color: {}; height: 20px; border-radius: 5px;"></div>'
            '</div> {}%',
            progress, color, int(progress)
        )
    progress_display.short_description = 'Progress'


@admin.register(GoalMilestone)
class GoalMilestoneAdmin(admin.ModelAdmin):
    list_display = ['health_goal', 'milestone_name', 'target_date', 'is_achieved_display']
    list_filter = ['achieved_date', 'target_date']
    search_fields = ['health_goal__goal_name', 'milestone_name']
    readonly_fields = ['created_at']
    
    def is_achieved_display(self, obj):
        """Display achievement status"""
        if obj.is_achieved:
            return format_html('<span style="color: green;">✓ Achieved</span>')
        return format_html('<span style="color: orange;">⏳ Pending</span>')
    is_achieved_display.short_description = 'Status'


@admin.register(MealReview)
class MealReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'meal', 'overall_rating_display', 'date_consumed', 'average_score']
    list_filter = ['date_consumed', 'overall_rating', 'satisfaction']
    search_fields = ['user__username', 'meal__name', 'notes']
    readonly_fields = ['created_at', 'updated_at', 'average_score']
    fields = ['user', 'meal', 'overall_rating', 'satisfaction', 'digestibility', 'energy_level', 'mood_after', 'notes', 'allergies_or_issues', 'date_consumed', 'time_consumed', 'health_condition_at_time', 'average_score', 'created_at', 'updated_at']
    date_hierarchy = 'date_consumed'
    
    def overall_rating_display(self, obj):
        """Display rating with stars"""
        stars = '⭐' * obj.overall_rating
        return format_html(f'<span>{stars}</span>')
    overall_rating_display.short_description = 'Rating'


@admin.register(MealEffectivenessScore)
class MealEffectivenessScoreAdmin(admin.ModelAdmin):
    list_display = ['meal', 'effectiveness_display', 'total_reviews', 'unique_users', 'last_updated']
    list_filter = ['last_updated', 'effectiveness_score']
    search_fields = ['meal__name']
    readonly_fields = ['last_updated']
    fields = ['meal', 'total_reviews', 'unique_users', 'avg_overall_rating', 'avg_satisfaction', 'avg_digestibility', 'avg_energy', 'avg_mood', 'effectiveness_score', 'last_updated']
    
    def effectiveness_display(self, obj):
        """Display effectiveness score with color"""
        score = float(obj.effectiveness_score)
        if score >= 80:
            color = 'green'
        elif score >= 60:
            color = 'orange'
        else:
            color = 'red'
        return format_html(f'<span style="color: {color}; font-weight: bold;">{score}%</span>')
    effectiveness_display.short_description = 'Effectiveness'


@admin.register(HealthReport)
class HealthReportAdmin(admin.ModelAdmin):
    list_display = ['user', 'report_type', 'report_date', 'is_shared']
    list_filter = ['report_type', 'report_date', 'is_shared_with_nutritionist']
    search_fields = ['user__username', 'report_title', 'summary']
    readonly_fields = ['created_at', 'updated_at']
    fields = ['user', 'report_type', 'report_title', 'report_date', 'summary', 'recommendations', 'key_findings', 'is_shared_with_nutritionist', 'generated_by', 'created_at', 'updated_at']
    date_hierarchy = 'report_date'
    
    def is_shared(self, obj):
        """Display sharing status"""
        if obj.is_shared_with_nutritionist:
            return format_html('<span style="color: green;">✓ Shared</span>')
        return format_html('<span style="color: gray;">✗ Private</span>')
    is_shared.short_description = 'Shared'


@admin.register(HealthAlert)
class HealthAlertAdmin(admin.ModelAdmin):
    list_display = ['user', 'alert_type', 'severity_display', 'is_acknowledged', 'created_at']
    list_filter = ['severity', 'alert_type', 'is_acknowledged', 'created_at']
    search_fields = ['user__username', 'title', 'message']
    readonly_fields = ['created_at', 'updated_at']
    fields = ['user', 'alert_type', 'severity', 'title', 'message', 'metric', 'goal', 'is_acknowledged', 'acknowledged_date', 'acknowledged_by', 'send_email', 'send_sms', 'notify_nutritionist', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    def severity_display(self, obj):
        """Display severity with color"""
        colors = {'critical': 'red', 'warning': 'orange', 'info': 'blue'}
        color = colors.get(obj.severity, 'gray')
        return format_html(f'<span style="color: {color}; font-weight: bold;">{obj.get_severity_display()}</span>')
    severity_display.short_description = 'Severity'
    
    actions = ['acknowledge_selected', 'mark_unacknowledged']
    
    def acknowledge_selected(self, request, queryset):
        """Bulk acknowledge alerts"""
        updated = queryset.update(is_acknowledged=True, acknowledged_by=request.user, acknowledged_date=timezone.now())
        self.message_user(request, f'{updated} alert(s) acknowledged.')
    acknowledge_selected.short_description = 'Mark selected as acknowledged'
    
    def mark_unacknowledged(self, request, queryset):
        """Bulk mark as unacknowledged"""
        updated = queryset.update(is_acknowledged=False)
        self.message_user(request, f'{updated} alert(s) marked as unacknowledged.')
    mark_unacknowledged.short_description = 'Mark selected as unacknowledged'


# Import timezone for bulk actions
from django.utils import timezone
