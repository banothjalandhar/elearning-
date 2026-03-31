from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Job",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=255)),
                ("company", models.CharField(max_length=255)),
                ("location", models.CharField(blank=True, max_length=255)),
                ("description", models.TextField()),
                ("skills", models.TextField(blank=True)),
                ("apply_link", models.URLField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="MockInterview",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date", models.DateField()),
                ("time", models.TimeField()),
                ("meeting_link", models.URLField(blank=True)),
                ("status", models.CharField(choices=[("scheduled", "Scheduled"), ("completed", "Completed"), ("cancelled", "Cancelled")], default="scheduled", max_length=20)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="mock_interviews", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["date", "time", "-created_at"]},
        ),
        migrations.CreateModel(
            name="JobApplication",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("resume", models.FileField(upload_to="placement/resumes/")),
                ("status", models.CharField(choices=[("applied", "Applied"), ("shortlisted", "Shortlisted"), ("rejected", "Rejected"), ("selected", "Selected")], default="applied", max_length=20)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("job", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="applications", to="placement.job")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="job_applications", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-created_at"], "unique_together": {("user", "job")}},
        ),
    ]

