from django.db import models

class Item(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name

from django.db import models

class HeucodEvent(models.Model):
    id = models.UUIDField(primary_key=True, editable=False)
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
