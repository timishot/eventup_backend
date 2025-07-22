import json
import logging
import uuid
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.utils import timezone
from poll.models import Question as PollQuestion, Choice, UserVote
from qns.models import Question as QnAQuestion, Answer
from event.models import Event
from qns.serializers import QuestionSerializer
from poll.serializers import PollQuestionSerializer

logger = logging.getLogger(__name__)
User = get_user_model()

class EventConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.event_id = self.scope['url_route']['kwargs']['event_id']
        self.event_group_name = f"event_{self.event_id}"
        query_string = self.scope.get('query_string', b'').decode()
        query_params = dict(qp.split('=') for qp in query_string.split('&') if '=' in qp)
        self.subscriptions = query_params.get('subscriptions', 'poll,qna').split(',')

        logger.info(f"WebSocket connecting for event {self.event_id} with subscriptions {self.subscriptions}")

        try:
            await database_sync_to_async(Event.objects.get)(id=self.event_id)
        except Event.DoesNotExist:
            logger.error(f"Event {self.event_id} does not exist")
            await self.close(code=4005)
            return

        await self.channel_layer.group_add(self.event_group_name, self.channel_name)
        await self.accept()

        try:
            user = self.scope.get('user')
            logger.debug(f"connect scope user: {user}, is_authenticated: {user.is_authenticated if user else False}")
            if user and user.is_authenticated:
                logger.info(f"Authenticated user: {user.id} ({user.username or 'N/A'})")
            else:
                logger.warning("No authenticated user in scope")
            await self.send_initial_data()
        except Exception as e:
            logger.error(f"Error during connect: {str(e)}")
            await self.send_json({'type': 'error', 'error': str(e)})
            await self.close(code=4000)

    async def disconnect(self, close_code):
        logger.info(f"WebSocket disconnected for event {self.event_id} with code {close_code}")
        await self.channel_layer.group_discard(self.event_group_name, self.channel_name)

    async def send_initial_data(self):
        if 'poll' in self.subscriptions:
            polls = await self.get_polls()
            for poll in polls:
                await self.send_json({
                    'type': 'poll_update',
                    'poll': poll
                })
        if 'qna' in self.subscriptions:
            questions = await self.get_questions()
            for question in questions:
                await self.send_json({
                    'type': 'qna_update',
                    'question': question
                })

    @database_sync_to_async
    def get_polls(self):
        try:
            event = Event.objects.get(id=self.event_id)
            polls = PollQuestion.objects.filter(event=event, is_active=True).select_related('event', 'user').prefetch_related('choices')
            serializer = PollQuestionSerializer(polls, many=True)
            logger.debug(f"Polls serialized data: {serializer.data}")
            return serializer.data
        except Exception as e:
            logger.error(f"Error in get_polls: {str(e)}")
            return []

    @database_sync_to_async
    def get_questions(self):
        try:
            event = Event.objects.get(id=self.event_id)
            questions = QnAQuestion.objects.filter(event=event).select_related('user', 'event').prefetch_related('answers')
            logger.debug(f"Retrieved {questions.count()} questions for event {self.event_id}")
            serialized_data = []
            for question in questions:
                try:
                    logger.debug(f"Processing question {question.id}: text={question.text}, user_id={question.user_id}, event_id={question.event_id}, is_answered={question.is_answered}")
                    if question.user:
                        logger.debug(f"User: id={question.user.id}, username={question.user.username}, email={question.user.email}")
                    else:
                        logger.warning(f"No user associated with question {question.id}")
                    if question.event:
                        logger.debug(f"Event: id={question.event.id}, title={question.event.title}")
                    else:
                        logger.warning(f"No event associated with question {question.id}")
                    for answer in question.answers.all():
                        logger.debug(f"Answer {answer.id}: text={answer.text}, user_id={answer.user_id}, event_id={answer.event_id}")
                    serializer = QuestionSerializer(question, context={'request': None})
                    serialized_data.append(serializer.data)
                    logger.debug(f"Serialized question {question.id}: {serializer.data}")
                except Exception as e:
                    logger.error(f"Serialization error for question {question.id}: {str(e)}")
                    raise
            logger.debug(f"Questions serialized data: {serialized_data}")
            return serialized_data
        except Exception as e:
            logger.error(f"Error in get_questions: {str(e)}")
            raise

    async def receive_json(self, content):
        logger.debug(f"receive_json scope user: {self.scope.get('user')}, is_authenticated: {self.scope.get('user').is_authenticated if self.scope.get('user') else False}")
        query_string = self.scope.get('query_string', b'').decode()
        query_params = dict(qp.split('=') for qp in query_string.split('&') if '=' in qp)
        token = query_params.get('token')

        if not token:
            logger.error("No token provided")
            await self.send_json({'type': 'error', 'error': 'Authentication required'})
            return

        user = self.scope.get('user')
        if not user or not user.is_authenticated:
            logger.error("User not authenticated in receive_json")
            await self.send_json({'type': 'error', 'error': 'Authentication required'})
            return

        action = content.get('action')
        if action == 'vote':
            question_id = content.get('question_id')
            choice_id = content.get('choice_id')
            try:
                if not question_id or not choice_id:
                    logger.error(f"Missing question_id or choice_id: question_id={question_id}, choice_id={choice_id}")
                    await self.send_json({'type': 'error', 'error': 'Missing question_id or choice_id'})
                    return
                try:
                    uuid.UUID(question_id)
                    uuid.UUID(choice_id)
                except ValueError:
                    logger.error(f"Invalid UUID format: question_id={question_id}, choice_id={choice_id}")
                    await self.send_json({'type': 'error', 'error': 'Invalid question_id or choice_id format'})
                    return

                try:
                    await database_sync_to_async(User.objects.get)(id=user.id)
                except User.DoesNotExist:
                    logger.error(f"User {user.id} does not exist in database")
                    await self.send_json({'type': 'error', 'error': 'User does not exist'})
                    return

                vote_data = await database_sync_to_async(self.create_vote)(question_id, choice_id, user)
                await self.channel_layer.group_send(
                    self.event_group_name,
                    {
                        'type': 'poll_update',
                        'poll': vote_data
                    }
                )
            except Exception as e:
                logger.error(f"Unexpected error in receive_json: {str(e)}")
                await self.send_json({'type': 'error', 'error': str(e)})
        elif action == 'new_answer':
            question_id = content.get('question_id')
            text = content.get('text')
            try:
                if not question_id or not text:
                    logger.error(f"Missing question_id or text: question_id={question_id}, text={text}")
                    await self.send_json({'type': 'error', 'error': 'Missing question_id or answer text'})
                    return
                try:
                    uuid.UUID(question_id)
                except ValueError:
                    logger.error(f"Invalid UUID format for question_id: {question_id}")
                    await self.send_json({'type': 'error', 'error': 'Invalid question_id format'})
                    return
                logger.info(f"Received answer for question {question_id}: {text}")
                question_data = await database_sync_to_async(self.handle_new_answer)(question_id, text, user)
                await self.channel_layer.group_send(
                    self.event_group_name,
                    {
                        'type': 'qna_update',
                        'question': question_data
                    }
                )
            except Exception as e:
                logger.error(f"Unexpected error in new_answer: {str(e)}")
                await self.send_json({'type': 'error', 'error': str(e)})

    async def poll_update(self, event):
        await self.send_json({
            'type': 'poll_update',
            'poll': event['poll']
        })

    async def qna_update(self, event):
        await self.send_json({
            'type': 'qna_update',
            'question': event['question']
        })

    def create_vote(self, question_id, choice_id, user):
        from django.db import transaction
        from django.utils import timezone
        try:
            with transaction.atomic():
                question = PollQuestion.objects.get(id=question_id)
                choice = Choice.objects.get(id=choice_id)
                if choice.question_id != question.id:
                    raise ValueError(f"Choice {choice_id} does not belong to question {question_id}")
                existing_vote = UserVote.objects.filter(user=user, choice__question=question).select_related('choice').first()
                if existing_vote:
                    if existing_vote.choice_id == choice.id:
                        raise ValueError("This choice is already selected")
                    old_choice = existing_vote.choice
                    old_choice.votes -= 1
                    old_choice.save()
                    existing_vote.choice = choice
                    existing_vote.created_at = timezone.now()
                    existing_vote.save()
                    choice.votes += 1
                    choice.save()
                else:
                    UserVote.objects.create(user=user, choice=choice)
                    choice.votes += 1
                    choice.save()
                question = PollQuestion.objects.prefetch_related('choices').get(id=question_id)
                serializer = PollQuestionSerializer(question)
                serialized_data = serializer.data
                logger.info(f"Vote created for question {question_id}, choice {choice_id} by user {user.id} ({user.username})")
                logger.debug(f"Vote serialized data: {serialized_data}")
                return serialized_data
        except Exception as e:
            logger.error(f"Error in create_vote: {str(e)}")
            raise

    def handle_new_answer(self, question_id, text, user):
        try:
            question = QnAQuestion.objects.get(id=question_id)
            logger.debug(f"Event ID: {self.event_id}")
            answer = Answer.objects.create(
                question=question,
                text=text,
                user=user,
                event_id=self.event_id,
                created_at=timezone.now(),
                updated_at=timezone.now()
            )
            logger.info(f"Answer created for question {question_id}: {text} by user {user.id} ({user.username})")
            question = QnAQuestion.objects.prefetch_related('answers').get(id=question_id)
            logger.debug(f"Question object: text={question.text}, user_id={question.user_id}, event_id={question.event_id}")
            serializer = QuestionSerializer(question, context={'request': None})
            serialized_data = serializer.data
            logger.debug(f"Serialized data: {serialized_data}")
            return serialized_data
        except QnAQuestion.DoesNotExist:
            logger.error(f"QnAQuestion does not exist: question_id={question_id}")
            raise ValueError(f"Question {question_id} does not exist")
        except Exception as e:
            logger.error(f"Error creating answer: {str(e)}")
            raise