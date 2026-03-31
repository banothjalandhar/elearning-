from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Exam",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=255)),
                ("category", models.CharField(choices=[("DSA", "DSA Round"), ("ADSA", "ADSA Round"), ("APTITUDE", "Aptitude Round"), ("COMMUNICATION", "Communication Round"), ("CODING", "Coding Round")], max_length=20)),
                ("duration", models.PositiveIntegerField(help_text="Duration in minutes")),
                ("total_marks", models.PositiveIntegerField()),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["category", "title"]},
        ),
        migrations.CreateModel(
            name="Question",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("question_text", models.TextField()),
                ("question_type", models.CharField(choices=[("MCQ", "MCQ"), ("TEXT", "TEXT"), ("CODE", "CODE")], max_length=10)),
                ("marks", models.PositiveIntegerField(default=1)),
                ("exam", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="questions", to="exams.exam")),
            ],
            options={"ordering": ["id"]},
        ),
        migrations.CreateModel(
            name="Option",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("option_text", models.CharField(max_length=255)),
                ("is_correct", models.BooleanField(default=False)),
                ("question", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="options", to="exams.question")),
            ],
        ),
        migrations.CreateModel(
            name="StudentExam",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("start_time", models.DateTimeField(default=django.utils.timezone.now)),
                ("end_time", models.DateTimeField()),
                ("score", models.FloatField(default=0)),
                ("submitted", models.BooleanField(default=False)),
                ("warning_count", models.PositiveIntegerField(default=0)),
                ("auto_submitted", models.BooleanField(default=False)),
                ("exam", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="student_exams", to="exams.exam")),
                ("student", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="student_exams", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-start_time"], "unique_together": {("student", "exam")}},
        ),
        migrations.CreateModel(
            name="Result",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("score", models.FloatField()),
                ("passed", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("exam", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="results", to="exams.exam")),
                ("student", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="results", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-created_at"], "unique_together": {("student", "exam")}},
        ),
        migrations.CreateModel(
            name="StudentAnswer",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("text_answer", models.TextField(blank=True, null=True)),
                ("code_answer", models.TextField(blank=True, null=True)),
                ("programming_language", models.CharField(blank=True, choices=[("python", "Python"), ("c", "C"), ("java", "Java")], max_length=20, null=True)),
                ("question", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="student_answers", to="exams.question")),
                ("selected_option", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="selected_answers", to="exams.option")),
                ("student_exam", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="answers", to="exams.studentexam")),
            ],
            options={"unique_together": {("student_exam", "question")}},
        ),
    ]
