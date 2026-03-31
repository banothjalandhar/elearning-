from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="LiveClass",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=255)),
                ("subject", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True)),
                ("date", models.DateField()),
                ("time", models.TimeField()),
                ("meeting_link", models.URLField()),
                ("notes_file", models.FileField(blank=True, null=True, upload_to="classroom/notes/")),
                ("recording_link", models.URLField(blank=True)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["date", "time", "-created_at"]},
        ),
    ]
