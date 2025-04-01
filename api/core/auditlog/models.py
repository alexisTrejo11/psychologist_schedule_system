from django.db import models
from users.models import User

class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('CREATE', 'Create'),
        ('READ', 'Read'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    resource = models.CharField(max_length=255) 
    data = models.JSONField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    status_code = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.action} on {self.resource} by {self.user} at {self.timestamp}"