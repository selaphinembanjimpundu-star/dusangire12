from django.apps import AppConfig


class NutritionistDashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'nutritionist_dashboard'
    verbose_name = 'Nutritionist Dashboard'

    def ready(self):
        """Register signal handlers when the app is ready"""
        import nutritionist_dashboard.signals  # noqa
