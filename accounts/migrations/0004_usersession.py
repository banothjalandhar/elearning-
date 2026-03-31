from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0003_remove_customuser_address_customuser_branch_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="UserSession",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("session_key", models.CharField(max_length=255, unique=True)),
                ("ip_address", models.GenericIPAddressField(blank=True, null=True)),
                ("device", models.CharField(blank=True, max_length=255)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="user_sessions", to="accounts.customuser"),
                ),
            ],
            options={"ordering": ["-updated_at"]},
        ),
    ]
