from rest_framework import serializers
from .models import Category

class CategorySerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)  # Explicitly handle UUID i
    class Meta:
        model = Category
        fields = ['id', 'name']
