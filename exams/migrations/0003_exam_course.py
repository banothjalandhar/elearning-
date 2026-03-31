from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("courses", "0005_enrollment_access_fields"),
        ("exams", "0002_exam_schedule_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="exam",
            name="course",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="exams",
                to="courses.course",
            ),
        ),
    ]
