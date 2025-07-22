from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django.core.exceptions import ObjectDoesNotExist
from .models import Question, Answer
from .serializers import QuestionSerializer, AnswerSerializer
from event.models import Event
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import logging

logger = logging.getLogger(__name__)

class QnSPagination(PageNumberPagination):
    page_size = 10

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def question_list_create(request, event_uuid):
    try:
        event = Event.objects.get(id=event_uuid)
    except ObjectDoesNotExist:
        logger.error(f"Event {event_uuid} does not exist")
        return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        pagination = QnSPagination()
        questions = Question.objects.filter(event_id=event_uuid).order_by('-created_at')
        paginated_questions = pagination.paginate_queryset(questions, request)
        serializer = QuestionSerializer(paginated_questions, many=True)
        return pagination.get_paginated_response(serializer.data)

    elif request.method == 'POST':
        if not request.user.is_authenticated:
            return Response({'detail': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        data = request.data.copy()
        data['event_uuid'] = str(event_uuid)
        serializer = QuestionSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            question = serializer.save()
            logger.info(f"Q&A question created for event {event_uuid}: {question.id}")
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"event_{event_uuid}",
                {
                    'type': 'qna_update',
                    'question': serializer.data
                }
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.error(f"Q&A question creation failed for event {event_uuid}: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def answer_list_create(request, event_uuid):
    try:
        event = Event.objects.get(id=event_uuid)
    except ObjectDoesNotExist:
        logger.error(f"Event {event_uuid} does not exist")
        return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)

    question_id = request.data.get('question_id')
    if request.method == 'POST' and not question_id:
        return Response({'detail': 'question_id is required'}, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'GET':
        question_id = request.GET.get('question_id')
        if not question_id:
            return Response({'detail': 'question_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        answers = Answer.objects.filter(question_id=question_id).order_by('-created_at')
        serializer = AnswerSerializer(answers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        if not request.user.is_authenticated:
            return Response({'detail': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            question = Question.objects.get(id=question_id, event_id=event_uuid)
        except ObjectDoesNotExist:
            logger.error(f"Question {question_id} does not exist for event {event_uuid}")
            return Response({'detail': 'Question not found'}, status=status.HTTP_404_NOT_FOUND)
        data = request.data.copy()
        data['event_uuid'] = str(event_uuid)
        data['question'] = question_id
        serializer = AnswerSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            answer = serializer.save()
            logger.info(f"Answer created for question {question_id}: {answer.id}")
            question_serializer = QuestionSerializer(question)
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"event_{event_uuid}",
                {
                    'type': 'qna_update',
                    'question': question_serializer.data
                }
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.error(f"Answer creation failed for question {question_id}: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticatedOrReadOnly])
def question_detail(request, event_uuid, question_id):
    try:
        question = Question.objects.get(id=question_id, event_id=event_uuid)
    except ObjectDoesNotExist:
        logger.error(f"Question {question_id} does not exist for event {event_uuid}")
        return Response({'detail': 'Question not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = QuestionSerializer(question)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method in ['PUT', 'DELETE']:
        if not request.user.is_authenticated:
            return Response({'detail': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        if request.user != question.event.organizer:
            return Response({'detail': 'Only the event organizer can modify or delete questions'}, status=status.HTTP_403_FORBIDDEN)

        if request.method == 'PUT':
            data = request.data.copy()
            data['event_uuid'] = str(event_uuid)
            serializer = QuestionSerializer(question, data=data, partial=True, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                logger.info(f"Question {question_id} updated for event {event_uuid}")
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f"event_{event_uuid}",
                    {
                        'type': 'qna_update',
                        'question': serializer.data
                    }
                )
                return Response(serializer.data, status=status.HTTP_200_OK)
            logger.error(f"Question update failed for {question_id}: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        elif request.method == 'DELETE':
            question.delete()
            logger.info(f"Question {question_id} deleted for event {event_uuid}")
            return Response({'detail': 'Question deleted successfully'}, status=status.HTTP_204_NO_CONTENT)