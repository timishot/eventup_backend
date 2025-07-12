import uuid
from django.db import models
from event.models import Event  # Adjust if your app name is different
from useraccount.models import User # Adjust for your actual user model


class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    stripe_id = models.CharField(max_length=255, unique=True)
    total_amount = models.CharField(max_length=100)

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='orders')
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')

    def __str__(self):
        return f"Order #{self.id} - {self.stripe_id}"
