from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0004_usersession"),
    ]

    operations = [
        migrations.CreateModel(
            name="LoginOTP",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("otp", models.CharField(max_length=6)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("is_used", models.BooleanField(default=False)),
                (
                    "user",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="login_otps", to="accounts.customuser"),
                ),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="SubscriptionPlan",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=150)),
                ("price", models.DecimalField(decimal_places=2, max_digits=8)),
                ("duration_days", models.PositiveIntegerField()),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={"ordering": ["price", "name"]},
        ),
        migrations.CreateModel(
            name="UserSubscription",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("start_date", models.DateTimeField()),
                ("end_date", models.DateTimeField()),
                ("is_active", models.BooleanField(default=True)),
                (
                    "plan",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="user_subscriptions", to="accounts.subscriptionplan"),
                ),
                (
                    "user",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="subscriptions", to="accounts.customuser"),
                ),
            ],
            options={"ordering": ["-end_date"]},
        ),
    ]
