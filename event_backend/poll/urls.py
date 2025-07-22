from django.urls import path
from .views import poll_list_create, poll_vote, user_votes

urlpatterns = [
    path('<uuid:event_uuid>/polls/', poll_list_create, name='poll_list_create'),
    path('polls/<uuid:question_id>/vote/', poll_vote, name='poll_vote'),
    path('user-votes/', user_votes, name='user_votes'),
]