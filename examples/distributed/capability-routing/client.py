import asyncio
from typing import Any

from common import MATH_CAPABILITY
from naylence.fame.core import FameFabric, AGENT_CAPABILITY

from naylence.agent import Agent, dev_mode
from naylence.fame.util.logging import enable_logging


enable_logging(log_level="warning")


async def main():
    async with FameFabric.create(root_config=dev_mode.CLIENT_CONFIG):
        math_agent: Any = Agent.remote_by_capabilities(
            [AGENT_CAPABILITY, MATH_CAPABILITY]
        )
        print(await math_agent.add(x=3, y=4))
        print(await math_agent.multiply(x=6, y=7))

        async for v in await math_agent.fib_stream(n=10, _stream=True):
            print(v, end=" ")
        print()


if __name__ == "__main__":
    asyncio.run(main())
