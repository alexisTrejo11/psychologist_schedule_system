from rest_framework import serializers
from users.serializers import UserSerializer
from .models import Therapist
from users.models import User

class TherapistSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=False)

    class Meta:
        model = Therapist
        fields = '__all__'
        read_only_fields = ['id']
        extra_kwargs = {
            'id': {'help_text': 'Unique therapist ID.'},
            'name': {'help_text': 'Name of the therapist.'},
            'license_number': {'help_text': "Therapist's license number.",},
            'specialization': {'help_text': "Therapist's specialization."},
        }

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create_user(**user_data, role='THERAPIST')
        return Therapist.objects.create(user=user, **validated_data)
    

class TherapistHomeDataSerializer(serializers.Serializer):
    therapist_patient_count = serializers.IntegerField()
    incoming_session_count = serializers.IntegerField()
    name = serializers.CharField()
    profile_picture = serializers.CharField()
