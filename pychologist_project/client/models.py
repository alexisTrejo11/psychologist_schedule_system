from django.db import models
from django.forms import ValidationError
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from phonenumber_field.modelfields import PhoneNumberField

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El email es obligatorio')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('role', 'ADMIN')
        extra_fields['is_staff'] = True
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser):
    ROLE_CHOICES = [
        ('THERAPIST', 'Terapeuta'),
        ('PATIENT', 'Paciente'),
        ('ADMIN', 'Administrador'),
    ]
    
    email = models.EmailField(unique=True)
    phone = PhoneNumberField(blank=True)
    role = models.CharField(max_length=15, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    first_therapy = models.DateTimeField(null=True, blank=True)
    last_therapy = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Therapist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='therapist_profile')
    license_number = models.CharField(max_length=50, unique=True)
    specialization = models.CharField(max_length=100)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Dr(a). {self.user.email}"

class TherapySession(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pendiente'),
        ('SCHEDULED', 'Agendada'),
        ('CANCELLED', 'Cancelada'),
        ('COMPLETED', 'Completada'),
        ('RESCHEDULED', 'Reagendada'),
    ]
    
    therapist = models.ForeignKey(Therapist, on_delete=models.CASCADE)
    patients = models.ManyToManyField(Patient, through='TherapyParticipant')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING')
    notes = models.TextField(blank=True)
    payment = models.OneToOneField('Payment', on_delete=models.SET_NULL, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    def clean(self):
        if self.end_time <= self.start_time:
            raise ValidationError('La hora de finalización debe ser posterior a la de inicio')

    def __str__(self):
        return f"Sesión {self.start_time.strftime('%Y-%m-%d %H:%M')}"

class TherapyParticipant(models.Model):
    therapy_session = models.ForeignKey(TherapySession, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    attended = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('therapy_session', 'patient')


class Payment(models.Model):
    PAYMENT_TYPES = [
        ('FREE', 'Gratis'),
        ('CASH', 'Efectivo'),
        ('TRANSFER', 'Transferencia'),
        ('CARD', 'Tarjeta'),
    ]
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_type = models.CharField(max_length=10, choices=PAYMENT_TYPES)
    paid_at = models.DateTimeField(auto_now_add=True)
    receipt_number = models.CharField(max_length=50, unique=True, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Pago {self.receipt_number} - {self.amount}"