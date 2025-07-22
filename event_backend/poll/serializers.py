from rest_framework import serializers
from .models import Question, Choice, UserVote
from event.models import Event
from event.serializers import EventSerializer
from useraccount.serializers import UserSerializer
import logging

logger = logging.getLogger(__name__)

class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'text', 'votes']
        read_only_fields = ['id', 'votes']

class PollQuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)
    input_choices = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField(),
            allow_empty=False
        ),
        write_only=True,
        min_length=1,
        max_length=10,
        source='choices'
    )
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
        fields = ['id', 'text', 'event', 'event_uuid', 'is_active', 'created_at', 'updated_at', 'choices', 'input_choices', 'user']
        read_only_fields = ['id', 'event', 'is_active', 'created_at', 'updated_at', 'user', 'choices']

    def validate_input_choices(self, value):
        logger.info(f"Validating input_choices: {value}")
        if not value or len(value) < 1:
            raise serializers.ValidationError("At least one choice is required to create a poll")
        for choice in value:
            if not choice.get('text') or not choice['text'].strip():
                raise serializers.ValidationError("Each choice must have a non-empty 'text' field")
        return value

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            validated_data['user'] = request.user
            logger.info(f"Set user: {request.user.id}")
        else:
            raise serializers.ValidationError("Authenticated user required to create a poll")
        choices_data = validated_data.pop('choices', [])
        logger.info(f"Choices data: {choices_data}")
        question = Question.objects.create(**validated_data)
        logger.info(f"Created question: {question.id}")
        for choice_data in choices_data:
            logger.info(f"Creating choice: {choice_data}")
            Choice.objects.create(question=question, **choice_data)
        return question

class UserVoteSerializer(serializers.ModelSerializer):
    question_id = serializers.UUIDField(read_only=True)
    choice_id = serializers.UUIDField(read_only=True)

    class Meta:
        model = UserVote
        fields = ['question_id', 'choice_id']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['question_id'] = str(instance.choice.question_id)
        representation['choice_id'] = str(instance.choice_id)
        return representation