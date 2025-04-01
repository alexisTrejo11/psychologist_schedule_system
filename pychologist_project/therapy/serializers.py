from rest_framework import serializers
from .models import TherapySession
from users.models import Patient, Therapist

class TherapySessionSerializer(serializers.ModelSerializer):
    therapist = serializers.PrimaryKeyRelatedField(
        queryset=Therapist.objects.all(),
    )
    patients = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Patient.objects.all(),
        required=False
    )

    class Meta:
        model = TherapySession
        fields = [
            'id',
            'therapist',
            'patients',
            'start_time',
            'end_time',
            'status',
            'notes',
        ]

    def validate(self, data):
        """
        Validaciones adicionales para la sesión.
        """
        if data['start_time'] >= data['end_time']:
            raise serializers.ValidationError("La hora de inicio debe ser anterior a la hora de finalización.")
        return data
    
