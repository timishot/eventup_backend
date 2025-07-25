from django.db.models.functions import Concat
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status

from .models import Order
from .serializers import OrderSerializer
from event.models import Event
from useraccount.models import User  # or get_user_model() if using custom user
from django.db.models import F, Value

@api_view(['POST'])
@permission_classes([AllowAny])
def create_order(request):
    try:
        data = request.data

        # Ensure required fields exist
        stripe_id = data.get('stripeId')
        total_amount = data.get('totalAmount')
        event_id = data.get('event_id')
        buyer_id = data.get('buyer_id')

        if not all([stripe_id, event_id, buyer_id]):
            return Response({"detail": "Missing required fields."}, status=status.HTTP_400_BAD_REQUEST)

        # Create the order
        order = Order.objects.create(
            stripe_id=stripe_id,
            total_amount=total_amount,
            event_id=event_id,
            buyer_id=buyer_id
        )

        serializer = OrderSerializer(order)
        print(serializer.data)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_user_orders(request):
    user = request.query_params.get('userId')
    limit = int(request.query_params.get('limit', 3))
    page = int(request.query_params.get('page', 1))

    orders = Order.objects.filter(buyer=user).order_by('-created_at')

    total_count = orders.count()
    start = (page - 1) * limit
    end = start + limit
    paginated_orders = orders[start:end]

    serializer = OrderSerializer(paginated_orders, many=True)
    print(serializer.data)
    return Response({
        'data': serializer.data,
        'totalPages': (total_count + limit - 1) // limit
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def get_orders_by_event(request):
    event_id = request.query_params.get('eventId')
    search_string = request.query_params.get('searchString', '')
    try:
        if not event_id:
            return Response({"detail": "Event ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        orders = Order.objects.filter(event_id=event_id).select_related('event', 'buyer').order_by('-created_at')

        if search_string:
            orders = orders.filter(
                buyer__name__icontains=search_string
            )

        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)