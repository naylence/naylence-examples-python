import asyncio
from typing import Any, Optional


from lost_ack_simulator import LostAckSimulator
from common import AGENT_ADDR
from naylence.fame.core import (
    FameMessageResponse,
)
from naylence.agent import BaseAgent, configs


class MessageAgent(BaseAgent):
    async def start(self) -> None:
        """
        Sets up event handling for lost acknowledgments for demonstration purposes.
        Not required for retries in real systems.
        """
        from naylence.fame.node.node import get_node

        get_node().add_event_listener(LostAckSimulator())

    async def on_message(self, message: Any) -> Optional[FameMessageResponse]:
        print("MessageAgent received message:", message)


if __name__ == "__main__":
    asyncio.run(
        MessageAgent().aserve(
            AGENT_ADDR, root_config=configs.NODE_CONFIG, log_level="info"
        )
    )
