# Generated by Django 5.0.4 on 2024-04-18 08:14

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MediRemind_WebApp', '0010_blinkconfiguration_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alertconfiguration',
            name='alert_id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
    ]
