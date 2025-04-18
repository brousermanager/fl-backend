from django.apps import AppConfig


class PodcastConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "podcast"

    def ready(self):
        import podcast.signals  # noqa
