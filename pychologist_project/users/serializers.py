from rest_framework import serializers
from .models import User, Patient, Therapist

class SignupSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    user_role = serializers.ChoiceField(choices=['admin', 'therapist', 'patient'], required=True)
    license_number = serializers.CharField(required=False, allow_blank=True)
    specialization = serializers.CharField(required=False, allow_blank=True)
    name = serializers.CharField(required=False, allow_blank=True)
    description = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        """
        Validaciones adicionales antes del registro.
        """
        user_role = data.get('user_role')

        if user_role == 'therapist':
            if not data.get('license_number'):
                raise serializers.ValidationError("El número de licencia es obligatorio para terapeutas.")
            if not data.get('specialization'):
                raise serializers.ValidationError("La especialización es obligatoria para terapeutas.")
        elif user_role == 'patient':
            if not data.get('name'):
                raise serializers.ValidationError("El nombre es obligatorio para pacientes.")

        return data


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        """
        Valida las credenciales del usuario.
        """
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            raise serializers.ValidationError("Se requieren email y contraseña.")

        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'phone', 'role', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']

class PatientSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Patient
        fields = ['id', 'user', 'name', 'description', 'first_therapy', 'last_therapy']
        read_only_fields = ['id']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create_user(**user_data, role='PATIENT')
        return Patient.objects.create(user=user, **validated_data)

class TherapistSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Therapist
        fields = ['id', 'user', 'license_number', 'specialization']
        read_only_fields = ['id']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create_user(**user_data, role='THERAPIST')
        return Therapist.objects.create(user=user, **validated_data)