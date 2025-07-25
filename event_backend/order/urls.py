from django.urls import path

from .views import create_order, get_user_orders, get_orders_by_event

urlpatterns = [
    path('create/', create_order, name='create_order'),
    path('orderlist/', get_user_orders, name='get_user_orders'),
    path('event-orders/', get_orders_by_event, name='get_orders_by_event'),
]