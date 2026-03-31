from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("courses", "0004_course_youtube_playlist_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="enrollment",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, null=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="enrollment",
            name="is_active",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="enrollment",
            name="payment_done",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="enrollment",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="enrollments",
                to="accounts.customuser",
            ),
        ),
        migrations.AlterField(
            model_name="enrollment",
            name="course",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="enrollments",
                to="courses.course",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="enrollment",
            unique_together={("user", "course")},
        ),
    ]
