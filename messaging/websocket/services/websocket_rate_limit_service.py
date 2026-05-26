from django.core.cache import cache


class WebsocketRateLimitService:

    @staticmethod
    def _key(user_id, action):
        return (
            f"ws:rate_limit:{action}:{user_id}"
        )

    @classmethod
    def allow(
        cls,
        *,
        user_id,
        action,
        limit,
        ttl=60,
    ):

        key = cls._key(
            user_id,
            action,
        )

        current = cache.get(key, 0)

        if current >= limit:
            return False

        cache.set(
            key,
            current + 1,
            timeout=ttl,
        )

        return True