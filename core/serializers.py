from rest_framework import serializers
from .models import LogEvent
from django.utils.timezone import now

class LogEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = LogEvent
        fields = '__all__'

    def create(self, validated_data):
        if 'ts' not in validated_data:
            validated_data['ts'] = now()
        return super().create(validated_data)
