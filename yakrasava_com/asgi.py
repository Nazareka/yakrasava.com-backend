import os

from django.urls import re_path

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.layers import get_channel_layer

from apps.web_socket import consumers, authentication

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "yakrasava_com.settings")

channel_layer = get_channel_layer()

websocket_urlpatterns = [
    re_path(r'ws/user$', consumers.UserConsumer),
]

application = ProtocolTypeRouter({
    # http is channels.http.AsgiHandler by default 
    'websocket': authentication.TokenAuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})

application = application