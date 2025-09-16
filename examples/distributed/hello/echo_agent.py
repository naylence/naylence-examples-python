import asyncio

from typing import Any
from common import AGENT_ADDR
from naylence.agent import BaseAgent, configs


class EchoAgent(BaseAgent):
    async def run_task(self, payload: Any, id: Any) -> Any:
        return payload


if __name__ == "__main__":
    asyncio.run(
        EchoAgent().aserve(
            AGENT_ADDR, root_config=configs.SENTINEL_CONFIG, log_level="info"
        )
    )
