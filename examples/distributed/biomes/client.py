import asyncio

from common import MATH_AGENT1_ADDR, MATH_AGENT2_ADDR
from naylence.fame.core import FameFabric
from naylence.agent import Agent, configs
from naylence.fame.util.logging import enable_logging

enable_logging(log_level="warning")


async def main():
    async with FameFabric.create(root_config=configs.CLIENT_CONFIG):
        agent1 = Agent.remote_by_address(MATH_AGENT1_ADDR)

        print(await agent1.add(x=3, y=4))

        agent2 = Agent.remote_by_address(MATH_AGENT2_ADDR)
        print(await agent2.multiply(x=6, y=7))

        async for v in await agent2.fib_stream(_stream=True, n=10):
            print(v, end=" ")
        print()


if __name__ == "__main__":
    asyncio.run(main())
