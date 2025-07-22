from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from .models import Relationship
from .serializers import RelationshipSerializer
from useraccount.models import User
import logging

logger = logging.getLogger(__name__)

@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def follow_unfollow(request, user_id):
    logger.debug(f"Received follow/unfollow request for user_id: {user_id}")
    logger.debug(f"Request data: {request.data}")
    followee = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        if request.user == followee:
            return Response({'detail': 'You cannot follow yourself.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if already following
        if Relationship.objects.filter(follower=request.user, followee=followee).exists():
            return Response({'detail': 'You are already following this user.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = RelationshipSerializer(data={'followee_id': str(user_id)}, context={'request': request})
        if serializer.is_valid():
            serializer.save(follower=request.user, followee=followee)
            logger.debug(f"Created relationship: {serializer.data}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.error(f"Serializer errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        relationship = get_object_or_404(Relationship, follower=request.user, followee=followee)
        relationship.delete()
        return Response({'detail': 'Unfollowed successfully.'}, status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@permission_classes([AllowAny])
def followers_list(request, user_id):
    user = get_object_or_404(User, id=user_id)
    page = int(request.GET.get('page', 1))
    limit = int(request.GET.get('limit', 10))
    skip = (page - 1) * limit

    relationships = Relationship.objects.filter(followee=user).order_by('-created_at')[skip:skip + limit]
    total = Relationship.objects.filter(followee=user).count()

    serializer = RelationshipSerializer(relationships, many=True)
    return Response({
        "data": serializer.data,
        "meta": {
            "total": total,
            "totalPages": (total + limit - 1) // limit,
        }
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([AllowAny])
def following_list(request, user_id):
    user = get_object_or_404(User, id=user_id)
    page = int(request.GET.get('page', 1))
    limit = int(request.GET.get('limit', 10))
    skip = (page - 1) * limit

    relationships = Relationship.objects.filter(follower=user).order_by('-created_at')[skip:skip + limit]
    total = Relationship.objects.filter(follower=user).count()

    serializer = RelationshipSerializer(relationships, many=True)
    logger.debug(f"Following fetched: {len(serializer.data)} for user_id={user_id}")
    return Response({
        "data": serializer.data,
        "meta": {
            "total": total,
            "totalPages": (total + limit - 1) // limit,
        }
    }, status=status.HTTP_200_OK)