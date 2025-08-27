import asyncio

from typing import Any
from common import AGENT_ADDR
from naylence.agent import BaseAgent, dev_mode


class EchoAgent(BaseAgent):
    async def run_task(self, payload: Any, id: Any) -> Any:
        return payload


if __name__ == "__main__":
    asyncio.run(
        EchoAgent().aserve(
            AGENT_ADDR, root_config=dev_mode.NODE_CONFIG, log_level="trace"
        )
    )
