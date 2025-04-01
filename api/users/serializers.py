from rest_framework import serializers
from .models import User, Patient, Therapist

class SignupSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True, 
        help_text="Email address of the user."
    )
    password = serializers.CharField(
        required=True, 
        write_only=True, 
        help_text="Password for the user (write-only)."
    )
    phone = serializers.CharField(
        required=False, 
        allow_blank=True, 
        help_text="Phone number of the user."
    )
    user_role = serializers.ChoiceField(
        choices=['admin', 'therapist', 'patient'], 
        required=True, 
        help_text="Role of the user (admin, therapist, patient)."
    )
    license_number = serializers.CharField(
        required=False, 
        allow_blank=True, 
        help_text="License number for therapists."
    )
    specialization = serializers.CharField(
        required=False, 
        allow_blank=True, 
        help_text="Specialization of the therapist."
    )
    name = serializers.CharField(
        required=False, 
        allow_blank=True, 
        help_text="Name of the patient."
    )
    description = serializers.CharField(
        required=False, 
        allow_blank=True, 
        help_text="Description of the patient."
    )

    def validate(self, data):
        """
        Additional validations before registration.
        """
        user_role = data.get('user_role')

        if user_role == 'therapist':
            if not data.get('license_number'):
                raise serializers.ValidationError("License number is required for therapists.")
            if not data.get('specialization'):
                raise serializers.ValidationError("Specialization is required for therapists.")
        elif user_role == 'patient':
            if not data.get('name'):
                raise serializers.ValidationError("Name is required for patients.")

        return data


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True, 
        help_text="Email address of the user."
    )
    password = serializers.CharField(
        required=True, 
        write_only=True, 
        help_text="Password for the user (write-only)."
    )

    def validate(self, data):
        """
        Validates user credentials.
        """
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            raise serializers.ValidationError("Email and password are required.")

        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'phone', 'role', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']
        extra_kwargs = {
            'id': {'help_text': 'Unique user ID.'},
            'email': {'help_text': "User's email address."},
            'phone': {'help_text': "User's phone number."},
            'role': {'help_text': "User's role (THERAPIST, PATIENT, ADMIN)."},
            'is_active': {'help_text': "Indicates if the user is active."},
            'created_at': {'help_text': "Date and time the user was created (ISO 8601 format)."},
        }


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


class TherapistSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=False)

    class Meta:
        model = Therapist
        fields = '__all__'
        read_only_fields = ['id']
        extra_kwargs = {
            'id': {'help_text': 'Unique therapist ID.'},
            'name': {'help_text': 'Name of the therapist.'},
            'license_number': {'help_text': "Therapist's license number.", 'unique': True},
            'specialization': {'help_text': "Therapist's specialization."},
        }

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create_user(**user_data, role='THERAPIST')
        return Therapist.objects.create(user=user, **validated_data)