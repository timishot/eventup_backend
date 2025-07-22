from django.urls import path
from . import views

urlpatterns = [
    path('<uuid:event_uuid>/questions/', views.question_list_create, name='question-list-create'),
    path('<uuid:event_uuid>/answers/', views.answer_list_create, name='answer-list-create'),
    path('<uuid:question_id>/', views.question_detail, name='question-detail'),
]