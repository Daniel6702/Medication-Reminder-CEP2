# Generated by Django 5.0.3 on 2024-04-24 16:18

import MediRemind_WebApp.models
import django.core.validators
import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MediRemind_WebApp', '0009_delete_item'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ManualInput',
            fields=[
                ('medication_name', models.CharField(max_length=100)),
                ('dosage', models.CharField(default='0 mg', max_length=100)),
                ('time', models.TimeField(default='00:00:00')),
                ('date', models.DateField(auto_now_add=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('input_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('user', models.ForeignKey(default=MediRemind_WebApp.models.get_default_user_id, on_delete=django.db.models.deletion.CASCADE, related_name='manual_inputs', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='StateConfig',
            fields=[
                ('state_config_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('state_name', models.CharField(choices=[('IDLE', 'IdleState'), ('ACTIVE', 'ActiveState'), ('MEDICATION_TAKEN', 'MedicationTakenState'), ('MEDICATION_MISSED', 'MedicationMissedState'), ('ALERT', 'AlertState')], max_length=100)),
                ('color_code', models.CharField(blank=True, max_length=7)),
                ('sound_file', models.FileField(blank=True, null=True, upload_to='sounds/')),
                ('blink', models.BooleanField(default=False)),
                ('blink_interval', models.FloatField(default=1.0, validators=[django.core.validators.MinValueValidator(0.1)])),
                ('blink_times', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1)])),
                ('care_giver', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='care_giver_configs', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='state_configs', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]