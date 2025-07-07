from django.urls import path, include

from . import api
from .views import event_list_create

urlpatterns = [
    path('', event_list_create, name='event_list'),
]