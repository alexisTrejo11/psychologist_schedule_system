from rest_framework import serializers
from users.core.presentation.api.serializers.serializers import UserSerializer
from users.models import User
from .....models import Patient

class PatientSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Patient
        fields = ['id', 'user', 'name', 'description', 'first_therapy', 'last_therapy']
        read_only_fields = ['id']
        extra_kwargs = {
            'id': {'help_text': 'Unique patient ID.'},
            'name': {'help_text': 'Name of the patient.'},
            'description': {'help_text': 'Description of the patient.'},
            'first_therapy': {'help_text': "Date and time of the patient's first therapy session (ISO 8601 format)."},
            'last_therapy': {'help_text': "Date and time of the patient's last therapy session (ISO 8601 format)."},
        }

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create_user(**user_data, role='PATIENT')
        return Patient.objects.create(user=user, **validated_data)

