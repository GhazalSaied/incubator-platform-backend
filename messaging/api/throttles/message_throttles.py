

from rest_framework.throttling import UserRateThrottle


class SendMessageThrottle(UserRateThrottle):

    scope = "send_message"


class ReadConversationThrottle(
    UserRateThrottle
):

    scope = "read_conversation"