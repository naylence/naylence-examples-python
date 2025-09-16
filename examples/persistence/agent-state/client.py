import asyncio
from datetime import datetime, timezone

from common import AGENT_ADDR
from naylence.fame.core import FameFabric

from naylence.agent import Agent, configs
from naylence.fame.util.logging import enable_logging


enable_logging(log_level="warning")


async def main():
    async with FameFabric.create(root_config=configs.CLIENT_CONFIG):
        agent = Agent.remote_by_address(AGENT_ADDR)

        retrieved_state = await agent.retrieve_value()
        print(f"Previous state: {retrieved_state}")

        value = f"{int(datetime.now(timezone.utc).timestamp() * 1000)}"
        stored_state = await agent.store_value(value)
        print(f"Updated state: {stored_state}")


if __name__ == "__main__":
    asyncio.run(main())
