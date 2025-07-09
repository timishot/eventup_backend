from django.urls import path, include

from . import api
from .views import event_list_create, event_detail

urlpatterns = [
    path('', event_list_create, name='event_list'),
    path('<uuid:event_id>/', event_detail, name='event-detail'),
]