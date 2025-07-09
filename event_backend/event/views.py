from rest_framework.decorators import api_view, permission_classes, authentication_classes
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db.models import Q

from .models import Event
from .serializers import EventSerializer

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])  # or [AllowAny] if public
def event_list_create(request):
    if request.method == 'GET':
        query = request.GET.get('query', '')
        category = request.GET.get('category', '')
        limit = int(request.GET.get('limit', 6))
        skip = int(request.GET.get('skip', 0))

        filters = Q()

        if query:
            filters &= Q(title__icontains=query)

        if category:
            filters &= Q(category__name__iexact=category)

        events = Event.objects.filter(filters).order_by('-created_at')[skip:skip + limit]
        total = Event.objects.filter(filters).count()

        serializer = EventSerializer(events, many=True)
        return Response({
            "data": serializer.data,
            "meta": {
                "total": total,
                "totalPages": (total + limit - 1) // limit,
            }
        })

    if request.method == 'POST':
        serializer = EventSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            print(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'DELETE'])
@permission_classes([IsAuthenticated])  # Only authenticated users can delete
def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if request.method == 'GET':
        serializer = EventSerializer(event)
        return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == 'DELETE':
        if request.user != event.organizer:
            return Response({'detail': 'You are not authorized to delete this event.'}, status=status.HTTP_403_FORBIDDEN)

        event.delete()
        return Response({'detail': 'Event deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
