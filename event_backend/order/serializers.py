from rest_framework import serializers
from .models import Order
from event.serializers import EventSerializer
from useraccount.serializers import UserSerializer
from event.models import Event
from useraccount.models import User


class OrderSerializer(serializers.ModelSerializer):
    event = EventSerializer(read_only=True)  # For GET
    buyer = UserSerializer(read_only=True)   # For GET

    event_id = serializers.PrimaryKeyRelatedField(  # For POST
        queryset=Event.objects.all(),
        source='event',
        write_only=True
    )
    buyer_id = serializers.PrimaryKeyRelatedField(  # For POST
        queryset=User.objects.all(),
        source='buyer',
        write_only=True
    )

    class Meta:
        model = Order
        fields = '__all__'

    def create(self, validated_data):
        return super().create(validated_data)
