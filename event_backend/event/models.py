import uuid
from  django.conf import  settings
from django.db import models
from django.db.models import CharField

from useraccount.models import User
from category.models import Category
# Create your models here.

class Event(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title =models.CharField(max_length=255)
    description = models.TextField()
    imagesUrl = models.CharField(max_length=255)
    categoryId = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='events')
    price = models.CharField(max_length=50)
    isFree = models.BooleanField(default=False)
    startDateTime = models.DateTimeField()
    endDateTime = models.DateTimeField()
    url =models.CharField(max_length=255, blank=True, null=True)
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events')
    created_at = models.DateTimeField(auto_now_add=True)

    def image_url(self):
        return f'{settings.WEBSITE_URL}{self.images.url}'