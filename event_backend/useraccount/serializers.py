# users/serializers.py
from rest_framework import serializers
from .models import User  # or from django.contrib.auth import get_user_model

class UserSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)  # Assuming User has a UUID field
    class Meta:
        model = User
        fields = ["id", "username", "email", "interests", "profession", "background"]  # or whatever fields you need
