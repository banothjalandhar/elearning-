from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import include, path, reverse_lazy
from django.views.generic.base import RedirectView
from rest_framework import routers

from accounts import views as account_views
from courses import views as course_views
from payments import views as payment_views


router = routers.DefaultRouter()
router.register(r"courses", course_views.CourseAPI)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("accounts/login/", RedirectView.as_view(url="/login/", permanent=False)),
    path("signup/", account_views.signup_view, name="signup"),
    path("login/", account_views.login_with_otp, name="login"),
    path("login/verify-otp/", account_views.login_otp_verify, name="login_otp_verify"),
    path("logout/", LogoutView.as_view(next_page=reverse_lazy("course_list")), name="logout"),
    path("forgot-password/", account_views.password_reset_request, name="password_reset"),
    path("verify-otp/", account_views.verify_otp, name="verify_otp"),
    path("reset-password/", account_views.reset_password, name="reset_password"),
    path("dashboard/", account_views.dashboard, name="dashboard"),
    path("chat/", include("chatbot.urls")),
    path("chatbot/", include("chatbot.urls")),
    path("classroom/", include("classroom.urls")),
    path("contact/", include("contact.urls"), name="contact"),
    path("exams/", include("exams.urls")),
    path("learn/", include("lms.urls")),
    path("payments/", include("payments.urls")),
    path("payment/webhook/", payment_views.payment_webhook, name="payment_webhook"),
    path("placements/", include("placement.urls")),
    path("pay/<int:course_id>/", payment_views.course_payment, name="course_payment"),
    path("upcoming-courses/", course_views.upcoming_course_list, name="upcoming_course_list"),
    path("upcoming-course/<int:course_id>/", course_views.upcoming_course_detail, name="upcoming_course_detail"),
    path("course/<int:course_id>/", course_views.course_detail, name="course_detail"),
    path("api/", include(router.urls)),
    path("blogs/", include("blogs.urls")),
    path("search/", course_views.search, name="search"),
    path("", course_views.course_list, name="course_list"),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


handler404 = "elearning.views.custom_page_not_found"
handler500 = "elearning.views.custom_server_error"
