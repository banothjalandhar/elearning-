from django.conf import settings
from django.db import models
from django.utils import timezone


class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to="course_images/")
    video_url = models.URLField(blank=True, null=True)
    youtube_playlist_id = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.title


class Enrollment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="enrollments")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    is_active = models.BooleanField(default=True)
    payment_done = models.BooleanField(default=False)
    payment_complete = models.BooleanField(default=False)
    progress = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "course")
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        self.payment_complete = self.payment_done
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user} - {self.course}"


class upcomingcourse(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to="upcoming/course")
    video_url = models.URLField(blank=True, null=True)
    start_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def is_upcoming(self):
        return self.start_date > timezone.now()

    def __str__(self):
        return self.title
