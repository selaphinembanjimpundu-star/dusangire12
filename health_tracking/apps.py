from django.apps import AppConfig


class HealthTrackingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'health_tracking'
    verbose_name = 'Health Tracking System'
    
    def ready(self):
        """Register signal handlers when app is ready"""
        import health_tracking.signals
