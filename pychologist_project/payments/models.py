from django.db import models

class Payment(models.Model):
    PAYMENT_TYPES = [
        ('FREE', 'Gratis'),
        ('CASH', 'Efectivo'),
        ('TRANSFER', 'Transferencia'),
        ('CARD', 'Tarjeta'),
    ]
    
    patient = models.ForeignKey('patients.Patient', on_delete=models.CASCADE, null=True)  
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_type = models.CharField(max_length=10, choices=PAYMENT_TYPES)
    paid_at = models.DateTimeField(auto_now_add=True)
    receipt_number = models.CharField(max_length=50, unique=True, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Pago {self.receipt_number} - {self.amount}"


class StripeProduct(models.Model):
    name = models.CharField(max_length=100)
    stripe_product_id = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name