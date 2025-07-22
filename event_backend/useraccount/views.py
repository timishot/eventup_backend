from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import User
from .serializers import UserSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated

from .utils import get_networking_suggestions


@api_view(['GET'])
@permission_classes([AllowAny])
def user_detail(request, user_id):
    user = get_object_or_404(User, id=user_id)
    serializer = UserSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    user = request.user
    serializer = UserSerializer(user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def networking_suggestions(request):
    suggestions = get_networking_suggestions(request.user, top_n=5)
    serialized_suggestions = [
        {**UserSerializer(user).data, 'similarity': score}
        for user, score in suggestions
    ]
    return Response({
        "data": serialized_suggestions,
        "meta": {"total": len(serialized_suggestions)}
    }, status=status.HTTP_200_OK)