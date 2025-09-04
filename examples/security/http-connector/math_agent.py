import asyncio

from common import AGENT_ADDR
from naylence.fame.service import operation
from naylence.agent import BaseAgent


class MathAgent(BaseAgent):
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
    """
    No config file is specified here. This demonstrates configuring the Naylence node
    using the default config at /etc/fame/fame-config.yml, which is mounted via Docker Compose.
    """
    asyncio.run(
        MathAgent().aserve(
            AGENT_ADDR, log_level="trace"
        )
    )
