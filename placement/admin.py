from django.contrib import admin

from .models import Job, JobApplication, MockInterview


class JobApplicationInline(admin.TabularInline):
    model = JobApplication
    extra = 0
    readonly_fields = ("user", "created_at")
    fields = ("user", "resume", "status", "created_at")


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("title", "company", "location", "is_active", "created_at", "applicant_count")
    list_filter = ("is_active", "company", "created_at")
    search_fields = ("title", "company", "location", "skills")
    inlines = [JobApplicationInline]

    @admin.display(description="Applicants")
    def applicant_count(self, obj):
        return obj.applications.count()


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ("user", "job", "status", "created_at")
    list_filter = ("status", "job", "created_at")
    search_fields = ("user__email", "user__username", "job__title", "job__company")
    autocomplete_fields = ("user", "job")


@admin.register(MockInterview)
class MockInterviewAdmin(admin.ModelAdmin):
    list_display = ("user", "date", "time", "status", "has_meeting_link")
    list_filter = ("status", "date")
    search_fields = ("user__email", "user__username", "meeting_link")
    autocomplete_fields = ("user",)

    @admin.display(boolean=True, description="Meeting Link")
    def has_meeting_link(self, obj):
        return bool(obj.meeting_link)
