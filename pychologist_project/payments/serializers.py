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

    amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Amount of the payment. Must be greater than 0."
    )

    payment_type = serializers.ChoiceField(
        choices=Payment.PAYMENT_TYPES,
        help_text="Type of payment (e.g., CASH, CARD, TRANSFER)."
    )

    receipt_number = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Receipt number for the payment. Must be unique if provided."
    )

    def validate_payment_type(self, value):
        """
        Verifies that the payment type is valid.
        """
        valid_types = dict(Payment.PAYMENT_TYPES)
        if value not in valid_types:
            raise serializers.ValidationError(f"Invalid payment type. Valid options: {list(valid_types.keys())}")
        return value

    def validate_amount(self, value):
        """
        Verifies that the amount is greater than 0.
        """
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0")
        return value

    def validate_receipt_number(self, value):
        """
        Verifies that the receipt number is unique if provided.
        """
        if value and Payment.objects.filter(receipt_number=value).exists():
            raise serializers.ValidationError("Receipt number already exists")
        return value
    

class PaymentSearchSerializer(serializers.Serializer):
    """Serializer to validate search parameters."""
    amount_min = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        help_text="Minimum amount for filtering payments."
    )

    amount_max = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        help_text="Maximum amount for filtering payments."
    )

    payment_type = serializers.ChoiceField(
        choices=Payment.PAYMENT_TYPES,
        required=False,
        help_text="Filter payments by type (e.g., CASH, CARD, TRANSFER)."
    )

    receipt_number = serializers.CharField(
        required=False,
        help_text="Filter payments by receipt number."
    )

    paid_after = serializers.DateField(
        required=False,
        help_text="Filter payments paid after this date (YYYY-MM-DD)."
    )

    paid_before = serializers.DateField(
        required=False,
        help_text="Filter payments paid before this date (YYYY-MM-DD)."
    )