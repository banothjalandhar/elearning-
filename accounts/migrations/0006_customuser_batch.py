from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("lms", "0001_initial"),
        ("accounts", "0005_loginotp_subscriptionplan_usersubscription"),
    ]

    operations = [
        migrations.AddField(
            model_name="customuser",
            name="batch",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="users", to="lms.batch"),
        ),
    ]
