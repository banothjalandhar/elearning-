from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.sessions.models import Session
from django.utils import timezone

from .models import CustomUser, UserSession

QUALIFICATION_CHOICES = [
    ("btech", "B.Tech"),
    ("mtech", "M.Tech"),
    ("bca", "BCA"),
    ("mca", "MCA"),
    ("bsc", "B.Sc"),
    ("msc", "M.Sc"),
    ("others", "Others"),
]

BRANCH_CHOICES = [
    ("cse", "Computer Science"),
    ("ece", "Electronics"),
    ("eee", "Electrical"),
    ("me", "Mechanical"),
    ("others", "Others"),
]


class CustomUserCreationForm(UserCreationForm):
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        required=True,
        label="Date of Birth",
    )
    qualification = forms.ChoiceField(
        choices=QUALIFICATION_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"}),
        required=True,
    )
    branch = forms.ChoiceField(
        choices=BRANCH_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"}),
        required=True,
    )
    passout_year = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Passout Year", "class": "form-control"}),
        required=True,
        label="Passout Year",
    )
    college_name = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "College Name", "class": "form-control"}),
        required=True,
        label="College Name",
    )
    phone = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "+91", "class": "form-control"}),
        required=True,
        label="Phone Number",
    )
    referral_code = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Referral code (optional)", "class": "form-control"}),
        required=False,
        label="Referral code",
    )

    class Meta:
        model = CustomUser
        fields = (
            "username",
            "email",
            "password1",
            "password2",
            "phone",
            "date_of_birth",
            "qualification",
            "branch",
            "passout_year",
            "college_name",
            "referral_code",
        )


class CustomLoginForm(AuthenticationForm):
    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request=request, *args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-control"

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        active_sessions = UserSession.objects.filter(user=user, is_active=True)
        valid_session_keys = set(
            Session.objects.filter(
                session_key__in=active_sessions.values_list("session_key", flat=True),
                expire_date__gte=timezone.now(),
            ).values_list("session_key", flat=True)
        )
        active_sessions.exclude(session_key__in=valid_session_keys).update(is_active=False)
        if active_sessions.filter(session_key__in=valid_session_keys).exists():
            raise forms.ValidationError(
                "You are already logged in another device. Contact admin.",
                code="already_logged_in_elsewhere",
            )


class LoginOTPForm(forms.Form):
    otp = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "6-digit OTP"}),
    )
