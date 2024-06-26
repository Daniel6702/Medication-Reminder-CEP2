# Generated by Django 5.0.4 on 2024-05-09 13:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MediRemind_WebApp', '0015_merge_20240509_1357'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='type',
            field=models.CharField(choices=[(1, 'ZigbeeMotionEvent'), (2, 'DEVICE_DISCOVERY'), (3, 'IDLE'), (4, 'ACTIVE'), (5, 'MEDICATION_TAKEN'), (6, 'MEDICATION_MISSED'), (7, 'ALERT'), (8, 'RGB_STRIP'), (9, 'PIR_SENSOR'), (10, 'SWITCH'), (11, 'VIBRATION_SENSOR'), (12, 'SEND_ZIGBEE'), (13, 'REQUEST_SCHEDULES'), (14, 'RESPONSE_SCHEDULES'), (15, 'ADD_DEVICE'), (16, 'HEUCOD_EVENT'), (17, 'REQUEST_DEVICES'), (18, 'RESPONSE_DEVICES'), (19, 'UPDATE_DB_INSTANCE'), (20, 'REQUEST_MQTT_CONF'), (21, 'RESPONSE_MQTT_CONF'), (22, 'REQUEST_ALERT_CONFS'), (23, 'RESPONSE_ALERT_CONFS'), (24, 'REQUEST_ROOMS'), (25, 'RESPONSE_ROOMS'), (26, 'UPDATE_DB_ATTRIBUTE'), (27, 'MOTION_ALERT'), (28, 'REMIND_HERE'), (30, 'REMIND_EVERYWHERE'), (31, 'NOTIFY_CAREGIVER'), (32, 'ALERT_RESOLVED'), (33, 'REQUEST_CAREGIVER'), (34, 'RESPONSE_CAREGIVER'), (35, 'NOTIFICATION'), (36, 'SEND_NOTIFICATION'), (37, 'REQUEST_STATE_CONFS'), (38, 'RESPONSE_STATE_CONFS'), (39, 'CHANGE_COLOR'), (40, 'SWITCH_LIGHT'), (41, 'PLAY_SOUND'), (42, 'SEND_EVENTS'), (43, 'TURN_ON'), (44, 'TURN_OFF'), (45, 'BLINK_TIMES'), (46, 'START_BLINK'), (47, 'STOP_BLINK'), (48, 'SETUP_FINISHED'), (49, 'STOP_SOUND'), (50, 'ROOM_EMPTY'), (51, 'ALARM'), (52, 'REQUEST_ALARM_STATE'), (53, 'RESPONSE_ALARM_STATE')], max_length=50),
        ),
    ]
