from rest_framework import serializers
from qns.models import Question, Answer
from event.models import Event
from event.serializers import EventSerializer
from useraccount.serializers import UserSerializer

class AnswerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    question = serializers.UUIDField(read_only=True, source='question.id')
    event = EventSerializer(read_only=True)
    event_uuid = serializers.PrimaryKeyRelatedField(
        queryset=Event.objects.all(),
        write_only=True,
        source='event'
    )
    id = serializers.UUIDField(read_only=True)

    class Meta:
        model = Answer
        fields = ['id', 'text', 'user', 'question', 'event', 'event_uuid', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'question', 'event', 'created_at', 'updated_at']

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            validated_data['user'] = request.user
        return super().create(validated_data)

class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)
    event = EventSerializer(read_only=True)
    event_uuid = serializers.PrimaryKeyRelatedField(
        queryset=Event.objects.all(),
        write_only=True,
        source='event'
    )
    id = serializers.UUIDField(read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'user', 'event', 'event_uuid', 'is_answered', 'answers', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'event', 'is_answered', 'answers', 'created_at', 'updated_at']

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            validated_data['user'] = request.user
        return super().create(validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Ensure UUIDs are strings
        representation['id'] = str(representation['id'])
        if 'event' in representation and representation['event'] and 'id' in representation['event']:
            representation['event']['id'] = str(representation['event']['id'])
        if 'user' in representation and representation['user'] and 'id' in representation['user']:
            representation['user']['id'] = str(representation['user']['id'])
        for answer in representation.get('answers', []):
            answer['id'] = str(answer['id'])
            answer['question'] = str(answer['question'])
            if 'user' in answer and answer['user'] and 'id' in answer['user']:
                answer['user']['id'] = str(answer['user']['id'])
            if 'event' in answer and answer['event'] and 'id' in answer['event']:
                answer['event']['id'] = str(answer['event']['id'])
        return representation





