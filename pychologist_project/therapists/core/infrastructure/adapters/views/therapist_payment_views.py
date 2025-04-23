from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from core.api_response.response import DjangoResponseWrapper as ResponseWrapper
from core.pagination import page_helper
from payments.core.infrastructure.api.serializers.serializers import PaymentSerializer
from payments.core.infrastructure.repository.django_payment_repository import DjangoPaymentRepository
from payments.core.app.use_cases.payment_use_cases import CreatePaymentUseCase, UpdatePaymentUseCase, SoftDeletePaymentUseCase
from therapists.core.application.therapist_use_case import GetTherapistByUserUseCase
from ....application.therpist_payment_user_case import (GetTherapistPaymentsListUseCase,GetTherapistPaymentUseCase,)
from ....infrastructure.repositories.django_therapist_repository import DjangoTherapistRepository
from payments.core.infrastructure.api.serializers.serializers import PaymentSerializer, PaymentOutputSerializer
from core.pagination.serializers.paginations_serializers import PaginatedResponseSerializer
from dataclasses import asdict


class TherapistPaymentView(APIView):
    def __init__(self, **kwargs):
        payment_repository = DjangoPaymentRepository()
        therapist_repository = DjangoTherapistRepository()
        self.get_therapist_by_user_use_case = GetTherapistByUserUseCase(therapist_repository)
        self.get_therapist_payment_use_case = GetTherapistPaymentUseCase(payment_repository)
        self.get_therapist_payment_list_use_case = GetTherapistPaymentsListUseCase(payment_repository)
        self.create_payment_use_case = CreatePaymentUseCase(payment_repository)
        self.update_payment_use_case = UpdatePaymentUseCase(payment_repository)
        self.delete_payment_use_case = SoftDeletePaymentUseCase(payment_repository)
        super().__init__(**kwargs)

    """
    API endpoints for managing therapist payments.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="List Therapist Payments",
        description="Retrieves a list of all payments associated with the authenticated therapist.",
        responses={
            200: PaymentSerializer(many=True),
            401: OpenApiTypes.OBJECT,
            500: OpenApiTypes.OBJECT,
        },
    )
    def list(self, request):
        """
        Retrieve a list of all payments for the authenticated therapist.
        """
        user = request.user
        pagination_input = page_helper.get_pagination_data(request)

        therapist = self.get_therapist_by_user_use_case.execute(user)

        paginated_payments = self.get_therapist_payment_list_use_case.execute(therapist, pagination_input)

        paginated_payments.items =[PaymentOutputSerializer(payment).data for payment in paginated_payments.items]
        paginated_response_data = serialize_pagination_response(paginated_payments, PaymentOutputSerializer)
        
        return ResponseWrapper.found(data=paginated_response_data, entity='Therapist Payments')

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

        payment = self.create_payment_use_case.execute(**serializer.validated_data)

        return ResponseWrapper.created(PaymentOutputSerializer(payment).data, 'Payment')


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
        therapist = self.get_therapist_by_user_use_case.execute(user)

        payment = self.get_therapist_payment_use_case.execute(therapist, payment_id)

        return ResponseWrapper.found(
            data=PaymentOutputSerializer(payment).data, 
            entity='Therapist Payment', 
            param='payment ID',
            value=payment_id,
        )

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

        payment = self.update_payment_use_case.execute(payment_id, user, serializer.validated_data)

        return ResponseWrapper.updated(PaymentSerializer(payment).data)
        
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

        self.delete_payment_use_case.execute(user, payment_id)

        return ResponseWrapper.no_content("Payment deleted successfully.")
    

def serialize_pagination_response(self, paginated_payments, serializer):
    paginated_response_serializer = PaginatedResponseSerializer(
            data={
                "items": paginated_payments.items,
                "metadata": asdict(paginated_payments.metadata),
            },
            item_serializer=serializer,  
        )

    paginated_response_serializer.is_valid(raise_exception=True)

    return paginated_response_serializer.data