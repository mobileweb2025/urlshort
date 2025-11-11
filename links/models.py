import secrets
import string

from django.db import models
from django.urls import reverse


class ShortLink(models.Model):
    original_url = models.URLField(max_length=2048)
    short_code = models.SlugField(max_length=20, unique=True)
    click_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"{self.short_code} → {self.original_url}"

    def get_absolute_url(self) -> str:
        return reverse("links:redirect", args=[self.short_code])

    @staticmethod
    def generate_unique_code(length: int = 6) -> str:
        """Generate a unique short code that does not exist in the database."""
        alphabet = string.ascii_letters + string.digits
        while True:
            candidate = "".join(secrets.choice(alphabet) for _ in range(length))
            if not ShortLink.objects.filter(short_code__iexact=candidate).exists():
                return candidate


class PushSubscription(models.Model):
    endpoint = models.URLField(unique=True)
    p256dh = models.CharField(max_length=255)
    auth = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.endpoint
