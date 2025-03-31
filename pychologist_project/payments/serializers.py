from rest_framework import serializers
from .models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id',
            'amount',
            'payment_type',
            'paid_at',
            'receipt_number',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'paid_at', 'created_at', 'updated_at']

    def validate_payment_type(self, value):
        """Verifica que el tipo de pago sea válido."""
        valid_types = dict(Payment.PAYMENT_TYPES)
        if value not in valid_types:
            raise serializers.ValidationError(f"Tipo de pago inválido. Opciones válidas: {list(valid_types.keys())}")
        return value

    def validate_amount(self, value):
        """Verifica que el monto sea mayor a 0."""
        if value <= 0:
            raise serializers.ValidationError("El monto debe ser mayor a 0")
        return value

    def validate_receipt_number(self, value):
        """Verifica que el número de recibo sea único si se proporciona."""
        if value and Payment.objects.filter(receipt_number=value).exists():
            raise serializers.ValidationError("El número de recibo ya existe")
        return value

class PaymentSearchSerializer(serializers.Serializer):
    """Serializador para validar parámetros de búsqueda."""
    amount_min = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    amount_max = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    payment_type = serializers.ChoiceField(choices=Payment.PAYMENT_TYPES, required=False)
    receipt_number = serializers.CharField(required=False)
    paid_after = serializers.DateField(required=False)
    paid_before = serializers.DateField(required=False)