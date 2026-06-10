from channels.generic.websocket import (
    AsyncJsonWebsocketConsumer,
)

from messaging.websocket.services.realtime_presence_service import (
    RealtimePresenceService,
)

from messaging.domain.services.realtime_service import (
    RealtimeService,
)

from channels.db import database_sync_to_async

from messaging.domain.selectors.conversation_selectors import (
    get_user_conversation_by_id,
)

from messaging.websocket.services.websocket_rate_limit_service import (
    WebsocketRateLimitService,
)


class RealtimeConsumer(
    AsyncJsonWebsocketConsumer
):

    @database_sync_to_async
    def _user_has_access_to_conversation(
        self,
        conversation_id,
    ):
        return bool(
            get_user_conversation_by_id(
                user=self.user,
                conversation_id=conversation_id,
            )
        )

    # =====================================
    # PRESENCE WRAPPERS
    # =====================================

    @database_sync_to_async
    def _connect_user_presence(self):

        RealtimePresenceService.connect_user(
            self.user.id
        )

    @database_sync_to_async
    def _disconnect_user_presence(self):

        RealtimePresenceService.disconnect_user(
            self.user.id
        )

    @database_sync_to_async
    def _refresh_user_presence(self):

        RealtimePresenceService.refresh_user_presence(
            self.user.id
        )

    @database_sync_to_async
    def _subscribe_conversation_presence(
        self,
        conversation_id,
    ):

        RealtimePresenceService.subscribe_conversation(
            user_id=self.user.id,
            conversation_id=conversation_id,
        )

    @database_sync_to_async
    def _unsubscribe_conversation_presence(
        self,
        conversation_id,
    ):

        RealtimePresenceService.unsubscribe_conversation(
            user_id=self.user.id,
            conversation_id=conversation_id,
        )

    # =====================================
    # CONNECT
    # =====================================

    async def connect(self):

        print("========== WS CONNECT ==========")
        print(
        "WS CONNECT USER",
        self.scope["user"].id,
        self.scope["user"].email,
    )

        user = self.scope.get("user")

        if not user or user.is_anonymous:
            await self.close()
            return

        self.user = user

        self.user_group_name = (
            RealtimeService.get_user_group_name(
                self.user.id
            )
        )

        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name,
        )

        await self._connect_user_presence()

        await self.accept()

        await self.send_json({
            "type": "TEST",
            "message": "CONNECTED"
        })

        await self.send_json({
            "type": "DEBUG_TEST",
            "message": "FROM_CONSUMER"
        })

    # =====================================
    # DISCONNECT
    # =====================================

    async def disconnect(
        self,
        close_code,
    ):

        if hasattr(self, "user"):

            await self.channel_layer.group_discard(
                self.user_group_name,
                self.channel_name,
            )

            await self._disconnect_user_presence()

    # =====================================
    # RECEIVE JSON
    # =====================================

    async def receive_json(
        self,
        content,
        **kwargs,
    ):
        print(
            "RAW WS MESSAGE:",
            content
        )

        event_type = content.get("type")

        # =================================
        # HEARTBEAT
        # =================================

        if event_type == "HEARTBEAT":

            allowed = (
                WebsocketRateLimitService.allow(
                    user_id=self.user.id,
                    action="heartbeat",
                    limit=120,
                )
            )

            if not allowed:

                await self.send_json({
                    "type": "ERROR",
                    "code": "RATE_LIMITED",
                })

                return

            await self._refresh_user_presence()

            await self.send_json({
                "type": "HEARTBEAT_ACK",
            })

            return

        # =================================
        # SUBSCRIBE CONVERSATION
        # =================================

        if event_type == "SUBSCRIBE_CONVERSATION":

            allowed = (
                WebsocketRateLimitService.allow(
                    user_id=self.user.id,
                    action="subscription",
                    limit=100,
                )
            )

            if not allowed:

                await self.send_json({
                    "type": "ERROR",
                    "code": "RATE_LIMITED",
                })

                return

            conversation_id = content.get(
                "conversation_id"
            )
            print(
                "SUBSCRIBE_CONVERSATION",
                conversation_id
            )

            if not conversation_id:
                return

            try:
                conversation_id = int(conversation_id)

            except (
                TypeError,
                ValueError,
            ):

                await self.send_json({
                    "type": "ERROR",
                    "code": "INVALID_CONVERSATION_ID",
                })

                return

            has_access = await self._user_has_access_to_conversation(
                conversation_id
            )

            if not has_access:

                await self.send_json({
                    "type": "ERROR",
                    "code": "CONVERSATION_ACCESS_DENIED",
                })

                return

            conversation_group = (
                RealtimeService
                .get_conversation_group_name(
                    conversation_id
                )
            )

            await self.channel_layer.group_add(
                conversation_group,
                self.channel_name,
            )

            await self._subscribe_conversation_presence(
                conversation_id
            )

            await self.send_json({
                "type": "SUBSCRIBED",
                "conversation_id": conversation_id,
            })

            return

        # =================================
        # UNSUBSCRIBE CONVERSATION
        # =================================

        if (
            event_type
            == "UNSUBSCRIBE_CONVERSATION"
        ):

            allowed = (
                WebsocketRateLimitService.allow(
                    user_id=self.user.id,
                    action="subscription",
                    limit=100,
                )
            )

            if not allowed:

                await self.send_json({
                    "type": "ERROR",
                    "code": "RATE_LIMITED",
                })

                return

            conversation_id = content.get(
                "conversation_id"
            )

            if not conversation_id:
                return

            conversation_group = (
                RealtimeService
                .get_conversation_group_name(
                    conversation_id
                )
            )

            await self.channel_layer.group_discard(
                conversation_group,
                self.channel_name,
            )

            await self._unsubscribe_conversation_presence(
                conversation_id
            )

            await self.send_json({
                "type": "UNSUBSCRIBED",
                "conversation_id": conversation_id,
            })

            return

    # =====================================
    # OUTGOING EVENTS
    # =====================================

    async def new_message(
        self,
        event,
    ):

        await self.send_json({
            "type": "NEW_MESSAGE",
            "data": event["data"],
        })

    async def message_read(
        self,
        event,
    ):

        await self.send_json({
            "type": "MESSAGE_READ",
            "data": event["data"],
        })

    async def notification_event(
        self,
        event,
    ):

        await self.send_json({
            "type": "NOTIFICATION",
            "data": event["data"],
        })

    async def conversation_updated(
        self,
        event,
    ):
        
        print(
            "WS SEND CONVERSATION_UPDATED TO",
            self.user.id,
            event["data"].get("unread_count"),
        )

        await self.send_json({
            "type": "CONVERSATION_UPDATED",
            "data": event["data"],
        })

    async def presence_event(
        self,
        event,
    ):

        await self.send_json({
            "type": "PRESENCE",
            "data": event["data"],
        })