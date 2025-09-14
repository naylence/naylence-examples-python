import asyncio

from naylence.fame.core import FameFabric
from naylence.fame.service import operation
from naylence.agent import Agent, BaseAgent
from naylence.fame.util.logging import enable_logging

enable_logging(log_level="warning")  # Enable trace logging for debugging


class SimpleAgent(BaseAgent):
    @operation  # exposed as "add"
    async def add(self, x: int, y: int) -> int:
        # print("Adding", x, "and", y)
        # if True:  # Simulate occasional failure
        #     raise Exception("Simulated failure")
        return x + y

    @operation(
        name="fib_stream", streaming=True
    )  # exposed as "fib_stream" with streaming enabled
    async def fib(self, n: int):
        a, b = 0, 1
        for _ in range(n):
            yield a
            a, b = b, a + b


async def main():
    # --- Start a FameFabric session and serve the agent ---
    async with FameFabric.create() as fabric:
        # Register the SimpleAgent with the fabric and get its address.
        # In real deployments, this would happen in the agent runtime process.
        agent_address = await fabric.serve(SimpleAgent())

        # Resolve a remote proxy to the agent.
        # This simulates a client or external caller invoking the agent.
        agent = Agent.remote_by_address(agent_address)

        # Send a new task to the remote agent.
        print(await agent.add(x=3, y=4))

        async for v in await agent.fib_stream(_stream=True, n=10):
            print(v, end=" ")
        print()


# Entry point for running this script directly.
if __name__ == "__main__":
    asyncio.run(main())
