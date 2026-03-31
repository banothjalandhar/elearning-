from django.contrib import admin
from django.utils.html import format_html, format_html_join

from .models import Course, Enrollment, upcomingcourse


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "price", "enrolled_students_count", "live_classes_count", "exams_count")
    search_fields = ("title", "description")
    readonly_fields = ("course_support_view",)
    fieldsets = (
        (None, {"fields": ("title", "description", "price", "image", "video_url", "youtube_playlist_id")}),
        ("Course Support View", {"fields": ("course_support_view",)}),
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.prefetch_related("enrollments__user", "live_classes", "exams")

    def enrolled_students_count(self, obj):
        return obj.enrollments.filter(payment_done=True, is_active=True).count()

    def live_classes_count(self, obj):
        return obj.live_classes.count()

    def exams_count(self, obj):
        return obj.exams.count()

    def course_support_view(self, obj):
        if obj is None:
            return "Save the course to view linked students, classes, and exams."

        students = list(obj.enrollments.filter(payment_done=True, is_active=True).select_related("user"))
        classes = list(obj.live_classes.all())
        exams = list(obj.exams.all())

        student_html = format_html_join("", "{}<br>", ((student.user.email,) for student in students)) if students else "No enrolled students"
        class_html = format_html_join("", "{}<br>", ((item.title,) for item in classes)) if classes else "No linked classes"
        exam_html = format_html_join("", "{}<br>", ((item.title,) for item in exams)) if exams else "No linked exams"

        return format_html(
            "<strong>Students enrolled in this course</strong><br>{}<br><br>"
            "<strong>Classes linked to this course</strong><br>{}<br><br>"
            "<strong>Exams linked to this course</strong><br>{}",
            student_html,
            class_html,
            exam_html,
        )

    course_support_view.short_description = "Support Summary"


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("user", "course", "is_active", "payment_done", "created_at")
    list_filter = ("is_active", "payment_done", "course", "user")
    search_fields = ("user__email", "user__username", "course__title")


@admin.register(upcomingcourse)
class UpcomingCourseAdmin(admin.ModelAdmin):
    list_display = ("title", "price", "start_date", "is_active")
    list_filter = ("is_active",)
    search_fields = ("title", "description")
