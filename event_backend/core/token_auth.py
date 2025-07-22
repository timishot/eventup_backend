import logging
import jwt
from urllib.parse import parse_qs
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.conf import settings

logger = logging.getLogger(__name__)
User = get_user_model()

@database_sync_to_async
def get_user(user_id):
    try:
        user = User.objects.get(id=user_id)
        logger.debug(f"TokenAuth: Retrieved user {user.id} ({user.username})")
        return user
    except User.DoesNotExist:
        logger.warning(f"TokenAuth: User {user_id} not found")
        return AnonymousUser()
    except Exception as e:
        logger.error(f"TokenAuth: Error retrieving user: {str(e)}")
        return AnonymousUser()

class TokenAuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        query_string = scope.get("query_string", b"").decode()
        query_params = parse_qs(query_string)
        token = query_params.get("token", [None])[0]

        logger.debug(f"TokenAuth: Query string: {query_string}, Token: {token[:10] if token else None}...")
        print("live", token)

        if not token or not isinstance(token, str):
            logger.warning("TokenAuth: No valid token provided")
            print("no_token")
            scope["user"] = AnonymousUser()
        else:
            try:
                print("attempt_validation")
                decoded = jwt.decode(token, settings.SIMPLE_JWT['SIGNING_KEY'], algorithms=[settings.SIMPLE_JWT['ALGORITHM']])
                print("validated_token", decoded)
                print("love", decoded)
                user_id = decoded.get("user_id")
                if user_id:
                    scope["user"] = await get_user(user_id)
                    logger.info(f"TokenAuth: Set user {scope['user'].id} ({scope['user'].username or 'N/A'})")
                else:
                    logger.warning("TokenAuth: No user_id in token")
                    print("no_user_id")
                    scope["user"] = AnonymousUser()
            except jwt.PyJWTError as e:
                logger.error(f"TokenAuth: Token decode failed: {str(e)}")
                print("jwt_validation_failed", str(e))
                scope["user"] = AnonymousUser()
            except Exception as e:
                logger.error(f"TokenAuth: Unexpected error: {str(e)}")
                print("unexpected_error", str(e))
                scope["user"] = AnonymousUser()

        return await self.app(scope, receive, send)