from django.urls import path
from .views import follow_unfollow, followers_list, following_list

urlpatterns = [
    path('<uuid:user_id>/follow/', follow_unfollow, name='follow-unfollow'),
    path('<uuid:user_id>/followers/', followers_list, name='followers-list'),
    path('<uuid:user_id>/following/', following_list, name='following-list'),
]