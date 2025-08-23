# accounts/apps.py
from django.apps import AppConfig

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    verbose_name = 'Accounts & Profiles'

    def ready(self):
        from . import signals  # noqa: F401  # ensure signal handlers are registered
