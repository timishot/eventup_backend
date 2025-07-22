from rest_framework import serializers
from .models import Relationship
from useraccount.serializers import UserSerializer
from useraccount.models import User

class RelationshipSerializer(serializers.ModelSerializer):
    follower = UserSerializer(read_only=True)
    followee = UserSerializer(read_only=True)
    followee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
        source='followee'
    )

    class Meta:
        model = Relationship
        fields = ['id', 'follower', 'followee', 'followee_id', 'created_at']

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['follower'] = request.user
        return super().create(validated_data)

    def validate(self, data):
        follower = self.context['request'].user
        followee = data.get('followee')
        if follower == followee:
            raise serializers.ValidationError("Users cannot follow themselves.")
        return data