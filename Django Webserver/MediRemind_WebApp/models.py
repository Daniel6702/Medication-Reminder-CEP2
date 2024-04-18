from django.db import models
from django.contrib.auth.models import User
import uuid

def get_default_user_id():
    return User.objects.first().id if User.objects.exists() else None

class Item(models.Model): #TEST
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name
    
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

class ManualInput(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='manual_inputs', default=get_default_user_id)
    medication_name = models.CharField(max_length=100)
    dosage = models.number(max_length=100)
    time = models.TimeField(default='00:00:00')
    date = models.DateField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    input_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    def __str__(self):
        return f"{self.medication_name} Input for {self.user.username}"

class Room(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rooms', null=True, blank=True)
    room_id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=100)
    

    def __str__(self):
        return self.name
    
class Sensor(models.Model):
    SENSOR_TYPES = (
        ('PIR', 'Passive Infrared'),
        ('VIB', 'Vibration'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sensors', null=True, blank=True)
    sensor_id = models.CharField(max_length=50, primary_key=True)
    type = models.CharField(max_length=3, choices=SENSOR_TYPES)
    zigbee_id = models.CharField(max_length=50)
    status = models.CharField(max_length=50)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='sensors')

    def __str__(self):
        return f"{self.type} Sensor {self.sensor_id} at {self.room}"
    
class AlertConfiguration(models.Model):
    ALERT_TYPES = (
        ('LIGHT', 'Light'),
        ('SOUND', 'Sound'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='alert_configurations', null=True, blank=True)
    alert_type = models.CharField(max_length=5, choices=ALERT_TYPES)
    color_code = models.CharField(max_length=7, blank=True)  # For RGB color code like '#FF5733'
    sound_file = models.FileField(upload_to='alerts/sounds/', blank=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='alert_configurations')
    
class MQTTConfiguration(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mqtt_configurations')
    broker_address = models.URLField()
    port = models.IntegerField()
    username = models.CharField(max_length=100, blank=True)
    password = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"MQTT Broker at {self.broker_address}"

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
