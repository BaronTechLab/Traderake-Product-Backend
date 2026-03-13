from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import random
import string

class CustomUser(AbstractUser):
    country_code = models.CharField(max_length=5, blank=False, null=False)
    phone_number = models.CharField(max_length=20, unique=True, null=False, blank=False)
    email = models.EmailField(unique=True, null=False, blank=False)
    whatsapp_opt_in = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.username

class OTP(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='otps')
    code = models.CharField(max_length=6)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = ''.join(random.choices(string.digits, k=6))
        if not self.expires_at:
            # OTP expires in 10 minutes
            self.expires_at = timezone.now() + timezone.timedelta(minutes=10)
        super().save(*args, **kwargs)

    def is_valid(self):
        return timezone.now() <= self.expires_at

    def __str__(self):
        return f"{self.user.username} - {self.code}"
