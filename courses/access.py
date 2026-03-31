from accounts.services import has_active_subscription

from .models import Enrollment


def get_active_enrollments(user):
    if not getattr(user, "is_authenticated", False):
        return Enrollment.objects.none()
    return Enrollment.objects.filter(user=user, is_active=True, payment_done=True)


def get_enrolled_course_ids(user):
    if not getattr(user, "is_authenticated", False) or not has_active_subscription(user):
        return []
    return list(get_active_enrollments(user).values_list("course_id", flat=True))


def has_course_access(user, course):
    if not getattr(user, "is_authenticated", False):
        return False
    if not has_active_subscription(user):
        return False
    if course is None:
        return True
    return get_active_enrollments(user).filter(course=course).exists()
