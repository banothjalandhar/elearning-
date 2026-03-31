from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser, LoginOTP, SubscriptionPlan, UserSession, UserSubscription


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ("email", "username", "batch", "phone", "is_staff", "is_active")
    list_filter = ("is_staff", "is_active", "is_superuser", "batch")
    fieldsets = (
        (None, {"fields": ("email", "username", "password")}),
        (
            "Personal info",
            {
                "fields": (
                    "batch",
                    "phone",
                    "date_of_birth",
                    "qualification",
                    "branch",
                    "passout_year",
                    "college_name",
                    "referral_code",
                )
            },
        ),
        ("Permissions", {"fields": ("is_staff", "is_active", "is_superuser", "groups", "user_permissions")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "username",
                    "batch",
                    "phone",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_active",
                ),
            },
        ),
    )
    search_fields = ("email", "username")
    ordering = ("email",)
    actions = ["unlock_selected_users"]

    @admin.action(description="Unlock selected users by deactivating sessions")
    def unlock_selected_users(self, request, queryset):
        UserSession.objects.filter(user__in=queryset, is_active=True).update(is_active=False)


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ("user", "session_key", "ip_address", "device", "is_active", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("user__email", "user__username", "session_key", "ip_address", "device")
    actions = ["deactivate_sessions"]

    @admin.action(description="Deactivate selected sessions")
    def deactivate_sessions(self, request, queryset):
        queryset.update(is_active=False)


@admin.register(LoginOTP)
class LoginOTPAdmin(admin.ModelAdmin):
    list_display = ("user", "otp", "created_at", "is_used")
    list_filter = ("is_used", "created_at")
    search_fields = ("user__email", "user__username", "otp")


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "duration_days", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user", "plan", "start_date", "end_date", "is_active")
    list_filter = ("plan", "is_active")
    search_fields = ("user__email", "user__username", "plan__name")
