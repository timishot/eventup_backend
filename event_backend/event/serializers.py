# from rest_framework import serializers
#
# from .models import Event
#
# class EventSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Event
#         fields = '__all__'
#         read_only_fields = ('id', 'created_at', 'organizer')
#
#     def create(self, validated_data):
#         request = self.context.get('request')
#         user = request.user if request else None
#         validated_data['organizer'] = user
#         return super().create(validated_data)

from rest_framework import serializers
from .models import Event

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'
