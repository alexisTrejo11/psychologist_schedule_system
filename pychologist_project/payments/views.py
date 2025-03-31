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