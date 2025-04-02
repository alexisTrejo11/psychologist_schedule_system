from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from .serializers import PaymentSerializer, PaymentSearchSerializer
from .services import PaymentService

class PaymentListCreateView(APIView):
    """
    View to list and create payments.
    """
    @extend_schema(
        summary="List payments",
        description="Lists payments with dynamic filters. If no filters are provided, all payments are returned.",
        responses={
            200: PaymentSerializer(many=True),
            400: OpenApiTypes.OBJECT,
        },
        parameters=[
            OpenApiParameter(
                name='amount_min',
                type=OpenApiTypes.DECIMAL,
                location=OpenApiParameter.QUERY,
                description='Minimum amount for filtering payments.',
            ),
            OpenApiParameter(
                name='amount_max',
                type=OpenApiTypes.DECIMAL,
                location=OpenApiParameter.QUERY,
                description='Maximum amount for filtering payments.',
            ),
            OpenApiParameter(
                name='payment_type',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter payments by type (e.g., CASH, CARD, TRANSFER).',
            ),
            OpenApiParameter(
                name='receipt_number',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter payments by receipt number.',
            ),
            OpenApiParameter(
                name='paid_after',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description='Filter payments paid after this date (YYYY-MM-DD).',
            ),
            OpenApiParameter(
                name='paid_before',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description='Filter payments paid before this date (YYYY-MM-DD).',
            ),
        ],
    )
    def get(self, request):
        """
        Lists payments with dynamic filters.
        """
        search_serializer = PaymentSearchSerializer(data=request.query_params)
        if not search_serializer.is_valid():
            return Response(search_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        payments = PaymentService.search_payments(**search_serializer.validated_data)
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Create a new payment",
        description="Creates a new payment record.",
        request=PaymentSerializer,
        responses={
            201: PaymentSerializer,
            400: OpenApiTypes.OBJECT,
        },
    )
    def post(self, request):
        """
        Creates a new payment.
        """
        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid():
            try:
                payment = PaymentService.create_payment(
                    amount=serializer.validated_data['amount'],
                    payment_type=serializer.validated_data['payment_type'],
                    receipt_number=serializer.validated_data.get('receipt_number'),
                )
                return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)
            except ValueError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PaymentRetrieveUpdateDestroyView(APIView):
    """
    View to retrieve, update, and delete a payment.
    """

    @extend_schema(
        summary="Retrieve a payment",
        description="Retrieves a single payment by ID.",
        responses={
            200: PaymentSerializer,
            404: OpenApiTypes.OBJECT,
        },
        parameters=[
            OpenApiParameter(
                name='payment_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='ID of the payment to retrieve.',
                required=True,
            ),
        ],
    )
    def get(self, request, payment_id):
        """
        Retrieves a payment by ID.
        """
        try:
            payment = PaymentService.get_payment_by_id(payment_id)
            serializer = PaymentSerializer(payment)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        summary="Update a payment",
        description="Updates an existing payment record.",
        request=PaymentSerializer,
        responses={
            200: PaymentSerializer,
            400: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
        parameters=[
            OpenApiParameter(
                name='payment_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='ID of the payment to update.',
                required=True,
            ),
        ],
    )
    def put(self, request, payment_id):
        """
        Updates an existing payment.
        """
        serializer = PaymentSerializer(data=request.data, partial=True)
        if serializer.is_valid():
            try:
                payment = PaymentService.update_payment(
                    payment_id=payment_id,
                    **serializer.validated_data,
                )
                return Response(PaymentSerializer(payment).data, status=status.HTTP_200_OK)
            except ValueError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Delete a payment",
        description="Deletes a payment.",
        responses={
            204: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
        parameters=[
            OpenApiParameter(
                name='payment_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='ID of the payment to delete.',
                required=True,
            ),
        ],
    )
    def delete(self, request, payment_id):
        """
        Deletes a payment.
        """
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