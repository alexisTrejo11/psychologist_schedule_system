from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from core.api_response.response import ApiResponse
from payments.serializers import PaymentSerializer
from ....application.therpist_payment_user_case import (
    GetTherapistPaymentsUseCase,
    GetTherapistPaymentUseCase,
    CreateTherapistPaymentUseCase,
    UpdateTherapistPaymentUseCase,
    DeleteTherapistPaymentUseCase,
)
from ..infrastructure.repositories import DjangoPaymentRepository
from payments.services import PaymentService

class TherapistPaymentView(APIView):
    """
    API endpoints for managing therapist payments.
    """
    permission_classes = [IsAuthenticated]
    payment_repository = DjangoPaymentRepository()
    payment_service = PaymentService()

    @extend_schema(
        summary="List Therapist Payments",
        description="Retrieves a list of all payments associated with the authenticated therapist.",
        responses={
            200: PaymentSerializer(many=True),
            401: OpenApiTypes.OBJECT,
            500: OpenApiTypes.OBJECT,
        },
    )
    def get(self, request):
        """
        Retrieve a list of all payments for the authenticated therapist.
        """
        user = request.user

        use_case = GetTherapistPaymentsUseCase(self.payment_repository)
        payments = use_case.execute(user)

        formatted_response = ApiResponse.format_response(
            data=PaymentSerializer(payments, many=True).data,
            success=True,
            message="Therapist payments retrieved successfully."
        )
        return Response(formatted_response, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Create a New Payment",
        description="Creates a new payment for the authenticated therapist.",
        request=PaymentSerializer,
        responses={
            201: PaymentSerializer,
            400: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
            500: OpenApiTypes.OBJECT,
        },
    )
    def post(self, request):
        """
        Create a new payment for the authenticated therapist.
        """
        serializer = PaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        use_case = CreateTherapistPaymentUseCase(self.payment_service)
        payment = use_case.execute(serializer.validated_data)

        formatted_response = ApiResponse.format_response(
            data=PaymentSerializer(payment).data,
            success=True,
            message="Payment created successfully."
        )
        return Response(formatted_response, status=status.HTTP_201_CREATED)


class TherapistPaymentDetailView(APIView):
    """
    API endpoints for managing individual therapist payments.
    """
    permission_classes = [IsAuthenticated]
    payment_repository = DjangoPaymentRepository()
    payment_service = PaymentService()

    @extend_schema(
        summary="Retrieve a Specific Payment",
        description="Retrieves a specific payment associated with the authenticated therapist.",
        responses={
            200: PaymentSerializer,
            401: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
            500: OpenApiTypes.OBJECT,
        },
        parameters=[
            OpenApiParameter(
                name='payment_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='ID of the payment to retrieve',
                required=True,
            ),
        ],
    )
    def get(self, request, payment_id):
        """
        Retrieve a specific payment for the authenticated therapist.
        """
        user = request.user

        use_case = GetTherapistPaymentUseCase(self.payment_repository)
        payment = use_case.execute(user, payment_id)

        if not payment:
            formatted_response = ApiResponse.format_response(
                data=None,
                success=False,
                message="Payment not found."
            )
            return Response(formatted_response, status=status.HTTP_404_NOT_FOUND)

        formatted_response = ApiResponse.format_response(
            data=PaymentSerializer(payment).data,
            success=True,
            message="Payment retrieved successfully."
        )
        return Response(formatted_response, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Update an Existing Payment",
        description="Updates an existing payment for the authenticated therapist.",
        request=PaymentSerializer,
        responses={
            200: PaymentSerializer,
            400: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
            500: OpenApiTypes.OBJECT,
        },
        parameters=[
            OpenApiParameter(
                name='payment_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='ID of the payment to update',
                required=True,
            ),
        ],
    )
    def patch(self, request, payment_id):
        """
        Update an existing payment for the authenticated therapist.
        """
        user = request.user

        serializer = PaymentSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        use_case = UpdateTherapistPaymentUseCase(self.payment_service, self.payment_repository)
        payment = use_case.execute(payment_id, user, serializer.validated_data)

        if not payment:
            formatted_response = ApiResponse.format_response(
                data=None,
                success=False,
                message="Payment not found."
            )
            return Response(formatted_response, status=status.HTTP_404_NOT_FOUND)

        formatted_response = ApiResponse.format_response(
            data=PaymentSerializer(payment).data,
            success=True,
            message="Payment updated successfully."
        )
        return Response(formatted_response, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Delete a Payment",
        description="Deletes a payment for the authenticated therapist.",
        responses={
            204: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
            500: OpenApiTypes.OBJECT,
        },
        parameters=[
            OpenApiParameter(
                name='payment_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='ID of the payment to delete',
                required=True,
            ),
        ],
    )
    def delete(self, request, payment_id):
        """
        Delete a payment for the authenticated therapist.
        """
        user = request.user

        use_case = DeleteTherapistPaymentUseCase(self.payment_service)
        use_case.execute(user, payment_id)

        formatted_response = ApiResponse.format_response(
            data=None,
            success=True,
            message="Payment deleted successfully."
        )
        return Response(formatted_response, status=status.HTTP_204_NO_CONTENT)