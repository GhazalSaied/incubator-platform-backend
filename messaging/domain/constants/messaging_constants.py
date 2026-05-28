class ConversationType:
    PRIVATE = "PRIVATE"
    GROUP = "GROUP"

    CHOICES = (
        (PRIVATE, "Private"),
        (GROUP, "Group"),
    )


class WebSocketEventType:
    NEW_MESSAGE = "NEW_MESSAGE"
    MESSAGE_READ = "MESSAGE_READ"
    USER_ONLINE = "USER_ONLINE"
    USER_OFFLINE = "USER_OFFLINE"
    CONVERSATION_UPDATED = "CONVERSATION_UPDATED"