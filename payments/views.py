import logging

import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from accounts.services import assign_default_subscription
from courses.models import Course, Enrollment

from .models import Payment


stripe.api_key = settings.STRIPE_SECRET_KEY or None
logger = logging.getLogger(__name__)


def _ensure_subscription(user):
    return assign_default_subscription(user)


def _get_checkout_metadata(session):
    return session.get("metadata") or {}


def _get_course_from_session(session, fallback_course_id=None):
    metadata = _get_checkout_metadata(session)
    course_id = metadata.get("course_id") or fallback_course_id
    if not course_id:
        return None
    return Course.objects.filter(id=course_id).first()


def _get_user_id_from_session(session, fallback_user_id=None):
    metadata = _get_checkout_metadata(session)
    return metadata.get("user_id") or fallback_user_id


def _finalize_paid_course_access(user, course):
    enrollment, _ = Enrollment.objects.get_or_create(
        user=user,
        course=course,
        defaults={
            "payment_done": True,
            "is_active": True,
        },
    )
    updates = []
    if not enrollment.payment_done:
        enrollment.payment_done = True
        updates.append("payment_done")
    if not enrollment.is_active:
        enrollment.is_active = True
        updates.append("is_active")
    if hasattr(enrollment, "payment_complete") and not enrollment.payment_complete:
        enrollment.payment_complete = True
        updates.append("payment_complete")
    if updates:
        enrollment.save(update_fields=updates)

    subscription = _ensure_subscription(user)
    return enrollment, subscription


def _mark_payment_paid(payment, session, extra_update_fields=None):
    payment.status = Payment.Status.PAID
    payment.razorpay_payment_id = session.get("payment_intent", "")
    update_fields = ["status", "razorpay_payment_id"]
    if extra_update_fields:
        update_fields.extend(extra_update_fields)
    payment.save(update_fields=update_fields)
    return payment


