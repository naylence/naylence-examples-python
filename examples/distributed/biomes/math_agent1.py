import asyncio

from naylence.fame.service import operation

from common import MATH_AGENT1_ADDR
from naylence.agent import BaseAgent, configs


class MathAgent(BaseAgent):
    @operation  # exposed as "add"
    async def add(self, x: int, y: int) -> int:
        return x + y

    @operation(name="multiply")  # exposed as "multiply"
    async def multi(self, x: int, y: int) -> int:
        return x * y


if __name__ == "__main__":
    asyncio.run(
        MathAgent().aserve(
            MATH_AGENT1_ADDR, root_config=configs.NODE_CONFIG, log_level="warning"
        )
    )
