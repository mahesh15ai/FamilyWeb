import logging
from urllib.parse import parse_qs
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import AccessToken

logger = logging.getLogger(__name__)
User = get_user_model()


@database_sync_to_async
def get_user_from_token(token_str):
    try:
        # Clean token string
        token_str = token_str.strip().replace("Bearer ", "").replace('"', '').replace("'", "")
        access_token = AccessToken(token_str)
        user_id = access_token.get("user_id")
        if not user_id:
            return AnonymousUser()
        return User.objects.get(id=user_id)
    except Exception as e:
        logger.warning(f"WebSocket Auth Error: {e}")
        return AnonymousUser()


class JwtAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        query_string = scope.get("query_string", b"").decode("utf-8")
        query_params = parse_qs(query_string)
        token_list = query_params.get("token", None)

        if token_list and token_list[0]:
            scope["user"] = await get_user_from_token(token_list[0])
        else:
            scope["user"] = AnonymousUser()

        return await self.inner(scope, receive, send)