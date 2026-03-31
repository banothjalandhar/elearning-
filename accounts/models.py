from datetime import timedelta

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    batch = models.ForeignKey("lms.Batch", on_delete=models.SET_NULL, null=True, blank=True, related_name="users")
    phone = models.CharField(max_length=15, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    qualification = models.CharField(max_length=100, blank=True, null=True)
    branch = models.CharField(max_length=100, blank=True, null=True)
    passout_year = models.CharField(max_length=4, blank=True, null=True)
    college_name = models.CharField(max_length=200, blank=True, null=True)
    referral_code = models.CharField(max_length=20, blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email


class UserSession(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="user_sessions")
    session_key = models.CharField(max_length=255, unique=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    device = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.user} - {self.device or 'unknown device'}"


class LoginOTP(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="login_otps")
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    @property
    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=5)

    def __str__(self):
        return f"OTP for {self.user}"


class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=150)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    duration_days = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["price", "name"]

    def __str__(self):
        return self.name


class UserSubscription(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="subscriptions")
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE, related_name="user_subscriptions")
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-end_date"]

    @property
    def is_current(self):
        return self.is_active and self.end_date >= timezone.now()

    def __str__(self):
        return f"{self.user} - {self.plan}"
