from django.urls import path

from .views import create_order, get_user_orders

urlpatterns = [
    path('create/', create_order, name='create_order'),
    path('orderlist/', get_user_orders, name='get_user_orders'),
]