from django.db import models


class LiveClass(models.Model):
    course = models.ForeignKey("courses.Course", on_delete=models.CASCADE, related_name="live_classes", null=True, blank=True)
    title = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    date = models.DateField()
    time = models.TimeField()
    meeting_link = models.URLField()
    notes_file = models.FileField(upload_to="classroom/notes/", blank=True, null=True)
    recording_link = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date", "time", "-created_at"]

    def __str__(self):
        return f"{self.title} - {self.subject}"
