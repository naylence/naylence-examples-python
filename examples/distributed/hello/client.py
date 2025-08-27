import asyncio

from common import AGENT_ADDR
from naylence.fame.core import FameFabric

from naylence.agent import Agent, dev_mode
from naylence.fame.util.logging import enable_logging

enable_logging(log_level="warning")


async def main():
    async with FameFabric.create(root_config=dev_mode.CLIENT_CONFIG):
        remote = Agent.remote(address=AGENT_ADDR)
        result = await remote.run_task("Hello, World!")
        print(result)


if __name__ == "__main__":
    asyncio.run(main())
