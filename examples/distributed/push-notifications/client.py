import asyncio

from common import RECEIVER_AGENT_ADDR
from naylence.fame.core import FameFabric

from naylence.agent import Agent, configs


async def main():
    async with FameFabric.create(root_config=configs.CLIENT_CONFIG):
        agent = Agent.remote_by_address(RECEIVER_AGENT_ADDR)
        result = await agent.run_task()
        print(result)


if __name__ == "__main__":
    asyncio.run(main())
