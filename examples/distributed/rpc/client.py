import asyncio

from common import AGENT_ADDR
from naylence.fame.core import FameFabric

from naylence.agent import Agent, dev_mode


async def main():
    async with FameFabric.create(root_config=dev_mode.CLIENT_CONFIG):
        agent = Agent.remote_by_address(AGENT_ADDR)
        print(await agent.add(x=3, y=4))
        print(await agent.multiply(x=6, y=7))

        async for v in await agent.fib_stream(_stream=True, n=10):
            print(v, end=" ")
        print()


if __name__ == "__main__":
    asyncio.run(main())
