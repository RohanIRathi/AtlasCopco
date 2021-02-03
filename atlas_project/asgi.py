import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'atlas_project.settings')
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

import stream.routing

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    # Just HTTP for now. (We can add other protocols later.)
    "websocket": AuthMiddlewareStack(
        URLRouter(
            stream.routing.websocket_urlpatterns
        )
    ),
})