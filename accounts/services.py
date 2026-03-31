import logging
import random
from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from .models import LoginOTP, SubscriptionPlan, UserSubscription


logger = logging.getLogger(__name__)


def issue_login_otp(user):
    LoginOTP.objects.filter(user=user, is_used=False).update(is_used=True)
    otp_value = f"{random.randint(100000, 999999)}"
    otp = LoginOTP.objects.create(user=user, otp=otp_value)
    subject = "Your login OTP"
    message = f"Your OTP is: {otp_value}. It expires in 5 minutes."

    print(f"OTP: {otp_value}")
    print(f"Email: {user.email}")
    logger.info("Issuing login OTP for %s", user.email)

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )
    return otp


def send_test_email(recipient_email):
    send_mail(
        "CodeWithJalandhar email test",
        "This is a test email from the OTP system.",
        settings.DEFAULT_FROM_EMAIL,
        [recipient_email],
        fail_silently=False,
    )


def get_active_subscription(user):
    UserSubscription.objects.filter(user=user, is_active=True, end_date__lt=timezone.now()).update(is_active=False)
    return (
        UserSubscription.objects.select_related("plan")
        .filter(user=user, is_active=True, end_date__gte=timezone.now())
        .order_by("-end_date")
        .first()
    )


def has_active_subscription(user):
    if not getattr(user, "is_authenticated", False):
        return False
    if not SubscriptionPlan.objects.filter(is_active=True).exists():
        return True
    return get_active_subscription(user) is not None


def assign_default_subscription(user):
    plan = SubscriptionPlan.objects.filter(is_active=True).order_by("price", "duration_days").first()
    if plan is None:
        return None

    current_subscription = get_active_subscription(user)
    start_date = timezone.now()
    if current_subscription is not None and current_subscription.end_date > start_date:
        start_date = current_subscription.end_date
        current_subscription.is_active = False
        current_subscription.save(update_fields=["is_active"])

    return UserSubscription.objects.create(
        user=user,
        plan=plan,
        start_date=start_date,
        end_date=start_date + timedelta(days=plan.duration_days),
        is_active=True,
    )
