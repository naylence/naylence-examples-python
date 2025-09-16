import asyncio

from common import MATH_CAPABILITY

from naylence.fame.core import AGENT_CAPABILITY
from naylence.fame.service import operation
from naylence.agent import BaseAgent, configs


class MathAgent(BaseAgent):
    def __init__(self, name: str | None = None):
        super().__init__(name=name)
        self._capabilities = [AGENT_CAPABILITY, MATH_CAPABILITY]

    @property
    def capabilities(self):
        return self._capabilities

    @operation  # exposed as "add"
    async def add(self, x: int, y: int) -> int:
        return x + y

    @operation(name="multiply")  # exposed as "multiply"
    async def multi(self, x: int, y: int) -> int:
        return x * y

    @operation(
        name="fib_stream", streaming=True
    )  # exposed as "fib_stream" with streaming enabled
    async def fib(self, n: int):
        a, b = 0, 1
        for _ in range(n):
            yield a
            a, b = b, a + b


if __name__ == "__main__":
    asyncio.run(
        MathAgent().aserve(
            "math@fame.fabric", root_config=configs.NODE_CONFIG, log_level="warning"
        )
    )
