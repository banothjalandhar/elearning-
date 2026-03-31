from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("courses", "0004_course_youtube_playlist_id"),
        ("payments", "0002_rename_stripe_charge_id_payment_razorpay_payment_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="payment",
            name="course",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="payments",
                to="courses.course",
            ),
        ),
        migrations.AddField(
            model_name="payment",
            name="provider",
            field=models.CharField(default="stripe", max_length=30),
        ),
        migrations.AddField(
            model_name="payment",
            name="status",
            field=models.CharField(
                choices=[("pending", "Pending"), ("paid", "Paid"), ("failed", "Failed")],
                default="pending",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="payment",
            name="stripe_session_id",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name="payment",
            name="razorpay_payment_id",
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
