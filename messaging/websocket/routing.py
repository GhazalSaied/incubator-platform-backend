from django.urls import path

from messaging.websocket.consumers.realtime_consumer import (
    RealtimeConsumer,
)

websocket_urlpatterns = [

    path(
        "ws/realtime/",
        RealtimeConsumer.as_asgi(),
    ),

]