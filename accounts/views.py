import random

from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.utils import timezone

from classroom.views import dashboard_class
from courses.access import get_active_enrollments
from lms.views import dashboard_context as lms_dashboard_context
from placement.views import placement_summary

from .forms import CustomLoginForm, CustomUserCreationForm, LoginOTPForm
from .models import LoginOTP
from .services import get_active_subscription, issue_login_otp


User = get_user_model()


def signup_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            messages.success(request, "Account created successfully.")
            return redirect("course_list")
    else:
        form = CustomUserCreationForm()
    return render(request, "accounts/registration/signup.html", {"form": form})


def login_with_otp(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method != "POST":
        request.session.pop("pending_login_user_id", None)

    form = CustomLoginForm(request=request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        try:
            issue_login_otp(user)
        except Exception:
            messages.error(
                request,
                "OTP email could not be sent. Check EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, and Gmail App Password.",
            )
            return render(request, "accounts/registration/login.html", {"form": form})
        request.session["pending_login_user_id"] = user.id
        messages.info(request, "OTP sent to your email. Please verify to continue.")
        return redirect("login_otp_verify")
    return render(request, "accounts/registration/login.html", {"form": form})


def login_otp_verify(request):
    pending_user_id = request.session.get("pending_login_user_id")
    if not pending_user_id:
        messages.error(request, "Please log in first.")
        return redirect("login")

    form = LoginOTPForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        otp_value = form.cleaned_data["otp"]
        otp = LoginOTP.objects.filter(user_id=pending_user_id, otp=otp_value, is_used=False).order_by("-created_at").first()
        if otp and not otp.is_expired:
            otp.is_used = True
            otp.save(update_fields=["is_used"])
            user = User.objects.filter(pk=pending_user_id).first()
            if user is None:
                request.session.pop("pending_login_user_id", None)
                messages.error(request, "Your login session expired. Please log in again.")
                return redirect("login")
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            request.session.pop("pending_login_user_id", None)
            messages.success(request, "Login successful.")
            return redirect("dashboard")
        messages.error(request, "Invalid or expired OTP.")

    return render(request, "accounts/login_otp_verify.html", {"form": form})


@login_required
def dashboard(request):
    enrollments = get_active_enrollments(request.user).select_related("course").order_by("course__title")
    active_subscription = get_active_subscription(request.user)
    context = {
        "enrollments": enrollments,
        "student_exam_count": request.user.student_exams.count(),
        "result_count": request.user.results.count(),
        "active_subscription": active_subscription,
        **lms_dashboard_context(request.user),
        **dashboard_class(request.user),
        **placement_summary(request.user),
    }
    return render(request, "accounts/dashboard.html", context)


def password_reset_request(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        user = User.objects.filter(email=email).first()
        messages.success(request, "If that email exists, an OTP has been sent.")
        if user:
            otp = random.randint(100000, 999999)
            request.session["reset_otp"] = str(otp)
            request.session["reset_email"] = email
            request.session["reset_otp_created_at"] = timezone.now().isoformat()
            send_mail(
                "Password Reset OTP",
                f"Your OTP is: {otp}",
                None,
                [email],
                fail_silently=True,
            )
        return redirect("verify_otp")
    return render(request, "accounts/password_reset_request.html")


def verify_otp(request):
    if request.method == "POST":
        input_otp = request.POST.get("otp", "").strip()
        if input_otp and input_otp == request.session.get("reset_otp"):
            request.session["otp_verified"] = True
            return redirect("reset_password")
        return render(request, "accounts/verify_otp.html", {"error": "Incorrect OTP"})
    return render(request, "accounts/verify_otp.html")


def reset_password(request):
    if not request.session.get("otp_verified"):
        messages.error(request, "Verify OTP before resetting password.")
        return redirect("password_reset")

    if request.method == "POST":
        new_password = request.POST.get("password", "")
        email = request.session.get("reset_email")
        user = User.objects.filter(email=email).first()
        if user and new_password:
            user.set_password(new_password)
            user.save()
            for key in ["reset_otp", "reset_email", "reset_otp_created_at", "otp_verified"]:
                request.session.pop(key, None)
            messages.success(request, "Password reset successful. Please log in.")
            return redirect("login")
        messages.error(request, "Unable to reset password.")
    return render(request, "accounts/reset_password.html")
