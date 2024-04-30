from rest_framework import serializers
from .models import HeucodEvent
from .models import MedicationSchedule
from .models import MQTTConfiguration
from .models import Room, Device, Notification, StateConfig, Event
from django.conf import settings


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'

class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = '__all__'

class StateConfigSerializer(serializers.ModelSerializer):
    sound_file = serializers.SerializerMethodField()

    class Meta:
        model = StateConfig
        fields = '__all__'

    def get_sound_file(self, obj):
        if obj.sound_file:
            return self.context['request'].build_absolute_uri(obj.sound_file.url)
        return None

class HeucodEventSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = HeucodEvent
        fields = '__all__'

class MedicationScheduleSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = MedicationSchedule
        fields = '__all__'

class MQTTConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = MQTTConfiguration
        fields = ['id', 'user', 'broker_address', 'port', 'username', 'password']

class EventSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = Event
        fields = '__all__' 
