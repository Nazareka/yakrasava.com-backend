from django.utils.translation import gettext_lazy as _
from urllib.parse import parse_qs

from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

class TokenAuthMiddleware:
    """
    Custom token auth middleware
    """
    def get_validated_token(self, token):
        messages = []
        for AuthToken in api_settings.AUTH_TOKEN_CLASSES:
            try:
                return AuthToken(token)
            except TokenError as e:
                messages.append({'token_class': AuthToken.__name__,
                                 'token_type': AuthToken.token_type,
                                 'message': e.args[0]})

        raise InvalidToken({
            'detail': _('Given token not valid for any token type'),
            'messages': messages,
        })
    def get_user(self, validated_token):
        try:
            user_id = validated_token[api_settings.USER_ID_CLAIM]
        except KeyError:
            raise InvalidToken(_('Token contained no recognizable user identification'))

        return user_id

    def __init__(self, inner):
        # Store the ASGI application we were passed
        self.inner = inner

    def __call__(self, scope):
        # Get the token
        token = parse_qs(scope["query_string"].decode("utf8"))["token"][0]
        try:
            validated_token = self.get_validated_token(token)
            user_id = self.get_user(validated_token)
            scope["user_id"] = user_id
            return self.inner(dict(scope, user_id=user_id, response='success'))
        except InvalidToken:
            return self.inner(dict(scope, user_id=None, response='InvalidToken'))
    
TokenAuthMiddlewareStack = lambda inner: TokenAuthMiddleware(inner)