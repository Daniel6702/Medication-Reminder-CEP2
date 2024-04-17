# Generated by Django 5.0.4 on 2024-04-16 11:39

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MediRemind_WebApp', '0007_alertconfiguration_blink_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('notification_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('type', models.CharField(choices=[('ROUTINE', 'Routine'), ('IMPORTANT', 'Important'), ('CRITICAL', 'Critical'), ('INFO', 'Informational'), ('SYSTEM', 'System')], max_length=20)),
                ('message', models.TextField()),
                ('timestamp', models.DateTimeField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notification', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]