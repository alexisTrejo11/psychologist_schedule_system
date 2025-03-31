from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services import PaymentService
from .serializers import PaymentSerializer, PaymentSearchSerializer

class PaymentListCreateView(APIView):
    def get(self, request):
        """
        Lista pagos con filtros dinámicos.
        Si no hay filtros, retorna todos los pagos.
        """
        search_serializer = PaymentSearchSerializer(data=request.query_params)
        if not search_serializer.is_valid():
            return Response(search_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        payments = PaymentService.search_payments(**search_serializer.validated_data)
        
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Crea un nuevo pago.
        """
        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid():
            try:
                payment = PaymentService.create_payment(
                    amount=serializer.validated_data['amount'],
                    payment_type=serializer.validated_data['payment_type'],
                    receipt_number=serializer.validated_data.get('receipt_number')
                )
                return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)
            except ValueError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PaymentRetrieveUpdateDestroyView(APIView):
    def get(self, request, payment_id):
        """Obtiene un pago por ID."""
        try:
            payment = PaymentService.get_payment_by_id(payment_id)
            serializer = PaymentSerializer(payment)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, payment_id):
        """Actualiza un pago existente."""
        serializer = PaymentSerializer(data=request.data, partial=True)
        if serializer.is_valid():
            try:
                payment = PaymentService.update_payment(
                    payment_id=payment_id,
                    **serializer.validated_data
                )
                return Response(PaymentSerializer(payment).data, status=status.HTTP_200_OK)
            except ValueError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, payment_id):
        """Elimina un pago."""
        try:
            PaymentService.delete_payment(payment_id)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        


from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import stripe
from .models import Payment
from django.conf import settings


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)

    # Manejar eventos
    if event["type"] == "payment_intent.succeeded":
        payment_intent = event["data"]["object"]
        # Actualiza el pago en tu base de datos
        Payment.objects.filter(
            stripe_payment_intent_id=payment_intent.id
        ).update(status="COMPLETED")

    return HttpResponse(status=200)