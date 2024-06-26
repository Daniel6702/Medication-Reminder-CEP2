# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models




class MediremindWebappHeucodevent(models.Model):
    id = models.UUIDField(primary_key=True)
    event_type = models.CharField(max_length=100)
    event_type_enum = models.IntegerField()
    description = models.TextField(blank=True, null=True)
    advanced = models.TextField(blank=True, null=True)
    timestamp = models.BigIntegerField()
    start_time = models.BigIntegerField(blank=True, null=True)
    end_time = models.BigIntegerField(blank=True, null=True)
    length = models.IntegerField(blank=True, null=True)
    sensor_blind_duration = models.IntegerField(blank=True, null=True)
    value = models.TextField(blank=True, null=True)
    unit = models.CharField(max_length=50, blank=True, null=True)
    value2 = models.TextField(blank=True, null=True)
    unit2 = models.CharField(max_length=50, blank=True, null=True)
    value3 = models.TextField(blank=True, null=True)
    unit3 = models.CharField(max_length=50, blank=True, null=True)
    direct_event = models.IntegerField(blank=True, null=True)
    sending_delay = models.IntegerField(blank=True, null=True)
    patient_id = models.CharField(max_length=100, blank=True, null=True)
    caregiver_id = models.IntegerField(blank=True, null=True)
    monitor_id = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    street_address = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    site = models.CharField(max_length=100, blank=True, null=True)
    room = models.CharField(max_length=100, blank=True, null=True)
    sensor_id = models.CharField(max_length=100, blank=True, null=True)
    sensor_type = models.CharField(max_length=100, blank=True, null=True)
    sensor_location = models.CharField(max_length=100, blank=True, null=True)
    sensor_rtc_clock = models.IntegerField(blank=True, null=True)
    device_model = models.CharField(max_length=100, blank=True, null=True)
    device_vendor = models.CharField(max_length=100, blank=True, null=True)
    gateway_id = models.CharField(max_length=100, blank=True, null=True)
    service_id = models.CharField(max_length=100, blank=True, null=True)
    power = models.IntegerField(blank=True, null=True)
    battery = models.IntegerField(blank=True, null=True)
    rssi = models.FloatField(blank=True, null=True)
    measured_power = models.FloatField(blank=True, null=True)
    signal_to_noise_ratio = models.FloatField(blank=True, null=True)
    accuracy = models.IntegerField(blank=True, null=True)
    link_quality = models.FloatField(blank=True, null=True)
    user = models.ForeignKey('AuthUser', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'MediRemind_WebApp_heucodevent'


class MediremindWebappItem(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()

    class Meta:
        managed = False
        db_table = 'MediRemind_WebApp_item'


class MediremindWebappMedicationschedule(models.Model):
    medication_name = models.CharField(max_length=100)
    reminder_time = models.TimeField()
    user = models.ForeignKey('AuthUser', models.DO_NOTHING)
    dosage = models.CharField(max_length=100)
    instructions = models.TextField(blank=True, null=True)
    time_window = models.IntegerField()
    schedule_id = models.UUIDField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'MediRemind_WebApp_medicationschedule'


class MediremindWebappMqttconfiguration(models.Model):
    broker_address = models.CharField(max_length=200)
    port = models.IntegerField()
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    user = models.ForeignKey('AuthUser', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'MediRemind_WebApp_mqttconfiguration'


class MediremindWebappRoom(models.Model):
    room_id = models.CharField(primary_key=True, max_length=50)
    name = models.CharField(max_length=100)
    user = models.ForeignKey('AuthUser', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'MediRemind_WebApp_room'


class MediremindWebappSensor(models.Model):
    sensor_id = models.CharField(primary_key=True, max_length=50)
    type = models.CharField(max_length=3)
    zigbee_id = models.CharField(max_length=50)
    status = models.CharField(max_length=50)
    room = models.ForeignKey(MediremindWebappRoom, models.DO_NOTHING)
    user = models.ForeignKey('AuthUser', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'MediRemind_WebApp_sensor'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class AuthtokenToken(models.Model):
    key = models.CharField(primary_key=True, max_length=40)
    created = models.DateTimeField()
    user = models.OneToOneField(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'authtoken_token'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class MyappItem(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()

    class Meta:
        managed = False
        db_table = 'myapp_item'
