import asyncio
from datetime import datetime, timezone

from common import AGENT_ADDR
from naylence.fame.core import FameFabric

from naylence.agent import Agent, configs


async def main():
    async with FameFabric.create(root_config=configs.CLIENT_CONFIG):
        agent = Agent.remote_by_address(AGENT_ADDR)
        key = f"key_{int(datetime.now(timezone.utc).timestamp() * 1000)}"

        stored_value = await agent.store_value(key, "Hello, World!")
        print(f"\nStored value: {stored_value}")

        retrieved_value = await agent.retrieve_value(key)
        print(f"\nRetrieved value: {retrieved_value}")

        print("\nAll stored key-values:")
        counter = 0
        async for v in await agent.retrieve_all_values(_stream=True):
            print(v)
            counter += 1
        print(f"\nTotal stored values: {counter}")


if __name__ == "__main__":
    asyncio.run(main())
