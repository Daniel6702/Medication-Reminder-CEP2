# Generated by Django 5.0.4 on 2024-04-29 08:33

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MediRemind_WebApp', '0012_room_position_x_room_position_y'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('event_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('type', models.CharField(choices=[(1, 'ZigbeeMotionEvent'), (2, 'DEVICE_DISCOVERY'), (3, 'IDLE'), (4, 'ACTIVE'), (5, 'MEDICATION_TAKEN'), (6, 'MEDICATION_MISSED'), (7, 'ALERT'), (8, 'RGB_STRIP'), (9, 'PIR_SENSOR'), (10, 'SWITCH'), (11, 'VIBRATION_SENSOR'), (12, 'SEND_ZIGBEE'), (13, 'REQUEST_SCHEDULES'), (14, 'RESPONSE_SCHEDULES'), (15, 'ADD_DEVICE'), (16, 'HEUCOD_EVENT'), (17, 'REQUEST_DEVICES'), (18, 'RESPONSE_DEVICES'), (19, 'UPDATE_DB_INSTANCE'), (20, 'REQUEST_MQTT_CONF'), (21, 'RESPONSE_MQTT_CONF'), (22, 'REQUEST_ALERT_CONFS'), (23, 'RESPONSE_ALERT_CONFS'), (24, 'REQUEST_ROOMS'), (25, 'RESPONSE_ROOMS'), (26, 'UPDATE_DB_ATTRIBUTE'), (27, 'MOTION_ALERT'), (28, 'REMIND_HERE'), (30, 'REMIND_EVERYWHERE'), (31, 'NOTIFY_CAREGIVER'), (32, 'ALERT_RESOLVED'), (33, 'REQUEST_CAREGIVER'), (34, 'RESPONSE_CAREGIVER'), (35, 'NOTIFICATION'), (36, 'SEND_NOTIFICATION'), (37, 'REQUEST_STATE_CONFS'), (38, 'RESPONSE_STATE_CONFS'), (39, 'CHANGE_COLOR'), (40, 'SWITCH_LIGHT'), (41, 'PLAY_SOUND'), (42, 'SEND_EVENTS')], max_length=50)),
                ('data', models.TextField()),
                ('time', models.TimeField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='event', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
