from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("courses", "0005_enrollment_access_fields"),
        ("classroom", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="liveclass",
            name="course",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="live_classes",
                to="courses.course",
            ),
        ),
    ]
