from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from rest_framework import viewsets

from blogs import models as blog_model

from .access import has_course_access
from .models import Course, Enrollment, upcomingcourse
from .serializers import CourseSerializer


def upcoming_course_list(request):
    upcoming_courses = upcomingcourse.objects.filter(
        is_active=True, start_date__gt=timezone.now()
    ).order_by("start_date")
    return render(request, "courses/upcoming_course_list.html", {"upcoming_courses": upcoming_courses})


def upcoming_course_detail(request, course_id):
    course = get_object_or_404(upcomingcourse, pk=course_id, is_active=True)
    return render(request, "courses/upcoming_course_detail.html", {"course": course})


def course_list(request):
    courses = Course.objects.all()
    return render(request, "courses/course_list.html", {"courses": courses})


@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    enrolled = has_course_access(request.user, course)
    return render(request, "courses/course_detail.html", {"course": course, "enrolled": enrolled})


class CourseAPI(viewsets.ReadOnlyModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer


def search(request):
    query = request.GET.get("q", "")
    courses = Course.objects.filter(title__icontains=query)
    blogs = blog_model.Blog.objects.filter(title__icontains=query)
    return render(
        request,
        "search_results.html",
        {
            "query": query,
            "courses": courses,
            "blogs": blogs,
        },
    )
