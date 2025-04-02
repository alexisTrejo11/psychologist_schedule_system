from django.db import models

class Therapist(models.Model):
    user = models.OneToOneField('users.User', on_delete=models.CASCADE, related_name='therapist_profile', null=True)
    name = models.CharField(max_length=100, default='')
    license_number = models.CharField(max_length=50, unique=True)
    specialization = models.CharField(max_length=100)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Dr(a). {self.name}"
