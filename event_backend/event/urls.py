from django.urls import path, include

from . import api
from .views import event_list_create, event_detail, event_detail_get, related_events, events_by_user, \
    get_profile_user_event

urlpatterns = [
    path('', event_list_create, name='event_list'),
    path('<uuid:event_id>/', event_detail, name='event-detail'),
    path('<uuid:event_id>/event/', event_detail_get, name='event-detail-get'),
    path('related/', related_events, name='related-events'),
    path('organized/', events_by_user, name='events_by_user'),
    path('profile/event/', event_list_create, name='profile_event_list_create'),
]
