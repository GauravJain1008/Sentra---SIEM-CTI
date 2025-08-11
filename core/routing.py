from django.urls import re_path
from .consumers import LiveLogConsumer

websocket_urlpatterns = [
    re_path(r"ws/logs/$", LiveLogConsumer.as_asgi()),
]
