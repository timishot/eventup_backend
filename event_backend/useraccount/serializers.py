# users/serializers.py
from rest_framework import serializers
from .models import User  # or from django.contrib.auth import get_user_model

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]  # or whatever fields you need
