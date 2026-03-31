from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from courses.access import get_enrolled_course_ids, has_course_access

from .models import LiveClass


def dashboard_class(user=None):
    today = timezone.localdate()
    now_time = timezone.localtime().time()
    active_classes = LiveClass.objects.select_related("course").filter(is_active=True)
    if user is not None and getattr(user, "is_authenticated", False):
        active_classes = active_classes.filter(course_id__in=get_enrolled_course_ids(user))

    todays_class = active_classes.filter(date=today).order_by("time").first()
    upcoming_class = (
        active_classes.filter(Q(date__gt=today) | Q(date=today, time__gte=now_time))
        .order_by("date", "time")
        .first()
    )
    if todays_class and upcoming_class and todays_class.pk == upcoming_class.pk:
        upcoming_class = (
            active_classes.filter(Q(date__gt=today) | Q(date=today, time__gt=todays_class.time))
            .order_by("date", "time")
            .first()
        )

    last_recording = (
        active_classes.exclude(recording_link="")
        .order_by("-date", "-time", "-created_at")
        .first()
    )

    return {
        "todays_class": todays_class,
        "upcoming_class": upcoming_class,
        "last_recording": last_recording,
    }


@login_required
def class_list(request):
    enrolled_course_ids = get_enrolled_course_ids(request.user)
    classes = LiveClass.objects.select_related("course").filter(
        is_active=True,
        course_id__in=enrolled_course_ids,
    ).order_by("date", "time")
    return render(request, "classroom/class_list.html", {"classes": classes})


@login_required
def class_detail(request, id):
    live_class = get_object_or_404(LiveClass.objects.select_related("course"), pk=id, is_active=True)
    if not has_course_access(request.user, live_class.course):
        messages.error(request, "You are not enrolled in this course")
        return redirect("classroom:class_list")
    return render(request, "classroom/class_detail.html", {"live_class": live_class})


@login_required
def whiteboard(request):
    return render(request, "classroom/whiteboard.html")


@login_required
def join_class(request, id):
    live_class = get_object_or_404(LiveClass.objects.select_related("course"), pk=id, is_active=True)
    if not has_course_access(request.user, live_class.course):
        messages.error(request, "You are not enrolled in this course")
        return redirect("classroom:class_list")
    if not live_class.meeting_link:
        messages.error(request, "Meeting link is not available yet.")
        return redirect("classroom:class_detail", id=live_class.id)
    return redirect(live_class.meeting_link)


@login_required
def download_notes(request, id):
    live_class = get_object_or_404(LiveClass.objects.select_related("course"), pk=id, is_active=True)
    if not has_course_access(request.user, live_class.course):
        messages.error(request, "You are not enrolled in this course")
        return redirect("classroom:class_list")
    if not live_class.notes_file:
        raise Http404("Notes not found.")
    return FileResponse(live_class.notes_file.open("rb"), as_attachment=True, filename=live_class.notes_file.name.split("/")[-1])


@login_required
def watch_recording(request, id):
    live_class = get_object_or_404(LiveClass.objects.select_related("course"), pk=id, is_active=True)
    if not has_course_access(request.user, live_class.course):
        messages.error(request, "You are not enrolled in this course")
        return redirect("classroom:class_list")
    if not live_class.recording_link:
        raise Http404("Recording not found.")
    return redirect(live_class.recording_link)
