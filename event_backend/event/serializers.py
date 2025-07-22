from rest_framework import serializers
from .models import Event
from category.serializers import CategorySerializer
from category.models import Category
from useraccount.serializers import UserSerializer


class EventSerializer(serializers.ModelSerializer):
    organizer = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)  # for GET
    category_uuid = serializers.PrimaryKeyRelatedField(  # for POST
        queryset=Category.objects.all(),
        write_only=True,
        source='category'
    )
    id = serializers.UUIDField(read_only=True)  # Assuming Event has a UUID field


    class Meta:
        model = Event
        fields = '__all__'
        organizer = UserSerializer(read_only=True)
        extra_kwargs = {
            'price': {'required': False, 'allow_null': True, 'allow_blank': True}
        }

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['organizer'] = request.user
        return super().create(validated_data)

