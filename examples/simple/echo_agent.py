import asyncio
from typing import Any

from naylence.fame.core import FameFabric

from naylence.agent import Agent, BaseAgent
from naylence.fame.util.logging import enable_logging

enable_logging(log_level="warning")


class EchoAgent(BaseAgent):
    async def run_task(self, payload: Any, id: Any) -> Any:
        return payload


async def main():
    # --- Start a FameFabric session and serve the agent ---
    async with FameFabric.create() as fabric:
        # Register the SimpleAgent with the fabric and get its address.
        # In real deployments, this would happen in the agent runtime process.
        agent_address = await fabric.serve(EchoAgent())

        # Resolve a remote proxy to the agent.
        # This simulates a client or external caller invoking the agent.
        remote = Agent.remote_by_address(agent_address)

        # Send a new task to the remote agent.
        result = await remote.run_task(payload="Hello, World!")
        print(result)


# Entry point for running this script directly.
if __name__ == "__main__":
    asyncio.run(main())
