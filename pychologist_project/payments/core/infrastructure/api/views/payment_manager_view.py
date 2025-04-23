from rest_framework.viewsets import ViewSet
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from dataclasses import asdict
import logging
from core.pagination.page_helper import get_pagination_data
from core.pagination.serializers.paginations_serializers import PaginatedResponseSerializer
from core.api_response.response import DjangoResponseWrapper as ResponseWrapper
from ..serializers.serializers import PaymentSerializer, PaymentSearchSerializer, PaymentOutputSerializer
from ...repository.django_payment_repository import DjangoPaymentRepository
from ....app.use_cases.payment_use_cases import (
    GetPaymentUseCase, 
    CreatePaymentUseCase, 
    UpdatePaymentUseCase,
    SearchPaymentsUseCase,
    SoftDeletePaymentUseCase
)

log = logging.getLogger('audit_logger')

class PaymentViewSet(ViewSet):
    # Add Permisions
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
    def list(self, request):
        user = request.user
        ip_address = request.META.get('REMOTE_ADDR')

        log.info(f"SEARCH PAYMENTS REQUEST | User: {user}, IP: {ip_address}, Query Params: ")

        search_serializer = PaymentSearchSerializer(data=request.query_params)
        search_serializer.is_valid(raise_exception=True)
        
        page_input = get_pagination_data(request)

        pagination_response = self.search_payment_use_case.execute(search_serializer.data, page_input=page_input)
        
        log.info(f"SEARCH PAYMENTS SUCCESS | Items Retrieved: {len(pagination_response.items)}")

        paginated_response_serializer = PaginatedResponseSerializer(
            data={
                "items": [PaymentOutputSerializer(payment).data for payment in pagination_response.items],
                "metadata": asdict(pagination_response.metadata),
            },
            item_serializer=PaymentOutputSerializer,  
        )
        paginated_response_serializer.is_valid(raise_exception=True)
        
        return ResponseWrapper.found(data=paginated_response_serializer.data, entity='Payments')
        

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
    def retrieve(self, request, pk):
        payment_id = pk 
        user = request.user if request.user.is_authenticated else None
        ip_address = request.META.get('REMOTE_ADDR')

        log.info(f"RETRIEVE PAYMENT REQUEST | User: {user}, IP: {ip_address}, Payment ID: {payment_id}")

        payment = self.get_payment_use_case.execute(payment_id)

        log.info(f"RETRIEVE PAYMENT SUCCESS | Payment ID: {payment.id}")

        from rest_framework.response import Response

        return ResponseWrapper.found(
            data=PaymentSerializer(payment).data,
            entity='Payment',
            param='ID',
            value=payment_id
        )

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

        return ResponseWrapper.created(data=PaymentSerializer(payment).data, entity='Payment')