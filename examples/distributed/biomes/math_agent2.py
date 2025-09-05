import asyncio

from naylence.fame.service import operation

from common import MATH_AGENT1_ADDR, MATH_AGENT2_ADDR
from naylence.agent import Agent, BaseAgent, dev_mode


class MathAgent(BaseAgent):
    
    @operation(name="multiply")
    async def multi(self, x: int, y: int) -> int:
        agent1 = Agent.remote_by_address(MATH_AGENT1_ADDR)
        return await agent1.multiply(x=x, y=y) # type: ignore
    
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
            MATH_AGENT2_ADDR, root_config=dev_mode.NODE_CONFIG, log_level="trace"
        )
    )
