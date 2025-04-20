from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
import logging
from core.pagination.serializers.paginations_serializers import PaginatedResponseSerializer
from core.api_response.response import ApiResponse
from ..serializers.serializers import PaymentSerializer, PaymentSearchSerializer
from ...repository.django_payment_repository import DjangoPaymentRepository
from ....app.use_cases.payment_use_cases import (
    GetPaymentUseCase, 
    CreatePaymentUseCase, 
    UpdatePaymentUseCase,
    SearchPaymentsUseCase,
    SoftDeletePaymentUseCase
)

log = logging.getLogger('audit_logger')

class PaymentApiView(APIView):
    def __init__(self, **kwargs):
        self.payment_repostiory = DjangoPaymentRepository()
        self.get_payment_use_case = GetPaymentUseCase(payment_repository=self.payment_repostiory)
        self.search_payment_use_case = SearchPaymentsUseCase(payment_repository=self.payment_repostiory)
        self.create_payment_use_case = CreatePaymentUseCase(payment_repository=self.payment_repostiory)
        self.update_payment_use_case = UpdatePaymentUseCase(payment_repository=self.payment_repostiory)
        self.soft_delete_payment_use_case = SoftDeletePaymentUseCase(payment_repository=self.payment_repostiory)
        super().__init__(**kwargs)

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
    def search(self, request):

        """
        Search payments with dynamic filters.
        """
        user = request.user if request.user.is_authenticated else None
        ip_address = request.META.get('REMOTE_ADDR')

        log.info(f"SEARCH PAYMENTS REQUEST | User: {user}, IP: {ip_address}, Query Params: ")

        search_serializer = PaymentSearchSerializer(data=request.query_params)
        search_serializer.is_valid(raise_exception=True)

        pagination_response = self.search_payment_use_case.execute(**search_serializer.validated_data)
        
        log.info(f"SEARCH PAYMENTS SUCCESS | Items Retrieved: {len(pagination_response.items)}")

        paginated_response_data = PaginatedResponseSerializer({
                "items": pagination_response.items,
                "metadata": pagination_response.metadata,
            }).data
        
        response = ApiResponse.format_response(
                data=paginated_response_data,
                success=True,
                message="Payments Successfully Retrieved",
            )
        
        return Response(response, status=status.HTTP_200_OK)

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
        user = request.user if request.user.is_authenticated else None
        ip_address = request.META.get('REMOTE_ADDR')

        log.info(f"CREATE PAYMENT REQUEST | User: {user}, IP: {ip_address}, Data: {request.data}")

        serializer = PaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        payment = self.create_payment_use_case.execute(**serializer.validated_data)

        log.info(f"CREATE PAYMENT SUCCESS | Payment ID: {payment.id}")

        response = ApiResponse.format_response(
                        data=PaymentSerializer(payment).data,
                        success=True,
                        message="Payments Successfully Retrieved",
                    )
        
        return Response(response, status=status.HTTP_201_CREATED)


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
    def retrieve(self, request, payment_id):
        user = request.user if request.user.is_authenticated else None
        ip_address = request.META.get('REMOTE_ADDR')

        log.info(f"RETRIEVE PAYMENT REQUEST | User: {user}, IP: {ip_address}, Payment ID: {payment_id}")

        payment = self.get_payment_use_case.execute(payment_id)
        
        log.info(f"RETRIEVE PAYMENT SUCCESS | Payment ID: {payment.id}")

        response = ApiResponse.format_response(
                data=PaymentSerializer(payment).data,
                success=True,
                message="Payments Successfully Retrieved",
            )

        return Response(response, status=status.HTTP_200_OK)

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
        user = request.user if request.user.is_authenticated else None
        ip_address = request.META.get('REMOTE_ADDR')

        log.info(f"UPDATE PAYMENT REQUEST | User: {user}, IP: {ip_address}, Payment ID: {payment_id}, Data: {request.data}")

        serializer = PaymentSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_expection=True)

        payment_updated = self.update_payment_use_case.execute(payment_id, **serializer.validated_data)

        log.info(f"UPDATE PAYMENT SUCCESS | Payment ID: {payment_updated.id}")

        response = ApiResponse.format_response(
            data=PaymentSerializer(payment_updated).data,
            success=True,
            message="Payment Succesfully Updated",
        )

        return Response(data=response, status=status.HTTP_200_OK)


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
        user = request.user if request.user.is_authenticated else None
        ip_address = request.META.get('REMOTE_ADDR')

        log.info(f"DELETE PAYMENT REQUEST | User: {user}, IP: {ip_address}, Payment ID: {payment_id}")

        self.soft_delete_payment_use_case.execute(payment_id)

        log.info(f"DELETE PAYMENT SUCCESS | Payment ID: {payment_id}")

        return Response(status=status.HTTP_204_NO_CONTENT)


