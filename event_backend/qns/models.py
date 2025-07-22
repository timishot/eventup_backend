import uuid
from django.db import models
from event.models import Event
from useraccount.models import User

class Question(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    text = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='qns_questions')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='qns_questions')
    is_answered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.text

class Answer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    text = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='qns_answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='qns_answers')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.text