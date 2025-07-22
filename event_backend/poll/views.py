from rest_framework import serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from .models import Question, Choice, UserVote
from .serializers import PollQuestionSerializer, UserVoteSerializer
from event.models import Event
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import logging

logger = logging.getLogger(__name__)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def poll_list_create(request, event_uuid):
    try:
        event = Event.objects.get(id=event_uuid)
    except ObjectDoesNotExist:
        logger.error(f"Event {event_uuid} does not exist")
        return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        questions = Question.objects.filter(event=event, is_active=True).order_by('-created_at')
        serializer = PollQuestionSerializer(questions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        if not request.user.is_authenticated:
            return Response({'detail': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        if request.user != event.organizer:
            return Response({'detail': 'Only the event organizer can create polls'}, status=status.HTTP_403_FORBIDDEN)
        data = request.data.copy()
        data['event_uuid'] = str(event_uuid)
        serializer = PollQuestionSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            question = serializer.save()
            logger.info(f"Poll created for event {event_uuid}: {question.id}")
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"event_{event_uuid}",
                {
                    'type': 'poll_update',
                    'poll': serializer.data
                }
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.error(f"Poll creation failed for event {event_uuid}: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def poll_vote(request, question_id):
    try:
        question = Question.objects.get(id=question_id)
    except ObjectDoesNotExist:
        logger.error(f"Question {question_id} does not exist")
        return Response({'detail': 'Question not found'}, status=status.HTTP_404_NOT_FOUND)

    choice_id = request.data.get('choice_id')
    try:
        choice = Choice.objects.get(id=choice_id, question=question)
    except ObjectDoesNotExist:
        logger.error(f"Choice {choice_id} does not exist for question {question_id}")
        return Response({'detail': 'Choice not found'}, status=status.HTTP_404_NOT_FOUND)

    from django.db import transaction
    with transaction.atomic():
        existing_vote = UserVote.objects.filter(user=request.user, choice__question=question).select_related('choice').first()
        if existing_vote:
            if existing_vote.choice_id == choice.id:
                logger.warning(f"User {request.user.id} already selected choice {choice_id} for question {question_id}")
                return Response({'detail': 'This choice is already selected'}, status=status.HTTP_400_BAD_REQUEST)
            # Update vote: decrement old choice, increment new choice
            old_choice = existing_vote.choice
            old_choice.votes -= 1
            old_choice.save()
            existing_vote.choice = choice
            existing_vote.created_at = timezone.now()
            existing_vote.save()
            choice.votes += 1
            choice.save()
            logger.info(f"Updated vote for user {request.user.id} from choice {old_choice.id} to {choice_id} for question {question_id}")
        else:
            # Create new vote
            UserVote.objects.create(user=request.user, choice=choice)
            choice.votes += 1
            choice.save()
            logger.info(f"Vote recorded for user {request.user.id} on choice {choice_id} for question {question_id}")

    serializer = PollQuestionSerializer(question)
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"event_{question.event_id}",
        {
            'type': 'poll_update',
            'poll': serializer.data
        }
    )
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_votes(request):
    try:
        votes = UserVote.objects.filter(user=request.user).select_related('choice__question')
        serializer = UserVoteSerializer(votes, many=True)
        logger.info(f"Fetched {len(votes)} votes for user {request.user.id}")
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error fetching user votes for {request.user.id}: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)