from django.apps import AppConfig


class HealthProfilesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'health_profiles'

    def ready(self):
        """Initialize signals when the app is ready."""
        import health_profiles.signals  # noqa
