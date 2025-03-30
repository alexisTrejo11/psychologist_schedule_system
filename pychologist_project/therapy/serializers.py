from rest_framework import serializers
from .models import TherapySession

class TherapySessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TherapySession
        fields = '__all__'