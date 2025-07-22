from django.urls import path
from dj_rest_auth.jwt_auth import get_refresh_view
from dj_rest_auth.views import LoginView, LogoutView, UserDetailsView
from dj_rest_auth.registration.views import RegisterView
from rest_framework_simplejwt.views import TokenRefreshView

from .views import user_detail, update_profile, networking_suggestions

urlpatterns =[
    path('login/', LoginView.as_view(), name='rest_login'),
    path('logout/', LogoutView.as_view(), name='rest_logout'),
    path('register/', RegisterView.as_view(), name='rest_register'),
    path('user/', UserDetailsView.as_view(), name='rest_user_details'),
    path('<uuid:user_id>/', user_detail, name='user-detail'),
    path('update/', update_profile, name='update-profile'),
    path('suggestions/', networking_suggestions, name='networking-suggestions'),
]