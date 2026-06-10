from asgiref.sync import async_to_sync

from channels.layers import get_channel_layer


class RealtimeService:

    # =====================================
    # GROUP NAMES
    # =====================================

    @staticmethod
    def get_user_group_name(user_id):

        return f"user_{user_id}"

    @staticmethod
    def get_conversation_group_name(
        conversation_id,
    ):

        return (
            f"conversation_{conversation_id}"
        )

    # =====================================
    # MESSAGE
    # =====================================

    @classmethod
    def broadcast_new_message(
        cls,
        *,
        conversation_id,
        payload,
    ):

        channel_layer = get_channel_layer()

        async_to_sync(
            channel_layer.group_send
        )(
            cls.get_conversation_group_name(
                conversation_id
            ),
            {
                "type": "new_message",
                "data": payload,
            },
        )

    # =====================================
    # MESSAGE READ
    # =====================================

    @classmethod
    def broadcast_message_read(
        cls,
        *,
        conversation_id,
        payload,
    ):

        channel_layer = get_channel_layer()

        async_to_sync(
            channel_layer.group_send
        )(
            cls.get_conversation_group_name(
                conversation_id
            ),
            {
                "type": "message_read",
                "data": payload,
            },
        )

    # =====================================
    # NOTIFICATION
    # =====================================

    @classmethod
    def broadcast_notification(
        cls,
        *,
        user_id,
        payload,
    ):

        channel_layer = get_channel_layer()

        async_to_sync(
            channel_layer.group_send
        )(
            cls.get_user_group_name(user_id),
            {
                "type": "notification_event",
                "data": payload,
            },
        )

    # =====================================
    # PRESENCE
    # =====================================

    @classmethod
    def broadcast_presence(
        cls,
        *,
        user_id,
        payload,
    ):

        channel_layer = get_channel_layer()

        async_to_sync(
            channel_layer.group_send
        )(
            cls.get_user_group_name(user_id),
            {
                "type": "presence_event",
                "data": payload,
            },
        )


    #=======================================
    #CONVERSATION REALTIME UPDATE
    #======================================

    @classmethod
    def broadcast_conversation_updated(
        cls,
        *,
        user_id,
        payload,
    ):
        
        print(
            "GROUP SEND",
            cls.get_user_group_name(user_id),
            payload.get("unread_count"),
        )

        channel_layer = get_channel_layer()

        async_to_sync(
            channel_layer.group_send
        )(
            cls.get_user_group_name(user_id),
            {
                "type": "conversation_updated",
                "data": payload,
            },
        )