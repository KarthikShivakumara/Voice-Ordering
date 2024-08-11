from django.urls import path
from .views import recognize_order, list_orders, confirm_order

urlpatterns = [
    path('recognize-order/', recognize_order, name='recognize_order'),
    path('list-orders/', list_orders, name='list_orders'),
    path('confirm-order/<int:order_id>/', confirm_order, name='confirm_order'),
]
    