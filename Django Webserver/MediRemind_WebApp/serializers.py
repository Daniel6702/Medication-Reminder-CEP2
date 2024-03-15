from rest_framework import serializers
from .models import HeucodEvent

class HeucodEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = HeucodEvent
        fields = '__all__'
