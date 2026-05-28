class PresenceConstants:

    # ==========================================
    # Presence TTL
    # ==========================================

    ONLINE_TTL = 70

    HEARTBEAT_INTERVAL = 30

    STALE_TOLERANCE = 90

    RECONNECT_GRACE_PERIOD = 15

    LAST_SEEN_TTL = 60 * 60 * 24 * 30

    # ==========================================
    # Redis Keys
    # ==========================================

    USER_CONNECTIONS_KEY = (
        "presence:user:{user_id}:connections"
    )

    USER_HEARTBEAT_KEY = (
        "presence:user:{user_id}:heartbeat"
    )

    USER_STATUS_KEY = (
        "presence:user:{user_id}:status"
    )

    SOCKET_HEARTBEAT_KEY = (
        "presence:heartbeat:{socket_id}"
    )

    USER_LAST_SEEN_KEY = (
        "presence:last_seen:{user_id}"
    )

    ONLINE_USERS_KEY = (
        "presence:online_users"
    )

    # ==========================================
    # Presence Status
    # ==========================================

    ONLINE = "ONLINE"

    OFFLINE = "OFFLINE"

    AWAY = "AWAY"

    # ==========================================
    # Presence Events
    # ==========================================

    USER_ONLINE_EVENT = "USER_ONLINE"

    USER_OFFLINE_EVENT = "USER_OFFLINE"

    USER_PRESENCE_SYNC_EVENT = (
        "USER_PRESENCE_SYNC"
    )