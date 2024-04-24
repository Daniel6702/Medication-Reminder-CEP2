from django.db import models
from django.contrib.auth.models import User
import uuid
from enum import Enum
from django.core.validators import MinValueValidator


def get_default_user_id():
    return User.objects.first().id if User.objects.exists() else None

class MedicationSchedule(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='medication_schedules', default=get_default_user_id)
    medication_name = models.CharField(max_length=100)
    reminder_time = models.TimeField(default='00:00:00')
    time_window = models.IntegerField(default=0)
    dosage = models.CharField(max_length=100, default = '0 mg')
    instructions = models.TextField(blank=True, null=True)  
    schedule_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    def __str__(self):
        return f"{self.medication_name} Schedule for {self.user.username}"

class Room(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rooms', null=True, blank=True)
    room_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    connected_rooms = models.ManyToManyField('self', blank=True)

    def __str__(self):
        return self.name
    
class Device(models.Model):
    DEVICE_TYPES = (
        ('PIR_SENSOR', 'Passive Infrared'),
        ('VIBRATION_SENSOR', 'Vibration'),
        ('RGB_STRIP', 'RGB Light'),
        ('SWITCH', 'Switch'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sensors', null=True, blank=True)
    device_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    zigbee_id = models.CharField(max_length=50)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=100, choices=DEVICE_TYPES)
    status = models.CharField(max_length=50)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='devices', null=True, blank=True)

    def __str__(self):
        return f"{self.type} Device {self.device_id} at {self.room}"

class BlinkConfiguration(models.Model):
    blink = models.BooleanField(default=False)
    blink_interval = models.FloatField(validators=[MinValueValidator(0.1)], default=1.0)
    blink_times = models.IntegerField(blank=True, null=True, validators=[MinValueValidator(1)])

    def __str__(self):
        return f"Blink: {'Enabled' if self.blink else 'Disabled'}, Interval: {self.blink_interval}s, Times: {self.blink_times or 'Unlimited'}"

class StateConfig(models.Model):
    color_code = models.CharField(max_length=7, default='Yellow')  # Default for illustrative purposes, set specifically in each instance
    sound_file = models.FileField(upload_to='sounds/', blank=True, null=True)
    blink_config = models.ForeignKey(BlinkConfiguration, on_delete=models.CASCADE)

    def __str__(self):
        return f"StateConfig {self.id} - Color: {self.color_code}"

class AlertConfiguration(models.Model):
    alert_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='alert_configurations', null=True, blank=True)
    active_config = models.ForeignKey(StateConfig, related_name='active_config', on_delete=models.CASCADE, null=True)
    med_taken_config = models.ForeignKey(StateConfig, related_name='med_taken_config', on_delete=models.CASCADE, null=True)
    med_missed_config = models.ForeignKey(StateConfig, related_name='med_missed_config', on_delete=models.CASCADE, null=True)
    alarmed_config = models.ForeignKey(StateConfig, related_name='alarmed_config', on_delete=models.CASCADE, null=True)

    @classmethod
    def create_default_configs(cls):
        blink_default = BlinkConfiguration.objects.create()
        active = StateConfig.objects.create(color_code='#FFFF00', blink_config=blink_default)
        med_taken = StateConfig.objects.create(color_code='Green', blink_config=blink_default)
        med_missed = StateConfig.objects.create(color_code='Red', blink_config=blink_default)
        alarmed = StateConfig.objects.create(color_code='Red', blink_config=blink_default)
        return cls.objects.create(
            active_config=active,
            med_taken_config=med_taken,
            med_missed_config=med_missed,
            alarmed_config=alarmed
        )

    def __str__(self):
        return f"AlertConfiguration {self.alert_id}"

# Remember to apply migrations
# python manage.py makemigrations
# python manage.py migrate

class MQTTConfiguration(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mqtt_configurations')
    mqtt_id = models.CharField(max_length=100, primary_key=True)
    broker_address = models.URLField()
    port = models.IntegerField()
    username = models.CharField(max_length=100, blank=True)
    password = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"MQTT Broker at {self.broker_address}"
    
class NotificationType(Enum):
    ROUTINE = "Routine"             
    IMPORTANT = "Important"          
    CRITICAL = "Critical"          
    INFO = "Informational"
    SYSTEM = "System"

class Notification(models.Model):
    notification_id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notification')
    type = models.CharField(max_length=20, choices=[(tag.name, tag.value) for tag in NotificationType])
    message = models.TextField()
    timestamp = models.DateTimeField()

    def __str__(self):
        return f"{self.notification_id} - {self.user}"

class HeucodEvent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='heucod_events', default=get_default_user_id)

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    event_type = models.CharField(max_length=100)
    event_type_enum = models.IntegerField()
    description = models.TextField(null=True, blank=True)
    advanced = models.TextField(null=True, blank=True)
    timestamp = models.BigIntegerField()
    start_time = models.BigIntegerField(null=True, blank=True)
    end_time = models.BigIntegerField(null=True, blank=True)
    length = models.IntegerField(null=True, blank=True)
    sensor_blind_duration = models.IntegerField(null=True, blank=True)
    value = models.TextField(null=True, blank=True)  # Since it's Any, using TextField
    unit = models.CharField(max_length=50, null=True, blank=True)
    value2 = models.TextField(null=True, blank=True)
    unit2 = models.CharField(max_length=50, null=True, blank=True)
    value3 = models.TextField(null=True, blank=True)
    unit3 = models.CharField(max_length=50, null=True, blank=True)
    direct_event = models.BooleanField(null=True, blank=True)
    sending_delay = models.IntegerField(null=True, blank=True)
    patient_id = models.CharField(max_length=100, null=True, blank=True)
    caregiver_id = models.IntegerField(null=True, blank=True)
    monitor_id = models.CharField(max_length=100, null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    street_address = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    postal_code = models.CharField(max_length=20, null=True, blank=True)
    site = models.CharField(max_length=100, null=True, blank=True)
    room = models.CharField(max_length=100, null=True, blank=True)
    sensor_id = models.CharField(max_length=100, null=True, blank=True)
    sensor_type = models.CharField(max_length=100, null=True, blank=True)
    sensor_location = models.CharField(max_length=100, null=True, blank=True)
    sensor_rtc_clock = models.BooleanField(null=True, blank=True)
    device_model = models.CharField(max_length=100, null=True, blank=True)
    device_vendor = models.CharField(max_length=100, null=True, blank=True)
    gateway_id = models.CharField(max_length=100, null=True, blank=True)
    service_id = models.CharField(max_length=100, null=True, blank=True)
    power = models.IntegerField(null=True, blank=True)
    battery = models.IntegerField(null=True, blank=True)
    rssi = models.FloatField(null=True, blank=True)
    measured_power = models.FloatField(null=True, blank=True)
    signal_to_noise_ratio = models.FloatField(null=True, blank=True)
    accuracy = models.IntegerField(null=True, blank=True)
    link_quality = models.FloatField(null=True, blank=True)

    # Add any other fields as necessary
