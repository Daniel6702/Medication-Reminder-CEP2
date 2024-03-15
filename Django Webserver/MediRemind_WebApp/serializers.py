from rest_framework import serializers
from .models import HeucodEvent

class HeucodEventSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = HeucodEvent
        fields = '__all__'
