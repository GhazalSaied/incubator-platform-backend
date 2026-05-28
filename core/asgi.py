
import os
import django

from channels.routing import (
    ProtocolTypeRouter,
    URLRouter,
)

from django.core.asgi import (
    get_asgi_application,
)

from messaging.websocket.middleware.jwt_auth_middleware import (
    JWTAuthMiddleware,
)


import messaging.websocket.routing

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "core.settings",
)

django.setup()

application = ProtocolTypeRouter({

    "http": get_asgi_application(),

    "websocket": JWTAuthMiddleware(

        URLRouter(
            
            messaging.websocket.routing.websocket_urlpatterns

        )

    ),
})

