from django.db import models
from django.contrib.auth.models import User
import uuid
from enum import Enum
from django.core.validators import MinValueValidator
import json
import datetime

def get_default_user_id():
    return User.objects.first().id if User.objects.exists() else None

class Alarmed(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='alarm', default=get_default_user_id)
    alarmed = models.BooleanField(default=False)

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
    dosage = models.CharField(max_length=100, default='0 mg')
    datetime = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    input_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    def __str__(self):
        return f"{self.medication_name} Input for {self.user.username}"

class Room(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rooms', null=True, blank=True)
    room_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    connected_rooms = models.ManyToManyField('self', blank=True)
    position_x = models.FloatField(default=0.0)
    position_y = models.FloatField(default=0.0)

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
    
class StateConfig(models.Model):
    STATE_NAMES = (
        ('IDLE', 'IdleState'),
        ('ACTIVE', 'ActiveState'),
        ('MEDICATION_TAKEN', 'MedicationTakenState'),
        ('MEDICATION_MISSED', 'MedicationMissedState'),
        ('ALERT', 'AlertState')
    )
        
    state_config_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='state_configs', null=True, blank=True)
    state_name = models.CharField(max_length=100, choices=STATE_NAMES)
    color_code = models.CharField(max_length=7, blank=True)  # For RGB color code like '#FF5733'
    sound_file = models.FileField(upload_to='sounds/', blank=True, null=True)
    blink = models.BooleanField(default=False)
    blink_interval = models.FloatField(validators=[MinValueValidator(0.1)], default=1.0)
    blink_times = models.IntegerField(blank=True, null=True, validators=[MinValueValidator(1)])
    care_giver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='care_giver_configs', null=True, blank=True)

    def __str__(self):
        return f"StateConfig {self.state_config_id} - Color: {self.color_code}"
    
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

class EventType(Enum):
    '''
    Represents different types of events that can be detected or generated within the system. 
    Acts like topics / channels functions can subscribe to. 
    '''
    ZigbeeMotionEvent = 1
    DEVICE_DISCOVERY = 2
    IDLE = 3
    ACTIVE = 4
    MEDICATION_TAKEN = 5
    MEDICATION_MISSED = 6
    ALERT = 7
    RGB_STRIP = 8
    PIR_SENSOR = 9
    SWITCH = 10
    VIBRATION_SENSOR = 11
    SEND_ZIGBEE = 12
    REQUEST_SCHEDULES = 13
    RESPONSE_SCHEDULES = 14
    ADD_DEVICE = 15
    HEUCOD_EVENT = 16
    REQUEST_DEVICES = 17
    RESPONSE_DEVICES = 18
    UPDATE_DB_INSTANCE = 19
    REQUEST_MQTT_CONF = 20
    RESPONSE_MQTT_CONF = 21
    REQUEST_ALERT_CONFS = 22
    RESPONSE_ALERT_CONFS = 23
    REQUEST_ROOMS = 24
    RESPONSE_ROOMS = 25
    UPDATE_DB_ATTRIBUTE = 26
    MOTION_ALERT = 27
    REMIND_HERE = 28
    REMIND_EVERYWHERE = 30
    NOTIFY_CAREGIVER = 31
    ALERT_RESOLVED = 32
    REQUEST_CAREGIVER = 33
    RESPONSE_CAREGIVER = 34
    NOTIFICATION = 35
    SEND_NOTIFICATION = 36
    REQUEST_STATE_CONFS = 37
    RESPONSE_STATE_CONFS = 38
    CHANGE_COLOR = 39
    SWITCH_LIGHT = 40
    PLAY_SOUND = 41
    SEND_EVENTS = 42

    @classmethod
    def choices(cls):
        return [(item.value, item.name) for item in cls]

class Event(models.Model):
    event_id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='event')
    type = models.CharField(max_length=50, choices=EventType.choices())
    data = models.TextField()  # Storing JSON data in a text field
    time = models.TimeField()

    def set_data(self, data):
        self.data = json.dumps(data)

    def get_data(self):
        return json.loads(self.data)

    def __str__(self):
        return f"{self.event_id} ({self.type})"