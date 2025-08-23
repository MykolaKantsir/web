from django.conf import settings
from django.db import models

class UserProfile(models.Model):
    class Country(models.TextChoices):
        SWEDEN = "SE", "Sweden"
        UKRAINE = "UA", "Ukraine"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="userprofile",
    )
    country = models.CharField(
        max_length=2,
        choices=Country.choices,
        default=Country.SWEDEN,  # default Sweden
    )

    def __str__(self):
        return f"{self.user} ({self.get_country_display()})"
