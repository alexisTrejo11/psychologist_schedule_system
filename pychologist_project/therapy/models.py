from django.db import models
from django.forms import ValidationError
from django.utils import timezone

class TherapySession(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pendiente'),
        ('SCHEDULED', 'Agendada'),
        ('CANCELLED', 'Cancelada'),
        ('COMPLETED', 'Completada'),
        ('RESCHEDULED', 'Reagendada'),
    ]
    
    therapist = models.ForeignKey('users.Therapist', on_delete=models.CASCADE)  
    patients = models.ManyToManyField('users.Patient', through='TherapyParticipant')  
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING')
    notes = models.TextField(blank=True)
    payment = models.OneToOneField('payments.Payment', on_delete=models.SET_NULL, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    def clean(self):
        if self.end_time <= self.start_time:
            raise ValidationError('La hora de finalización debe ser posterior a la de inicio')
        
    def soft_delete(self):
        if self.deleted_at != None:
            raise ValidationError('La sesion ya fue borrada(soft)')
        self.deleted_at = timezone.now()


    def __str__(self):
        return f"Sesión {self.start_time.strftime('%Y-%m-%d %H:%M')}"

class TherapyParticipant(models.Model):
    therapy_session = models.ForeignKey(TherapySession, on_delete=models.CASCADE)
    patient = models.ForeignKey('users.Patient', on_delete=models.CASCADE) 
    attended = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('therapy_session', 'patient')
