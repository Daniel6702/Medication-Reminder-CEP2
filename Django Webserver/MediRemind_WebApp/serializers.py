from rest_framework import serializers
from .models import HeucodEvent
from .models import MedicationSchedule

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