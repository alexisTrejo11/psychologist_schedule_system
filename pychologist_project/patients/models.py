from django.db import models
from django.utils import timezone

class Patient(models.Model):
    user = models.OneToOneField('users.User', on_delete=models.CASCADE, related_name='patient_profile', null=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    first_therapy = models.DateTimeField(null=True, blank=True)
    last_therapy = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def set_as_deleted(self):
        if self.deleted_at != None:
            raise ValueError("Patient Already Deleted")
        
        self.deleted_at = timezone.now()
    

    def set_as_inactive(self):
        if self.is_active is True:
            raise ValueError("Patient Is Already Inactive")
        
        self.is_active = True
        self.updated_at = timezone.now()

    def __str__(self):
        return self.name



