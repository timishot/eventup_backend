from django.db import models

import uuid
from useraccount.models import User

class Relationship(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
    )
    followee = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followers'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'followee')
        indexes = [
            models.Index(fields=['follower']),
            models.Index(fields=['followee']),
        ]

    def __str__(self):
        return f"{self.follower.email} follows {self.followee.email}"