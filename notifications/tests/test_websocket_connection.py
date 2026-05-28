import pytest

from channels.testing import (
    WebsocketCommunicator,
)

from core.asgi import application


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
class TestWebsocketConnection:

    async def test_websocket_connect_with_valid_token(
        self,
        access_token,
    ):

        communicator = WebsocketCommunicator(
            application,
            f"/ws/realtime/?token={access_token}",
        )

        try:

            connected, _ = await communicator.connect()

            assert connected is True

        finally:

            await communicator.disconnect()

    # -------------------------------------

    async def test_websocket_rejects_invalid_token(
        self,
    ):

        communicator = WebsocketCommunicator(
            application,
            "/ws/realtime/?token=invalid-token",
        )

        connected, _ = await communicator.connect()

        assert connected is False

    # -------------------------------------

    async def test_websocket_rejects_missing_token(
        self,
    ):

        communicator = WebsocketCommunicator(
            application,
            "/ws/realtime/",
        )

        connected, _ = await communicator.connect()

        assert connected is False