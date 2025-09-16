import asyncio
import sys
from typing import Any, Optional

from common import AGENT_ADDR
from naylence.fame.core import FameMessageResponse
from naylence.agent import BaseAgent, BaseAgentState, configs


class Counter(BaseAgentState):
    count: int = 0


class MessageAgent(BaseAgent[Counter]):
    async def on_message(self, message: Any) -> Optional[FameMessageResponse]:
        async with self.state as state:
            print("MessageAgent current state:", state.count)
            state.count += 1
            should_exit = bool(state.count % 2)

        if should_exit:
            await asyncio.sleep(1)
            print("MessageAgent simulating crash while processing message...")
            sys.exit(1)

        print("MessageAgent processed message successfully:", message)

        return None


if __name__ == "__main__":
    asyncio.run(
        MessageAgent().aserve(
            AGENT_ADDR, root_config=configs.NODE_CONFIG, log_level="info"
        )
    )
