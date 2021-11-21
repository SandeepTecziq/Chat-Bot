from django.urls import re_path, path

from . import consumers

websocket_urlpatterns = [
    # re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer),
    path('ws/chat_to_customer/<secret_key>/<user_email>/', consumers.ChatToCustomerConsumer.as_asgi()),
    path('ws/notify/<secret_key>/', consumers.Notify.as_asgi()),
    path('ws/alert_employee/<secret_key>/<employee_id>/', consumers.AlertEmployee.as_asgi()),
    # path('add_question/', consumers.Notify),
]