@login_required
def course_payment(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if Enrollment.objects.filter(user=request.user, course=course, payment_done=True, is_active=True).exists():
        messages.info(request, "You already have access to this course.")
        return redirect("course_detail", course_id=course.id)

    context = {
        "course": course,
        "stripe_pub_key": settings.STRIPE_PUBLISHABLE_KEY,
        "stripe_ready": bool(settings.STRIPE_SECRET_KEY and settings.STRIPE_PUBLISHABLE_KEY),
    }
    return render(request, "payments/payment.html", context)


@login_required
@require_POST
def create_checkout_session(request, course_id):
    if not settings.STRIPE_SECRET_KEY or not settings.STRIPE_PUBLISHABLE_KEY:
        return JsonResponse({"error": "Payment gateway is not configured yet."}, status=503)

    course = get_object_or_404(Course, id=course_id)
    success_url = request.build_absolute_uri(reverse("payments:payment_success")) + "?session_id={CHECKOUT_SESSION_ID}"
    cancel_url = request.build_absolute_uri(reverse("payments:payment_cancel") + f"?course_id={course.id}")

    try:
        session = stripe.checkout.Session.create(
            mode="payment",
            payment_method_types=["card"],
            billing_address_collection="required",
            customer_email=request.user.email,
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={"course_id": str(course.id), "user_id": str(request.user.id)},
            client_reference_id=str(request.user.id),
            line_items=[
                {
                    "quantity": 1,
                    "price_data": {
                        "currency": "inr",
                        "unit_amount": int(course.price * 100),
                        "product_data": {"name": course.title},
                    },
                }
            ],
        )
    except stripe.error.StripeError as exc:
        logger.exception("Stripe checkout session creation failed for course %s.", course_id)
        return JsonResponse({"error": str(exc)}, status=502)

    Payment.objects.update_or_create(
        stripe_session_id=session.id,
        defaults={
            "user": request.user,
            "course": course,
            "amount": course.price,
            "provider": "stripe",
            "status": Payment.Status.PENDING,
        },
    )
    return JsonResponse({"sessionId": session.id})


@login_required
@require_GET
def payment_success(request):
    session_id = request.GET.get("session_id", "").strip()
    fallback_course_id = request.GET.get("course_id")

    if not session_id or session_id == "{CHECKOUT_SESSION_ID}" or not settings.STRIPE_SECRET_KEY:
        messages.error(request, "Unable to verify your payment.")
        return redirect("dashboard")

    try:
        session = stripe.checkout.Session.retrieve(session_id)
    except stripe.error.StripeError:
        logger.exception("Stripe payment verification failed for session %s.", session_id)
        messages.error(request, "Unable to verify your payment with Stripe.")
        return redirect("dashboard")
    if session.get("payment_status") != "paid":
        messages.warning(request, "Your payment is still pending confirmation.")
        course = _get_course_from_session(session, fallback_course_id=fallback_course_id)
        if course:
            return redirect("course_detail", course_id=course.id)
        return redirect("dashboard")

    expected_user_id = str(request.user.id)
    session_user_id = str(_get_user_id_from_session(session, fallback_user_id=request.user.id))
    if session_user_id != expected_user_id:
        messages.error(request, "This payment does not belong to your account.")
        return redirect("dashboard")

    course = _get_course_from_session(session, fallback_course_id=fallback_course_id)
    if course is None:
        messages.error(request, "Unable to identify the purchased course.")
        return redirect("dashboard")

    payment = Payment.objects.filter(stripe_session_id=session_id, user=request.user).select_related("course").first()
    if payment is None:
        payment = Payment.objects.create(
            user=request.user,
            course=course,
            amount=course.price,
            stripe_session_id=session_id,
            razorpay_payment_id=session.get("payment_intent", ""),
            provider="stripe",
            status=Payment.Status.PAID,
        )
    else:
        extra_update_fields = ["amount", "provider"]
        if payment.course_id != course.id:
            payment.course = course
            extra_update_fields.append("course")
        payment.amount = course.price
        payment.provider = "stripe"
        _mark_payment_paid(payment, session, extra_update_fields=extra_update_fields)

    if payment.course:
        _finalize_paid_course_access(request.user, payment.course)
        messages.success(request, "Payment successful. Course access is now active.")
        return redirect("course_detail", course_id=payment.course.id)

    messages.success(request, "Payment successful.")
    return redirect("dashboard")


@login_required
@require_GET
def payment_cancel(request):
    course_id = request.GET.get("course_id")
    messages.info(request, "Payment cancelled.")
    if course_id:
        return redirect("course_detail", course_id=course_id)
    return redirect("course_list")


@csrf_exempt
@require_POST
def payment_webhook(request):
    if not settings.STRIPE_WEBHOOK_SECRET:
        return HttpResponse(status=503)

    payload = request.body
    signature = request.META.get("HTTP_STRIPE_SIGNATURE", "")
    try:
        event = stripe.Webhook.construct_event(payload, signature, settings.STRIPE_WEBHOOK_SECRET)
    except (ValueError, stripe.error.SignatureVerificationError):
        logger.warning("Invalid Stripe webhook signature.")
        return HttpResponse(status=400)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        payment = Payment.objects.filter(stripe_session_id=session.get("id")).select_related("course", "user").first()
        course = _get_course_from_session(session)

        if payment is None and course is not None:
            user_id = _get_user_id_from_session(session)
            if user_id:
                payment = Payment.objects.create(
                    user_id=user_id,
                    course=course,
                    amount=course.price,
                    stripe_session_id=session.get("id", ""),
                    razorpay_payment_id=session.get("payment_intent", ""),
                    provider="stripe",
                    status=Payment.Status.PAID,
                )

        if payment:
            extra_update_fields = ["amount", "provider"]
            if course is not None and payment.course_id != course.id:
                payment.course = course
                extra_update_fields.append("course")
            payment.amount = payment.course.price if payment.course else payment.amount
            payment.provider = "stripe"
            _mark_payment_paid(payment, session, extra_update_fields=extra_update_fields)
            if payment.course:
                _finalize_paid_course_access(payment.user, payment.course)

    return HttpResponse(status=200)


stripe_webhook = payment_webhook
