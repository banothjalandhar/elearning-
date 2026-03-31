from django.urls import path

from . import views


app_name = "payments"

urlpatterns = [
    path("pay/<int:course_id>/", views.course_payment, name="course_payment"),
    path("checkout/<int:course_id>/", views.create_checkout_session, name="create_checkout_session"),
    path("success/", views.payment_success, name="payment_success"),
    path("cancel/", views.payment_cancel, name="payment_cancel"),
    path("webhook/", views.payment_webhook, name="payment_webhook"),
    path("webhook/stripe/", views.stripe_webhook, name="stripe_webhook"),
]
